import sys
sys.path.append('/home/michael/jupyter/local-packages')

# A python module that returns stock, cryptocurrency,
# forex, mutual fund, commodity futures, ETF,
# and US Treasury financial data from Yahoo Finance.
# todo: https://pypi.org/project/yahoofinancials/ or https://pypi.org/project/yfinance/
# ToDo: review investpy as an alternative to yahoofinancials // https://investpy.readthedocs.io
# todo: https://www.alphavantage.co/#about

from yahoofinancials import YahooFinancials
import yfinance as yf
import yahoo_fin.stock_info as si  

import pandas as pd
import numpy as np
import math

from localUtilities import dateUtils, config
from localUtilities.ibUtils.getClosest import Closest as close

from datetime import date, timedelta
# to handle json errors
from json.decoder import JSONDecodeError

# ================================================================

def addCurrentMarketData(earningsDF, anIndex, symbol):
    """
    Update earningDF -> High, Open,Volume,Low,Close,Option_Volume,CallOpenInterest, PutOpenInterest,
    impliedVolatility, Expected_Range,  histVolatility
    :param earningsDF:
    :type earningsDF: Dataframe
    :param anIndex: current row in earningDF
    :type anIndex: row index
    :param symbol: stock
    :type symbol: str

    """
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
    
    # Get Stock Stats
    getStats(earningsDF, anIndex, symbol)

    if allOptions == 0: # no options - can't calculate these
        earningsDF.at[anIndex, 'impliedVolatility'] = 0
        earningsDF.at[anIndex, 'Expected_Range'] = 0
        earningsDF.at[anIndex, 'histVolatility'] = getHistoricVol(symbol)
    else:
        try:
            iv, days2Expiry = getIV(ayfTicker)
            earningsDF.at[anIndex, 'impliedVolatility'] = iv
            earningsDF.at[anIndex, 'Expected_Range'] = getExpectedRange(iv, currentPrice, days2Expiry)
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
            
def getStats(earningsDF, anIndex, symbol):
    """
    
    :param earningsDF: DF of Stock's of interest
    :type earningsDF: Dataframe
    :param anIndex: 
    :type anIndex: 
    :param symbol: 
    :type symbol: 
    :return: 
    :rtype: 
    """
    # get Stats from Yahoo
    mktData = YahooFinancials(symbol)

    # Company Stats                                          [0:-2]
    earningsDF.at[anIndex, 'Beta (5Y Monthly)']          = YahooFinancials.get_beta(mktData)             #= aSI.at[0,'Value']
    earningsDF.at[anIndex, '52 Week High']               = YahooFinancials.get_yearly_high(mktData)
    earningsDF.at[anIndex, '52 Week Low']                = YahooFinancials.get_yearly_low(mktData)
    earningsDF.at[anIndex, '50-Day Moving Average']      = YahooFinancials.get_50day_moving_avg(mktData)
    earningsDF.at[anIndex, '200-Day Moving Average']     = YahooFinancials.get_200day_moving_avg(mktData)
    earningsDF.at[anIndex, 'Avg Vol (3 month)']          = YahooFinancials.get_three_month_avg_daily_volume(mktData)
    earningsDF.at[anIndex, 'Avg Vol (10 day)']           = YahooFinancials.get_ten_day_avg_daily_volume(mktData)
    earningsDF.at[anIndex, 'Current Shares Outstanding'] = YahooFinancials.get_num_shares_outstanding(mktData, price_type='current')
    earningsDF.at[anIndex,'Average Shares Outstanding']  = YahooFinancials.get_num_shares_outstanding(mktData, price_type='average')
    # get key company share stats from YahooFinancials.get_key_statistics_data(mktData)
    companyKeyStats = pd.DataFrame()
    theStats = YahooFinancials.get_key_statistics_data(mktData)
    companyKeyStats = companyKeyStats.from_dict(theStats, orient='index')

    # ToDo: check on 52-week change data - seems to not be coming in
    earningsDF.at[anIndex, '52-Week Change']                              = companyKeyStats.at[symbol, '52WeekChange']
    earningsDF.at[anIndex, 'S&P500 52-Week Change']                       = companyKeyStats.at[symbol, 'SandP52WeekChange']
    earningsDF.at[anIndex, 'Float Shares']                                = companyKeyStats.at[symbol, 'floatShares']
    earningsDF.at[anIndex, '% Held by Insiders']                          = companyKeyStats.at[symbol, 'heldPercentInsiders']
    earningsDF.at[anIndex, 'Shares Short (previous month)']               = companyKeyStats.at[symbol, 'sharesShort']
    earningsDF.at[anIndex, 'Shares Ratio (previous month)']               = companyKeyStats.at[symbol, 'shortRatio']
    earningsDF.at[anIndex, 'Short % of Float (previous month)']           = companyKeyStats.at[symbol, 'shortPercentOfFloat']
    # earningsDF.at[anIndex, 'Short % Shares Outstanding (previous month)'] = companyKeyStats.at[symbol, 'sharesPercentSharesOut']
    earningsDF.at[anIndex, 'Shares Short (prior month)']                  = companyKeyStats.at[symbol, 'sharesShortPriorMonth']



