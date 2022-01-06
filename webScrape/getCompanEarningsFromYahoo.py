import pandas as pd
import requests
from bs4 import BeautifulSoup
import datetime

# Chrome linux User Agent - needed to not get blocked as a bot
#Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36
headers = {'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'}


def getPastEarnings(stock="AAPL"):
    """

    Parameters
    ----------
    stock : a Stock / default to AAPL

    Returns
    -------
    DF of scraped data
    """
    aURL = "https://finance.yahoo.com/calendar/earnings/?symbol=" + stock
    result = requests.get(aURL, headers = headers)
    result.close()

    # print(result.status_code)
    # Todo capture 400 error and such

    src = result.content
    soup = BeautifulSoup(src, 'html.parser')  # change to 'lxml')

    # Creating an empty Dataframe with column names only
    earningsDataDF = pd.DataFrame(
        columns=['Symbol', 'Earnings_Date', 'Company', 'EPS_Estimate', 'Reported_EPS', 'Surprise(%)'])

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
                    elif aria_label == "Earnings Date":
                        ed = td_tag.get_text('td')
                        ed = ed.replace('td', ' ')
                    elif aria_label == "EPS Estimate":
                        epsE = td_tag.get_text('td')
                    elif aria_label == "Reported EPS":
                        epsR = td_tag.get_text('td')
                    elif aria_label == "Surprise(%)":
                        susp = td_tag.get_text('td')
                        # remove the '+td' which came along - 12/20/21
                        susp = susp.replace('+td', '')

                # create a dictionary from <td> scrape data
                # try:
                aRow = {'Symbol': [sym],
                    'Earnings_Date': [ed],
                    'Company': [co],
                    'EPS_Estimate': [epsE],
                    'Reported_EPS': [epsR],
                    'Surprise(%)': [susp]}
                # except UnboundLocalError:
                #     print('     ', UnboundLocalError, '       In getPastEarnings for: ', sym)
                #     break
                # create DF from one <td> scrape data
                oneEarningDateDF = earningsDataDF.from_dict(aRow)
                # capture all earnings data in DF
                earningsDataDF = earningsDataDF.append(oneEarningDateDF, sort=False)

    earningsDataDF = earningsDataDF.reset_index(drop=True)
    # change string date to datetime date
    earningsDataDF['Earnings_Date'] = earningsDataDF.Earnings_Date.apply(
        lambda date: datetime.datetime.strptime(date, '%b %d, %Y, %I %p %Z'))

    # Drop future earnings dates and reindex ===================================
    earningsDataDF.drop(earningsDataDF[earningsDataDF['Earnings_Date'] > datetime.datetime.today()].index, inplace=True)
    earningsDataDF = earningsDataDF.reset_index(drop=True)

    # Check to see if there is a Dup for last Earnings
    # This Dup was coming from Yahoo - two earnings dates with different times
    # - So need to clean it out...
    # Drop one of the Dup dates and reindex
    # drop Dup based on 'Earnings_Date'
    # get the Day w/out any time - normalized
    if earningsDataDF.empty: # first check if DF is empty
        print("in getPastEarnings -- earningsDataDF is empty" )
        return earningsDataDF
    else:
        theNormalizedDates = earningsDataDF['Earnings_Date'].dt.normalize()
        # if first 2 dates are the same remove and reindex
        if theNormalizedDates.at[0] == theNormalizedDates.at[1]:
            earningsDataDF = earningsDataDF.drop(0, axis=0)
            earningsDataDF = earningsDataDF.reset_index(drop=True)

    return earningsDataDF
