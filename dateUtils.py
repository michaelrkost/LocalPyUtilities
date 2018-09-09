import datetime


def getDate(date):
    """Get the datetime.date from string formated as '20180718'

    Keyword arguments:
    date         -- Date in string formated: '20180406'
    """
    y = int(date[0:4])
    m = int(date[4:6])
    d = int(date[6:8])
    dd = datetime.date(y, m, d)
    return dd

# ==============================================================
def getDateString(date):
    """from Date return a string formated as '20180718'

    Keyword arguments:
    date         -- Datetime
    return the string formated as '20180718'
    """

    return datetime.datetime.strftime(date, '%Y%m%d')
# ==============================================================
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

# ==============================================================
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

# ==============================================================
# Friday Utilities
    
def isFriday(date):
    """See if date id Friday formated: '20180406'

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

def daysToExpiry(theExpiry):
    """

    :param   theExpiry: string formated as '20180718'
    :return: Days between today and theExpiry
    """
    today = datetime.date.today()

    return (getDate(theExpiry) - today).days

def getTodayStr(): #Todo refactor Today in this module
    return datetime.date.today().strftime("%a, %b %d")

def get30DaysOutStr():

    to30DaysOut = datetime.date.today() + datetime.timedelta(30)

    return to30DaysOut.strftime("%a, %b %d")

def get45DaysOutStr():

    to45DaysOut = datetime.date.today() + datetime.timedelta(45)

    return to45DaysOut.strftime("%a, %b %d")

def daysInYear():
    return 365



if __name__ == "__main__":
    print(getTodayStr())
