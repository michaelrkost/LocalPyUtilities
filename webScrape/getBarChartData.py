import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
import sys
sys.path.append('/home/michael/jupyter/local-packages')


# Chrome linux User Agent - needed to not get blocked as a bot
headers = {
 'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'}

def getCompanyStockInfo(aStock):
    """
    This will scrape BarChart page for the company info / aStock
    :param aStock:
    :type aStock: String
    :return: Panda DF
    :rtype:
    """
    # Creating an empty Dataframe with column names only
    companyInfoDF = pd.DataFrame(
    columns=['symbol','symbolName','symbolType','lastPrice','priceChange','percentChange','bidPrice','askPrice','bidSize','askSize',
          'tradeTime','lastPriceExt','priceChangeExt','percentChangeExt','tradeTimeExt','contractName','daysToContractExpiration',
          'symbolCode','exchange','sicIndustry','sessionDateDisplayLong','shouldUpdate'])

    # Get the page and pull in the HTML
    s = requests.Session()
    # include stock in URL
    aURL = "http://www.barchart.com/stocks/quotes/" + aStock + "/overview"
    r = s.get(aURL, headers = headers)
    s.close()
    src = r.content
    soup = BeautifulSoup(src, 'html.parser')

    # get the init(...) info
    # initPageVars = soup.find("div", "bc-quote-overview row")
    anInitPageVars = soup.find("div","page-title symbol-header-info")

    # parse out the class "bc-quote-overview" data
    initPageVarsAttrs = anInitPageVars.attrs
    # get the data in the init(...) section
    initStr = initPageVarsAttrs.get('data-ng-init')

    # Split out the header "init(" - use remaining data in initStrSplit[1] / throw out initStrSplit[0]
    initStrSplitFront = initStr.split('(', 1)

    initStrSplitEnd = "".join(reversed(initStrSplitFront[1]))
    initStrSplitEnd = initStrSplitEnd.split(')', 1)
    initStrSplitEnd = "".join(reversed(initStrSplitEnd[1]))

    # #Split out the ")" at the end of initStrSplit[1]
    # initStrSplitEnd = initStrSplitFront[1].split(')', 1)
    # Make into a dictionary
    companyInfoDict = json.loads(initStrSplitEnd)

    # create DF from scrape data
    # needed the orient='index' to avoid scalar error
    companyInfoDF = companyInfoDF.from_dict(companyInfoDict, orient='index')

    return companyInfoDF

def getQuoteOverview(aStock):
    # Creating an empty Dataframe with column names only
    companyInfoDF = pd.DataFrame(
        columns=['symbol', 'symbolName', 'symbolType', 'lastPrice', 'priceChange', 'percentChange', 'bidPrice',
                 'askPrice', 'bidSize', 'askSize',
                 'tradeTime', 'lastPriceExt', 'priceChangeExt', 'percentChangeExt', 'tradeTimeExt', 'contractName',
                 'daysToContractExpiration',
                 'symbolCode', 'exchange', 'sicIndustry', 'sessionDateDisplayLong', 'shouldUpdate'])

    # Get the page and pull in the HTML
    s = requests.Session()
    # include stock in URL
    aURL = "http://www.barchart.com/stocks/quotes/" + aStock + "/overview"
    r = s.get(aURL, headers=headers)
    s.close()
    src = r.content
    soup = BeautifulSoup(src, 'html.parser')

    # get the init(...) info
    # initPageVars = soup.find("div", "bc-quote-overview row")
    anInitPageVars = soup.find("div", "bc-quote-overview row")

    companyInfoDict = getInitDict(anInitPageVars)

    # create DF from scrape data
    # needed the orient='index' to avoid scalar error
    # companyInfoDF = companyInfoDF.from_dict(companyInfoDict, orient='index')

    return companyInfoDict #companyInfoDF





