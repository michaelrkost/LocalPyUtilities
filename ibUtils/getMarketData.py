"""
module: setup

"""
#Todo - error management / ib.errorEvent += onError
import sys
sys.path.append('/home/michael/jupyter/local-packages')

# A python module that returns stock, cryptocurrency,
# forex, mutual fund, commodity futures, ETF,
# and US Treasury financial data from Yahoo Finance.
# todo: https://pypi.org/project/yahoofinancials/ or https://pypi.org/project/yfinance/
# ToDo: review investpy as an alternative to yahoofinancials // https://investpy.readthedocs.io
from yahoofinancials import YahooFinancials

# todo: use yfinance to get option info - is this better than yahoofinancials??
import yfinance as yf
import pandas as pd
import numpy as np
import math

from localUtilities import dateUtils
from datetime import date, timedelta
from localUtilities.ibUtils.getClosest import Closest as close

# to handle json errors
from json.decoder import JSONDecodeError

# ================================================================

def addCurrentMarketData(earningsDF, anIndex, symbol):
    mktData = YahooFinancials(symbol)
    # The Ticker module, which allows you to access yfinance ticker data in a more Pythonic way
    ayfTicker = yf.Ticker(symbol)


    earningsDF.at[anIndex, 'High'] = mktData.get_daily_high()
    earningsDF.at[anIndex, 'Open'] = mktData.get_open_price()
    earningsDF.at[anIndex, 'Volume'] = mktData.get_current_volume()
    earningsDF.at[anIndex, 'Low'] = mktData.get_daily_low()
    earningsDF.at[anIndex, 'Close'] = mktData.get_prev_close_price()

    currentPrice = mktData.get_current_price()
    earningsDF.at[anIndex, 'Last'] = currentPrice

    allOptions, callOptions, putOptions = getOptionVolume(ayfTicker)
    earningsDF.at[anIndex, 'Option_Volume'] = allOptions
    earningsDF.at[anIndex, 'CallOpenInterest'] = callOptions
    earningsDF.at[anIndex, 'PutOpenInterest'] = putOptions

    if allOptions == 0: # no options - cant calculate these
        earningsDF.at[anIndex, 'impliedVolatility'] = 0
        earningsDF.at[anIndex, 'Expected_Range'] = 0
        earningsDF.at[anIndex, 'histVolatility'] = getHistoricVol(symbol)
    else:
        try:
            iv = getIV(ayfTicker, currentPrice)
            earningsDF.at[anIndex, 'impliedVolatility'] = iv
            earningsDF.at[anIndex, 'Expected_Range'] = getExpectedRange(iv, currentPrice)
            earningsDF.at[anIndex, 'histVolatility'] = getHistoricVol(symbol)
        except KeyError:
            print('     Stock: ', symbol)
            print('         ', KeyError, )
            earningsDF.at[anIndex, 'impliedVolatility'] = 0
            earningsDF.at[anIndex, 'Expected_Range'] = 0
            earningsDF.at[anIndex, 'histVolatility'] = 0
        except ValueError:
            print('     Stock: ', symbol)
            print('         ', ValueError, )
            earningsDF.at[anIndex, 'impliedVolatility'] = 0
            earningsDF.at[anIndex, 'Expected_Range'] = 0
            earningsDF.at[anIndex, 'histVolatility'] = 0

    print('\thistVolatility: ', earningsDF.at[anIndex, 'histVolatility'],
          '  Expected_Range: ', earningsDF.at[anIndex, 'Expected_Range'],
          '  Option_Volume: ',    earningsDF.at[anIndex, 'Option_Volume'],
          '  impliedVolatility', earningsDF.at[anIndex, 'impliedVolatility']
          )

def getIV(aYFTicker, currentPrice, pushDateOutNDays = 10):
    #  Implied Volatility: The average implied volatility (IV) of the nearest monthly options contract.
    #  IV is a forward looking prediction of the likelihood of price change of the underlying asset,
    #  with a higher IV signifying that the market expects significant price movement, and a lower IV signifying
    #  the market expects the underlying asset price to remain within the current trading range.

    # Find the next month Option - after - at least 10 days out -  at the current price
    # Get the Put/Call IV - use this as the Stock IV

    # get the date 'pushDateOutNDays' number of days out
    startDate = dateUtils.getTodayOffsetDays(pushDateOutNDays)
    # now find the next monthly option expiry date
    optionExpiryDate = dateUtils.getNextThirdFridayFromStr(startDate)
    # Get the option chain for next monthly option expiry date // optionExpiryDate
    optionExpiryChain = aYFTicker.option_chain(optionExpiryDate)
    # find the closest option strike to current price in option chain
    closestStrike = close.get_closestInDFCol(optionExpiryChain.calls, "strike", currentPrice)

    aChain = aYFTicker.option_chain(optionExpiryDate)
    # get the IV
    ivC = aChain.calls.at[closestStrike, "impliedVolatility"]

    return ivC