def getIV_CallIV(aYFTicker, currentPrice, pushIVout = config.pushIVDateOutNDays):
    #  Implied Volatility: The average implied volatility (IV) of the ""nearest"" monthly options contract.
    #  IV is a forward looking prediction of the likelihood of price change of the underlying asset,
    #  with a higher IV signifying that the market expects significant price movement, and a lower IV signifying
    #  the market expects the underlying asset price to remain within the current trading range.
    # Approach:
    #   1) Find the next month Option - after - at least 10 days out -  at the current price
    #       a) Get the Put/Call IV at the current stock - use this as the Stock IV
    #     or
    #       b) The average implied volatility (IV) of the ""nearest"" monthly options contract

    # get the date 'pushIVout' number of days out
    startDate = dateUtils.getTodayOffsetDays(pushIVout)
    # now find the next monthly option expiry date
    optionExpiryDate = dateUtils.getNextThirdFridayFromStr(startDate)
    # get number of days to optionExpiryDate
    days2Expiry = dateUtils.getDateFromISO8601(optionExpiryDate) - dateUtils.getTodayDateTime()
    # Get the option chain for next monthly option expiry date // optionExpiryDate
    optionExpiryChain = aYFTicker.option_chain(optionExpiryDate)
    # find the closest option strike to current price in option chain
    closestStrike = close.get_closestInDFCol(optionExpiryChain.calls, "strike", currentPrice)

    aChain = aYFTicker.option_chain(optionExpiryDate)
    # get the IV
    ivC = aChain.calls.at[closestStrike, "impliedVolatility"]

    return ivC, days2Expiry

def getIV_meanPnC(aYFTicker, pushIVout = config.pushIVDateOutNDays):
    #  IV is commonly expressed using percentages and standard deviations over a specified time horizon.
    #
    # Implied volatility (IV) in the stock market refers to the implied magnitude, or one standard deviation range,
    # of potential movement away from the stock price in a year's time.

    #
    #  IV is a forward looking prediction of the likelihood of price change of the underlying asset,
    #  with a higher IV signifying that the market expects significant price movement, and a lower IV signifying
    #  the market expects the underlying asset price to remain within the current trading range.
    # Approach:
    #   1) pushIVout -
    #       how far to look for the next monthly option - at least ""pushIVout"" days out past the current date
    #       pushIVout set to 10 on 2/6/22
    #   1) Find the next month Option - after - at least 10 days out -  at the current price
    #       a) Get the Put/Call IV at the current stock - use this as the Stock IV // getIV_CallIV()
    #     or
    #       b) The average implied volatility (IV) of the ""nearest"" monthly options contract // getIV()

    # get the date 'pushIVout' number of days out
    startDate = dateUtils.getTodayOffsetDays(pushIVout)
    # now find the next monthly option expiry date
    optionExpiryDate = dateUtils.getNextThirdFridayFromStr(startDate)
    # get number of days to optionExpiryDate
    days2Expiry = dateUtils.getDateFromISO8601(optionExpiryDate) - dateUtils.getTodayDateTime()
    # Get the option chain for next monthly option expiry date // optionExpiryDate
    # optionExpiryChain = aYFTicker.option_chain(optionExpiryDate)
    # # find the closest option strike to current price in option chain
    # closestStrike = close.get_closestInDFCol(optionExpiryChain.calls, "strike", currentPrice)

    aChain = aYFTicker.option_chain(optionExpiryDate)
    # get the IV
    ivC = aChain.calls["impliedVolatility"].mean()
    ivP = aChain.puts["impliedVolatility"].mean()

    avgIV = (ivC + ivP) / 2

    return avgIV, days2Expiry.days

