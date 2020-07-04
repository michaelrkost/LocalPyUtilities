"""
module: dateUtils

This file is intended to be imported as a module and contains the following
functions:

    * goOutXWeekdays(startDay, nextXDays) - Get the next nextXDays weekdays - no weekends
                                            nextXDays: if positive go forward in time / Negative go backwards
    * getWorkdaysBetween(start, end) - get workdays(not Weekends) from start to end - return list datetime
    * ensureItsaWeekDay(date) - checks if previous date is a weekend - if so return previous weekday
    * getDate('20180718') - return datetime.date
    * getDayFormat(datetime) -  - returns formatted 'Sun, Aug 11'
    * getDateFromISO8601('2019-08-19') - return datetime.date
    * getDateStringDashSeprtors(datetime)- from datetime return formatted date: 2018-07-18'
    * getDateString(date) - from datetime return formatted sting '20180718'
    * getDateFromMonthYear('Mon'YY') - from 'Mon'YY' return datetime.date - first day of Month
    * month3Format('20180718') - from '20180718' return format "Apr06'18"
    * getMonthExpiries() - get about 5 months of Friday Monthly expiry dates
    * getNext5MonthsExpires() - - get about 5 months of Friday Monthly and Weekly expiry dates
    * getNextExpiryDate() - get the next Friday Monthly expiry
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
    * nextFridayOrgFormat(datetime) returns str format: '20180718'
    * third_friday(year, month) - Return datetime.date for monthly Friday option expiration given year and month
    * daysToExpiry('20180718') - Days between today and theExpiry
    * getTodayStr() - returns formatted 'Sun, Aug 11'
    * get45DaysOutStr - out 45 days - returns formatted 'Sun, Aug 11'
    * daysInYear - returns 365
    * monToDigits('aug') - from 3 letter name(case insensitive) return 2 digits
    * toExpiryStr(2019, 'dec', 8) - integers for day and year, Str 3 day Month - 'dec' - case insensitive
                                    return Option expiry date str format '20191208'
    * getNextThirdFridayFromDate(aDate) - Return str for next monthly 3rd Friday option expiration given aDate(Date)
    * breakDateToSting('20191004') - return tuple ( YYYY, MM, DD)
    * getListofFridayExpiryDate(num) - list of Friday Option Expiry Dates out "num" weeks / 10 is default

"""

#=============================================================
import datetime

# Stock Market Holidays 2020/2021
stockMarketHolidays = [datetime.date(2016, 1, 1),
                       datetime.date(2016, 1, 18),
                       datetime.date(2016, 2, 15),
                       datetime.date(2016, 3, 25),
                       datetime.date(2016, 5, 30),
                       datetime.date(2016, 7, 4),
                       datetime.date(2016, 9, 5),
                       datetime.date(2016, 11, 24),
                       datetime.date(2016, 12, 26),
                       datetime.date(2017, 1, 1),
                       datetime.date(2017, 1, 16),
                       datetime.date(2017, 2, 20),
                       datetime.date(2017, 4, 14),
                       datetime.date(2017, 5, 29),
                       datetime.date(2017, 7, 4),
                       datetime.date(2017, 9, 4),
                       datetime.date(2017, 11, 23),
                       datetime.date(2017, 12, 25),
                       datetime.date(2018, 1, 1),
                       datetime.date(2018, 1, 15),
                       datetime.date(2018, 2, 19),
                       datetime.date(2018, 3, 30),
                       datetime.date(2018, 5, 28),
                       datetime.date(2018, 7, 4),
                       datetime.date(2018, 9, 3),
                       datetime.date(2018, 11, 22),
                       datetime.date(2018, 12, 25),
                       datetime.date(2019, 1, 1),
                       datetime.date(2019, 1, 21),
                       datetime.date(2019, 2, 18),
                       datetime.date(2019, 4, 19),
                       datetime.date(2019, 5, 27),
                       datetime.date(2019, 7, 4),
                       datetime.date(2019, 9, 2),
                       datetime.date(2019, 11, 28),
                       datetime.date(2019, 12, 25),
                       datetime.date(2020, 1, 1), 
                       datetime.date(2020, 1, 20),
                       datetime.date(2020, 2, 17),
                       datetime.date(2020, 4, 10),
                       datetime.date(2020, 5, 25),
                       datetime.date(2020, 7, 3),
                       datetime.date(2020, 9, 7),
                       datetime.date(2020, 11, 26),
                       datetime.date(2020, 12, 25),
                       datetime.date(2021, 1, 1),
                       datetime.date(2021, 1, 18),
                       datetime.date(2021, 2, 15),
                       datetime.date(2021, 4, 2),
                       datetime.date(2021, 5, 31),
                       datetime.date(2021, 7, 5),
                       datetime.date(2021, 9, 6),
                       datetime.date(2021, 11, 25),
                       datetime.date(2021, 12, 24),
                       datetime.date(2022, 1, 17),
                       datetime.date(2022, 2, 21),
                       datetime.date(2022, 4, 15),
                       datetime.date(2022, 5, 30),
                       datetime.date(2022, 7, 4),
                       datetime.date(2022, 9, 5),
                       datetime.date(2022, 11, 24),
                       datetime.date(2022, 12, 26)]

