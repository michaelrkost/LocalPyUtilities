
import numpy as np
import pandas as pd
import datetime
import random
import itertools

from ib_insync import *
import sys



def qualify_index_option_chain(ib, index):
    print("in qualify_index_option_chain >>  ")
    # Fully qualify the given contracts in-place.
    # This will fill in the missing fields in the contract, especially the conId.
    # list of options
    listOptionChainSPX = ib.reqSecDefOptParams(index.symbol, '', index.secType, index.conId)

    # filter out for SMART and do not include SPXW
    # this should give us all the Thursday Expiries
    listSmartOptionChainSPX = next(c for c in listOptionChainSPX if c.exchange == 'SMART' and c.tradingClass == 'SPX')
    print(listSmartOptionChainSPX)




if __name__ == "__main__":
    ib = IB()
    ib.connect('127.0.0.1', 4002, clientId=4)
    a_underlying = Index('SPX', 'CBOE')
    the_underlying = ib.qualifyContracts(a_underlying)
    qualify_index_option_chain(ib, the_underlying.pop())
    print("the cat's pajamas")