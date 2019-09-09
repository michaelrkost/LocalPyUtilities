"""
module: getOptionStrategyPrice

This file is intended to be imported as a module and contains the following
functions:

    * getHistoricIVnPrice - Get IB Historic Price & IV time series
    * getEstimatedPriceMovefor1Day - Estimate Stock Price Move for 1 Day
    * getEstimatedPercentMovefor1Day - Estimate Stock Price Move for 1 Day
    * getExpectedPriceRangeTillNextExpiryDays - Estimate Stock Price Move till next Monthly expiry
    * getSnapshotTickersMarketPrice - stock Market price
    * getOptionStraddlePrice - option straddle price

"""
#=============================================================
import sys
sys.path.append('/home/michael/jupyter/local-packages')

import datetime
import pandas as pd

import math
from ib_insync import *
# ToDo add logging capability / swithch on/off debug

# Get my Utilities (localUtilities)
from localUtilities import dateUtils

# =========================================================

def getMinMaxPricePercent(earningsPastStock, earningsPastImpVol, yahooEarningsDF, theDays=10):

    listOfEarningDeltas = []
    priceEarnDay = []
    iv_DayAfterEarnings =[]
    iv_DayOfEarnings =[]
    iv_Dif = []

    # Get Min/Max Price/Percent in data set
    for count in range(0, len(yahooEarningsDF)):  # for all the dates in earningsCalendar
        # recreate index as the 'date' column for price
        ePSPrice = earningsPastStock[count].set_index("date", drop=False)
        ePSPrice.index = pd.to_datetime(ePSPrice.index)

        # recreate index as the 'date' column for IV
        eImpVol = earningsPastImpVol[count].set_index("date", drop=False)
        eImpVol.index = pd.to_datetime(eImpVol.index)

        # get current earningsdate in yahooEarningsDF / count
        theEarningDate = yahooEarningsDF['Earnings_Date'][count].date()
        # the day before earnings
        dayBeforeEarnings = theEarningDate - datetime.timedelta(days=2)
        # So this should be the day from one day before Earnings + theDays // default theDays to 10
        onEarningDateForward = theEarningDate + datetime.timedelta(days=theDays)

        # Create new dataframe from old // example -> old[['A', 'C', 'D']].copy()
        # Create a new DF subset[columns = date,close] of ePSPrice
        # this is the prices for days
        # within Date span of dayBeforeEarnings and onEarningDateForward // ePSPrice.loc[dayBeforeEarnings:onEarningDateForward
        # and set index to date // ['date', 'close']].copy()).set_index("date", drop=False)
        onEarningDatePlusTheDaysForwardDF = (ePSPrice.loc[dayBeforeEarnings:onEarningDateForward, ['date', 'close']].copy()).set_index("date", drop=False)

        # Let’s add a new column onEarningDatePlusTheDaysForwardDF['$Deltas'] and
        # onEarningDatePlusTheDaysForwardDF['%Deltas'] where
        # entry at each index will calculate  the values in other columns at that index i.e.
        #   = onEarningDatePlusTheDaysForwardDF.close - ePSPrice.close.at[theEarningDate]
        # Will get Price Delta $Delta and Percent Delta %Delta
        # Price Delta [$Delta] = new closing price minus closing on earnings date
        # %Delta = Price Delta [$Delta]/ earning date closing price
        try:
            onEarningDatePlusTheDaysForwardDF['$Deltas'] = onEarningDatePlusTheDaysForwardDF.close - ePSPrice.close.at[theEarningDate]
            onEarningDatePlusTheDaysForwardDF['%Deltas'] = (onEarningDatePlusTheDaysForwardDF.close - ePSPrice.close.at[theEarningDate]) / ePSPrice.close.at[theEarningDate]
        except KeyError:
            print('     ', KeyError, '       In getMinMaxPricePercent')
            continue

        # keep running list of earnings date deltas $% in this list
        listOfEarningDeltas.append(onEarningDatePlusTheDaysForwardDF)

        # keep a running list of earnings closing price
        priceEarnDay.append(ePSPrice.close.at[theEarningDate])
        # keep a running list of "day after eanrings" price
        afterEarnDate = dateUtils.ensureItsaWeekDay(theEarningDate + datetime.timedelta(days=2))

        # work with IV
        # - day of / day after earnings
        # - keep the delta between the day of and the day after IV
        try:
            iv_DayAfterEarnings.append(eImpVol.close.at[afterEarnDate])
            iv_DayOfEarnings.append(eImpVol.close.at[theEarningDate])
            iv_Dif.append(eImpVol.close.at[afterEarnDate] - eImpVol.close.at[theEarningDate])
        except KeyError:
            print('     ', KeyError, 'In getMinMaxPricePercent // afterEarnDate is a holiday: ', afterEarnDate) #todo write a routine to handle holidays
            # use onEarningDate instead of after/on EarningSDate
            iv_DayAfterEarnings.append(eImpVol.close.at[theEarningDate])
            iv_DayOfEarnings.append(eImpVol.close.at[theEarningDate])
            iv_Dif.append(eImpVol.close.at[theEarningDate] - eImpVol.close.at[theEarningDate])
            continue


    try:
        yahooEarningsDF['iv_DayOf'] = iv_DayOfEarnings
        yahooEarningsDF['iv_DayAfter'] = iv_DayAfterEarnings
        yahooEarningsDF['iv_Dif'] = iv_Dif
    except ValueError:
        print('     ', ValueError, 'In getMinMaxPricePercent')
        yahooEarningsDF['iv_DayOf'] = 0
        yahooEarningsDF['iv_DayAfter'] = 0
        yahooEarningsDF['iv_Dif'] = 0

    # keep the list of earnings closing price
    priceEarnDay = getEqualLenList(priceEarnDay, yahooEarningsDF)
    yahooEarningsDF['EarnDay$Close'] = priceEarnDay
    # keep list of earnings date deltas $ and % in this list
    yahooEarningsDF = addMinMax(listOfEarningDeltas, yahooEarningsDF)

    return yahooEarningsDF

