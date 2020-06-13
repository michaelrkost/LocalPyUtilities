"""
module: getStrategyPrice

This file is intended to be imported as a module and contains the following
functions:

    * getHistoricStockPrices - Get Historic Price from YahooFinancials
    * getEarningsDayPricing  - Get earning day closing prices and calculate deltas out 1 & 4 days
    * getExpectedPriceRangeTillNextExpiryDays - Get the expected price range at the next monthly expiry of an underlying.

"""
#=============================================================
import sys
sys.path.append('/home/michael/jupyter/local-packages')

import datetime
import numpy as np
import pandas as pd

import math
# ToDo add logging capability / switch on/off debug

# Get my Utilities (localUtilities)
from localUtilities import dateUtils

# YahooFinancials
# https://pypi.org/project/yahoofinancials/
# A python module that returns stock, cryptocurrency,
# forex, mutual fund, commodity futures, ETF,
# and US Treasury financial data from Yahoo Finance.
# TODO: Determine if this is adequate or if we should creat a Database with this info.
# ToDo: review investpy as an alternative to yahoofinancials // https://investpy.readthedocs.io
from yahoofinancials import YahooFinancials

#===========================================================================

def getHistoricStockPrices(stock, yahooEarningsDF, daysAroundEarnings = 10):
    """
    Get Historic Stock Price data from YahooFinancials----
    add daysAroundEarnings Days forward/back - this will be used to earnDateRow back and plot time
    durationString,The amount of time (or Valid Duration String units) to go back from the
    request's given end date and time.

    Parameters
    ----------
    stock :             Stock symbol string
    yahooEarningsDF:    a pandas DF of scraped companies and earnings data
    daysAroundEarnings: Number for Number of Days before / after Earnings date to use for processing

    Returns
    -------
    # update yahooEarningsDF - panda dataframe - closing prince info and closing $ and % deltas
    yahooEarningsDF

        """

    yahooEarningsDF['EDClosePrice'] = np.nan
    yahooEarningsDF['EDPlus1ClosePrice'] = np.nan
    yahooEarningsDF['EDMinus1ClosePrice'] = np.nan
    yahooEarningsDF['EDPlus4ClosePrice'] = np.nan
    yahooEarningsDF['Plus4MinusED'] = np.nan
    yahooEarningsDF['Plus1MinusED'] = np.nan
    yahooEarningsDF['EDPlus4ClosePriceDiffPercent'] = np.nan
    yahooEarningsDF['EDPlus1ClosePriceDiffPercent'] = np.nan
    yahooEarningsDF['EDCloseToFwd1DayOpen'] = np.nan


    # get the Stock into yahoofinancials module
    yahoo_financials = YahooFinancials(stock)

    # Bar Size = Daily weekly etc
    barSizeSetting = 'daily'

    # Get Historical price data for each Stock past earnings Dates
    for earnDateRow in range(0, len(yahooEarningsDF)):
        # set start and end Date
        # set to format 2018-09-29 // String Dash Separator
        endDateTime = dateUtils.getDateStringDashSeprtors(yahooEarningsDF['Earnings_Date'][earnDateRow]
                                                          +datetime.timedelta(days=daysAroundEarnings))
        startDateTime = dateUtils.getDateStringDashSeprtors(yahooEarningsDF['Earnings_Date'][earnDateRow]
                                                            -datetime.timedelta(days=daysAroundEarnings))

        # Get historic stock prices from yahoofinancials within daysAroundEarnings timeframe
        historical_stock_prices = yahoo_financials.get_historical_price_data(startDateTime, endDateTime, barSizeSetting)
        #create DF from prices
        historical_stock_prices = pd.DataFrame(historical_stock_prices[stock]['prices'])

        yahooEarningsDF = getEarningsDayPricing(earnDateRow, historical_stock_prices, yahooEarningsDF, yahooEarningsDF['Earnings_Date'][earnDateRow])

    # calculate price and persent deltas
    yahooEarningsDF['Plus4MinusED'] = yahooEarningsDF['EDPlus4ClosePrice'] - yahooEarningsDF['EDClosePrice']
    yahooEarningsDF['Plus1MinusED'] = yahooEarningsDF['EDPlus1ClosePrice'] - yahooEarningsDF['EDClosePrice']

    yahooEarningsDF['EDPlus4ClosePriceDiffPercent'] = 1-(yahooEarningsDF['EDClosePrice'] / yahooEarningsDF['EDPlus4ClosePrice'])
    yahooEarningsDF['EDPlus1ClosePriceDiffPercent'] = 1-(yahooEarningsDF['EDClosePrice'] / yahooEarningsDF['EDPlus1ClosePrice'])

    print("-------------------------------------- cat \n Meow------------------------------")


    return yahooEarningsDF

