import datetime

def getDate(date):
    """Get the datetime.date from string formated as '20180406'

    Keyword arguments:
    date         -- Date in string formated: '20180406'
    """
    y = int(date[0:4])
    m = int(date[4:6])
    d = int(date[6:8])
    dd = datetime.date(y, m, d)
    return dd

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
import datetime

def third_friday(year, month):
    """Return datetime.date for monthly Friday option expiration given year and month
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

if __name__ == "__main__":
    isFriday()
