"""
module: setup

"""

import sys
sys.path.append('/home/michael/jupyter/local-packages')

import datetime
# Get my Utilities (localUtilities)
from localUtilities import dateUtils

# YahooFinancials
# https://pypi.org/project/yahoofinancials/

# A python module that returns stock, cryptocurrency,
# forex, mutual fund, commodity futures, ETF,
# and US Treasury financial data from Yahoo Finance.
# TODO: Determine if yahoofinancials is adequate or if we should create a Database with this info.
# ToDo: review investpy as an alternative to yahoofinancials // https://investpy.readthedocs.io
from yahoofinancials import YahooFinancials
from localUtilities.ibUtils import getMarketData

import numpy as np
import pandas as pd
# ================================================================

def addMarketData(earningsDF):
    """
    Add Market Data / 'histVolatility', 'impliedVolatility', 'avOptionVolume','Expected_Range' etc./
    to companies in passed DF

    Parameters
    ----------
    earningsDF: DF of 'Symbol', 'Earnings_Date', 'Company', 'Earnings Call Time'
    startday: the starting date

    Returns
    -------
    DF w/ Market Data for companies w/ greater than some number, say 500,
    in Option Volume - worthwhile causes
    """
# get info from the time of this run
    earningsDF['Open'] = np.nan
    earningsDF['Volume'] = np.nan
    earningsDF['High'] = np.nan
    earningsDF['Low'] = np.nan
    earningsDF['Close'] = np.nan

    earningsDF['Option_Volume'] = np.nan
    earningsDF['PutOpenInterest'] = np.nan
    earningsDF['CallOpenInterest'] = np.nan

    earningsDF['histVolatility'] = np.nan
    earningsDF['impliedVolatility'] = np.nan
    earningsDF['Expected_Range'] = np.nan

    lenDF = len(earningsDF)

    for row in earningsDF.itertuples():
        # print(row.Symbol, ' @  ', lenDF,  end=", ")
        lenDF = lenDF - 1

        # TODO - OCC change their Web Site -- need to rework if we want open interest
        # putsOpenInterest, callsOpenInterest = getOptionInfo.getOptionVolumeNextFriExpiryCount(row.Symbol, startday,lenDF)
        # depreciated code 8/8/21: mktData = getMarketData.getMarketDataFromOptionistics(row.Symbol)
        print(lenDF, '|  add market data for: ',row.Index, "   ",  row.Symbol)
        # print("earningsDF befor == ", earningsDF)
        getMarketData.addCurrentMarketData(earningsDF, row.Index, row.Symbol)


    print('\nDone - setup.addCurrentMarketData....')
    #remove companies w/ less that 300 in Call Open Interest
    earningsDFOptionVolGood = earningsDF[(earningsDF['Option_Volume'] >= 300)]

    return earningsDFOptionVolGood.reset_index(drop=True), earningsDF


def addPastMarketData(stocksPastEarningsDF, daysAroundEarnings = 10):
    """
    Add Market Data to companies in  stocksPastEarningsDF
    #todo remove daysAroundEarnings = 10 // should be 5??
    Parameters
    ----------
    stocksPastEarningsDF: DF of 'Symbol', 'Earnings_Date', 'Company', 'Earnings Call Time'

    Returns
    -------
    updated DF w/ Market Data for companies in earningsDF

    """
