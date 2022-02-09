"""
module: setup

"""
import sys
sys.path.append('/home/michael/jupyter/local-packages')
# Save the data
from pathlib import Path

from localUtilities import dateUtils, config
import datetime

import pyarrow.feather as feather

from yahoofinancials import YahooFinancials
import yahoo_fin.stock_info as si

from localUtilities.ibUtils import getMarketData

import numpy as np
import pandas as pd


# ================================================================

def getEarningsForWeek(startday, theRange=5):
    """
    get earnings currently scheduled on ""startday"" thru ""startdate + theRange""
    si.get_earnings_for_date(aDay)
    Returns a list of dictionaries. Each dictionary contains a ticker,
    its corresponding EPS estimate, and the time of the earnings release.

    Add each Earnings Dictionary to DF and return

    :param startday: The starting day for the Earnings week - usually a Monday
    :type startday: str # Format YYYY-MM-DD
    :param theRange: number of days to process; default is work week of 5
    :type theRange: integer

    :return: DF of Weekly earnings
    :rtype:
    """

    aStartDay = dateUtils.getDateFromISO8601(startday)

    # total up the number of companies with earnings
    totalEarnings = 0
    theWeekDF = pd.DataFrame()

    # Start Monday go to Friday
    for x in range(theRange):
        aDay = aStartDay + datetime.timedelta(days=x)
        anEarningDayDict = si.get_earnings_for_date(aDay)
        theLen = len(anEarningDayDict)
        totalEarnings = totalEarnings + theLen
        print('On Day:  ', aDay, ' The Company Earnings Count: ', theLen)
        #todo: pandas.DataFrame.from_dict with orient='index':
        theWeekDF = theWeekDF.append(anEarningDayDict, ignore_index=True)
    print('totalEarnings: ', totalEarnings)

    # remove unused columns
    theWeekDF.drop(labels=['epsactual', 'epssurprisepct', 'timeZoneShortName', 'gmtOffsetMilliSeconds', 'quoteType'],
                   axis=1, inplace=True)
    # update the column names
    theWeekDF.rename(columns={"ticker": "Symbol", "companyshortname": "Company", "startdatetime": 'Earnings_Date',
                              "startdatetimetype": "Earnings Call Time", "epsestimate": 'EPS Estimate'}, inplace=True)

    # clean up the date from: 2022-02-14T21:00:00.000Z to: 2022-02-14
    theWeekDF['Earnings_Date'] = theWeekDF['Earnings_Date'].map(lambda a: a.split("T", 1)[0])

    return theWeekDF


def addMarketData(earningsDF, startday, getFeather = False):
    """
    Add Market Data / 'histVolatility', 'impliedVolatility', 'avOptionVolume','Expected_Range' etc./
    to companies in passed earningsDF

    Parameters
    ----------
    earningsDF: DF of 'Symbol', 'Earnings_Date', 'Company', 'Earnings Call Time' etc.

    Returns
    -------
    DF w/ Market Data for companies w/ greater than some number, say 500,
    in Option Volume - worthwhile causes
    """
    # use feather to keep data in case of an error and need to recover data
    # rather than starting from the beginning
    addMarketDataFeather = config.theBaseCompaniesDirectory + startday + '/rawData/'
    Path(addMarketDataFeather).mkdir(parents=True, exist_ok=True)
    addMarketDataFeather = addMarketDataFeather + 'addMarketData.feather'

    if getFeather:
        earningsDF = feather.read_feather(addMarketDataFeather)
        lenDF = len(earningsDF.index)
    else:
        updateDFCols(earningsDF)
        lenDF = len(earningsDF)

    for row in earningsDF.itertuples():
        lenDF = lenDF - 1
        print(lenDF, '|  adding market data for: ', row.Symbol)
        getMarketData.addCurrentMarketData(earningsDF, row.Index, row.Symbol)
        earningsDF.to_feather(addMarketDataFeather)

    readFeather = pd.read_feather(addMarketDataFeather, use_threads=True)

    print('\n************** Done - setup.addCurrentMarketData **************\n')
    #remove companies w/ less that 300 in Call Open Interest
    earningsDFOptionVolGood = earningsDF[(earningsDF['Option_Volume'] >= 300)]

    return earningsDFOptionVolGood.reset_index(drop=True), earningsDF, readFeather

