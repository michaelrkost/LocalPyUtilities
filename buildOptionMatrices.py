from localUtilities import ibPyUtils, dateUtils

from ib_insync import *
import sys



def qualify_index_option_chain(ib, index):
    print("<<in qualify_index_option_chain >>  ")
    # Fully qualify the given contracts in-place.
    # This will fill in the missing fields in the contract, especially the conId.
    # list of options
    listOptionChainSPX = ib.reqSecDefOptParams(index.symbol, '', index.secType, index.conId)
    print(listOptionChainSPX)
    # filter out for SMART
    # this should give us all the Thursday Expiries
    listSmartOptionChainSPX = next(c for c in listOptionChainSPX
                                   if c.exchange == 'SMART')
    print(listSmartOptionChainSPX)

    [tickerSPX] = ib.reqTickers(index)

    # Get the Strikes as defined by current price, strikePriceRange and strikePriceMultiple
    strikesSPX = ibPyUtils.getStrikes(listSmartOptionChainSPX, tickerSPX.last, 10, 5)
    print(tickerSPX.last)
    print(strikesSPX)

    # Get the SPX expirations set
    # as picked from aMonth iWidget
    sortedExpirations = sorted(exp for exp in listSmartOptionChainSPX.expirations
                            if dateUtils.isThursday(exp))
    print(sortedExpirations)





if __name__ == "__main__":
    ib = IB()
    ib.connect('127.0.0.1', 4002, clientId=5)
    a_underlying = Stock('FB', 'SMART',  primaryExchange='NASDAQ')
    the_underlying = ib.qualifyContracts(a_underlying)
    qualify_index_option_chain(ib, the_underlying.pop())
    print("the cat's pajamas - meow!!")