def getEqualLenList(createdList, primaryList, aType=0):
    """
    We are going to add createdList to DF primaryList,
    This functions makes sure these are the same size
    Parameters
    ----------
    createdList : newly created list
    primaryList : DF to which we add createdList

    Returns right sized createdList
    -------

    """
    #todo can pass in variable to allow for differet types of updates / here using 0
    if len(createdList) != len(primaryList):
        createdList.extend([aType for i in range(len(primaryList) - len(createdList) )])

    return createdList

def addMinMax(listOfEarningDeltas, yahooEarningsDF):

    priceMaxDelta = []
    priceMaxPercentDelta = []
    priceMinDelta = []
    priceMinPercentDelta = []
    priceDeltaOneDay = []
    pricePercentDeltaOneDay = []
    priceStdWeek = []
    priceMeanWeek = []

    # Count to keep track of the number of earnings in Yahoo Earnings / yahooEarningsDF
    count = 0
    for earnDateDF in listOfEarningDeltas:
        # Get earning date
        anEarningDate = yahooEarningsDF['Earnings_Date'][count].date()

        # Get Earning date +1
        # if Friday / goto Monday
        if anEarningDate.weekday() == 4:
            onEarningDatePlus1 = anEarningDate + datetime.timedelta(days=3)
        else:
            onEarningDatePlus1 = anEarningDate + datetime.timedelta(days=1)

        # Get Max/Min % / $
        priceMaxDelta.append(earnDateDF['$Deltas'].max())
        priceMaxPercentDelta.append(earnDateDF['%Deltas'].max())
        priceMinDelta.append(earnDateDF['$Deltas'].min())
        priceMinPercentDelta.append(earnDateDF['%Deltas'].min())
        priceStdWeek.append(round(earnDateDF['close'].std(), 2))
        priceMeanWeek.append(round(earnDateDF['close'].mean(), 2))

        # Get earning day + 1 info
        try:
            priceDeltaOneDay.append(earnDateDF.loc[onEarningDatePlus1, '$Deltas'])
            pricePercentDeltaOneDay.append(earnDateDF.loc[onEarningDatePlus1, '%Deltas'])
        except KeyError:
            print('     ', KeyError, '       In addMinMax // afterEarnDate is a holiday: ',onEarningDatePlus1,  KeyError) #todo write a routine to handle holidays
            priceDeltaOneDay.append(0) #earnDateDF.loc[anEarningDate, '$Deltas'])
            pricePercentDeltaOneDay.append(0) #earnDateDF.loc[anEarningDate, '%Deltas'])
            continue
        # Count for number of earnings in Yahoo Earnings / yahooEarningsDF
        count = count + 1

    # add info to yahooEarningsDF dataframe make sure yahooEarningsDF and new list are the same length
    yahooEarningsDF['day1After%Delta'] = getEqualLenList(pricePercentDeltaOneDay, yahooEarningsDF)
    yahooEarningsDF['day1After$Delta'] = getEqualLenList(priceDeltaOneDay, yahooEarningsDF)
    yahooEarningsDF['CloseMean$'] = getEqualLenList(priceMeanWeek, yahooEarningsDF)
    yahooEarningsDF['CloseStanDev$'] = getEqualLenList(priceStdWeek, yahooEarningsDF)
    yahooEarningsDF['Max$Delta'] = getEqualLenList(priceMaxDelta, yahooEarningsDF)
    yahooEarningsDF['Max%Delta'] = getEqualLenList(priceMaxPercentDelta, yahooEarningsDF)
    yahooEarningsDF['Min$Delta'] = getEqualLenList(priceMinDelta, yahooEarningsDF)
    yahooEarningsDF['Min%Delta'] = getEqualLenList(priceMinPercentDelta, yahooEarningsDF)


    return yahooEarningsDF