def getExpectedRange(iv, currentPrice, days2Expiration=None):
    # A stock’s “expected move” represents the one standard deviation expected range
    # for a stock’s price in the future.

   # A one standard deviation range encompasses 68% of the expected outcomes, so a stock’s
    # expected move is the magnitude of that stock’s future price movements with 68% certainty.

    # There are three variables that go into the expected move formula:
    # 1) The current stock price
    # 2) The stock’s implied volatility
    # 3) The desired expected move period (expressed as the number of days)
    #       -- using 252 as this is the number of trading days in a year
    # 4) using days to next months expiry / Days2Expiration

    # Expected Range = StockPrice * IV * sqrt(Days2Expiration/ 252)
    if days2Expiration == None:
        days2Expiration = dateUtils.getDays2Expiration()

    expectedRange = (currentPrice * iv) * math.sqrt(days2Expiration / 252)

    return expectedRange

def getExpectedRange4BinaryEvent():
#     Calculating Expected Move
# Expected move is the amount that a stock is predicted to increase or decrease from its current price,
# based on the current level of implied volatility for binary events.
#
# We use this calculation on the day before the binary event or very close to the expiration date.
# The expected move of a stock for a binary event can be found by calculating 85% of the value of the
# front month at the money (ATM) straddle. Add the price of the front month ATM call and the price of
# he front month ATM put, then multiply this value by 85%. Another easy way to calculate the expected
# move for a binary event is to take the ATM straddle, plus the 1st OTM strangle and then divide the sum by 2.
#
# We only use this for a binary event because the accuracy of premium decay and all of the variables a
# ssociated with implied volatility are too rich to accurately reflect expected move for a longer time period.

    return None
# ================================================================

def getOptionVolume(aTicker):

    # setup counters
    putsOptionVolCount = 0
    callsOptionVolCount = 0

    # get the ticker info
    optionExpiry = aTicker.options
    if not all(optionExpiry): # no options
        return 0, 0, 0

    for anOptionExpiry in optionExpiry:
        try:
            putsDF = aTicker.option_chain(anOptionExpiry).puts
            callsDF = aTicker.option_chain(anOptionExpiry).calls
            putsOptionVolCount = putsDF['openInterest'].sum() + putsOptionVolCount
            callsOptionVolCount = callsDF['openInterest'].sum() + callsOptionVolCount
        except JSONDecodeError  as e:
            print('     Stock: ', aTicker)
            print('         ', JSONDecodeError, )
            continue


    allOptionVolCount = callsOptionVolCount + putsOptionVolCount

    return allOptionVolCount, callsOptionVolCount, putsOptionVolCount

def getHistoricVol(symbol):
    #
    # 20-Day Historical Volatility:
    # The average deviation from the average price over the last 20 days. Historical Volatility is a
    # measurement of how fast the underlying security has been changing in price back in time.
    #

    # get Historic Volatility
    # https://corporatefinanceinstitute.com/resources/knowledge/trading-investing/historical-volatility-hv/
    # https://www.macroption.com/historical-volatility-calculation/

    # The basic period (for which we calculate returns in the beginning) – often 1 day is used

    # How many periods enter the calculation (we will refer to this as n) – often 20 or 21 days
    # or 63 days (representing 1 month or 3 months)
    # (the number of trading days and therefore the number of basic periods in one month)
    calcPeriod = 21

    # How many periods there are in a year (T; this is used for annualizing volatility in the end)
    #
    # Use 1 day (day-to-day returns), 21 or 63 days (representing 1 month or 3 months),
    # and 252 (as there are 252 trading days per year on average).
    yearTradingDays = 252

    # set date range for historical prices
    # using expiryDate Days
    end_time = date.today()
    start_time = end_time - timedelta(days=calcPeriod)

    # reformat date range
    end = end_time.strftime('%Y-%m-%d')
    start = start_time.strftime('%Y-%m-%d')

    # get daily stock prices over date range
    json_prices = YahooFinancials(symbol).get_historical_price_data(start, end, 'daily')


    # transform json file to dataframe
    prices = pd.DataFrame(json_prices[symbol]
                          ['prices'])[['formatted_date', 'close']]

    # sort dates in descending order
    prices.sort_index(ascending=False, inplace=True)

    # calculate daily logarithmic return
    prices['returns'] = (np.log(prices.close /
                                prices.close.shift(-1)))

    # calculate daily standard deviation of returns
    daily_std = np.std(prices.returns)

    # annualized daily standard deviation
    annualStd = daily_std * yearTradingDays ** 0.5
    return annualStd
