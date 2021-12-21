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

from localUtilities import dateUtils
from datetime import date, timedelta
from localUtilities.ibUtils.getClosest import Closest as close

# ================================================================

def addCurrentMarketData(earningsDF, anIndex, symbol):
    mktData = YahooFinancials(symbol)
    aTicker = yf.Ticker(symbol)


    earningsDF.at[anIndex, 'High'] = mktData.get_daily_high()
    earningsDF.at[anIndex, 'Open'] = mktData.get_open_price()
    earningsDF.at[anIndex, 'Volume'] = mktData.get_current_volume()
    earningsDF.at[anIndex, 'Low'] = mktData.get_daily_low()
    earningsDF.at[anIndex, 'Close'] = mktData.get_prev_close_price()

    currentPrice = mktData.get_current_price()
    earningsDF.at[anIndex, 'Last'] = currentPrice

    allOptions, callOptions, putOptions = getOptionVolume(aTicker)
    earningsDF.at[anIndex, 'Option_Volume'] = allOptions
    earningsDF.at[anIndex, 'CallOpenInterest'] = callOptions
    earningsDF.at[anIndex, 'PutOpenInterest'] = putOptions

    neededExpiry = dateUtils.getNeededExpiry(30)

    if allOptions == 0: # no options cant calculate these
        earningsDF.at[anIndex, 'impliedVolatility'] = 0
        earningsDF.at[anIndex, 'Expected_Range'] = 0
        earningsDF.at[anIndex, 'histVolatility'] = getHistoricVol(symbol, neededExpiry)
    else:
        try:
            iv, expectedRange = getIV_and_ExpectedRange(aTicker, currentPrice, neededExpiry)
            earningsDF.at[anIndex, 'impliedVolatility'] = iv
            earningsDF.at[anIndex, 'Expected_Range'] = expectedRange
            earningsDF.at[anIndex, 'histVolatility'] = getHistoricVol(symbol, neededExpiry)
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

def getIV_and_ExpectedRange(aTicker, currentPrice, neededExpiry):

    optionExpiry = aTicker.option_chain(dateUtils.getDateStringDashSeprtors(dateUtils.getDate(neededExpiry)))
    #print("next monthly pass 2 Weeks  // optionExpiry: ", optionExpiry)

    aCloseStrike = close.get_closestInDFCol(optionExpiry.calls, "strike", currentPrice)

    aChain = aTicker.option_chain(dateUtils.getDateStringDashSeprtors(dateUtils.getDate(neededExpiry)))
    ivC = aChain.calls.at[aCloseStrike, "impliedVolatility"]
    strikeC = aChain.calls.at[aCloseStrike, "strike"]
    lastPriceC = aChain.calls.at[aCloseStrike, "lastPrice"]
    print("Call // iv: ", ivC, "strike: ", strikeC, "lastPrice: ", lastPriceC)

    ivP = aChain.puts.at[aCloseStrike, "impliedVolatility"]
    strikeP = aChain.calls.at[aCloseStrike, "strike"]
    lastPriceP = aChain.calls.at[aCloseStrike, "lastPrice"]
    print("Put  // iv: ", ivP, "strike: ", strikeP, "lastPrice: ", lastPriceP)

    expectedRange = (lastPriceC + lastPriceP) / currentPrice

    return ivP, expectedRange
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
        putsDF = aTicker.option_chain(anOptionExpiry).puts
        callsDF = aTicker.option_chain(anOptionExpiry).calls
        putsOptionVolCount = putsDF['openInterest'].sum() + putsOptionVolCount
        callsOptionVolCount = callsDF['openInterest'].sum() + callsOptionVolCount

    allOptionVolCount = callsOptionVolCount + putsOptionVolCount

    return allOptionVolCount, callsOptionVolCount, putsOptionVolCount

def getHistoricVol(symbol, expiryDate):
#todo make this 30 days rather than 365
    # set date range for historical prices
    # using expiryDate Days
    end_time = date.today()
    dateDiff1 = abs(((end_time - dateUtils.getDate(expiryDate)).days))
    dateDiff = dateUtils.days_between_Date(end_time, dateUtils.getDate(expiryDate))
    print("\ndateDiff1:  ", type(dateDiff1), 'datediff :  ', dateDiff)
    start_time = end_time - timedelta(days=60) #dateUtils.getDate(expiryDate) # end_time - timedelta(days=expiryDate)

    # reformat date range
    end = end_time.strftime('%Y-%m-%d')
    start = start_time.strftime('%Y-%m-%d')


    print("end:  ", end)
    print("start: ", start)

    # get daily stock prices over date range
    json_prices = YahooFinancials(symbol
                                  ).get_historical_price_data(start, end, 'daily')

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
    annualStd = daily_std * 252 ** 0.5
    return annualStd
