import sys

# Path is needed to save the data
from pathlib import Path

sys.path.append('/home/michael/jupyter/local-packages')
from localUtilities.webScrape import getBarChartData as companyInfo
from localUtilities.webScrape import getBarChartOptionsSelenium as companyOptions
import pandas as pd


theBaseCompaniesDirectory = '/home/michael/jupyter/earningDateData/Companies/'
csvSuffix = '.csv'
excelSuffix = '.xlsx'

def buildExcelFile(aStock, startday, theExpiryDateText = '2020-05-29-w'):

    # Get the company info from BarChart
    stockInfo = companyInfo.getCompanyStockInfo(aStock)
    stockOverview = companyInfo.getCompanyOverview(aStock)
    stockFundamentals = companyInfo.getCompanyFundamentals(aStock)
    aText, stockRatings = companyInfo.getCompanyRatings(aStock)

    # get the company Option info
    callOptions, putOptions, expiryText = companyOptions.scrapeCompanyOptionData(aStock, theExpiryDateText)

    # Setup Excel output file
    outExcelFile = theBaseCompaniesDirectory + startday + '/' + aStock + '_SummaryWeekOf-' + startday + excelSuffix

    sheetIsFundamentals = 'Fundamentals'
    sheetRowStart = 5
    sheetColStart = 1

    writer = pd.ExcelWriter(outExcelFile, engine='xlsxwriter')

    fundamentalsWorkbook = writer.book
    fmt = fundamentalsWorkbook.add_format()

    stockFundamentalsTranposed = stockFundamentals.T

    # Add the Ratings next
    stockRatings.to_excel(writer, sheet_name= sheetIsFundamentals,
                                        startrow=sheetRowStart+3, startcol= sheetColStart)
    # Add the fundamentals
    stockInfo.to_excel(writer, sheet_name= sheetIsFundamentals,  startrow=sheetRowStart+7, startcol=sheetColStart)
    stockFundamentalsTranposed.to_excel(writer, sheet_name= sheetIsFundamentals, startrow=sheetRowStart+7,
                                        startcol= sheetColStart+3)
    stockOverview.to_excel(writer, sheet_name= sheetIsFundamentals,
                                        startrow=sheetRowStart+7, startcol= sheetColStart+6)

    # Add the text info on Expiry and Recommendations
    fundamentalsWorkbookSheet = writer.sheets['Fundamentals']
    fundamentalsWorkbookSheet.write(sheetRowStart+1,1, aText)
    fundamentalsWorkbookSheet.write(sheetRowStart,1, expiryText)

    #setup the Option Excel Sheets
    callOptions.to_excel(writer, sheet_name= 'Call Options',
                                        startrow=2, startcol= sheetColStart)
    putOptions.to_excel(writer, sheet_name= 'Put Options',
                                        startrow=2, startcol= sheetColStart)

    #=================================================================
    # add data from Raw CSV files
    #=================================================================
    # Get aStock CSV file and add as a sheet
    # companyEarningsWeek = theBaseCompaniesDirectory + startday + '/rawCSV/'
    # inCsvFile_aSymbol = companyEarningsWeek + aStock + csvSuffix
    # yahooEarningsDf_aSymbol = pd.read_csv(inCsvFile_aSymbol, index_col=0)
    # yahooEarningsDf_aSymbol.to_excel(writer, sheet_name= aStock+'-EarningsHistory',
    #                                     startrow=2, startcol= sheetColStart)


    # Get aStock Excel file and add as a sheet
    inExcelFile = theBaseCompaniesDirectory + startday +\
                          '/SummaryWeekOf-' + startday + excelSuffix
    # Need to use pd.ExcelFile to read in the file to manipulate
    yahooEarningsDf_aSymbol_Sheet = pd.ExcelFile(inExcelFile).parse(aStock)
    # Add the aStock sheet to our Company Info
    yahooEarningsDf_aSymbol_Sheet.to_excel(writer, sheet_name= aStock+'-EarningsHistory',
                                        startrow=2, startcol= sheetColStart)

    # get 2 rows of summary data
    summaryRow = yahooEarningsDf_aSymbol_Sheet.iloc[3,4 :]
    summaryRow = summaryRow.to_frame().T
    summaryRow.to_excel(writer, sheet_name= sheetIsFundamentals,
                                        startrow=1, startcol= 1)

    # Save excel
    writer.save()