def getHistoricIVnPrice(ib, contract, yahooEarningsDF,  daysPassEarnings = 60, durationStrDays = '90 D', setBarSizeSetting = '1 day'):
    """
    Get Historic IV and Price data ----
    add daysAroundEarnings Days forward - this will be used to count back and plot time
    durationString,The amount of time (or Valid Duration String units) to go back from the request's given end date and time.

    Historical data is obtained from the the TWS via the IBApi.EClient.reqHistoricalData function. Every request needs:
        tickerId:       A unique identifier which will serve to identify the incoming data.
        contract:       The IBApi.Contract you are interested in.
        endDateTime:    The request's end date and time (the empty string indicates current present moment).
        durationString: The amount of time (or Valid Duration String units) to go back from the request's given end date and time.
        barSizeSetting: The data's granularity or Valid Bar Sizes
        whatToShow:     The type of data to retrieve. See Historical Data Types
                           TRADES, HISTORICAL_VOLATILITY, OPTION_IMPLIED_VOLATILITY,....FEE_RATE
        useRTH:         Whether (1) or not (0) to retrieve data generated only within Regular Trading Hours (RTH)
        formatDate:     The format in which the incoming bars' date should be presented. Note that for day bars: only yyyyMMdd format is available.
        keepUpToDate:   Whether a subscription is made to return updates of unfinished real time bars as they are available (True),
                        or all data is returned on a one-time basis (False).
                        Available starting with API v973.03+ and TWS v965+. If True: and endDateTime cannot be specified.

    Parameters
    ----------
    ib : ib instance
    yahooEarningsDF: a pandas DF of scraped companies and earnings data

    daysPassEarnings: 60 / add X(daysPassEarnings) Days forward past earnings
                           this will be used to count back from endDateTime
    durationStrDays; '90 D' / How far back from daysPassEarnings
    setBarSizeSetting: '1 day' / Bar size

    Returns
    -------
    # time series panda dataframes from IB
    earningsPastStock
    earningsPastImpVol

        """
    # create time series panda dataframes from IB
    earningsPastStock = []
    earningsPastImpVol = []

    # Get Historical price (earningsPastStock) and Implied Volatility (earningsPastImpVol) Data
    for earnData in range(0, len(yahooEarningsDF)):
            earningsPastStock.append(util.df(ib.reqHistoricalData(contract, endDateTime=yahooEarningsDF['Earnings_Date'][earnData]
                                                                  +datetime.timedelta(days=daysPassEarnings),
                                                                  durationStr=durationStrDays,barSizeSetting=setBarSizeSetting,
                                                                  whatToShow='TRADES', useRTH=True)))
            earningsPastImpVol.append(util.df(ib.reqHistoricalData(contract, endDateTime=yahooEarningsDF['Earnings_Date'][earnData]
                                                                   +datetime.timedelta(days=daysPassEarnings),
                                                                   durationStr=durationStrDays,barSizeSetting=setBarSizeSetting,
                                                                   whatToShow='OPTION_IMPLIED_VOLATILITY', useRTH=True)))

    return earningsPastStock, earningsPastImpVol