def updateDFCols(earningsDF):
    # add Columns to DF
    earningsDF['Open'] = np.nan
    earningsDF['Volume'] = np.nan
    earningsDF['High'] = np.nan
    earningsDF['Low'] = np.nan
    earningsDF['Close'] = np.nan

    earningsDF['Option_Volume'] = np.nan
    earningsDF['PutOpenInterest'] = np.nan
    earningsDF['CallOpenInterest'] = np.nan
    # Calculated info
    earningsDF['histVolatility'] = np.nan
    earningsDF['impliedVolatility'] = np.nan
    earningsDF['Expected_Range'] = np.nan
    # Company Stats
    earningsDF['Beta (5Y Monthly)'] = np.nan
    earningsDF['52 Week High'] = np.nan
    earningsDF['52 Week Low'] = np.nan
    earningsDF['50-Day Moving Average'] = np.nan
    earningsDF['200-Day Moving Average'] = np.nan
    earningsDF['Avg Vol (3 month)'] = np.nan
    earningsDF['Avg Vol (10 day)'] = np.nan
    earningsDF['Current Shares Outstanding'] = np.nan
    earningsDF['Average Shares Outstanding'] = np.nan
    earningsDF['52-Week Change'] = np.nan
    earningsDF['S&P500 52-Week Change'] = np.nan
    earningsDF['Float'] = np.nan
    earningsDF['% Held by Insiders'] = np.nan
    earningsDF['Shares Short (previous month)'] = np.nan
    earningsDF['Shares Ratio (previous month)'] = np.nan
    earningsDF['Short % of Float (previous month)'] = np.nan
    # earningsDF['Short % of Shares Outstanding (previous month)'] = np.nan
    earningsDF['Shares Short (prior month)'] = np.nan


