import sys

sys.path.append('/home/michael/jupyter/local-packages')

from localUtilities import dateUtils, config
from localUtilities.ibUtils import getEarningsData, buildCsvSummary, getCompanyData
from localUtilities.ibUtils import buildCsvSummary, buildExcelDiary

import time
import pandas as pd
import yahoo_fin.stock_info as si
from yahoofinancials import YahooFinancials


def getEarningsDataFromYahoo(startday, earningWeekRange=5):
    # get Earnings Data - driven by Jupyter Notebook ""1) GetEarningsDataFromYahooV4""

    # get companies with earnings on ""startday"" plus ""earningWeekRange"" days from Yahoo
    aWeeksEarningsDF = getEarningsData.getEarningsForWeek(startday, earningWeekRange)
    # Add Market Data:
    #   Close Price, Last Price, Historic Volatility, Implied Volatility, Option Volume, Expected Range $ move
    #   use feather as data store in case there is a processing issue with large sets of earnings
    yahooEarningsOfInterestDF, allYahooEarningsForWeekDF = getEarningsData.addMarketData(aWeeksEarningsDF,
                                                                                         startday, getFeather=False)
    # Build CSV files:
    buildCsvSummary.saveCsvSummary(yahooEarningsOfInterestDF, allYahooEarningsForWeekDF, startday)


def getHistoricStockData(startday):
    # get Historic Stock Data - driven by Jupyter Notebook ""2) GetPriceMovesAtEarnings.ipynb""

    # setup directory location for stock ""startday"" stock data
    theDirectory = config.theBaseCompaniesDirectory + startday + '/rawData/'
    inFile = theDirectory + 'EarningOfInterestforweekOf-' + startday + config.csvSuffix

    # get all the stocks in ""EarningOfInterestforweekOf"" during ""startday"" earning week
    earningsDFfromFile = pd.read_csv(inFile)

    # Get the length of the DF so we can display a countdown 
    count = 0
    thelen = len(earningsDFfromFile)

    # Loop through Earnings Data ""earningsDFfromFile""
    for row in earningsDFfromFile.itertuples():
        print('\n', thelen - count, ') ', row.Symbol, end=' ', sep='')
        # get the stock
        theStock = row.Symbol

        # get ""theStock"" historic EPS info
        yahooTheStocksPastEarningsDF = getCompanyData.getHistoricEpsData(theStock)

        if yahooTheStocksPastEarningsDF.empty:
            print("\t/ oops - try again... / ", theStock, " is EMPTY - no data!!")
            for i in range(4):
                if yahooTheStocksPastEarningsDF.empty:
                    print("\t/ Trying again... attempt: ", i+1)
                    time.sleep(.5)
                    yahooTheStocksPastEarningsDF = getCompanyData.getHistoricEpsData(theStock)
                else:
                    print("\t/ Got Data!!! for: ", theStock)
                    count = count + 1
                    break
                continue

        yahooTheStocksPastEarningsMarketDataDF \
            = getCompanyData.addPastMarketData(yahooTheStocksPastEarningsDF)

        aStockOutFile = theDirectory + theStock + config.csvSuffix
        yahooTheStocksPastEarningsMarketDataDF.to_csv(aStockOutFile)

        count = count + 1


def createExcelEarningHistory(startday):
    # create excel 'Earnings History' book

    buildCsvSummary.createWeeklySummary(startday)
    buildExcelDiary.saveDiary2Excel(startday)
