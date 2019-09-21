"""
module: setup

This file contains functions to support the common setup of ib_insync functions:

    * getQualityContracts

"""
#Todo - error management / ib.errorEvent += onError
import os
import sys
sys.path.append('/home/michael/jupyter/local-packages')

from ib_insync import *
from localUtilities.ibUtils import getOptionStrategyPrice as strat

import numpy as np
import pandas as pd
import datetime
import random
import itertools


def getQualityContracts(ib, aSymbol, anExchange = 'SMART', theCurrency = 'USD' ):
    """
    Get Qualify Contracts and return the quality contracts

    Returns
    -------
    qualityContracts
    contract
    """

    contract = Stock(aSymbol, anExchange, theCurrency)
    qualityContracts = contract
    ib.qualifyContracts(qualityContracts)

    return qualityContracts, contract

def addFrozenMarketData(ib, earningsDF):

    # Request Frozen Market Data Type // 2=Frozen
    ib.reqMarketDataType(2)

    anExchange = 'SMART'
    theCurrency = 'USD'

    # add info
    earningsDF['close'] = np.nan
    earningsDF['last'] = np.nan

    for row in earningsDF.itertuples():
        print(row.Symbol, end=", ")

        qualityContracts, contract = getQualityContracts(ib, row.Symbol, anExchange, theCurrency)

        #request realtime market data / see     ib.reqMarketDataType(2)
        mktData = ib.reqMktData(contract, "", False, False, [])
        ib.sleep(2)

        aticker = ib.ticker(contract)

        # add close / last
        earningsDF.at[row.Index, 'last'] = aticker.close
        earningsDF.at[row.Index, 'close'] = aticker.last

        # sleep to ensure we get the data
        ib.sleep(3)
        # cancel Market data to not to hit the Data limit
        ib.cancelMktData(mktData.contract)

    return earningsDF


def addMarketData(ib, earningsDF):
    """
    Add Market Data / 'histVolatility', 'impliedVolatility', 'avOptionVolume','Expected_Range' /
    to companies in passed DF

    Parameters
    ----------
    ib : instance of ib_insyc
    earningsDF : DF of 'Symbol', 'EarningmktDatas_Date', 'Company', 'Earnings Call Time'

    Returns
    -------
    DF w/ Market Data for companies w/ greater than some number, say 5000,
    in Option Volume - worthwhile causes
    """

    anExchange = 'SMART'
    theCurrency = 'USD'

    # get close/last from frozen data
    addFrozenMarketData(ib, earningsDF)

    # Request Live Market Data Type // 2=Frozen
    # get generic tick types
    ib.reqMarketDataType(2)

    earningsDF['histVolatility'] = np.nan
    earningsDF['impliedVolatility'] = np.nan
    earningsDF['avOptionVolume'] = np.nan
    earningsDF['Expected_Range'] = np.nan

    lenDF = len(earningsDF)

    for row in earningsDF.itertuples():
        print(row.Symbol, ' -  ', lenDF,  end=", ")

        qualityContracts, contract = getQualityContracts(ib, row.Symbol, anExchange, theCurrency)

        mktData = ib.reqMktData(contract, "100,101,104,105, 106", False, False, [])

        ib.sleep(3)

        # ToDo is this aticker needed????
        aticker = ib.ticker(contract)


        earningsDF.at[row.Index, 'histVolatility'] = mktData.histVolatility
        earningsDF.at[row.Index, 'impliedVolatility'] = mktData.impliedVolatility
        earningsDF.at[row.Index, 'avOptionVolume'] = mktData.avOptionVolume
        earningsDF.at[row.Index, 'Expected_Range'] = strat.getExpectedPriceRangeTillNextExpiryDays( earningsDF.at[row.Index, 'last'] ,
                                                                                                   mktData.impliedVolatility)

        ib.sleep(2)
        ib.cancelMktData(mktData.contract)

    #remove companies w/ less that 5000 in Option Volume
    earningsDFOptionVolGood = earningsDF[(earningsDF['avOptionVolume'] >= 5000)]

    return earningsDFOptionVolGood.reset_index(drop=True), earningsDF
