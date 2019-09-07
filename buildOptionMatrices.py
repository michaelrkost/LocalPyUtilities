from localUtilities.ibQT import ibPyUtils

from ib_insync import *


def qualify_option_chain(ib, aContract, rights, exchange,
                               strikePriceRange=10, strikePriceMultiple=5):
    print("<<in qualify_index_option_chain >>  ")
    # Fully qualify the given contracts in-place.
    # This will fill in the missing fields in the contract, especially the conId.
    # list of options
    listOptionChain = ib.reqSecDefOptParams(aContract.symbol, '', aContract.secType, aContract.conId)
    print(listOptionChain)
    # filter out for SMART ????
    listSmartOptionChain = next(c for c in listOptionChain
                                  if c.exchange == 'SMART')
    # print("listSmartOptionChain: \n", listSmartOptionChain)

    [aTicker] = ib.reqTickers(aContract)
    print('++++++++++++++++++++++++++++++++')
    # Get the Strikes as defined by current price, strikePriceRange and strikePriceMultiple
    strikes = ibPyUtils.getStrikes(listSmartOptionChain, aTicker.close,
                                   strikePriceRange, strikePriceMultiple)
    print('aTicker.close:  ', aTicker.close)
    print('strikes: ', strikes)

    # Get the SPX expirations set
    # to narrow to Friday or Thursdays use isThursday/isFriday
    # if dateUtils.isFriday(exp))
    sortedExpirations = sorted(exp for exp in listSmartOptionChain.expirations)

    print("sortedExpirations: ", sortedExpirations)

    # Build requested options based on expriy and price range
    contracts = [Option(aContract.symbol, expiration, strike, right, exchange='SMART')
            for right in rights for expiration in sortedExpirations for strike in strikes]
    # Qualify the options
    ib.qualifyContracts(*contracts)
    print("Contracts: \n", contracts)

    toIntStrikes = strikes
    toIntStrikes = [int(i) for i in toIntStrikes]
    print("toIntStrikes:  ", toIntStrikes)
    return contracts


def qualify_option_chain_close(ib, param, param1, param2, param3):
    pass


if __name__ == "__main__":
    ib = IB()
    ib.connect('127.0.0.1', 4002, clientId=5)
    a_underlying = Stock('NFLX', 'ISLAND', currency='USD', primaryExchange='ISLAND')
    the_underlying = ib.qualifyContracts(a_underlying)
    z=qualify_option_chain_close(ib, the_underlying.pop(), 'C', 20, 5)
    print("the cat's pajamas - meow!!", z)