def getEarningsDayPricing(earnDateRow, historical_stock_prices, yahooEarningsDF, daysAroundEarnings=10):
    """
    Get earning closing price data from  historical_stock_prices for days before / after ----

    Parameters
    ----------
    earnDateRow : current row in yahooEarningsDF / aStock
    historical_stock_prices: Get historic stock prices from yahoofinancials :             Stock symbol string
    yahooEarningsDF:    a pandas DF of scraped companies and earnings data
    daysAroundEarnings: Number for Number of Days before / after Earnings date

    Returns
    -------
    # time series panda dataframes
    yahooEarningsDF
        """

    # recreate index as the 'date' column for price
    historical_stock_prices['date'] = historical_stock_prices['formatted_date'].apply(dateUtils.getDateFromISO8601)

    historical_stock_prices = historical_stock_prices.set_index("date", drop=False)
    # historical_stock_prices.index = pd.to_datetime(historical_stock_prices.index)

    # get current earningsdate in yahooEarningsDF / count
    earningsDate = yahooEarningsDF['Earnings_Date'][earnDateRow].date()
    yahooEarningsDF.at[earnDateRow, 'EDClosePrice'] = historical_stock_prices.close[earningsDate]

    # the day before earnings date
    theEDMinus1Date = dateUtils.goOutXWeekdays(earningsDate, -1)
    yahooEarningsDF.at[earnDateRow, 'EDMinus1ClosePrice'] = historical_stock_prices.close[theEDMinus1Date]

    # the day after earnings date
    theEDPlus1Date = dateUtils.goOutXWeekdays(earningsDate, 1)
    yahooEarningsDF.at[earnDateRow, 'EDPlus1ClosePrice'] = historical_stock_prices.close[theEDPlus1Date]

    yahooEarningsDF.at[earnDateRow, 'EDPlus1OpenPrice'] = historical_stock_prices.open[theEDPlus1Date]

    # plus 4 days after earnings date
    theEDplus4Date = dateUtils.goOutXWeekdays(earningsDate, 4)
    yahooEarningsDF.at[earnDateRow, 'EDPlus4ClosePrice'] = historical_stock_prices.close[theEDplus4Date]

    return yahooEarningsDF


def getExpectedPriceRangeTillNextExpiryDays(underlyingPrice, impVol):
    """
    Get the expected price range of an underlying at the next
    monthly expiry.

    using:
    (Stock Price * IV)/SQRT(Days to Expiry/#Days in a Year)

    suggest using: # todo -- update to this Expected Price Range - do not think this is correct
                   # todo -- continue to include Days to Expiry. 6/10/2020
    (Stock Price * IV)/SQRT(#Days in a Year)


    Parameters
    ----------
    underlyingPrice : price of the underlying stock
    impVol : implied volatility of the underlying

    Returns
    -------

    """
    # print('underlyingPrice: ', type(underlyingPrice))
    # print('impVol: ', type(impVol))

    try:
        priceTimesImpvol = underlyingPrice * impVol
        sqrtOfDaysDiv = math.sqrt(dateUtils.daysToExpiry(dateUtils.getNextExpiryDate()) / 365)
    except ValueError:
        print("****   in getExpectedPriceRangeTillNextExpiryDays")
        print("          ValueError: ", ValueError)
        print('          underlyingPrice: ', underlyingPrice)
        print('          impVol: ', impVol)
        return 0

    return round((priceTimesImpvol * sqrtOfDaysDiv),2)