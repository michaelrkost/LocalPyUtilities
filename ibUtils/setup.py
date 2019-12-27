"""
module: setup

"""
#Todo - error management / ib.errorEvent += onError
import sys
sys.path.append('/home/michael/jupyter/local-packages')

import datetime
# Get my Utilities (localUtilities)
from localUtilities import dateUtils

from yahoofinancials import YahooFinancials

from localUtilities.ibUtils import getStrategyPrice as strat, getOptionInfo
from localUtilities.webScrape import getMarketData

import numpy as np
import pandas as pd
# ================================================================

def addMarketData(earningsDF, startday):
    """
    Add Market Data / 'histVolatility', 'impliedVolatility', 'avOptionVolume','Expected_Range' etc./
    to companies in passed DF

    Parameters
    ----------
    earningsDF: DF of 'Symbol', 'Earnings_Date', 'Company', 'Earnings Call Time'
    startday: the starting date

    Returns
    -------
    DF w/ Market Data for companies w/ greater than some number, say 5000,
    in Option Volume - worthwhile causes
    """
# get info from the time of this run
    earningsDF['High'] = np.nan
    earningsDF['Open'] = np.nan
    earningsDF['Volume'] = np.nan
    earningsDF['Option_Volume'] = np.nan
    earningsDF['Low'] = np.nan
    earningsDF['Close'] = np.nan
    earningsDF['histVolatility'] = np.nan
    earningsDF['impliedVolatility'] = np.nan
    earningsDF['Expected_Range'] = np.nan
    earningsDF['PutFridayOpenInterest'] = np.nan
    earningsDF['CallFridayOpenInterest'] = np.nan

    lenDF = len(earningsDF)

    for row in earningsDF.itertuples():
        print(row.Symbol, ' @  ', lenDF,  end=", ")
        lenDF = lenDF - 1

        putsOpenInterest, callsOpenInterest = getOptionInfo.getOptionVolumeNextFriExpiryCount(row.Symbol, startday)
        dict_MktData = getMarketData.getMarketDataFromOptionistics(row.Symbol)

        # todo can append the dictionary to the DF as well.
        earningsDF.at[row.Index, 'High'] = dict_MktData['HIGH']
        earningsDF.at[row.Index, 'Open'] = dict_MktData['OPEN']
        earningsDF.at[row.Index, 'Volume'] = dict_MktData['VOLUME']
        earningsDF.at[row.Index, 'Option_Volume'] = dict_MktData['OPTION VOLUME']
        earningsDF.at[row.Index, 'Low'] = dict_MktData['LOW']
        earningsDF.at[row.Index, 'Close'] = dict_MktData['CLOSE']
        earningsDF.at[row.Index, 'Last'] = dict_MktData['LAST']
        earningsDF.at[row.Index, 'histVolatility'] = dict_MktData['HISTORICAL VOL']
        earningsDF.at[row.Index, 'impliedVolatility'] = dict_MktData['IMPLIED VOLATILITY']

        earningsDF.at[row.Index, 'PutFridayOpenInterest'] = putsOpenInterest
        earningsDF.at[row.Index, 'CallFridayOpenInterest'] = callsOpenInterest
        earningsDF.at[row.Index, 'Expected_Range'] = strat.getExpectedPriceRangeTillNextExpiryDays( float(dict_MktData['LAST']) ,
                                                                                                   float(dict_MktData['IMPLIED VOLATILITY']))
        #print(earningsDF)

    print('Done.....')
    #remove companies w/ less that 500 in Call Open Interest
    earningsDFOptionVolGood = earningsDF[(earningsDF['CallFridayOpenInterest'] >= 500)]

    return earningsDFOptionVolGood.reset_index(drop=True), earningsDF


