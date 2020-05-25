import sys
sys.path.append('/home/michael/jupyter/local-packages')
from localUtilities.webScrape import getBarChartData as companyInfo
from localUtilities.webScrape import getBarChartOptionsSelenium as companyOptions
import pandas as pd


theBaseCompaniesDirectory = '/home/michael/jupyter/earningDateData/Companies/'
csvSuffix = '.csv'
excelSuffix = '.xlsx'

def buildExcelFile(aStock, startday):
    stockInfo = companyInfo.getCompanyStockInfo(aStock)
    stockOverview = companyInfo.getCompanyOverview(aStock)
    stockFundamentals = companyInfo.getCompanyFundamentals(aStock)
    aText, stockRatings = companyInfo.getCompanyRatings(aStock)
    theExpiryDateText = '2020-05-29-w'
    callOptions, putOptions, expiryText = companyOptions.scrapeCompanyOptionData(aStock, theExpiryDateText)

    # Setup Excel output file
    outExcelFile = theBaseCompaniesDirectory + startday + '/' + aStock + '_SummaryWeekOf-' + startday + excelSuffix


    sheetIsFundamentals = 'Fundamentals'
    sheetRowStart = 7
    sheetColStart = 3

    writer = pd.ExcelWriter(outExcelFile, engine='xlsxwriter')

    fundamentalsWorkbook = writer.book
    fmt = fundamentalsWorkbook.add_format()

    stockFundamentalsTranposed = stockFundamentals.T

    # Add the Ratings next
    stockRatings.to_excel(writer, sheet_name= sheetIsFundamentals,
                                        startrow=3, startcol= sheetColStart)
    # Add the fundamentals
    stockInfo.to_excel(writer, sheet_name= sheetIsFundamentals,  startrow=sheetRowStart, startcol=sheetColStart)
    stockFundamentalsTranposed.to_excel(writer, sheet_name= sheetIsFundamentals, startrow=sheetRowStart,
                                        startcol= sheetColStart + 3)
    stockOverview.to_excel(writer, sheet_name= sheetIsFundamentals,
                                        startrow=sheetRowStart, startcol= sheetColStart + 6)

    # Add the text info on Expiry and Recommendations
    fundamentalsWorkbookSheet = writer.sheets['Fundamentals']
    fundamentalsWorkbookSheet.write(2,1, aText)
    fundamentalsWorkbookSheet.write(1,1, expiryText)

    callOptions.to_excel(writer, sheet_name= 'Call Options',
                                        startrow=2, startcol= sheetColStart)
    putOptions.to_excel(writer, sheet_name= 'Put Options',
                                        startrow=2, startcol= sheetColStart)


    # Save excel
    writer.save()
