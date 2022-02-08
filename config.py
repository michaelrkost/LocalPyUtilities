
daysAroundEarnings = 10
pushDateOutNDays = None

# Max number of Earnings Quarters to process 0-9
maxQtrs = 10

theBaseCompaniesDirectory = '/home/michael/jupyter/earningDateData/Companies/'
csvSuffix = '.csv'

# Find the next month Option - after - at least 10 days out -  at the current price
# Get the Put/Call IV - use this as the Stock IV
# if we dont want to push out the date use pushIVout == 0
# ******* coordinate with getMarketData.getExpectedRange()
# Usages:
#   def getMarketData.getIV(aYFTicker, currentPrice, pushIVout = config.pushIVDateOutNDays):
#   def getMarketData.getIV_CallIV(aYFTicker, currentPrice, pushIVout = config.pushIVDateOutNDays):
pushIVDateOutNDays = 10

# Get the next monthly expiration date out offsetDays Days
# def dateUtils.getDays2ExpirationAndExpiry(offsetDays = config.offsetExpiryDays):
# originally set to "10"
offsetExpiryDays = 10

