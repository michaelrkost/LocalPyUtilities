"""
module: getOptionStrategyPrice

This file is intended to be imported as a module and contains the following
functions:

    * ensureItsaWeekDay(date) - checks if previous date is a weekend - if so return previous weekday
    * getDate('20180718') - return datetime.date
    * getDateFromISO8601('2019-08-19') - return datetime.date
    * getDateStringDashSeprtors(datetime)- from datetime return formatted date: 2018-07-18'
    * getDateString(date) - from datetime return formatted sting '20180718'
    * getDateFromMonthYear('Mon'YY') - from 'Mon'YY' return datetime.date - first day of Month
    * month3Format('20180718') - from '20180718' return format "Apr06'18"
    * getMonthExpiries() - get about 5 months of Friday expiry dates
    * getNextExpiryDate() - get the next Friday monthly expiry
    * getExpiries() - get about 18 months of Friday expiry dates
    * isThursday('20180406') - is date a Thursday
    * nextThursday(date) - get the next Thursday
    * nextThursdayExpiryFormat(datetime) -  next Thursday Options close in format: Apr06'18
    * nextThursdayOrgFormat(datetime) -  next Thursday in format: 20180718
    * third_Thursday(year, month) - Return datetime.date for monthly option Thursday
                                    Index expiration given year and month
    * isFriday('20180406') - See if date is a Friday
    * nextFriday(date) - get next Friday
    * nextFridayExpiryFormat(date) - Returns the next Friday date for Friday Options close in format: 20180718
    * third_friday(year, month) - Return datetime.date for monthly Friday option expiration given year and month
    * daysToExpiry('20180718') - Days between today and theExpiry
    * getTodayStr() - returns formatted 'Sun, Aug 11'
    * get45DaysOutStr - out 45 days - returns formatted 'Sun, Aug 11'
    * daysInYear - returns 365
    * monToDigits('aug') - from 3 letter name(case insensitive) return 2 digits
    * toExpiryStr(2019, 'dec', 8) - integers for day and year, Str 3 day Month - 'dec' - case insensitive
                                    return Option expiry date str format '20191208'


"""

#=============================================================
import datetime

#=============================================================

def ensureItsaWeekDay(aDate):
    """
    if day is weekend return Friday's date

    Parameters
    ----------
    aDate : the day in datetime

    Returns
    -------
    returnDate /  a weekday
    """

    if aDate.weekday() == 5:
        # print('back to: ', datetime.datetime.strftime((aDate - datetime.timedelta(days=1)), '%A'))
        returnDate = aDate - datetime.timedelta(days=1)
    elif aDate.weekday() == 6:
        # print('back to: ', datetime.datetime.strftime((aDate - datetime.timedelta(days=2)), '%A'))
        returnDate = aDate - datetime.timedelta(days=2)
    else:
        # print('Weekday is: ', datetime.datetime.strftime(aDate, '%A'))
        returnDate = aDate

    return returnDate

def getDateFromISO8601(date):
    """
    Get the datetime.date from string formatted as ISO 8601 '2018-07-18'

        Parameters
        ----------
        date         -- Date in ISO 8601 string formatted: '20180406'

        Returns
        -------
        datetime.date of parameter string
        """

    y = int(date[0:4])
    m = int(date[5:7])
    d = int(date[8:10])
    dd = datetime.date(y, m, d)

    return dd


def getDate(date):
    """
    Get the datetime.date from string formatted as '20180718'

        Parameters
        ----------
        date         -- Date in string formated: '20180406'

        Returns
        -------
        datetime.date date
        """

    y = int(date[0:4])
    m = int(date[4:6])
    d = int(date[6:8])
    dd = datetime.date(y, m, d)

    return dd

def getDateStringDashSeprtors(date):
    """
    from Date return a string formatted as '2018-07-18'

        Parameters
        ----------
    date         -- Datetime
    return the string formated as '20180718'

        Returns
        -------

    return the string formated as '20180718'

        """
    return datetime.datetime.strftime(date, '%Y-%m-%d')

