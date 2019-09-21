import os
import sys
import datetime
sys.path.append('/home/michael/jupyter/local-packages')

from ib_insync import *

# Get my Utilities (localUtilities)
from localUtilities import dateUtils

# ****************************- mrk- ***************************************
# ******************** 8/11/19 - not used **********************************
# **************************************************************************

def getStockOptionPrice(ib, aStockSymbol, exchange = 'SMART'):
        """
        getStockOptionPrices

        :Keyword arguments
        ib                  -- ib_insync instance
        aStockSymbol        -- the Stock Symbol
        exchange            -- the exchange default is 'SMART'
        optionChain         -- type is ib_insync.objects.OptionChain
        marketPrice         -- Market Price of  the Underlying/Stock
        strikePriceRange    -- Strike prices within +- strikePriceRange dollar value of
                               the current marketPrice (default 20 )
        strikePriceMultiple -- Strike prices that are a multitude (eg $5 goes to 20, 25) of
                               strikePriceMultiple dollar value (default 5 )
        :returns
        Call price, Put Price
        """

        qualityContracts = Stock(aStockSymbol, 'SMART')
        ib.qualifyContracts(qualityContracts)
        qualityContracts

        chains = ib.reqSecDefOptParams(qualityContracts.symbol, '', qualityContracts.secType, qualityContracts.conId)
        chain = next(c for c in chains if c.tradingClass == aStockSymbol and c.exchange == exchange)

        [ticker] = ib.reqTickers(qualityContracts)

        # Get to the next 5 dont want to deal with missing data at the 1 and 2 level
        strike5 = (5 * round(ticker.marketPrice() / 5))
        # get strikes at strike5
        strikes = [strike for strike in chain.strikes
                   if strike5 == strike]

        expiration = dateUtils.getNextExpiryDate()  # = sorted(exp for exp in chain.expirations)
        rights = ['P', 'C']

        contracts = [Option(aStockSymbol, expiration, strike5, right, 'SMART')
                     for right in rights]

        ib.qualifyContracts(*contracts)

        contractsForExpiry = [aContract for aContract in contracts
                              if aContract.lastTradeDateOrContractMonth == dateUtils.getNextExpiryDate()]


        tickers = ib.reqTickers(*contractsForExpiry)

        if tickers[0].contract.right == 'C':
                tickerPriceCall = tickers[0].last
                tickerPricePut = tickers[1].last
        else:
                tickerPriceCall = tickers[1].last
                tickerPricePut = tickers[0].last

        return tickerPriceCall, tickerPricePut


def getCloseStrikePrice(ib, qualityContracts, aStockSymbol, price, startDate, right, exchange = 'SMART' ):
    """
    Get closes prices that is five points above, five points below

        :Keyword arguments
        ib                  -- ib_insync instance
        qualityContracts    -- a qualified Stock Symbol
        aStockSymbol        -- the stock
        price               -- price to find Option
        :returns
        Strike Prices
        """
    # print(qualityContracts.symbol)
    # [ticker] = ib.reqTickers(qualityContracts)

    chains = ib.reqSecDefOptParams(qualityContracts.symbol, '', qualityContracts.secType, qualityContracts.conId)
    chain = next(c for c in chains if c.tradingClass == aStockSymbol and c.exchange == exchange)

    # if price >= then $40 Get to the next round at +/- 5
    # if price < $40 get to round at the +/-2
    if price >= 40 :
        strikePlus = (5 * round(price / 5))  + 5
        strikeMinus = (5 * round(price / 5)) - 5
        # print('strikePlus', strikePlus)
        # print('strikeMinus', strikeMinus)
    else:
        strikePlus = (2 * round(price / 2)) + 3
        strikeMinus = (2 * round(price / 2)) - 3
        # print('strikePlus', strikePlus)
        # print('strikeMinus', strikeMinus)

    # get strikes at strikePlus
    strikes = [strike for strike in chain.strikes
               if strike >= strikeMinus and strike <= strikePlus ]
    # print('strikes: ', strikes)

    # get experation date in proper format
    dateFromISOFromat = dateUtils.getDateFromISO8601(startDate)
    nextFridayDateFormat = dateUtils.nextFriday(dateFromISOFromat)
    expiration = dateUtils.nextFridayOrgFormat(nextFridayDateFormat)  # = sorted(exp for exp in chain.expirations)
    print('expiration: ', expiration)

    contracts = [Option(qualityContracts.symbol, expiration, strike, right, exchange)
                 for strike in strikes]
    ib.qualifyContracts(*contracts)
    # print('contracts:  ', contracts, '\n\n\n')

    # Todo: should this be ib.reqSecDefOptParams instead of ib.reqContractDetails???
    optionContractsDetails = [ib.reqContractDetails(cd)
                                for cd in contracts]

    return strikes, contracts

    # # # Todo - need to update to return close price when market closed else return last
    # # return tickers[0].close + tickers[1].close

def buildEarnOptionPriceDF(strikes, right):

    rights = [right]

    headerPrice = ['openInterest', 'impliedVol', 'last', 'close']
    indexRangeList = list(itertools.product(rights, strikes))

    multiIndexRange = pd.MultiIndex.from_tuples(indexRangeList,
                                                names=['Right', 'Strikes'])

    earnOptionPricesDF = pd.DataFrame(0.0, index=multiIndexRange,
                                        columns=headerPrice)

    return earnOptionPricesDF

