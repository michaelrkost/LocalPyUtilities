import requests
import pandas as pd

import sys
from pathlib import Path 
sys.path.append('/home/michael/jupyter/local-packages')

from localUtilities import dateUtils
from localUtilities.ibUtils import getOptionPrice

# Chrome linux User Agent - needed to not get blocked as a bot
headers = {
 'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'}

pd.set_option('display.max_rows', 1000)

theBaseCompaniesDirectory = '/home/michael/jupyter/earningDateData/Companies/'

csvSuffix = '.csv'
excelSuffix = '.xlsx'

# TODO - do we need to do MinMaxDF for option prices??????
#=========================================================================
def getOccVolume(symbol):
    """
    Get option volume from OCC rather than IBKR as it is unreliable.
    Parameters
    ----------
    symbol : stock

    Returns
    -------
    Dataframe with all options
    """
    s = requests.Session()
    #ONN Volume Search
    # url = 'https://www.theocc.com/webapps/series-search'
    url = 'https://www.theocc.com/Market-Data/Market-Data-Reports/Series-and-Trading-Data/Series-Search'
    r = s.post(url,data={'symbolType': 'U','symbolText': symbol}, headers = headers)
    print("response:  ", r)
    r.close()

    # check to make sure passing a valid symbol
    try:
        df = pd.read_html(r.content)[0]
    except ValueError:
        print('     ', ValueError, 'In getOptionInfo.getOccVolume')
        print('              Symbol: ', symbol)
        df = pd.DataFrame()
        print('              df.empty: ', df.empty)
        return df
    df.columns = df.columns.droplevel()
    # Combine Cents/Decimal in Strike price
    df['Strike'] = df['Integer'] + (df['Dec']*0.001)
    cols_of_interest=['Product Symbol', 'Year', 'Month', 'Day', 'Strike', 'Call', 'Put']
    df = df[cols_of_interest]
    # get an expiry info
    df['expiry'] = df.apply(lambda x: dateUtils.toExpiryStr(x.Year, x.Month, x.Day), axis = 1)

    return df


def getOptionVolumeNextFriExpiryCount(aSymbol, startDay, lenDF):
    """
    # TODO - OCC change their Web Site -- need to rework if we want open interest
Calculate the next Friday total Call / Put Open Interest
If there are no options for Friday goto Monthly else return O
    Parameters
    ----------
    aSymbol : Stock

    startDay : Earnings week

    Returns
    -------
    Volume of Call / Put open interest
    """

    # get OCC Volume for aSymbol
    aOccVolumeDF = getOccVolume(aSymbol)
    # if aOccVolumeDF is empty send back 0 and empty DF
    if aOccVolumeDF.empty:
        print(lenDF, '-  ' + aSymbol + ':  No OCC Option Volume')
        return (0, 0)
    # else:
    #     print(aSymbol + ':  OCC Option Volumes')


    # Get the Volume for Next Friday Option Strikes
    aOccVolumeDFNextWeek = aOccVolumeDF.loc[(aOccVolumeDF.expiry ==
                                            dateUtils.nextFridayOrgFormat(dateUtils.getDateFromISO8601(startDay)))]
    if aOccVolumeDFNextWeek.empty: #nothing for Next Friday?
        # Get the Volume for Next Friday Monthly Option Strikes
        aOccVolumeDFNextMontlyExpiry = aOccVolumeDF.loc[aOccVolumeDF.expiry ==
                                                        dateUtils.getNextThirdFridayFromDate(dateUtils.getDateFromISO8601(startDay))]
        theCallsOpenInterest = aOccVolumeDFNextMontlyExpiry.Call.sum()
        thePutsOpenInterest = aOccVolumeDFNextMontlyExpiry.Put.sum()
    else: #use puts/calls for next Friday
        theCallsOpenInterest = aOccVolumeDFNextWeek.Call.sum()
        thePutsOpenInterest = aOccVolumeDFNextWeek.Put.sum()

    return theCallsOpenInterest, thePutsOpenInterest