def addPastMarketData(stocksPastEarningsDF, maxQtrs = config.maxQtrs):
    """
    Add Market Data to companies in  stocksPastEarningsDF
    Parameters
    ----------
    stocksPastEarningsDF: DF of 'Symbol', 'Earnings_Date', 'Company', 'Earnings Call Time'

    Returns
    -------
    updated DF w/ Market Data for companies in earningsDF

    """
    # Add Columns to the DF
    updateMarketDataCols(stocksPastEarningsDF)

    # is this DF empty?
    if (stocksPastEarningsDF.empty):
        print( " ===========> theStock <========== EMPTY ============> No data!!")
        return stocksPastEarningsDF
    else:
        theStock = stocksPastEarningsDF.Symbol[0]

    lenDF = len(stocksPastEarningsDF)
    # Use maxQtrs or less
    if lenDF > maxQtrs:
        lenDF = maxQtrs
        print('--> Calculating',  lenDF, 'past Qtrs // ', ' Max Qtrs:  ', maxQtrs)
        pruneDF = True
    else:
        print('--> Calculating', lenDF, 'past Qtrs //', f'{lenDF/4:1.1f}', 'years')
        pruneDF = False

    yahoo_financials = YahooFinancials(theStock)
    # ToDo: drop the rows > maxQtrs before processing
    # stocksPastEarningsDF.head(maxQtrs)
    for earnDateRow in stocksPastEarningsDF.itertuples():
        if lenDF == 0:
            break # no data
        else:
            lenDF = lenDF - 1 # rows start at 0

        # Drop future earnings dates
        if earnDateRow.Earnings_Date + datetime.timedelta(days=config.daysAroundEarnings) > dateUtils.getTodayDateTime():
            # todo can append the dictionary to the DF as well.
            stocksPastEarningsDF.at[earnDateRow.Index, 'High']   = np.nan
            stocksPastEarningsDF.at[earnDateRow.Index, 'Open']   = np.nan
            stocksPastEarningsDF.at[earnDateRow.Index, 'Volume'] = np.nan
            stocksPastEarningsDF.at[earnDateRow.Index, 'Low']    = np.nan
            stocksPastEarningsDF.at[earnDateRow.Index, 'Close']  = np.nan
            continue

        # get the Historic Date span start/end
        startDateTime = dateUtils.getDateStringDashSeprtors(dateUtils.goOutXWeekdays(earnDateRow.Earnings_Date,
                                                                                     -config.daysAroundEarnings))
        endDateTime = dateUtils.getDateStringDashSeprtors(dateUtils.goOutXWeekdays(earnDateRow.Earnings_Date,
                                                                                   config.daysAroundEarnings))

        # Get historic stock prices from yahoo_financials within daysAroundEarnings timeframe
        historical_stock_prices = yahoo_financials.get_historical_price_data(startDateTime, endDateTime, 'daily')
        # add historic price data
        try:
            historical_stock_pricesDF = pd.DataFrame(historical_stock_prices[theStock]['prices'])
        except KeyError:
            print('     Stock: ', theStock)
            print('     prices:  ', historical_stock_prices)
            print('         ', KeyError, 'Prices: ', '       setup.addPastMarketData')
            break
        except TypeError:
            print('     Stock: ', theStock)
            print('     prices:  ', historical_stock_prices)
            print('         ', TypeError, 'NoneType', '       setup.addPastMarketData')
            continue

        # recreate 'date' index as a 'dateTime' column for historical_stock_pricesDF
        historical_stock_pricesDF['date'] = historical_stock_pricesDF['formatted_date'].apply(
            dateUtils.getDateFromISO8601)
        historical_stock_pricesDF = historical_stock_pricesDF.set_index("date", drop=False)
        # ToDo: should we use append instead of = ??
        try:
            stocksPastEarningsDF.at[earnDateRow.Index, 'High']   = historical_stock_pricesDF.high[earnDateRow.Earnings_Date]
            stocksPastEarningsDF.at[earnDateRow.Index, 'Open']   = historical_stock_pricesDF.open[earnDateRow.Earnings_Date]
            stocksPastEarningsDF.at[earnDateRow.Index, 'Volume'] = historical_stock_pricesDF.volume[earnDateRow.Earnings_Date]
            stocksPastEarningsDF.at[earnDateRow.Index, 'Low']    = historical_stock_pricesDF.low[earnDateRow.Earnings_Date]
            stocksPastEarningsDF.at[earnDateRow.Index, 'Close']  = historical_stock_pricesDF.close[earnDateRow.Earnings_Date]
        except KeyError:
            print('     Stock: ', theStock)
            print('         ', KeyError, 'Historical Price Issue in:', '       setup.addPastMarketData')

            continue

        stocksPastEarningsDF = getDaysPastEarningsClosePrices(earnDateRow, historical_stock_pricesDF, stocksPastEarningsDF)

        stocksPastEarningsDF = calcPriceDeltas(stocksPastEarningsDF)

    stocksPastEarningsDF = formatForCSVFile(stocksPastEarningsDF, pruneDF)

    return stocksPastEarningsDF.head(maxQtrs)