def buildEarnDF(ib, qualityContracts, aStockSymbol, maxPriceMoveCl, minPriceMoveCl, startday):


    # Request Frozen Market Data Type // 2=Frozen
    ib.reqMarketDataType(2)

    maxPriceLast = []
    maxPriceClose = []
    maxCallOpenInte = []
    maxLastGreeksImpliedVol = []
    maxModelGreeksImpliedVol = []
    maxModelGreeksOptPrice =[]
    minPriceLast = []
    minPriceClose = []
    minPutOpenInte = []
    minLastGreeksImpliedVol = []
    minModelGreeksImpliedVol = []
    minModelGreeksOptPrice =[]

    maxStrikesC, maxContractsC = getCloseStrikePrice(ib, qualityContracts, aStockSymbol, maxPriceMoveCl, startday, 'C')
    minStrikesP, minContractsP = getCloseStrikePrice(ib, qualityContracts, aStockSymbol, minPriceMoveCl, startday, 'P')

    print(maxStrikesC)
    for cd in maxContractsC:
        mktData = ib.reqMktData(cd, "100,101,104,106,291", False, False, [])
        ib.sleep(5)
        maxPriceLast.append(mktData.last)
        maxPriceClose.append(mktData.close)
        maxCallOpenInte.append(mktData.callOpenInterest)
        # try:
        #     maxLastGreeksImpliedVol.append(mktData.lastGreeks.impliedVol)
        #     maxModelGreeksImpliedVol.append(mktData.modelGreeks.impliedVol)
        #     maxModelGreeksOptPrice.append(mktData.modelGreeks.optPrice)
        # except AttributeError:
        #     maxLastGreeksImpliedVol.append(mktData.modelGreeks.impliedVol)
        #     maxModelGreeksImpliedVol.append(mktData.modelGreeks.impliedVol)
        #     maxModelGreeksOptPrice.append(mktData.modelGreeks.optPrice)
        ib.cancelMktData(mktData.contract)

    print(minStrikesP)
    for cd in minContractsP:
        mktData = ib.reqMktData(cd, "100,101,104,106", False, False, [])
        ib.sleep(3)
        print(mktData)
        minPriceLast.append(mktData.last)
        minPriceClose.append(mktData.close)
        minPutOpenInte.append(mktData.putOpenInterest)
        # try:
        #     minLastGreeksImpliedVol.append(mktData.lastGreeks.impliedVol)
        #     minModelGreeksImpliedVol.append(mktData.modelGreeks.impliedVol)
        #     minModelGreeksOptPrice.append(mktData.modelGreeks.optPrice)
        # except AttributeError:
        #     minLastGreeksImpliedVol.append(0)
        #     minModelGreeksImpliedVol.append(0)
        #     minModelGreeksOptPrice.append(0)
        ib.cancelMktData(mktData.contract)

    print('maxPriceLast', maxPriceLast)
    print('maxPriceClose' , maxPriceClose)
    print('maxCallOpenInte', maxCallOpenInte)
    # print('maxLastGreeksImpliedVol', maxLastGreeksImpliedVol)
    # print('maxModelGreeksImpliedVol', maxModelGreeksImpliedVol)
    # print('maxModelGreeksOptPrice', maxModelGreeksOptPrice)
    print('minPriceLast', minPriceLast)
    print('minPriceClose', minPriceClose)
    print('minPutOpenInte', minPutOpenInte)
    # print('minLastGreeksImpliedVol', minLastGreeksImpliedVol)
    # print('minModelGreeksImpliedVol', minModelGreeksImpliedVol)
    # print('minModelGreeksOptPrice', minModelGreeksOptPrice)

    minMDF =  buildEarnOptionPriceDF(minStrikesP, 'P')
    maxMDF =  buildEarnOptionPriceDF(maxStrikesC, 'C')

    maxMDF['maxPriceLast'] = maxPriceLast
    maxMDF['maxPriceClose'] = maxPriceClose
    maxMDF['maxCallOpenInte'] = maxCallOpenInte
    # maxMDF['maxLastGreeksImpliedVol'] = maxLastGreeksImpliedVol
    # maxMDF['maxModelGreeksImpliedVol'] = maxModelGreeksImpliedVol
    # maxMDF['maxModelGreeksOptPrice'] = maxModelGreeksOptPrice
    minMDF['minPriceLast'] = minPriceLast
    minMDF['minPriceClose'] = minPriceClose
    minMDF['minPutOpenInte'] = minPutOpenInte
    # minMDF['minLastGreeksImpliedVol'] = minLastGreeksImpliedVol
    # minMDF['minModelGreeksImpliedVol'] = minModelGreeksImpliedVol
    # minMDF['minModelGreeksOptPrice'] = minModelGreeksOptPrice


    frames = [maxMDF, minMDF]
    return  pd.concat(frames, sort=False)

def third_friday(aDate):
    """Return datetime.date for next monthly Friday option expiration given year and month

    Keyword arguments:
    aDate -- format '20190919

    """
    # The 15th is the lowest third day in the month

    print('aDate: ', aDate)
    if aDate.day > 15:
            # See if we need to push out to the next month for Friday Expiry
            if aDate.day > 24: third = aDate + datetime.timedelta(10)
            else: third = aDate + datetime.timedelta(20)
            third = datetime.date(third.year, third.month, 15)
    else:  third = datetime.date(aDate.year, aDate.month, 15)
    print('thirdvvv: ', third)
    # What day of the week is the 15th?
    w = third.weekday()
    # Friday is weekday 4
    if w != 4:
        # Replace just the day (of month)
        third = third.replace(day=(15 + (4 - w) % 7))

    return datetime.datetime.strftime(third, "%Y%m%d")




