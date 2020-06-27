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

    # percentFormat  = fundamentalsWorkbook.add_format({'num_format': '0.0%'})
    # currencyFormat = fundamentalsWorkbook.add_format({'num_format': '$#,##0.00'})

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
    # Setup Trade Plan Worksheet
    # ------------------------------------------------------------------
    # set up Trade Worksheet as the First Tab this is crudely done by instanciting the sheet first
    # this is done above   -->  tradePlanWorkbookSheet = writer.sheets[aStock+'-Trade Plan']
    # Todo - figure out how to order workbook sheets
    #        the worksheets are kept in "writer" as dict
    # format line like: 21 Days to expiration on 2020-07-17 -- Implied Volatility: 68.32%
    expiry_text_format = fundamentalsWorkbook.add_format({'bold': True, 'font_color': '#C00000'})
    expiry_format = fundamentalsWorkbook.add_format({'bold': True, 'font_color': '#C00000', 'border': 2,
                                                          'valign': 'vcenter', 'align': 'center','fg_color': '#FAF1D3',})
    # For headers:  Strike, Price, IV etc
    strangle_header_format = fundamentalsWorkbook.add_format({'bold': True, 'font_color': 'navy', 'fg_color': '#D7E4BC',
                                                            'border': 2, 'valign': 'vcenter', 'align': 'center'})
    buy_format = fundamentalsWorkbook.add_format({'bold': True, 'font_color': 'navy', 'fg_color': '#93D07B',
                                                            'border': 2, 'valign': 'vcenter', 'align': 'center'})
    sell_format = fundamentalsWorkbook.add_format({'bold': True, 'font_color': 'navy', 'fg_color': '#FCB19C',
                                                            'border': 2, 'valign': 'vcenter', 'align': 'center'})


    # Where the Data will be entered by hand.
    strangle_data_format = fundamentalsWorkbook.add_format({'bold': True, 'font_color': 'navy', 'fg_color': '#D7E4BC',
                                                            'border': 2, 'valign': 'vcenter'})

    empty_cell_format = fundamentalsWorkbook.add_format({'border': 2, 'valign': 'center'})
    data_row_format = fundamentalsWorkbook.add_format({'font_color': 'navy', 'valign': 'center'})

    summaryRow.iloc[0:1,0:8].to_excel(writer, sheet_name= aStock+'-Trade Plan',
                                           startrow=0, startcol= 0, index=False)    # suppress index // index = False

    summaryRow.iloc[0:1,8:12].to_excel(writer, sheet_name= aStock+'-Trade Plan',
                                           startrow=3, startcol= 1, index=False)
    summaryRow.iloc[0:1,12:19].to_excel(writer, sheet_name= aStock+'-Trade Plan',
                                           startrow=6, startcol= 1, index=False) # suppress index

    tradePlanWorkbookSheet = writer.sheets[aStock+'-Trade Plan']

    tradePlanWorkbookSheet.set_row(1, None, data_row_format)
    tradePlanWorkbookSheet.set_row(4, None, data_row_format)
    tradePlanWorkbookSheet.set_row(7, None, data_row_format)

       # header_format = workbook.add_format({'bold': True,'text_wrap': True, 'valign': 'top',
       #     'fg_color': '#D7E4BC','border': 1})

    tradePlanWorkbookSheet.write(9,1, expiryText, expiry_text_format)
    tradePlanWorkbookSheet.write(11, 0, 'Expiry', expiry_format)
    tradePlanWorkbookSheet.write(11, 1, '', expiry_format)

    tradePlanWorkbookSheet.write(11, 2, 'Strike', strangle_header_format)
    tradePlanWorkbookSheet.write(11, 3, 'Price', strangle_header_format)
    tradePlanWorkbookSheet.write(11, 4, 'IV', strangle_header_format)
    tradePlanWorkbookSheet.write(11, 5, 'Volume', strangle_header_format)
    tradePlanWorkbookSheet.write(11, 6, 'IV', strangle_header_format)
    tradePlanWorkbookSheet.write(11, 7, 'Time Exectuted', strangle_header_format)

    tradePlanWorkbookSheet.write(12, 0, 'Buy', buy_format)
    tradePlanWorkbookSheet.write(12, 1, 'Call', strangle_header_format)
    tradePlanWorkbookSheet.write(13, 1, 'Put', strangle_header_format)

    [tradePlanWorkbookSheet.write(12, x, '', empty_cell_format) for x in range(2,8,1)]
    [tradePlanWorkbookSheet.write(13, x, '', empty_cell_format) for x in range(2,8,1)]
    [tradePlanWorkbookSheet.write(15, x, '', empty_cell_format) for x in range(2,8,1)]
    [tradePlanWorkbookSheet.write(16, x, '', empty_cell_format) for x in range(2,8,1)]

    tradePlanWorkbookSheet.write(15, 0, 'Sell', sell_format)
    tradePlanWorkbookSheet.write(15, 1, 'Call', strangle_header_format)
    tradePlanWorkbookSheet.write(16, 1, 'Put', strangle_header_format)
    tradePlanWorkbookSheet.set_row(11, 30, data_row_format)
    tradePlanWorkbookSheet.set_row(12, 85, data_row_format)
    tradePlanWorkbookSheet.set_row(13, 85, data_row_format)
    tradePlanWorkbookSheet.set_row(15, 85, data_row_format)
    tradePlanWorkbookSheet.set_row(16, 85, data_row_format)

    tradePlanWorkbookSheet.set_tab_color('green')
    tradePlanWorkbookSheet.set_column('B:K', 22)
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