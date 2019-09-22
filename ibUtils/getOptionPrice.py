import os
import sys
import datetime

from py_lets_be_rational.exceptions import BelowIntrinsicException

sys.path.append('/home/michael/jupyter/local-packages')

import math
from ib_insync import *

# Get my Utilities (localUtilities)
from localUtilities import dateUtils
from localUtilities.ibUtils import getOptionStrategyPrice

from datetime import datetime
from dateutil.relativedelta import relativedelta

import numpy as np
import pandas as pd
from py_vollib.black.implied_volatility import *
from py_vollib.black.greeks.analytical import *

# **************************************************************************

def getStockOptionPrice(ib, aStockSymbol, strikesDF, aRight, closeCLPrice, exchange = 'SMART'):
        """
        getStockOptionPrices

        :Keyword arguments
        ib                  -- ib_insync instance
        aStockSymbol        -- the Stock Symbol
        exchange            -- the exchange default is 'SMART'
        strikesDF           -- DF with expiry and Strike prices

        :returns
        """

        # Request Frozen Market Data Type // 2=Frozen
        ib.reqMarketDataType(2)

        # needed to add "primaryExchange='ISLAND'" to avoid contract ambiguity
        qualityContracts = Stock(aStockSymbol, 'SMART', 'USD',  primaryExchange='ISLAND')
        ib.qualifyContracts(qualityContracts)
        qualityContracts

        # chains = ib.reqSecDefOptParams(qualityContracts.symbol, '', qualityContracts.secType, qualityContracts.conId)
        # chain = next(c for c in chains if c.tradingClass == aStockSymbol and c.exchange == exchange)
        # [ticker] = ib.reqTickers(qualityContracts)

        # just on expiry date in the MultiIndex on strikesDF
        anExpiry = strikesDF.index.unique(level='Expiry')
        anExpiry = anExpiry[0]

        # Get the Strikes
        strikesInDF = strikesDF.index.unique(level='Strikes')

        # get contracts for all the Strikes in strikeDF for the anExpiry
        contracts = [Option(aStockSymbol, anExpiry, strike, aRight, 'SMART')
                     for strike in strikesInDF]
        # Qualify all the contracts
        ib.qualifyContracts(*contracts)

        closePrice = []
        lastPrice = []
        impVolList = []

        for aContract in contracts:
            mktData = ib.reqMktData(aContract, "100, 101, 106", False, False, [])
            ib.sleep(2)
            ticker = ib.ticker(aContract)
            closePrice.append(ticker.close)
            lastPrice.append(ticker.last)

            # IV Parameters:
            # discounted_option_price (float) – discounted Black price of a futures option
            # F (float) – underlying futures price
            # K (float) – strike price
            # r (float) – the riskgetStockOptionPrice-free interest rate
            # t (float) – time to expiration in years
            # flag (str) – ‘p’ or ‘c’ for put or call
            F = float(closeCLPrice[1:]) #change from str to float
            K = aContract.strike
            sigma = 0 # not using here as this is the IV
            flag =  (lambda x: 'c' if aRight == 'C' else 'p')(aRight) # need in lower case
            t = relativedelta(dateUtils.getDate(anExpiry), datetime.now()).days/365 # get time in years
            r = .02  #todo - update this calculation for treasury bonds

            # if calculate IV if there is an option price / ticker.close
            if math.isnan(F):
                iv = np.nan
            else:
                try:
                    # print(ticker.close, F, K, r, t, flag)
                    iv = implied_volatility(ticker.close, F, K, r, t, flag)
                except BelowIntrinsicException:
                    print('     ', BelowIntrinsicException, '       getStockOptionPrice')
                    iv = np.nan
                    continue
                except ValueError:
                    print('Stock: ', aStockSymbol)
                    print('     ', BelowIntrinsicException, '       getStockOptionPrice')
                    iv = np.nan
                    continue

            impVolList.append(iv)

            ib.cancelMktData(mktData.contract)

        strikesDF['last'] = lastPrice
        strikesDF['close'] = closePrice
        strikesDF['impVolList'] = getOptionStrategyPrice.getEqualLenList(impVolList, strikesDF, np.nan)

        # print('aStockSymbol: ', aStockSymbol, '\n', strikesDF)
        return strikesDF


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
    # print('expiration: ', expiration)

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