def getOptionVolume(aSymbol, aPrice, startDay):
    """
    this routine will provide option volume for one Stock Symbol around one price.
    Will retrun a list of strike prices
    Parameters
    ----------
    aSymbol : Stock
    aPrice : the Max or Min move for a closing price
    startDay : Earnings week

    Returns
    -------

    Tuples: ([0] strikePlus, [1] strikeMinus, [2] aOccVolumeDFNextWeek, [3] aOccVolumeDFNextMontlyExpiry)
        strikePlus/strikeMinus: Strike bounds Plus/Minus from aPrice - to id Min/Max parameters
        aOccVolumeDFNextWeek: Option Volume for next week around strike price,
        aOccVolumeDFNextMontlyExpiry: Option Volume for next Monthly Expiry around strike pric
    """
    # todo - if next week equals next expiry push out next expiry

    # get OCC Volume for aSymbol
    aOccVolumeDF = getOccVolume(aSymbol)

    # if aOccVolumeDF is empty send back 0 and empty DF
    if aOccVolumeDF.empty:
        return (0, 0, pd.DataFrame(), pd.DataFrame())

    strikePlus, strikeMinus = getStrikes(aPrice, aOccVolumeDF, startDay)
    # print('strikePlus: ', strikePlus)
    # print(('strikeMinus: ', strikeMinus))

    # get list of OCC strikes between <= strikePlus and >= StrikeMinus
    strikes = [strike for strike in aOccVolumeDF.Strike
               if (strike >= strikeMinus and strike <= strikePlus)]
    # print('strikes:  \n', strikes)
    # strikes = list(set(strikes))
    # print('unique strikes: ', strikes)

    # get the Volume for Strikes
    aOccVolumeDF = aOccVolumeDF[aOccVolumeDF.Strike.isin(strikes)]
    # print('aOccVolumeDF:\n', aOccVolumeDF)
    # Get the Volume for Next Friday Option Strikes
    aOccVolumeDFNextWeek = aOccVolumeDF.loc[(aOccVolumeDF.expiry ==
                                            dateUtils.nextFridayOrgFormat(dateUtils.getDateFromISO8601(startDay)))]

    # Get the Volume for Next Friday Monthly Option Strikes
    aOccVolumeDFNextMontlyExpiry = aOccVolumeDF.loc[aOccVolumeDF.expiry ==
                                                    dateUtils.getNextThirdFridayFromDate(dateUtils.getDateFromISO8601(startDay))]
    # print('aOccVolumeDFNextWeek:\n', aOccVolumeDFNextWeek)
    # print('aOccVolumeDFNextMontlyExpiry: \n', aOccVolumeDFNextMontlyExpiry)


    return (strikePlus, strikeMinus, aOccVolumeDFNextWeek, aOccVolumeDFNextMontlyExpiry)

def getStrikes(aPrice, aOccVolumeDF, startDay):

    #todo adjust to the proper size strikes

    # Compute interested Strike Prices
    # if price >= then $40 Get to the next round at +/- 5
    # if price < $40 get to round at the +/-2
    if aPrice >= 40:
        strikePlus = (5 * round(aPrice / 5)) +5 # + 10
        strikeMinus = (5 * round(aPrice / 5)) -5 #- 10
        # print('strikePlus', strikePlus)
        # print('strikeMinus', strikeMinus)
    elif aPrice >= 20:
        strikePlus = (2 * round(aPrice / 2)) +2 #+ 5
        strikeMinus = (2 * round(aPrice / 2)) -2 #- 5
    else:
        strikePlus = (2 * round(aPrice / 2)) +1 #+ 2
        strikeMinus = (2 * round(aPrice / 2)) -2# - 2

    strikePlus, strikeMinus = checkStrikePrices(strikePlus, strikeMinus, aOccVolumeDF, startDay)

    return strikePlus, strikeMinus

def checkStrikePrices(strikePlus, strikeMinus, aOccVolumeDF, startDay):

    aOccVolumeDFpd = pd.DataFrame(aOccVolumeDF)

    nextThrdFri = dateUtils.getNextThirdFridayFromDate(dateUtils.getDateFromISO8601(startDay))
    nexFriday = dateUtils.nextFridayOrgFormat(dateUtils.getDateFromISO8601(startDay))

    listOfExpiryNextThrdFriday = aOccVolumeDFpd.loc[aOccVolumeDFpd['expiry'] == nextThrdFri]
    listOfExpiryNextFriday = aOccVolumeDFpd.loc[aOccVolumeDFpd['expiry'] == nexFriday]

    #todo make sure the +2 amnd -2 are good adjustments
    if listOfExpiryNextFriday.Strike.min() > strikeMinus:
        strikeMinus=listOfExpiryNextFriday.Strike.min() +2

    if listOfExpiryNextFriday.Strike.max() < strikePlus:
        strikePlus=listOfExpiryNextFriday.Strike.max() -2


    return strikePlus, strikeMinus


def addMinMaxDFsToExcel(maxDF, minDF, yahooEarningDfRow, aSymbol, writer):

    # add yahooEarningsDFRow with Header
    # add some color to Header
    # keep track of Excel Rows

    # skip some rows

    # get CSV earnings info for aSymbol
    # keep track of Excel Rows

    maxDF.to_excel(writer, sheet_name=aSymbol)
    minDF.to_excel(writer, sheet_name=aSymbol, startcol=10)