def getDateString(date):
    """from Date return a string formated as '20180718'

    Keyword arguments:
    date         -- Datetime
    return the string formated as '20180718'
    """

    return datetime.datetime.strftime(date, '%Y%m%d')

def getDateFromMonthYear(dateString):
    """Return datetime.date from 'Mon'YY' string

    Keyword arguments:
    dateString   -- 'Mon'YY' string format
    """
    theMMMYY = dateString.split("'")
    aYY  = theMMMYY.pop()
    aMMM = theMMMYY.pop()

    aYY  = datetime.datetime.strptime('20' + aYY, '%Y').year
    aMMM = datetime.datetime.strptime(aMMM, '%b').month

    return datetime.date(aYY, aMMM, 1)


def month3Format(pickedDate):
    """Returns the date in format: Apr06'18

    Keyword arguments:
    pickedDate   -- datetime format
    """
    return datetime.datetime.strftime(getDate(pickedDate), "%b%d'%y")

# ==============================================================
def getMonthExpiries():
    """Get about 18 months of Fridays

    Keyword arguments:
    none
    """
   # today
    today = datetime.date.today()

    # get day multiple
    one_day = datetime.timedelta(days=1)

    # if past 3rd friday move calculation to next month
    if today > third_friday(today.year, today.month):
        today = today + (one_day * 30)


    # go out about 18 months = 548
    # go out about 6 mounth = 180
    # 5 months
    outNumberOfMonths = today + (one_day * 150)

    expiries = []

    while today <= outNumberOfMonths:
        today = third_friday(today.year, today.month)
        expiries.append(today.strftime("%b'%y"))
        today = today + (one_day * 20)

    return expiries

# ==============================================================
def getNextExpiryDate():
    """Get next expiry date
    Keyword arguments:
    none
    """
   # today
    today = datetime.date.today()

    # get day multiple
    one_day = datetime.timedelta(days=1)

    # if past 3rd friday move calculation to next month
    if today > third_friday(today.year, today.month):
        today = today + (one_day * 30)
    # return in format '20190816'
    today = third_friday(today.year, today.month)
    expiry = (today.strftime("%Y%m%d"))

    return expiry


# ==============================================================
# Expiry Utilities
def getExpiries():
    """Get about 18 months of Fridays

    Keyword arguments:
    none
    """
   # today
    today = datetime.date.today()

    # get day multiple
    one_day = datetime.timedelta(days=1)

    # if past 3rd friday move calculation to next month
    if today > third_friday(today.year, today.month):
        today = today + (one_day * 30)

    # go out about 18 months
    out18Months = today + (one_day * 548)

    expiries = []

    while today <= out18Months:
        today = third_friday(today.year, today.month)
        expiries.append(today.strftime("%b%d'%y"))
        today = today + (one_day * 20)

    return expiries

# ==============================================================
# Thursday Utilities
def isThursday(date):
    """See if date id Thursday formated: '20180406'

    Keyword arguments:
    date         -- Date in string format: '20180406'
    """
    dd = getDate(date)
    return dd.weekday() == 3 and dd > datetime.date.today()

def nextThursday(pickedDate):
    """Get the next Thursday date for Thursday Options close 

    Keyword arguments:
    pickedDate   -- datetime format
    """
    return pickedDate + datetime.timedelta( (3-pickedDate.weekday()) % 7 )

def nextThursdayExpiryFormat(pickedDate): 
    """Returns the next Thursday date for Thursday Options close in format: Apr06'18

    Keyword arguments:
    pickedDate   -- datetime format
    """  
    return datetime.datetime.strftime(nextThursday(pickedDate), "%b%d'%y")

def nextThursdayOrgFormat(pickedDate): 
    """Returns the next Thursday date for Thursday Options close in format: 20180718

    Keyword arguments:
    pickedDate   -- datetime format
    """  
    return datetime.datetime.strftime(nextThursday(pickedDate), "%Y%m%d")