def updateMarketDataCols(stocksPastEarningsDF):
    stocksPastEarningsDF['High'] = np.nan
    stocksPastEarningsDF['Open'] = np.nan
    stocksPastEarningsDF['Volume'] = np.nan
    stocksPastEarningsDF['Low'] = np.nan
    stocksPastEarningsDF['Close'] = np.nan
    # ----- get historic closing price --------------------------------------------------------------
    stocksPastEarningsDF['EDClose'] = np.nan  # Earning Day Closing Price
    stocksPastEarningsDF['EDFwd1DayClose'] = np.nan  # Earning Day Forward 1 Day - Closing Price
    stocksPastEarningsDF['EDFwd4DayClose'] = np.nan  # Earning Day Forward 4 Days - Closing Price
    stocksPastEarningsDF['EDBak1DayClose'] = np.nan  # Earning Day Back 1 Day - Closing Price
    stocksPastEarningsDF['EDBak4DayClose'] = np.nan  # Earning Day Back 4 Days - Closing Price
    # ------ get Differences between forward closing prices for 1 & 4 Days ---------------------------
    stocksPastEarningsDF['EDDiffFwd4Close'] = np.nan  # Earning Day Subtract the Forward 4 Days Closing Price
    stocksPastEarningsDF['EDDiffFwd1Close'] = np.nan  # Earning Day Subtract the Forward 1 Day Closing Price
    stocksPastEarningsDF['EDFwd1DayClosePercentDelta'] = np.nan  # Earning Day % Delta the Forward 1 Day Closing Price
    stocksPastEarningsDF['EDFwd4DayClosePercentDelta'] = np.nan  # Earning Day % Delta the Forward 4 Day Closing Price
    # ------ get Differences between backward looking closing prices for 1 & 4 Days ---------------------------
    stocksPastEarningsDF['EDDiffBak4Close'] = np.nan  # Earning Day Subtract the Back 4 Days Closing Price
    stocksPastEarningsDF['EDDiffBak1Close'] = np.nan  # Earning Day Subtract the Back 1 Day Closing Price
    stocksPastEarningsDF['EDBak1DayClosePercentDelta'] = np.nan  # Earning Day % Delta the Back 1 Day Closing Price
    stocksPastEarningsDF['EDBak4DayClosePercentDelta'] = np.nan  # Earning Day % Delta the Back 4 Day Closing Price
    # ------ get Differences between forward looking opening prices for 1 & 4 Days ---------------------------
    stocksPastEarningsDF['EDFwd1DayOpen'] = np.nan  # Earning Day Forward 1 Day Open Price
    stocksPastEarningsDF['EDFwd4DayOpen'] = np.nan  # Earning Day Forward 1 Day Open Price
    stocksPastEarningsDF['EDBak1DayOpenPercentDelta'] = np.nan  # Earning Day % Delta the Back 1 Day Closing Price
    stocksPastEarningsDF['EDBak4DayOpenPercentDelta'] = np.nan  # Earning Day % Delta the Back 4 Day Closing Price
    # ------ get Differences between backward looking opening prices for 1 & 4 Days ---------------------------
    stocksPastEarningsDF['EDBak4DayOpen'] = np.nan  # Earning Day Back 1 Day Open Price
    stocksPastEarningsDF['EDBak1DayOpen'] = np.nan  # Earning Day Back 1 Day Open Price
    stocksPastEarningsDF['EDBak1DayOpenPercentDelta'] = np.nan  # Earning Day % Delta the Back 1 Day Closing Price
    stocksPastEarningsDF['EDBak4DayOpenPercentDelta'] = np.nan  # Earning Day % Delta the Back 4 Day Closing Price


