from ib_insync import *

from localUtilities import dateUtils, configIB, logger

import datetime
from datetime import date,timedelta

from decimal import Decimal

def getStrikes(optionChain, marketPrice, strikePriceRange = 20, strikePriceMultiple = 5 ):
    """Get range of Option Strike prices as integers.

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

    # to Integers
    strikes = [int(i) for i in strikes]

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

def security_type(aTableWidget, the_underlying, the_exchange):
    """ from the GUI radio buttons determine if this a Stock/Index/Option and get the underlying.
    Create Contract.
    :param the_underlying: Stock/Index
    :param the_exchange: CBOE etc
    :return:
    """
    if aTableWidget.radioButton_Index.isChecked():
        a_underlying = Index(the_underlying, the_exchange, 'USD')
        aTableWidget.securityType = "IND"
    elif aTableWidget.radioButton_Stock.isChecked():
        a_underlying = Stock(the_underlying, the_exchange, 'USD')
        aTableWidget.securityType = "STK"
    else: #todo Add Option type
        logger.logger.ERROR('<<<< in bullSpreadViewSmall.get_underlying_info(self)>>>>> Option Radio not !completed!')
    return a_underlying


def marketDataType(aTableWidgetRadioButtonFrozen):
    if aTableWidgetRadioButtonFrozen.isChecked():
        return configIB.MARKET_DATA_TYPE_FROZEN
    else:
        return configIB.MARKET_DATA_TYPE_LIVE

def doExpiry(comboBox_Expiry, a_translate):
    """Create a list of 18 Months of Option Fridays
    for the Expiry DropDown: comboBox_Expiry

    Keyword arguments:
    none
    """
    orderNum = 0
    expiry_list = dateUtils.getMonthExpiries()
    for anExpiry in expiry_list:
        comboBox_Expiry.addItem("")
        comboBox_Expiry.setItemText(orderNum, a_translate("MainWindow", anExpiry))
        orderNum += 1


def right(aTableWidget):
    if aTableWidget.radioButton_Call.isChecked():
        return configIB.CALL_RIGHT
    else:
        return configIB.PUT_RIGHT

def put_right():
    return configIB.PUT_RIGHT


def call_right():
    return configIB.CALL_RIGHT

def reqMarketData_Setup(aTableWidget):

    # set the type of Price Data to receive
    #   - Frozen market data is the last data recorded at market close.
    #   - Last market data is the last data set, which may be empty after hours
    # To receive the last know bid/ask price before the market close, switch to market data type 2
    # from the API before requesting market data. API frozen data requires TWS/IBG v.962 or higher
    # and the same market data subscriptions necessary for real time streaming data.

    #todo - this needs to use live or frozen - it is only set up for frozen
    aTableWidget.ib.reqMarketDataType(marketDataType(aTableWidget.radioButton_MktDataType_Frozen))
    logger.logger.info("frozenVS:  %s", aTableWidget.radioButton_MktDataType_Frozen.isChecked())

def roundToNearest10(num):
    return round(num,-1)

def roundToNearest5(num):
    return round(num*2,-1)/2

def getNearestExpiryFromToday():
    '''
    Calculate the next Expiry from today.
    If the current month Expiry is less than or equal 15 days out return Next Month
    else return this months Expiry
    :return: Expiry Date in string formated: '20180406'
    '''
    todayDate = date.today()
    nextExpiry = dateUtils.third_friday(todayDate.year, todayDate.month)

    # get day multiple
    oneDayTimedelta = datetime.timedelta(days=1)

    #get days till Expiry
    daysTillExpiry = nextExpiry - (todayDate + oneDayTimedelta)

    useThisExpriy = nextExpiry

    # if the current month Expiry is less than or equal 15 days out -> return Next Month
    if daysTillExpiry <= (oneDayTimedelta * 15):
        useThisExpriy = dateUtils.third_friday(todayDate.year, todayDate.month + 1)

    theExpiryStr = dateUtils.getDateString(dateUtils.third_friday(useThisExpriy.year, useThisExpriy.month))

    return theExpiryStr

if __name__ == "__main__":
    getStrikes()
