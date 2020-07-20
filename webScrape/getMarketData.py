# %%

import requests
from bs4 import BeautifulSoup
import pandas as pd

# Chrome linux User Agent - needed to not get blocked as a bot
headers = {
 'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'}


def getMarketDataFromOptionistics(symbol):
    """
    Get Today's Market Data from Optionistics
    :param symbol: the Stock Symbol
    :type symbol:
    :return:
    :rtype:
    """
    # get Martket data - do web call
    # post symbol
    s = requests.Session()
    aURL = "http://www.optionistics.com/quotes/stock-quotes"
    r = s.post(aURL, data={'symbol': symbol}, headers = headers)
    r.close()

    # get web page into BeautifulSoup
    src = r.content
    soup = BeautifulSoup(src, 'html.parser')

    # Find the data in the table with the id: 'mainbody'
    # and table class: 'quotem'
    table = soup.find_all('table', {'class': 'quotem'})
    #got it - now put it in a DF
    try:
        df = pd.read_html(str(table))
    except ValueError:
        print('str(table): ', dict())
        print('     ValueError', ValueError, '       getMarketData.getMarketDataFromOptionistics')
        return dict()

    # get the last stock price
    lastStockPrice = df[0][6][0]

    # get the section of the page in which we are interested
    df = df[1]
    df = df.drop([0])
    # put the data into 2 columns - Name / Value pair
    part1 = df[df.columns[0:2]]

    part2 = df[df.columns[2:4]]
    part2.reset_index(inplace=True, drop=True)
    part2.columns = [0, 1]

    part3 = df[df.columns[4:6]]
    part3.reset_index(inplace=True, drop=True)
    part3.columns = [0, 1]

    result = pd.concat((part1, part2, part3))
    result.reset_index(drop=True, inplace=True)

    # set index to first column of our DF and remove default index
    result = result.set_index([0])
    # create dictionary to access items
    # remove first layer to get to items
    res_dict = result.to_dict()
    res_dict = res_dict[1]

    # Add Last Stock price to dictionary
    # todo Removed last 7/19/2020
    # res_dict.update({'LAST': lastStockPrice})

    #return dictionary of MarketData
    return res_dict




