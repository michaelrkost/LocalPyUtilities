import requests
import pandas as pd
import html5lib

import os
import sys
from pathlib import Path 
sys.path.append('/home/michael/jupyter/local-packages')

from localUtilities import dateUtils


pd.set_option('display.max_rows', 1000)

#=========================================================================
def getOccVolume(symbol):
    s = requests.Session()
    #ONN Volume Search
    url = 'https://www.theocc.com/webapps/series-search'
    r = s.post(url,data={'symbolType': 'U','symbolId': symbol})
    df = pd.read_html(r.content)[0]
    df.columns = df.columns.droplevel()
    # Combine Cents/Decimal in Strike price
    df['Strike'] = df['Integer'] + (df['Dec']*0.001)
    cols_of_interest=['Product Symbol', 'Year', 'Month', 'Day', 'Strike', 'Call', 'Put']
    df = df[cols_of_interest]
    # get an expiry info
    df['expiry'] = df.apply(lambda x: dateUtils.toExpiryStr(x.Year, x.Month, x.Day), axis = 1)

    return df

def getOptionVolume(aSymbol, aPrice, startDay):
    # todo - if next week equals next expiry pust out next expiry
    # get OCC Volume for aSymbol
    aOccVolumeDF = getOccVolume(aSymbol)

    strikePlus, strikeMinus = getStrikes(aPrice)

    # get list of OCC strikes between <= strikePlus and >= StrikeMinus
    strikes = [strike for strike in aOccVolumeDF.Strike
               if (strike >= strikeMinus and strike <= strikePlus)]

    # get the Volume for Strikes
    aOccVolumeDF = aOccVolumeDF[aOccVolumeDF.Strike.isin(strikes)]
    # Get the Volume for Next Friday Option Strikes
    aOccVolumeDFNextWeek = aOccVolumeDF.loc[(aOccVolumeDF.expiry ==
                                            dateUtils.nextFridayOrgFormat(dateUtils.getDateFromISO8601(startDay)))]
    # Get the Volume for Next Friday Monthly Option Strikes
    aOccVolumeDFNextMontlyExpiry = aOccVolumeDF.loc[aOccVolumeDF.expiry ==
                                             dateUtils.third_fridayFromOrgFormat(dateUtils.getDateFromISO8601(startDay))]

    return (strikePlus, strikeMinus, aOccVolumeDFNextWeek, aOccVolumeDFNextMontlyExpiry)

def getStrikes(aPrice):

    # Compute interested Strike Prices
    # if price >= then $40 Get to the next round at +/- 5
    # if price < $40 get to round at the +/-2
    if aPrice >= 40:
        strikePlus = (5 * round(aPrice / 5)) + 10
        strikeMinus = (5 * round(aPrice / 5)) - 10
        # print('strikePlus', strikePlus)
        # print('strikeMinus', strikeMinus)
    else:
        strikePlus = (2 * round(aPrice / 2)) + 5
        strikeMinus = (2 * round(aPrice / 2)) - 5

    # print('strikePlus', strikePlus)
    # print('strikeMinus', strikeMinus)

    return strikePlus, strikeMinus

def getMinMaxVols(yahooEarningDf, startday, writer):

    maxDFList = []
    minDFList = []

    for i in range(0, len(yahooEarningDf)):
        aSymbol = yahooEarningDf.loc[i,].Symbol
        aMaxPrice = yahooEarningDf.loc[i,]['Max$MoveCl']
        maxMoveTuples = getOptionVolume(aSymbol, float(yahooEarningDf.loc[i,]['Max$MoveCl'][1:]), startday)
        minMoveTuples = getOptionVolume(aSymbol, float(yahooEarningDf.loc[i,]['Min$MoveCl'][1:]), startday)
        nextFriIndexMax = pd.MultiIndex.from_product([[dateUtils.month3Format(maxMoveTuples[2].expiry[:1].values[0])],
                                                      list(maxMoveTuples[2].Strike)], names=['Expiry', 'Strikes'])
        expiryIndexMax = pd.MultiIndex.from_product([[dateUtils.month3Format(maxMoveTuples[3].expiry[:1].values[0])],
                                                     list(maxMoveTuples[3].Strike)], names=['Expiry', 'Strikes'])

        nextFriIndexMin = pd.MultiIndex.from_product([[dateUtils.month3Format(minMoveTuples[2].expiry[:1].values[0])],
                                                      list(minMoveTuples[2].Strike)], names=['Expiry', 'Strikes'])
        expiryIndexMin = pd.MultiIndex.from_product([[dateUtils.month3Format(minMoveTuples[3].expiry[:1].values[0])],
                                                     list(minMoveTuples[3].Strike)], names=['Expiry', 'Strikes'])

        dfExpiryMax = pd.DataFrame(list(maxMoveTuples[3].Call), index=expiryIndexMax, columns=['Call Volume'])
        dfNextFriMax = pd.DataFrame(list(maxMoveTuples[2].Call), index=nextFriIndexMax, columns=['Call Volume'])

        dfExpiryMin = pd.DataFrame(list(minMoveTuples[3].Put), index=expiryIndexMin, columns=['Put Volume'])
        dfNextFriMin = pd.DataFrame(list(minMoveTuples[2].Put), index=nextFriIndexMin, columns=['Put Volume'])

        framesMax = [dfExpiryMax, dfNextFriMax]
        framesMin = [dfExpiryMin, dfNextFriMin]

        maxDF = pd.concat(framesMax, names=["Company"], keys=[aSymbol])
        minDF = pd.concat(framesMin, names=["Company"], keys=[aSymbol])

        maxDFList.append(maxDF)
        minDFList.append(minDF)

        maxDF.to_excel(writer, sheet_name=aSymbol)
        minDF.to_excel(writer, sheet_name=aSymbol, startcol=7)

       # Close the Pandas Excel writer and output the Excel file.
    writer.save()

    return

def saveDiary2Excel(yahooEarningDf, startday):

    theDirectory = '/home/michael/jupyter/earningDateData/' + 'Companies/' + startday + '/'
    excelSuffix = '.xlsx'
    outExcelFile = theDirectory + 'weekOf-' + startday + excelSuffix

    # Create a Pandas Excel writer using XlsxWriter as the engine
    writer = pd.ExcelWriter(outExcelFile, engine='xlsxwriter')

    # Convert the dataframe to an XlsxWriter Excel object.
    yahooEarningDf.to_excel(writer, sheet_name='Week of ' + startday)

    # Close the Pandas Excel writer and output the Excel file.
    #writer.save()

    return writer
