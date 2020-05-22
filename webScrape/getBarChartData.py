import requests
from bs4 import BeautifulSoup
import json
import numpy as np
import pandas as pd
import sys
sys.path.append('/home/michael/jupyter/local-packages')


# Chrome linux User Agent - needed to not get blocked as a bot
headers = {'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
                         '(KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'}

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

def getCompanyOverview(aStock):
    # Creating an empty Dataframe with column names only
    companyQuoteDF = pd.DataFrame(
        columns=[{'lowPrice':float(),'openPrice':float(), 'highPrice':float(),
                  'lastPrice':float(),'previousPrice':float(),'volume':int(),
                 'averageVolume':int(),'stochasticK14d':float(),'weightedAlpha':float(),
                  'priceChange5d':float(),'percentChange5d':float(),'lowPrice1y':float(),'highPrice1y':float()}])

    # Get the page and pull in the HTML
    s = requests.Session()
    # include stock in URL
    aURL = "http://www.barchart.com/stocks/quotes/" + aStock + "/overview"
    r = s.get(aURL, headers=headers)
    s.close()
    src = r.content
    soup = BeautifulSoup(src, 'html.parser')

    # get the init(...) info
    initPageVars = soup.find("div", "bc-quote-overview row")
    # parse out the class "bc-quote-overview" data
    initPageVarsAttrs = initPageVars.attrs
    # get the data in the init(...) section
    initStr = initPageVarsAttrs.get('data-ng-init')
    # Split out the header "init(" - use remaining data in initStrSplit[1] / throw out initStrSplit[0]
    initStrSplitFront = initStr.split(',', 1)
    # get the raw data
    justInitDataReversed = "".join(reversed(initStrSplitFront[1]))
    justInitDataReversed = justInitDataReversed.split('}', 1)
    justInitData = "".join(reversed(justInitDataReversed[1]))
    justInitData = justInitData.split(('},'))
    getRawData = justInitData[2].split(',"raw":', 1)
    # get the dictionary of Stock Overview data
    companyInfoDict = json.loads(getRawData[1])

    # create DF from scrape data
    # needed the orient='index' to avoid scalar error
    companyQuoteDF = companyQuoteDF.from_dict(companyInfoDict, orient='index')

    return companyQuoteDF


def getCompanyFundamentals(aStock):
    # Get the page and pull in the HTML
    s = requests.Session()
    aURL = "http://www.barchart.com/stocks/quotes/BAC/overview"
    r = s.get(aURL, headers=headers)
    s.close()

    src = r.content
    soup = BeautifulSoup(src, 'html.parser')
    fundamentalsDict = {}

    # get the Fundamentals section of the page
    for div_tag in soup.find_all("div", "barchart-content-block symbol-fundamentals"):
        # get all the HTML <li> / list items
        for tBody in div_tag.find_all('li'):
            # capture the left side info into DF Series if exist
            leftSide = tBody.find(class_='left')
            if leftSide is not None:
                leftSideText = leftSide.get_text()
                fundamentalsDict.update({leftSideText: np.nan})
            # capture the right side info into DF Series if exist
            rightSide = tBody.find(class_='right')
            if rightSide is not None:
                rightSideText = rightSide.get_text()
                fundamentalsDict.update({leftSideText: rightSideText})

    fundamentalsDF = pd.DataFrame(fundamentalsDict, index=[0])

    return fundamentalsDF



def getCompanySectors(aStock):

    # Get the page and pull in the HTML
    s = requests.Session()
    aURL = "http://www.barchart.com/stocks/quotes/BAC/overview"
    r = s.get(aURL, headers=headers)
    s.close()

    src = r.content
    soup = BeautifulSoup(src, 'html.parser')

    sectorsList = []
    for div_tag in soup.find_all("div","barchart-content-block symbol-fundamentals"):
        for aLi in div_tag.find_all('li'):
            for theSectors in aLi.find_all('a'):
                sectorsList.append(theSectors.text)

    sectorsDF = pd.DataFrame(sectorsList, columns=['Sectors'])

    return sectorsDF

def getCompanyRatings(aStock):

    # Get the page and pull in the HTML
    s = requests.Session()
    aURL = "http://www.barchart.com/stocks/quotes/BAC/overview"
    r = s.get(aURL, headers=headers)
    s.close()

    src = r.content
    soup = BeautifulSoup(src, 'html.parser')

    # get the Consensus Rating String
    consensusRating = soup.find('div', class_ = 'bc-rating-and-estimates__content')

    div_tag = soup.find('div', class_='diagram')
    nextLevel = div_tag.contents[1]
    dataContentAttrs = nextLevel.attrs
    theRatingsDict = dataContentAttrs.get('data-content')

    analysisRatingsDict = json.loads(theRatingsDict)

    analysisRatingsDF = pd.DataFrame.from_dict(analysisRatingsDict)

    return consensusRating.text, analysisRatingsDF