def getMinMaxVolsSaveAsCSV(ib, yahooEarningDf, startday):

    aMaxRight = 'C'
    aMinRight ='P'

    for i in range(0, len(yahooEarningDf)):
        aSymbol = yahooEarningDf.loc[i,].Symbol

        print('working: ', aSymbol )

        aMaxPrice = yahooEarningDf.loc[i,]['Max$MoveCl']
        #todo handle if getOptionVol return empty

        # call getOptionVol to get the set of options around a strike price
        # getOptionVol returns
        # Tuple: ([0] strikePlus, [1] strikeMinus, [2] aOccVolumeDFNextWeek, [3] aOccVolumeDFNextMontlyExpiry)
        # [2] aOccVolumeDFNextWeek - may be empty if only Monthly options
        maxMoveTuples = getOptionVolume(aSymbol, float(yahooEarningDf.loc[i,]['Max$MoveCl'][1:]), startday)
        minMoveTuples = getOptionVolume(aSymbol, float(yahooEarningDf.loc[i,]['Min$MoveCl'][1:]), startday)
        # todo not sure how to work this
        #       if there is no Volume info from OCC
        if maxMoveTuples[2].empty and maxMoveTuples[3].empty:
            print('min-maxMoveTuples.empty for symbol: ', aSymbol)
            continue

        # if [2] aOccVolumeDFNextWeek is empty
        if maxMoveTuples[2].empty:
            nextFriIndexMax = pd.MultiIndex.from_product([[maxMoveTuples[3].expiry[:1].values[0]],
                                                          list(maxMoveTuples[3].Strike)], names=['Expiry', 'Strikes'])

            nextFriIndexMin = pd.MultiIndex.from_product([[minMoveTuples[3].expiry[:1].values[0]],
                                                          list(minMoveTuples[3].Strike)], names=['Expiry', 'Strikes'])

            dfNextFriMax = pd.DataFrame(list(maxMoveTuples[3].Call), index=nextFriIndexMax, columns=['Call Volume'])

            dfNextFriMin = pd.DataFrame(list(minMoveTuples[3].Put), index=nextFriIndexMin, columns=['Put Volume'])

        else:
            nextFriIndexMax = pd.MultiIndex.from_product([[maxMoveTuples[2].expiry[:1].values[0]],
                                                          list(maxMoveTuples[2].Strike)], names=['Expiry', 'Strikes'])

            nextFriIndexMin = pd.MultiIndex.from_product([[minMoveTuples[2].expiry[:1].values[0]],
                                                          list(minMoveTuples[2].Strike)], names=['Expiry', 'Strikes'])

            dfNextFriMax = pd.DataFrame(list(maxMoveTuples[2].Call), index=nextFriIndexMax, columns=['Call Volume'])

            dfNextFriMin = pd.DataFrame(list(minMoveTuples[2].Put), index=nextFriIndexMin, columns=['Put Volume'])

        # Finish next Friday
        dfNextFriMax = getOptionPrice.getStockOptionPrice(ib, aSymbol, dfNextFriMax, aMaxRight, yahooEarningDf.loc[i,].close)
        # print('dfNextFriMax: ',dfNextFriMax)
        dfNextFriMin = getOptionPrice.getStockOptionPrice(ib, aSymbol, dfNextFriMin, aMinRight, yahooEarningDf.loc[i,].close)
        # print('dfExpiryMin: ', dfExpiryMin)


        expiryIndexMax = pd.MultiIndex.from_product([[maxMoveTuples[3].expiry[:1].values[0]],
                                                     list(maxMoveTuples[3].Strike)], names=['Expiry', 'Strikes'])

        expiryIndexMin = pd.MultiIndex.from_product([[minMoveTuples[3].expiry[:1].values[0]],
                                                     list(minMoveTuples[3].Strike)], names=['Expiry', 'Strikes'])
        # print('expiryIndexMax: ', expiryIndexMax)
        # print('expiryIndexMin: ', expiryIndexMin)

        dfExpiryMax = pd.DataFrame(list(maxMoveTuples[3].Call), index=expiryIndexMax, columns=['Call Volume'])


        dfExpiryMax = getOptionPrice.getStockOptionPrice(ib, aSymbol, dfExpiryMax, aMaxRight, yahooEarningDf.loc[i,].close)
        # print('dfExpiryMax: ', dfExpiryMax)


        dfExpiryMin = pd.DataFrame(list(minMoveTuples[3].Put), index=expiryIndexMin, columns=['Put Volume'])
        # print('dfExpiryMin: ', dfExpiryMin)
        dfExpiryMin = getOptionPrice.getStockOptionPrice(ib, aSymbol, dfExpiryMin, aMinRight, yahooEarningDf.loc[i,].close)
        # print('dfExpiryMin: ', dfExpiryMin)

        # todo - when Next Fri = next Expiry redundant data - only use one set.
        print('next Fri and Expiry EQUAL - Fix Please  ', dfNextFriMax.equals(dfExpiryMax))
        framesMax = [dfExpiryMax, dfNextFriMax]
        framesMin = [dfExpiryMin, dfNextFriMin]
        # print('framesMax:\n', framesMax)

        #todo - add the symbol name to the new dataframe as a column
        maxDF = pd.concat(framesMax)
        # print('maxDF:\n', maxDF)
        minDF = pd.concat(framesMin)

        saveMinMaxDF2CSV(maxDF, minDF, aSymbol, startday)

    return