def calcPriceDeltas(stocksPastEarningsDF):
    """
    Calculate past earnings Price and Percent Deltas from  historical_stock_prices

    Parameters
    ----------
    stockPastEarningsDF:    a pandas DF historic stock prices from yahoofinancials


    Returns
    -------
    # updated stockPastEarningsDF
    stocksPastEarningsDF

    """
    # todo add Earning day Close to next Day Open
    # todo --- if earnings is before earning day then
    #           EarningDayPriceDif-CloseOpen = (EarningDayClose - 1) - EarningDayOpen
    #      --- if earnings is after earning day then
    #           EarningDayPriceDif-CloseOpen = EarningDayClose - (EarningDayOpen + 1)
    # calculate price and percent deltas
    stocksPastEarningsDF['EDFwd1DayClosePercentDelta'] = 1 - (stocksPastEarningsDF['EDClose'] / stocksPastEarningsDF['EDFwd1DayClose'])
    stocksPastEarningsDF['EDDiffFwd1Close'] = stocksPastEarningsDF['EDFwd1DayClose'] - stocksPastEarningsDF['EDClose']

    stocksPastEarningsDF['EDFwd4DayClosePercentDelta'] = 1 - (stocksPastEarningsDF['EDClose'] / stocksPastEarningsDF['EDFwd4DayClose'])
    stocksPastEarningsDF['EDDiffFwd4Close'] = stocksPastEarningsDF['EDFwd4DayClose'] - stocksPastEarningsDF['EDClose']

    stocksPastEarningsDF['EDBak1DayClosePercentDelta'] = 1 - (stocksPastEarningsDF['EDClose'] / stocksPastEarningsDF['EDBak1DayClose'])
    stocksPastEarningsDF['EDDiffBak1Close'] = stocksPastEarningsDF['EDBak1DayClose'] - stocksPastEarningsDF['EDClose']

    stocksPastEarningsDF['EDBak4DayClosePercentDelta'] = 1 - (stocksPastEarningsDF['EDClose'] / stocksPastEarningsDF['EDBak4DayClose'])
    stocksPastEarningsDF['EDDiffBak4Close'] = stocksPastEarningsDF['EDBak4DayClose'] - stocksPastEarningsDF['EDClose']

    return stocksPastEarningsDF

def getDaysPastEarningsClosePrices(earnDateRow, historical_stock_pricesDF, stockPastEarningsDF):
    """
    Get earning price data from  historical_stock_prices for days before / after ----

    Parameters
    ----------
    earnDateRow : current row in yahooEarningsDF / aStock
    historical_stock_pricesDF:  historic stock prices from yahoofinancials :             Stock symbol string
    stockPastEarningsDF:    companies and earnings data
    daysAroundEarnings: Number for Number of Days before / after Earnings date

    Returns
    -------
    # time series panda dataframes
    yahooEarningsDF
        """

    # get current earnings date
    # Earning Day Closing Price
    earningsDate = earnDateRow.Earnings_Date
    stockPastEarningsDF.at[earnDateRow.Index, 'EDClose'] = historical_stock_pricesDF.close[earningsDate]

    try:
        # the day before earnings date
        # Earning Days Back 4 Day - Closing Price
        theEDMinus4Date = dateUtils.goOutXWeekdays(earningsDate, -4)
        stockPastEarningsDF.at[earnDateRow.Index, 'EDBak4DayClose'] = historical_stock_pricesDF.close[theEDMinus4Date]
        stockPastEarningsDF.at[earnDateRow.Index, 'EDBak4DayDate'] = theEDMinus4Date

        # Earning Day Back 1 Day - Closing Price
        theEDMinus1Date = dateUtils.goOutXWeekdays(earningsDate, -1)
        stockPastEarningsDF.at[earnDateRow.Index, 'EDBak1DayClose'] = historical_stock_pricesDF.close[theEDMinus1Date]
        stockPastEarningsDF.at[earnDateRow.Index, 'EDBak1DayDate'] = theEDMinus1Date
        # the day after earnings date
        # Earning Day Forward 1 Day - Closing Price
        theEDPlus1Date = dateUtils.goOutXWeekdays(earningsDate, 1)
        stockPastEarningsDF.at[earnDateRow.Index, 'EDFwd1DayClose'] = historical_stock_pricesDF.close[theEDPlus1Date]
        stockPastEarningsDF.at[earnDateRow.Index, 'EDFwd1DayDate'] = theEDPlus1Date

        # plus 4 days after earnings date
        # Earning Day Forward 4 Days Closing Price
        theEDPlus4Date = dateUtils.goOutXWeekdays(earningsDate, 4)
        stockPastEarningsDF.at[earnDateRow.Index, 'EDFwd4DayClose'] = historical_stock_pricesDF.close[theEDPlus4Date]
        stockPastEarningsDF.at[earnDateRow.Index, 'EDFwd4DayDate'] = theEDPlus4Date

        # plus 1 days after earnings date
        # Earning Day Forward 1 Day Open Price
        stockPastEarningsDF.at[earnDateRow.Index, 'EDFwd1DayOpen'] = historical_stock_pricesDF.open[theEDPlus1Date]
        stockPastEarningsDF.at[earnDateRow.Index, 'EDBak1DayOpen'] = historical_stock_pricesDF.open[theEDMinus1Date]
        stockPastEarningsDF.at[earnDateRow.Index, 'EDFwd4DayOpen'] = historical_stock_pricesDF.open[theEDPlus4Date]
        stockPastEarningsDF.at[earnDateRow.Index, 'EDBak4DayOpen'] = historical_stock_pricesDF.open[theEDMinus4Date]

        stockPastEarningsDF.at[earnDateRow.Index, 'EDFwd1DayHigh'] = historical_stock_pricesDF.high[theEDPlus1Date]
        stockPastEarningsDF.at[earnDateRow.Index, 'EDBak1DayHigh'] = historical_stock_pricesDF.high[theEDMinus1Date]
        stockPastEarningsDF.at[earnDateRow.Index, 'EDFwd4DayHigh'] = historical_stock_pricesDF.high[theEDPlus4Date]
        stockPastEarningsDF.at[earnDateRow.Index, 'EDBak4DayHigh'] = historical_stock_pricesDF.high[theEDMinus4Date]

        stockPastEarningsDF.at[earnDateRow.Index, 'EDFwd1DayLow'] = historical_stock_pricesDF.low[theEDPlus1Date]
        stockPastEarningsDF.at[earnDateRow.Index, 'EDBak1DayLow'] = historical_stock_pricesDF.low[theEDMinus1Date]
        stockPastEarningsDF.at[earnDateRow.Index, 'EDFwd4DayLow'] = historical_stock_pricesDF.low[theEDPlus4Date]
        stockPastEarningsDF.at[earnDateRow.Index, 'EDBak4DayLow'] = historical_stock_pricesDF.low[theEDMinus4Date]

    except KeyError:
        print('     KeyError', KeyError, '       setup.getDaysPastEarningsClosePrices')
        print('         earningsDate:', earningsDate)


    return stockPastEarningsDF