def third_Thursday(year, month):
    """Return datetime.date for monthly option Thursday Index expiration given year and month
    """
    # The 15th is the lowest third day in the month
    third = datetime.date(year, month, 15)
    # What day of the week is the 15th?
    w = third.weekday()
    # Thursday is weekday 3
    if w != 3:
        # Replace just the day (of month)
        third = third.replace(day=(15 + (3 - w) % 7))
    return third


#==============================================================
# Friday Utilities
    
def isFriday(date):
    """See if date is Friday formated: '20180406'

    Keyword arguments:
    date         -- Date in string format: '20180406'
    """
    dd = getDate(date)
    return dd.weekday() == 4 and dd > datetime.date.today()

def nextFriday(pickedDate):
    """Get the next Friday date for Friday Options close 

    Keyword arguments:
    pickedDate   -- datetime format
    """
    return pickedDate + datetime.timedelta( (4-pickedDate.weekday()) % 7 )

def nextFridayExpiryFormat(pickedDate): 
    """Returns the next Friday date for Friday Options close in format: Apr06'18

    Keyword arguments:
    pickedDate   -- datetime format
    """  
    return datetime.datetime.strftime(nextFriday(pickedDate), "%b%d'%y")

def nextFridayOrgFormat(pickedDate): 
    """Returns the next Friday date for Friday Options close in format: 20180718

    Keyword arguments:
    pickedDate   -- datetime format
    """  
    return datetime.datetime.strftime(nextFriday(pickedDate), "%Y%m%d")


def third_friday(year, month):
    """Return datetime.date for monthly Friday option expiration given year and month

    Keyword arguments:
    year   -- datetime format
    month  -- datetime format
    """
    # The 15th is the lowest third day in the month
    third = datetime.date(year, month, 15)
    # What day of the week is the 15th?
    w = third.weekday()
    # Friday is weekday 4
    if w != 4:
        # Replace just the day (of month)
        third = third.replace(day=(15 + (4 - w) % 7))
    return third


def third_fridayFromOrgFormat(aDate):
    """
    Return datetime.date for next monthly Friday option expiration given year and month

    Keyword arguments:
    aDate -- format '20190919

    """
    # The 15th is the lowest third day in the month

    # print('aDate: ', aDate)
    third = third_friday(aDate.year, aDate.month)

    return datetime.datetime.strftime(third, "%Y%m%d")

def daysToExpiry(theExpiry):
    """

    :param   theExpiry: string formated as '20180718'
    :return: Days between today and theExpiry
    """
    today = datetime.date.today()

    return (getDate(theExpiry) - today).days

def getTodayStr(): #Todo refactor Today in this module

    #returns : 'Sun, Aug 11'
    return datetime.date.today().strftime("%a, %b %d")

def get30DaysOutStr():

    to30DaysOut = datetime.date.today() + datetime.timedelta(30)

    return to30DaysOut.strftime("%a, %b %d")

def get45DaysOutStr():

    to45DaysOut = datetime.date.today() + datetime.timedelta(45)

    return to45DaysOut.strftime("%a, %b %d")

def daysInYear():
    return 365

def monToDigits(aMon):
    mon = aMon.upper()
    if   mon == "JAN": return '01'
    elif mon == "FEB": return '02'
    elif mon == "MAR": return '03'
    elif mon == "APR": return '04'
    elif mon == "MAY": return '05'
    elif mon == "JUN": return '06'
    elif mon == "JUL": return '07'
    elif mon == "AUG": return '08'
    elif mon == "SEP": return '09'
    elif mon == "OCT": return '10'
    elif mon == "NOV": return '11'
    elif mon == "DEC": return '12'
    else: raise ValueError


def toExpiryStr(aYear, aMonth, aDay):
    theYearStr = str(aYear)
    if aDay < 9:
        aDayStr = str(aDay).zfill(2)
    else:
        aDayStr = str(aDay)

    return theYearStr + monToDigits(aMonth) + aDayStr

if __name__ == "__main__":
    print(getTodayStr())