# get info from the time of this run
    stocksPastEarningsDF['High'] = np.nan
    stocksPastEarningsDF['Open'] = np.nan
    stocksPastEarningsDF['Volume'] = np.nan
    stocksPastEarningsDF['Low'] = np.nan
    stocksPastEarningsDF['Close'] = np.nan
    # Closing Prices of Interest
    stocksPastEarningsDF['EDClose'] = np.nan          # Earning Day Closing Price
    stocksPastEarningsDF['EDFwd1DayClose'] = np.nan   # Earning Day Forward 1 Day - Closing Price
    stocksPastEarningsDF['EDBak1DayClose'] = np.nan   # Earning Day Back 1 Day - Closing Price
    stocksPastEarningsDF['EDFwd4DayClose'] = np.nan   # Earning Day Forward 4 Days - Closing Price
    # Deltas on Closing Prices of Interest
    stocksPastEarningsDF['EDDiffFwd4Close'] = np.nan # Earning Day Subtract the Forward 4 Days Closing Price
    stocksPastEarningsDF['EDDiffFwd1Close'] = np.nan # Earning Day Subtract the Forward 1 Day Closing Price
    stocksPastEarningsDF['EDFwd1DayClosePercentDelta'] = np.nan # Earning Day % Delta the Forward 1 Day Closing Price
    stocksPastEarningsDF['EDFwd4DayClosePercentDelta'] = np.nan # Earning Day % Delta the Forward 4 Day Closing Price

    stocksPastEarningsDF['EDFwd1DayOpen'] = np.nan # Earning Day Forward 1 Day Open Price
    stocksPastEarningsDF['EDBak1DayOpen'] = np.nan # Earning Day Back 1 Day Open Price



    if (stocksPastEarningsDF.empty):
        print( " ===========> theStock <========== EMPTY ============no data!!")
        return stocksPastEarningsDF
    else:
        theStock = stocksPastEarningsDF.Symbol[0]
        print("stocksPastEarningsDF.Symbol[0] = ", theStock)

    lenDF = len(stocksPastEarningsDF)
    if lenDF > 32:
        lenDF = 32
        print('--> Calculating',  lenDF, 'past Qtrs // 8 years - Max')
        pruneDF = True
    else:
        print('--> Calculating', lenDF, 'past Qtrs //', f'{lenDF/4:1.1f}', 'years')
        pruneDF = False

    yahoo_financials = YahooFinancials(theStock)

    for earnDateRow in stocksPastEarningsDF.itertuples():
        #print(earnDateRow.Symbol, ' / theStock: ', theStock,  ' @  ', lenDF, 'earnDateRow.Index: ', earnDateRow.Index, end=", ")

        if lenDF == 0:
            break
        else:
            lenDF = lenDF - 1

        # set start and end Date
        # set to format 2018-09-29 // String Dash Separator
        endDateTime = dateUtils.getDateStringDashSeprtors(earnDateRow.Earnings_Date
                                                          +datetime.timedelta(days=daysAroundEarnings))
        startDateTime = dateUtils.getDateStringDashSeprtors(earnDateRow.Earnings_Date
                                                            -datetime.timedelta(days=daysAroundEarnings))

        # Drop future earnings dates
        if earnDateRow.Earnings_Date + datetime.timedelta(days=daysAroundEarnings) > datetime.datetime.today():
            # todo can append the dictionary to the DF as well.
            stocksPastEarningsDF.at[earnDateRow.Index, 'High']   = np.nan
            stocksPastEarningsDF.at[earnDateRow.Index, 'Open']   = np.nan
            stocksPastEarningsDF.at[earnDateRow.Index, 'Volume'] = np.nan
            stocksPastEarningsDF.at[earnDateRow.Index, 'Low']    = np.nan
            stocksPastEarningsDF.at[earnDateRow.Index, 'Close']  = np.nan
            # stocksPastEarningsDF.at[earnDateRow.Index, 'Last']   = np.nan
            continue

        # Get historic stock prices from yahoofinancials within daysAroundEarnings timeframe
        historical_stock_prices = yahoo_financials.get_historical_price_data(startDateTime, endDateTime, 'daily')
        #print("historical_stock_prices: ", historical_stock_prices)

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

        # recreate index as the 'date' column for price
        historical_stock_pricesDF['date'] = historical_stock_pricesDF['formatted_date'].apply(
            dateUtils.getDateFromISO8601)

        historical_stock_pricesDF = historical_stock_pricesDF.set_index("date", drop=False)
        # historical_stock_prices.index = pd.to_datetime(historical_stock_prices.index)

        try:
            # todo can append the dictionary to the DF as well.
            stocksPastEarningsDF.at[earnDateRow.Index, 'High']   = historical_stock_pricesDF.high[earnDateRow.Earnings_Date.date()]
            stocksPastEarningsDF.at[earnDateRow.Index, 'Open']   = historical_stock_pricesDF.open[earnDateRow.Earnings_Date.date()]
            stocksPastEarningsDF.at[earnDateRow.Index, 'Volume'] = historical_stock_pricesDF.volume[earnDateRow.Earnings_Date.date()]
            stocksPastEarningsDF.at[earnDateRow.Index, 'Low']    = historical_stock_pricesDF.low[earnDateRow.Earnings_Date.date()]
            stocksPastEarningsDF.at[earnDateRow.Index, 'Close']  = historical_stock_pricesDF.close[earnDateRow.Earnings_Date.date()]
            # stocksPastEarningsDF.at[earnDateRow.Index, 'Last']   = historical_stock_pricesDF.adjclose[earnDateRow.Earnings_Date.date()]
        except KeyError:
            print('     Stock: ', theStock)
            print('         ', KeyError, 'Historical Price Issue in:', '       setup.addPastMarketData')

            continue

        stocksPastEarningsDF = getDaysPastEarningsClosePrices(earnDateRow, historical_stock_pricesDF, stocksPastEarningsDF)
        stocksPastEarningsDF = calcPriceDeltas(stocksPastEarningsDF)

    stocksPastEarningsDF = formatForCSVFile(stocksPastEarningsDF, pruneDF)

    return stocksPastEarningsDF

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
    # calculate price and persent deltas
    stocksPastEarningsDF['EDFwd1DayClosePercentDelta'] = 1 - (stocksPastEarningsDF['EDClose'] / stocksPastEarningsDF['EDFwd1DayClose'])
    stocksPastEarningsDF['EDDiffFwd1Close'] = stocksPastEarningsDF['EDFwd1DayClose'] - stocksPastEarningsDF['EDClose']

    stocksPastEarningsDF['EDFwd4DayClosePercentDelta'] = 1 - (stocksPastEarningsDF['EDClose'] / stocksPastEarningsDF['EDFwd4DayClose'])
    stocksPastEarningsDF['EDDiffFwd4Close'] = stocksPastEarningsDF['EDFwd4DayClose'] - stocksPastEarningsDF['EDClose']


    return stocksPastEarningsDF