#===============================================================
def getEstimatedPriceMovefor1Day(ib, qualityContracts, chain):
    """
    Returns the one day expected price move at 86%

        Parameters
        ----------
        ib : ib_insyc instance
        qualityContracts : qualifed quality contracts
        chain : Option thain

        Returns
        -------
        expected 1 day price move
        """

    expectedMovePercent = (getOptionStraddlePrice(ib, qualityContracts, chain) * .84)

    return expectedMovePercent


def getEstimatedPercentMovefor1Day(ib, qualityContracts, chain):
    """
    Returns the one day expected % move at 86%

        Parameters
        ----------
        ib : ib_insyc instance
        qualityContracts : qualifed quality contracts
        chain : Option thain

        Returns
        -------
        expected 1 day % move
        """

    expectedMovePercent = (getOptionStraddlePrice(ib, qualityContracts, chain) * .84)

    return expectedMovePercent / getSnapshotTickersMarketPrice(ib, qualityContracts)


def getExpectedPriceRangeTillNextExpiryDays(underlyingPrice, impVol):
    """
    Get the expected price range of an underlying at the next
    monthly expiry.

    Parameters
    ----------
    underlyingPrice : price of the underlying stock
    impVol : implied volatility of the underlying

    Returns
    -------

    """

    priceTimesImpvol = underlyingPrice * impVol

    sqrtOfDaysDiv = math.sqrt(dateUtils.daysToExpiry(dateUtils.getNextExpiryDate()) / 365)

    return round((priceTimesImpvol * sqrtOfDaysDiv),2)


def getSnapshotTickersMarketPrice(ib, qualityContracts):
    """
    Get the current Market Price at close

    Parameters
    ----------
    ib : ib_insyc instance
    qualityContracts : qualifed quality contracts

    Returns
    -------
    stock market price
    """
    [ticker] = ib.reqTickers(qualityContracts)

    return ticker.marketPrice()  # ToDo can we get ticker.last()


def getOptionStraddlePrice(ib, qualityContracts, chain):
    """
    Get ATM (at the money) Option Straddle Price.

        :Keyword arguments
        ib                  -- ib_insync instance
        qualityContracts    -- a qualified Stock Symbol
        chain               -- chain of Options / list of expires and strike prices.

        :returns
        Straddle Price: which is to buy a call option and a put option on the same underlying stock
                        with the same expiration date and strike price.
        """

    [ticker] = ib.reqTickers(qualityContracts)

    # Get to the next round at 5  don't want to deal with missing data at the increments of 1 and 2
    # eg:  we want 125 or 130
    #      don't get 126,127,128, 129 / these price option are not always available
    strike5 = (5 * round(ticker.marketPrice() / 5))
    # ToDo should be a better way to get strike5 then loop
    # get strikes at strike5
    strikes = [strike for strike in chain.strikes
               if strike5 == strike]

    expiration = dateUtils.getNextExpiryDate()  # = sorted(exp for exp in chain.expirations)
    rights = ['P', 'C']

    contracts = [Option(qualityContracts.symbol, expiration, strike5, right, 'SMART')
                 for right in rights]
    print('Straddle ', contracts)
    ib.qualifyContracts(*contracts)

    contractsForExpiry = [aContract for aContract in contracts
                          if aContract.lastTradeDateOrContractMonth == dateUtils.getNextExpiryDate()]

    tickers = ib.reqTickers(*contractsForExpiry)

    # Todo - need to update to return close price when market closed else return last
    return tickers[0].close + tickers[1].close