def getIV_Binomial(aYFTicker, pushIVout=config.pushIVDateOutNDays):
    # This model uses a tree-style diagram that factors in volatility at multiple levels.
    # It shows the many ways it could branch off price-wise.
    # Then, it goes backward to determine what seems like a reasonable average.
    # https://ec.europa.eu/energy/sites/ener/files/documents/volatility_methodology.pdf
    return None

def getIV(aYFTicker):
    #  IV is commonly expressed using percentages and standard deviations over a specified time horizon.
    #
    # Implied volatility (IV) in the stock market refers to the implied magnitude, or one standard deviation range,
    # of potential movement away from the stock price in a year's time.
    #
    #  IV is a forward looking prediction of the likelihood of price change of the underlying asset,
    #  with a higher IV signifying that the market expects significant price movement, and a lower IV signifying
    #  the market expects the underlying asset price to remain within the current trading range.
    #  For this method  - Find the next 3rd Friday -""optionExpiryDate""- monthly Option Chain ""aChain""
    #    - after, at least, 10 days out -""pushIVout""
    #
    # Parameters:
    #   aYFTicker - yfinance ticker data
    #   offsetDays - offset day for daysOffset as: <class 'datetime.date'> // default is in config.py
    # return:
    #   avgIv : calculated IV
    #             - take the mean of the put & call IV - then average - (put+call) / 2
    #   monthlyOptionExpiryDate: the Expiry date as str

    # get the days to Expiry and the monthly OptionExpiry as Date string format -- '2018-07-18'
    days2Expiry, monthlyOptionExpiryDate = dateUtils.getDays2ExpirationAndExpiry()
    # get the option chain
    aChain = aYFTicker.option_chain(monthlyOptionExpiryDate)
    # get the IV
    ivC = aChain.calls["impliedVolatility"].mean()
    ivP = aChain.puts["impliedVolatility"].mean()
    # average the put.mean/call.mean
    avgIV = (ivC + ivP) / 2

    return avgIV, days2Expiry


def getExpectedRange(iv, currentPrice, days2Expiry):
    # A stock’s “expected move” represents the one standard deviation expected range
    # for a stock’s price in the future.
    # https://www.tastytrade.com/concepts-strategies/standard-deviation#what-is-standard-deviation?
    # expectedRange = 1SD Expected Move
    # A one standard deviation range encompasses 68% of the expected outcomes, so a stock’s
    # expected move is the magnitude of that stock’s future price movements with 68% certainty.

    # There are Four variables that go into the expected move formula:
    # 1) currentPrice = The current stock price
    # 2) iv = The stock’s implied volatility / IV of Option’s Expiration Cycle
    # 3) days2Expiry = The desired expected move period (expressed as the number of days)
    #       -- Days to Expiration of your Option Contract
    #       -- using days to next months expiry / so this number is the Days2Expiration
    # 4) Trading Days in a year - currently using 252, rather than 365 as this is the number of trading days in a year

    # Expected Range = StockPrice * IV * sqrt(Days2Expiration/ 252)
    expectedRange = (currentPrice * iv) * math.sqrt(days2Expiry / 252)

    return expectedRange

def getExpectedRange4BinaryEvent():
#  Calculating Expected Move Standard Deviation of a stock
# https://www.tastytrade.com/concepts-strategies/standard-deviation
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
    # Get the Option Volume of all the Tickers/aTicker Options
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
    # historical volatility is the annualized standard deviation of the stock.

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