def getDaysPastEarningsClosePrices(earnDateRow, historical_stock_pricesDF, stockPastEarningsDF, daysAroundEarnings=10):
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
    earningsDate = earnDateRow.Earnings_Date.date()
    stockPastEarningsDF.at[earnDateRow.Index, 'EDClose'] = historical_stock_pricesDF.close[earningsDate]

    try:
        # the day before earnings date
        # Earning Day Back 1 Day - Closing Price
        theEDMinus1Date = dateUtils.goOutXWeekdays(earningsDate, -1)
        stockPastEarningsDF.at[earnDateRow.Index, 'EDBak1DayClose'] = historical_stock_pricesDF.close[theEDMinus1Date]

        # the day after earnings date
        # Earning Day Forward 1 Day - Closing Price
        theEDPlus1Date = dateUtils.goOutXWeekdays(earningsDate, 1)
        stockPastEarningsDF.at[earnDateRow.Index, 'EDFwd1DayClose'] = historical_stock_pricesDF.close[theEDPlus1Date]

        # plus 4 days after earnings date
        # Earning Day Forward 4 Days Closing Price
        theEDplus4Date = dateUtils.goOutXWeekdays(earningsDate, 4)
        stockPastEarningsDF.at[earnDateRow.Index, 'EDFwd4DayClose'] = historical_stock_pricesDF.close[theEDplus4Date]

        # plus 1 days after earnings date
        # Earning Day Forward 1 Day Open Price
        stockPastEarningsDF.at[earnDateRow.Index, 'EDFwd1DayOpen'] = historical_stock_pricesDF.open[theEDPlus1Date]

        stockPastEarningsDF.at[earnDateRow.Index, 'EDBak1DayOpen'] = historical_stock_pricesDF.open[theEDMinus1Date]
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
    stocksPastEarningsDF['EDFwd4DayClose'] = stocksPastEarningsDF['EDFwd4DayClose'].round(2)
    stocksPastEarningsDF['EDDiffFwd4Close'] = stocksPastEarningsDF['EDDiffFwd4Close'].round(2)
    stocksPastEarningsDF['EDDiffFwd1Close'] = stocksPastEarningsDF['EDDiffFwd1Close'].round(2)
    stocksPastEarningsDF['EDFwd1DayClosePercentDelta'] = stocksPastEarningsDF['EDFwd1DayClosePercentDelta'].round(4)
    stocksPastEarningsDF['EDFwd4DayClosePercentDelta'] = stocksPastEarningsDF['EDFwd4DayClosePercentDelta'].round(4)

    # Todo - take out last
    # stocksPastEarningsDF['Last'] = stocksPastEarningsDF['Last'].round(2)


    stocksPastEarningsDF['EDFwd1DayOpen'] = stocksPastEarningsDF['EDFwd1DayOpen'].round(2)
    stocksPastEarningsDF['EDBak1DayOpen'] = stocksPastEarningsDF['EDBak1DayOpen'].round(2)

    stocksPastEarningsDF['Earnings_Date'] = stocksPastEarningsDF['Earnings_Date'].apply(dateUtils.getDateStringDashSeprtors)

    stocksPastEarningsDF = stocksPastEarningsDF[['Symbol', 'Company', 'Earnings_Date', 'EPS_Estimate', 'Reported_EPS',
                                                  'Surprise(%)', 'High', 'Open', 'Volume', 'Low', 'Close', 'EDClose', 'EDFwd1DayOpen',
                                                  'EDFwd1DayClose', 'EDBak1DayOpen', 'EDBak1DayClose', 'EDFwd4DayClose', 'EDDiffFwd4Close',
                                                  'EDDiffFwd1Close', 'EDFwd1DayClosePercentDelta',
                                                  'EDFwd4DayClosePercentDelta']]

    # if we are using the Max Earnings Quarters (32) prune off the remaining years data
    if pruneDF == True:
        stocksPastEarningsDF = stocksPastEarningsDF.iloc[0:32]

    return stocksPastEarningsDF