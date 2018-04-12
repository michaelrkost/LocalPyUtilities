from ib_insync import OptionChain
from localUtilities import dateUtils

def getStrikes(optionChain, marketPrice, strikePriceRange = 20, strikePriceMultiple = 5 ):
    """Get range of Option Strike prices.

    Keyword arguments:
    optionChain         -- type is ib_insync.objects.OptionChain
    marketPrice         -- Market Price of  the Underlying/Stock
    strikePriceRange    -- Strike prices within +- strikePriceRange dollar value of 
                           the current marketPrice (default 20 )
    strikePriceMultiple -- Strike prices that are a multitude (eg $5 goes to 20, 25) of 
                       strikePriceMultiple dollar value (default 5 )
    """
    strikes = [strike for strike in optionChain.strikes if
        strike % strikePriceMultiple == 0 and
        marketPrice - strikePriceRange < strike < marketPrice + strikePriceRange]

    return strikes

def getSPXmonthlyStrikesNearDate(optionChain, marketPrice, forDate, strikePriceRange = 20, strikePriceMultiple = 5 ):
    """Get one SPX Option Strike prices.

    Keyword arguments:
    optionChain         -- type is ib_insync.objects.OptionChain
    marketPrice         -- Market Price of the SPX Underlying
    fordate             -- the near date of desire strike
    strikePriceRange    -- Strike prices within +- strikePriceRange dollar value of 
                           the current marketPrice (default 20 )
    strikePriceMultiple -- Strike prices that are a multitude (eg $5 goes to 20, 25) of 
                       strikePriceMultiple dollar value (default 5 )
    """
    #forDate = dateUtils.nextFriday(forDate)
    forDate = dateUtils.nextThursdayOrgFormat(forDate)
    nextValidThursday = [expiry for expiry in optionChain.expirations 
                    if expiry == forDate]
    return nextValidThursday

if __name__ == "__main__":
    getStrikes()

