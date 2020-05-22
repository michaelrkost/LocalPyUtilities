

import requests
from bs4 import BeautifulSoup
import math

from localUtilities import dateUtils
import pandas as pd
import datetime

# Chrome linux User Agent - needed to not get blocked as a bot
headers = {
 'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'}


def getEarningsForWeek(startday):
    """
    This is the function that is called to start the Yahoo page scraping.

    Parameters
    ----------
    startday : date on which to start earnings week

    Returns
    -------
    anEarningsDF: a DF of companies for the earnings week
    """
    anEarningsDF = pd.DataFrame(columns=['Symbol', 'Earnings_Date', 'Company', 'Earnings Call Time'])

    # Week start date
    aStartDay = dateUtils.getDateFromISO8601(startday)

    #Start Monday go to Friday
    for x in range(5):
        aDay = aStartDay + datetime.timedelta(days=x)
        aNewEarningsDF = getEarningsOnDate(dateUtils.getDateStringDashSeprtors(aDay))
        try:
            anEarningsDF = anEarningsDF.append(aNewEarningsDF)
        except TypeError:
            print("No Earnings on: ", aDay)
            continue
        print('Working Day: ', aDay)

    return  anEarningsDF.reset_index(drop=True)

def getEarningsOnDate(aDay):
    """
    Get Yahoo earnings for week starting @ aDay
    Parameters
    ----------
    aDay : first day of week

    Returns
    -------
    DF w/ Symbol', 'Earnings_Date', 'Company', 'Earnings Call Time'
    """
    # Yahoo earnings page
    aURL = "https://finance.yahoo.com/calendar/earnings?day=" + aDay
    result = requests.get(aURL, headers = headers)
    result.close()

    src = result.content
    soup = BeautifulSoup(src, 'html.parser')

    # We know page has a page count
    #  1-100 of 252 results
    # get the second number between front and back
    front = 'of '
    back = ' results'

    # Find the earnings in the table with the id: 'fin-cal-table'
    # see how many earnings are present
    try:
        for div_tag in soup.find_all('div', {'id': 'fin-cal-table'}):
            for aspan in div_tag.find('h3'):
                for anotherSPan in aspan.find_all('span', {'data-reactid': '8'}):
                    numPages = math.ceil(int(aspan.text[aspan.text.find(front) + 2: aspan.text.find(back)])/100)
                    print(aspan.text)
    except TypeError:
        print('No earnings found.')    # todo  - move this first aDay out of this loop
        return 0

    # Creating an empty Dataframe with column names only
    earningsDataDF = pd.DataFrame(columns=['Symbol', 'Earnings_Date', 'Company', 'Earnings Call Time'])
    oneEarningDateDF = pd.DataFrame(columns=['Symbol', 'Earnings_Date', 'Company', 'Earnings Call Time'])

    # get earnings per page
    # just on page
    if numPages < 1:
        oneEarningDateDF = getEarningPage(aURL, earningsDataDF, aDay)
    # more than one page
    else:
        for i in range(numPages):
            aNewURL = aURL + "&offset=" + str(i*100) + '&size=100'
            oneEarningDateDF = oneEarningDateDF.append(getEarningPage(aNewURL, earningsDataDF, aDay))
            #capture all earnings data in DF
            earningsDataDF.drop(earningsDataDF.index, inplace=True)
    # reset the index and return
    oneEarningDateDF = oneEarningDateDF.reset_index(drop=True)
    return oneEarningDateDF

def getEarningPage(aURL, earningsDataDF, aDay, numPages=0):
    """
    Yahoo will have a number of pages of earnings, here we get Yahoo earnings on specific page
    Parameters
    ----------
    aURL : URL for the specific earnings page
    earningsDataDF: the DF to keep earnings
    aDay: the earning day
    numPages: not used #todo remove numPages

    Returns
    -------
    DF w/ Symbol', 'Earnings_Date', 'Company', 'Earnings Call Time'
    """

    result = requests.get(aURL, headers=headers)
    result.close()

    src = result.content
    soup = BeautifulSoup(src, 'html.parser')

    # Find the earnings in the table with the id: 'fin-cal-table'
    for div_tag in soup.find_all('div', {'id': 'fin-cal-table'}):
        # need to get to the 'tbody' go right into the table - so not to get header data
        for tBody in div_tag.find_all('tbody'):
            # get on earning date element and save
            for tr_tag in tBody.find_all('tr'):
                for td_tag in tr_tag.find_all('td'):
                    aria_label = td_tag.attrs['aria-label']
                    if aria_label == "Symbol":
                        aTag = td_tag.find('a')
                        sym = aTag.text
                    elif aria_label == "Company":
                        co = td_tag.get_text("td")
                    elif aria_label == "Earnings Call Time":
                        ect = td_tag.get_text('td')

                # create a dictionary from <td> scraped data
                aRow = {'Symbol': [sym],
                        'Company': [co],
                        'Earnings Call Time': [ect],
                        'Earnings_Date': aDay}

                # create DF from one <td> scrape data
                oneEarningDateDF = earningsDataDF.from_dict(aRow)
                # capture all earnings data in DF
                earningsDataDF = earningsDataDF.append(oneEarningDateDF, sort=False)
    return earningsDataDF