#=============================================================
def goOutXWeekdays(startDate, nextXDays, excluded=(6, 7)):
    """
     Get the nextXDays forward or backwards - a positive number moves forward
     while a negative number returns nextXDays backwards
     and bypass weekends and Stock Market Holidays

     using isoweekday() where weekends are integers 6 and 7


    Parameters
    ----------
    aDate : the day in datetime
    nextXDays: how many days to go out

    Returns
    -------
    returnDate /  a weekday

    """
    # no movement so return the startDate
    if nextXDays == 0:
        return startDate
    # if positive nextXDay number go forward in time
    elif nextXDays > 0:
        count = 1
        while count <= nextXDays:
            startDate += datetime.timedelta(days=1)
            if startDate.isoweekday() not in excluded and startDate not in stockMarketHolidays:
                count += 1
        return startDate
    # Negative nextXDay number so go backwards in time
    else:
        count = -1
        while count >= nextXDays:
            startDate -= datetime.timedelta(days=1)
            if startDate.isoweekday() not in excluded and startDate not in stockMarketHolidays:
                count -= 1
        return startDate


def workdaysBetween(start, end, excluded=(6, 7)):
    """
     Get the workdays days between start and end - no weekends

    Parameters
    ----------
    start : the starting day in datetime
    end: last day in series

    Returns
    -------
    days - list of datatime days with no weekends

    """

    days = []
    while start.date() <= end.date():
        if start.isoweekday() not in excluded:
            days.append(start)
        start += datetime.timedelta(days=1)
    return days


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
        date         -- Date in ISO 8601 string formatted: '2018-04-06'

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
    """Get about 5 months of Fridays

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
    """Get next Monthly expiry date
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
# Expiry Utilities
def getNext5MonthsExpires():
    """Get next 5 months of Fridays
    in format
    2020-07-17-m  // monthly expiry
    2020-07-03-w  // weekly expiry

    Keyword arguments:
    none
    """
   # today
    today = datetime.date.today()

    # get day multiple
    one_day = datetime.timedelta(days=1)

    theNextFriday = nextFriday(today)
    third_friday()

    # if past 3rd friday move calculation to next month
    if today > third_friday(today.year, today.month):
        today = today + (one_day * 30)
        expirySuffix = '-w'

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

def getNextFridayExpiryFormat():
    """Returns the next Friday date for Friday Options close in format: Apr06'18

    Keyword arguments:

    """
    #Todo if the Friday is a holiday return the next Thursday
    return datetime.datetime.strftime(nextFriday(datetime.date.today()), "%b%d'%y")

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


def getNextThirdFridayFromDate(aDate):
    """
    Return str for next monthly 3rd Friday option expiration given Date.

    Take into account
        - end of year month & year change
        - today is past this months third Friday / go to next month

    Keyword arguments:
    aDate -- 'datetime.date' / '2019-12-30

    Returns:
        str: "2020-01-17"
    """

    # if this months 3rd friday has passed
    if third_friday(aDate.year, aDate.month) < datetime.date.today():
        third = third_friday(aDate.year, nextMonthDate(aDate))
    # if  Dec  need to get to next year
    elif aDate.month == 12:
        third = third_friday(aDate.year + 1 , nextMonthDate(aDate))
    # ok - just get this months 3rd Friday
    else:
        third = third_friday(aDate.year, aDate.month)

    return datetime.date.strftime(third, "%Y%m%d")

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

def getDayFormat(aDateTime) :

    return aDateTime.strftime("%a, %b %d")

def daysInYear():
    return 365

def nextMonthDate(aDate):

    return (aDate.month + 1) % 12


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


def toExpiryStr(aYear, aMonth, aDay):
    theYearStr = str(aYear)
    if aDay < 9:
        aDayStr = str(aDay).zfill(2)
    else:
        aDayStr = str(aDay)

    return theYearStr + monToDigits(aMonth) + aDayStr

def breakDateToSting(dateStr):
    """

    Parameters
    ----------
    dateStr : a Date String '20191004'

    Returns
    -------
    return a 3 String tuple ( 'YYYY', 'MM', 'DD')
    """

    aYear = dateStr[0:4]
    aMonth = dateStr[4:6]
    aDay = dateStr[6:8]
    return aYear, aMonth, aDay

if __name__ == "__main__":
    print(getTodayStr())
def getListOfFridayExpiryDate(numOfWeeks=10):
    '''
    create a list of Friday option expiry dates in str format
    :param numOfWeeks: default to 10 weeks
    :type numOfWeeks: int
    :return: list of option expiry dates in str format
    :rtype:
    '''

    #number of days to next weeks check point
    six_days = datetime.timedelta(days=6)
    # get Today's info
    dateCheck = datetime.date.today()
    # get next Friday and The Monthly Friday
    theNextFriday = nextFriday(dateCheck)
    thisMonthsThirdFriday = third_friday(dateCheck.year, dateCheck.month)

    listOfDates = []
    for x in range(20):
        if nextFriday(dateCheck) == third_friday(dateCheck.year, dateCheck.month):
            aMStr = getDateStringDashSeprtors(nextFriday(dateCheck)) + '-m'
            listOfDates.append(aMStr)
        else:
            aWStr = getDateStringDashSeprtors(nextFriday(dateCheck)) + '-w'
            listOfDates.append(aWStr)
        dateCheck = nextThursday(dateCheck + six_days)

    return listOfDates