def saveMinMaxDF2CSV(maxDF, minDF, aSymbol, startday):

    theDirectory = '/home/michael/jupyter/earningDateData/' + 'Companies/' + startday + '/'
    csvSuffix = '.csv'
    aStockOutFile = theDirectory + aSymbol + '-MinMaxDF' + csvSuffix

    maxDF.to_csv(aStockOutFile, mode='a', header=True)
    minDF.to_csv(aStockOutFile, mode='a', header=True)


def saveSummaryToExcel(yahooEarningsDF, startday ):
    """

    Parameters
    ----------
    yahooEarningsDF: the Yahoo earnings DF
    startday : Earnings week startday

    Returns
    -------

    """

    # Setup Excel output file
    companyEarningsWeek = theBaseCompaniesDirectory + startday + '/'
    outExcelFile = companyEarningsWeek + 'SummaryWeekOf-' + startday + excelSuffix

    # Create a Pandas Excel writer using XlsxWriter as the engine
    # assuming Path is setup
    writer = pd.ExcelWriter(outExcelFile, engine='xlsxwriter')

    summaryWorkbook = writer.book
    fmt = summaryWorkbook.add_format()

    # Summary Sheet Name
    yahooEarningsDF.to_excel(writer, sheet_name='Summary Earnings')

    for i in range(0, len(yahooEarningsDF)):
        # get the symbol and transpose data to fit Horizontally, creat sheet
        aSymbol = yahooEarningsDF.loc[i,].Symbol
        theHeader = yahooEarningsDF.loc[i,].to_frame()
        theHeaderTransposed = theHeader.T
        theHeaderTransposed.to_excel(writer, sheet_name= aSymbol)

        inCsvFile_aSymbol = companyEarningsWeek + aSymbol + csvSuffix
        yahooEarningsDf_aSymbol = pd.read_csv(inCsvFile_aSymbol, index_col=0)
        startRow = 3

        yahooEarningsDF.at[i, "Earnings_Date"] = dateUtils.getDateFromISO8601(yahooEarningsDF.loc[i,].Earnings_Date)

        yahooEarningsDf_aSymbol.to_excel(writer, sheet_name= aSymbol,  startrow=startRow)

    # Convert the dataframe to an XlsxWriter Excel object.
    # yahooEarningDf.to_excel(writer, sheet_name='Week of ' + startday)

    # format Earnings_Date Column C Row to len(yahooEarningsDF)+1

    worksheet = writer.sheets['Summary Earnings']

    cellRowFormat = summaryWorkbook.add_format({'bold': True, 'bg_color': 'green'})
    cellColFormat = summaryWorkbook.add_format()
    cellColFormat.set_shrink()

    worksheet.set_row(0, 15, cellRowFormat)
    worksheet.set_column(0, 20, 15 ,cellColFormat)


    # Close the Pandas Excel writer and output the Excel file.
    writer.save()

    return

def saveDiary2Excel(startday):

    companyEarningsWeek = theBaseCompaniesDirectory + startday + '/'

    # Get saved Summary data
    earningWeekDir = Path(companyEarningsWeek)

    # Save Week Summary
    companySummaryListFile = 'SummaryOfWeek-' + startday + csvSuffix

    # read in CSV summary file based on startday
    yahooEarningsDF = pd.read_csv(earningWeekDir / companySummaryListFile, index_col=0)

    # todo determine if we need Put/Call MinMaxVolsSav
    # save Put/Call Volumes to CSV files
    # getMinMaxVolsSaveAsCSV(ib, yahooEarningsDF, startday)
    # save the weeks earning Summary to Excel
    saveSummaryToExcel(yahooEarningsDF, startday)

    return
