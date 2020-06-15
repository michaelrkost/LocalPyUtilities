import sys

# Path is needed to save the data
from pathlib import Path

sys.path.append('/home/michael/jupyter/local-packages')
from localUtilities.webScrape import getBarChartData as companyInfo
from localUtilities.webScrape import getBarChartOptionsSelenium as companyOptions
import pandas as pd

#plot imports
from localUtilities.plotEarnings import getEarningsData

theBaseCompaniesDirectory = '/home/michael/jupyter/earningDateData/Companies/'
csvSuffix = '.csv'
excelSuffix = '.xlsx'

def buildExcelFile(aStock, startday, theExpiryDateText):

    # Get the company info from BarChart.com
    stockInfo = companyInfo.getCompanyStockInfo(aStock)
    stockOverview = companyInfo.getCompanyOverview(aStock)
    stockFundamentals = companyInfo.getCompanyFundamentals(aStock)
    aText, stockRatings = companyInfo.getCompanyRatings(aStock)
    callOptions, putOptions, expiryText = companyOptions.scrapeCompanyOptionData(aStock, theExpiryDateText)

    # Setup Excel output file
    outExcelFile = theBaseCompaniesDirectory + startday + '/' + aStock + '_SummaryWeekOf-' + startday + excelSuffix
    # Setup Fundamentals worksheet name
    sheetIsFundamentals = aStock + '-Fundamentals'

    # Starting point for data
    sheetRowStart = 4
    sheetColStart = 1

    # create writer and workbook
    writer = pd.ExcelWriter(outExcelFile, engine='xlsxwriter')
    fundamentalsWorkbook = writer.book

    # ------------------------------------------------------------------
    # set up fundamentals Worksheet
    # ------------------------------------------------------------------
    # Transpose
    stockFundamentalsTranposed = stockFundamentals.T

    # Add the Ratings next
    stockRatings.to_excel(writer, sheet_name= sheetIsFundamentals,
                                        startrow=sheetRowStart+3, startcol= sheetColStart)
    # Add the fundamentals
    stockInfo.to_excel(writer, sheet_name= sheetIsFundamentals,  startrow=sheetRowStart+7,
                       startcol=sheetColStart, header=False)
    stockFundamentalsTranposed.to_excel(writer, sheet_name= sheetIsFundamentals, startrow=sheetRowStart+7,
                                        startcol= sheetColStart+2, header=False)
    stockOverview.to_excel(writer, sheet_name= sheetIsFundamentals,
                           startrow=sheetRowStart+7, startcol= sheetColStart+4, header=False)

    # Add the text info on Expiry and Recommendations
    fundamentalsWorkbookSheet = writer.sheets[sheetIsFundamentals]
    fundamentalsWorkbookSheet.write(sheetRowStart+1,1, aText)
    fundamentalsWorkbookSheet.write(sheetRowStart,1, expiryText)
    fundamentalsWorkbookSheet.set_column('B:F', 25)
    fundamentalsWorkbookSheet.set_column('G:S', 18)
    # fundamentalsWorkbookSheet.conditional_format('B2:B8', {'type': '3_color_scale'})

    # ------------------------------------------------------------------
    # setup the Call/Put Option Worksheets
    # ------------------------------------------------------------------
    # include the DF header as Excel Header
    callOptions.to_excel(writer, sheet_name= aStock + '-Call Options',
                                        startrow=0, header=True)
    putOptions.to_excel(writer, sheet_name= aStock + '-Put Options',
                                        startrow=0, header=True)

    # ------------------------------------------------------------------
    # setup the Call/Put Option Worksheets
    # ------------------------------------------------------------------
    # Get aStock Excel file and add as a sheet
    inExcelFile = theBaseCompaniesDirectory + startday +\
                          '/SummaryWeekOf-' + startday + excelSuffix
    # Need to use pd.ExcelFile to read in the file to manipulate
    yahooEarningsDf_aSymbol_Sheet = pd.ExcelFile(inExcelFile).parse(aStock)
    # Add the aStock sheet to our Company Info
    yahooEarningsDf_aSymbol_Sheet.to_excel(writer, sheet_name= aStock+'-EarningsHistory',
                                           startrow=2, startcol= sheetColStart)

    # ------------------------------------------------------------------
    # setup summary Worksheet
    # ------------------------------------------------------------------
    # get 2 rows of summary data
    summaryRow = yahooEarningsDf_aSymbol_Sheet.iloc[0:1,0:19]

    summaryRow.to_excel(writer, sheet_name= sheetIsFundamentals,
                        startrow=0, startcol= 1, index=False)

    # ------------------------------------------------------------------
    # Create Plot and save as png file
    # Setup plot Worksheet
    # ------------------------------------------------------------------
    plotEarningPngFile(aStock, startday)
    # Get Plot file path
    aStockEarningsPlot = theBaseCompaniesDirectory + startday + '/rawData/' + aStock + '.png'
    # create image worksheet then add image
    imageWorksheet = fundamentalsWorkbook.add_worksheet(aStock + '-Earnings History Plot')
    imageWorksheet.insert_image('B3',aStockEarningsPlot)

    # ------------------------------------------------------------------
    # Setup Trade Worksheet
    # ------------------------------------------------------------------

    # Save excel
    writer.save()


def plotEarningPngFile(aStock, startday):

    # Get weekly earnings
    theEarningsDataList = getEarningsData.getWeeklyExcelSummary(startday, aStock)

    earnings1DayMove_np = theEarningsDataList[0]
    earnings4DayMove_np = theEarningsDataList[1]
    earningsMdate_np = theEarningsDataList[2]
    earnings1DayCandlestick = theEarningsDataList[3]
    earningsDayEPS = theEarningsDataList[4]

    # earningsDayEPS
    getEarningsData.plotEarnings(earningsMdate_np, earnings1DayMove_np, earnings4DayMove_np,
                                 earningsDayEPS, startday, aStock)


# def imageSheetFormatting(fundamentalsWorkbook):
#
#     imageWorkbookSheet = fundamentalsWorkbook[']
#     imageWorkbookSheet.set_row(3, 'E:E', 10, percentFormat)
#     # imageWorkbookSheet.set_column('M:M', 10, currencyFormat)
#     # imageWorkbookSheet.set_column('N:O', 10, percentFormat)
#     # imageWorkbookSheet.set_column('P:T', 10, currencyFormat)
#     return imageWorkbookSheet