def addPastMarketData(stocksPastEarningsDF, daysAroundEarnings = 10):
    """
    Add Market Data to companies in  stocksPastEarningsDF

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

    stocksPastEarningsDF['EDClosePrice'] = np.nan
    stocksPastEarningsDF['EDPlus1ClosePrice'] = np.nan
    stocksPastEarningsDF['EDMinus1ClosePrice'] = np.nan
    stocksPastEarningsDF['EDPlus4ClosePrice'] = np.nan
    stocksPastEarningsDF['EDMinusPlus4ClosePrice'] = np.nan
    stocksPastEarningsDF['EDMinusPlus1ClosePrice'] = np.nan
    stocksPastEarningsDF['EDPlus4ClosePriceDiffPercent'] = np.nan
    stocksPastEarningsDF['EDPlus1ClosePriceDiffPercent'] = np.nan


    theStock = stocksPastEarningsDF.Symbol[0]
    lenDF = len(stocksPastEarningsDF)
    yahoo_financials = YahooFinancials(theStock)

    for earnDateRow in stocksPastEarningsDF.itertuples():
        print(earnDateRow.Symbol, ' / theStock: ', theStock,  ' @  ', lenDF, 'earnDateRow.Index: ',  earnDateRow.Index, end=", ")
        lenDF = lenDF - 1

        # set start and end Date
        # set to format 2018-09-29 // String Dash Separator
        endDateTime = dateUtils.getDateStringDashSeprtors(earnDateRow.Earnings_Date
                                                          +datetime.timedelta(days=daysAroundEarnings))
        startDateTime = dateUtils.getDateStringDashSeprtors(earnDateRow.Earnings_Date
                                                            -datetime.timedelta(days=daysAroundEarnings))

        # Get historic stock prices from yahoofinancials within daysAroundEarnings timeframe
        historical_stock_prices = yahoo_financials.get_historical_price_data(startDateTime, endDateTime, 'daily')
        historical_stock_pricesDF = pd.DataFrame(historical_stock_prices[theStock]['prices'])

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
            stocksPastEarningsDF.at[earnDateRow.Index, 'Last']   = historical_stock_pricesDF.adjclose[earnDateRow.Earnings_Date.date()]
        except KeyError:
            print('Stock: ', theStock)
            print('     ', KeyError, '       setup.addPastMarketData')
            continue

        stocksPastEarningsDF = getEarningsPriceMoves(earnDateRow, historical_stock_pricesDF, stocksPastEarningsDF)


    # calculate price and persent deltas
    stocksPastEarningsDF['EDMinusPlus4ClosePrice'] = stocksPastEarningsDF['EDPlus4ClosePrice'] - stocksPastEarningsDF['EDClosePrice']
    stocksPastEarningsDF['EDMinusPlus1ClosePrice'] = stocksPastEarningsDF['EDPlus1ClosePrice'] - stocksPastEarningsDF['EDClosePrice']

    stocksPastEarningsDF['EDPlus4ClosePriceDiffPercent'] = 1-(stocksPastEarningsDF['EDClosePrice'] / stocksPastEarningsDF['EDPlus4ClosePrice'])
    stocksPastEarningsDF['EDPlus1ClosePriceDiffPercent'] = 1-(stocksPastEarningsDF['EDClosePrice'] / stocksPastEarningsDF['EDPlus1ClosePrice'])
    
    print('\nDone.........')

    return stocksPastEarningsDF


def getEarningsPriceMoves(earnDateRow_In, historical_stock_pricesDF_In, stockPastEarningsDF_In, daysAroundEarnings=10):
    """
    Get earning closing price data from  historical_stock_prices for days before / after ----

    Parameters
    ----------
    earnDateRow_In : current row in yahooEarningsDF / aStock
    historical_stock_pricesDF_In: Get historic stock prices from yahoofinancials :             Stock symbol string
    stockPastEarningsDF_In:    a pandas DF of scraped companies and earnings data
    daysAroundEarnings: Number for Number of Days before / after Earnings date

    Returns
    -------
    # time series panda dataframes
    yahooEarningsDF
        """

    # get current earningsdate
    earningsDate = earnDateRow_In.Earnings_Date.date()
    stockPastEarningsDF_In.at[earnDateRow_In.Index, 'EDClosePrice'] = historical_stock_pricesDF_In.close[earningsDate]

    # the day before earnings date
    theEDMinus1Date = dateUtils.goOutXWeekdays(earningsDate, -1)
    stockPastEarningsDF_In.at[earnDateRow_In.Index, 'EDMinus1ClosePrice'] = historical_stock_pricesDF_In.close[theEDMinus1Date]

    # the day after earnings date
    theEDPlus1Date = dateUtils.goOutXWeekdays(earningsDate, 1)
    stockPastEarningsDF_In.at[earnDateRow_In.Index, 'EDPlus1ClosePrice'] = historical_stock_pricesDF_In.close[theEDPlus1Date]

    # plus 4 days after earnings date
    theEDplus4Date = dateUtils.goOutXWeekdays(earningsDate, 4)
    stockPastEarningsDF_In.at[earnDateRow_In.Index, 'EDPlus4ClosePrice'] = historical_stock_pricesDF_In.close[theEDplus4Date]

    return stockPastEarningsDF_In