def formatForCSVFile(stocksPastEarningsDF, pruneDF):

    stocksPastEarningsDF['Close'] = stocksPastEarningsDF['Close'].round(2)
    stocksPastEarningsDF['High'] = stocksPastEarningsDF['High'].round(2)
    stocksPastEarningsDF['Open'] = stocksPastEarningsDF['Open'].round(2)
    stocksPastEarningsDF['Low'] = stocksPastEarningsDF['Low'].round(2)
    stocksPastEarningsDF['EDClose'] = stocksPastEarningsDF['EDClose'].round(2)
    stocksPastEarningsDF['EDFwd1DayClose'] = stocksPastEarningsDF['EDFwd1DayClose'].round(2)
    stocksPastEarningsDF['EDBak1DayClose'] = stocksPastEarningsDF['EDBak1DayClose'].round(2)
    stocksPastEarningsDF['EDBak4DayClose'] = stocksPastEarningsDF['EDBak4DayClose'].round(2)
    stocksPastEarningsDF['EDFwd4DayClose'] = stocksPastEarningsDF['EDFwd4DayClose'].round(2)
    stocksPastEarningsDF['EDDiffFwd4Close'] = stocksPastEarningsDF['EDDiffFwd4Close'].round(2)
    stocksPastEarningsDF['EDDiffFwd1Close'] = stocksPastEarningsDF['EDDiffFwd1Close'].round(2)
    stocksPastEarningsDF['EDFwd1DayClosePercentDelta'] = stocksPastEarningsDF['EDFwd1DayClosePercentDelta'].round(4)
    stocksPastEarningsDF['EDFwd4DayClosePercentDelta'] = stocksPastEarningsDF['EDFwd4DayClosePercentDelta'].round(4)
    stocksPastEarningsDF['EDFwd1DayHigh']  = stocksPastEarningsDF['EDFwd1DayHigh'].round(2)
    stocksPastEarningsDF['EDBak1DayHigh']  = stocksPastEarningsDF['EDBak1DayHigh'].round(2)
    stocksPastEarningsDF['EDFwd4DayHigh']  = stocksPastEarningsDF['EDFwd4DayHigh'].round(2)
    stocksPastEarningsDF['EDBak4DayHigh']  = stocksPastEarningsDF['EDBak4DayHigh'].round(2)
    stocksPastEarningsDF['EDBak1DayLow']  = stocksPastEarningsDF['EDBak1DayLow'].round(2)
    stocksPastEarningsDF['EDFwd4DayLow']  = stocksPastEarningsDF['EDFwd4DayLow'].round(2)
    stocksPastEarningsDF['EDBak4DayLow']  = stocksPastEarningsDF['EDBak4DayLow'].round(2)
    stocksPastEarningsDF['EDFwd1DayLow']  = stocksPastEarningsDF['EDFwd1DayLow'].round(2)
    stocksPastEarningsDF['EDBak4DayClosePercentDelta']  = stocksPastEarningsDF['EDBak4DayClosePercentDelta'].round(2)
    stocksPastEarningsDF['EDDiffBak4Close']  = stocksPastEarningsDF['EDDiffBak4Close'].round(2)
    stocksPastEarningsDF['EDBak1DayClosePercentDelta']  = stocksPastEarningsDF['EDBak1DayClosePercentDelta'].round(2)
    stocksPastEarningsDF['EDDiffBak1Close']  = stocksPastEarningsDF['EDDiffBak1Close'].round(2)



    # Todo - take out last
    # stocksPastEarningsDF['Last'] = stocksPastEarningsDF['Last'].round(2)


    stocksPastEarningsDF['EDFwd1DayOpen'] = stocksPastEarningsDF['EDFwd1DayOpen'].round(2)
    stocksPastEarningsDF['EDBak1DayOpen'] = stocksPastEarningsDF['EDBak1DayOpen'].round(2)

    stocksPastEarningsDF['Earnings_Date'] = stocksPastEarningsDF['Earnings_Date'].apply(dateUtils.getDateStringDashSeprtors)

    stocksPastEarningsDF = stocksPastEarningsDF[['Symbol', 'Company', 'Earnings_Date', 'EPS_Estimate', 'Reported_EPS',
                                                    'Surprise(%)', 'High', 'Open', 'Volume', 'Low', 'Close', 'EDClose',
                                                    'EDFwd1DayOpen', 'EDFwd1DayClose', 'EDBak1DayOpen', 'EDBak1DayClose',
                                                    'EDBak4DayClose', 'EDFwd4DayClose', 'EDDiffFwd4Close',
                                                    'EDDiffFwd1Close', 'EDFwd1DayClosePercentDelta',
                                                    'EDFwd4DayClosePercentDelta','EDFwd1DayHigh','EDBak1DayHigh',
                                                    'EDFwd4DayHigh', 'EDBak4DayHigh', 'EDFwd1DayLow', 'EDBak1DayLow',
                                                    'EDFwd4DayLow', 'EDBak4DayLow', 'EDBak4DayClosePercentDelta',
                                                    'EDDiffBak4Close', 'EDDiffBak1Close', 'EDBak1DayClosePercentDelta',
                                                    'EDBak4DayDate','EDBak1DayDate', 'EDFwd1DayDate', 'EDFwd4DayDate']]

    # if we are using the Max Earnings Quarters (32) prune off the remaining years data
    if pruneDF == True:
        stocksPastEarningsDF = stocksPastEarningsDF.iloc[0:32]

    return stocksPastEarningsDF