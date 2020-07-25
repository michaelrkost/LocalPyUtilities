import sys

# Path is needed to save the data
from pathlib import Path

sys.path.append('/home/michael/jupyter/local-packages')
from localUtilities.webScrape import getBarChartData as companyInfo
from localUtilities.webScrape import getBarChartOptionsSelenium as companyOptions
from localUtilities import dateUtils
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
    callOptions, putOptions, expiryText, aWebDriver = companyOptions.scrapeCompanyOptionData(aStock, theExpiryDateText)

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
    summaryRow = yahooEarningsDf_aSymbol_Sheet.iloc[0:1,0:21]

    summaryRow = summaryRow[["Symbol", "Company", "Earnings_Date", "Time", "Close", "ABSFwd1MinusClose", "ABSFwd1PlusClose",
                             "Exp$Range",  "Volume",  "Option_Volume", "histVol", "impVol", "IV_Delta",
                              "stdFwd1%", "stdFwd1$TimesClose", "std25Fwd1%",  "std25Fwd1$TimesClose", "max1DayABS$Delta" ]].copy()

    summaryRow.rename(columns={'ABSFwd1MinusClose' : 'ABS $ Minus'}, inplace=True)
    summaryRow.rename(columns={'ABSFwd1PlusClose' : 'ABS $ Plus'}, inplace=True)
    summaryRow.rename(columns={'stdFwd1%' : '1-SD % Move'}, inplace=True)
    summaryRow.rename(columns={"stdFwd1$TimesClose" : '1-SD $ Move'}, inplace=True)
    summaryRow.rename(columns={'std25Fwd1%' :'2.5-SD % Move'}, inplace=True)
    summaryRow.rename(columns={'max1DayABS$Delta' :'1Day Max ABS Delta'}, inplace=True)
    summaryRow.rename(columns={'std25Fwd1$TimesClose' : '2.5-SD $ Move'}, inplace=True)
    summaryRow.rename(columns={'Earnings_Date': 'Earnings'}, inplace=True)
    summaryRow.rename(columns={'histVol': 'Historic Vol'}, inplace=True)
    summaryRow.rename(columns={'impVol': 'Implied Vol'}, inplace=True)
    summaryRow.rename(columns={'IV_Delta': 'Vol Delta'}, inplace=True)


    #  Change to Earning Date Format: "Mon, Jul 06"
    summaryRow['Earnings'] = summaryRow['Earnings'].apply(str.replace, args=('-', '')).apply(dateUtils.monthDayFormat)

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
    expiry_format = fundamentalsWorkbook.add_format({'bold': True, 'font_color': 'navy', 'border': 2,
                                                          'valign': 'vcenter', 'align': 'center','fg_color': '#FAF1D3',})
    today_format = fundamentalsWorkbook.add_format({'bold': True, 'font_color': '#C00000', 'border': 2,
                                                     'valign': 'vcenter','align': 'center','fg_color': '#FAF1D3',})
    call_label_format = fundamentalsWorkbook.add_format({'bold': True, 'font_color': 'navy', 'fg_color': '#D7E4BC',
                                                            'border': 2, 'valign': 'vcenter', 'align': 'center'})
    put_label_format = fundamentalsWorkbook.add_format({'bold': True, 'font_color': 'navy', 'fg_color': '#f9cfb5',
                                                                'border': 2, 'valign': 'vcenter', 'align': 'center'})
    open_format = fundamentalsWorkbook.add_format({'bold': True, 'font_color': 'navy', 'fg_color': '#93D07B',
                                                            'border': 2, 'valign': 'vcenter', 'align': 'center'})
    close_format = fundamentalsWorkbook.add_format({'bold': True, 'font_color': 'navy', 'fg_color': '#eb813d',
                                                            'border': 2, 'valign': 'vcenter', 'align': 'center'})
    trade_header_format = fundamentalsWorkbook.add_format({'bold': True, 'font_color': 'navy', 'fg_color': '#D7E4BC',
                                                            'border': 2, 'valign': 'vcenter', 'align': 'center'})
    trade_text_format = fundamentalsWorkbook.add_format({ 'border': 1, 'valign': 'vcenter', 'align': 'center'})
    empty_expiryW_format = fundamentalsWorkbook.add_format({'bold': True, 'font_color': 'navy', 'border': 2,
                                                            'valign': 'vcenter', 'align': 'center','fg_color': '#F2E1A9'})  # f2e1a9
    empty_expiryM_format = fundamentalsWorkbook.add_format({'border': 2, 'fg_color': '#FAF1D3'})
    empty_cell_format = fundamentalsWorkbook.add_format({'border': 2, 'valign': 'center'})

    # tradePlanWorkbookSheet = writer.sheets[aStock+'-Trade Plan']
    tradePlanWorkbookSheet = fundamentalsWorkbook.add_worksheet(aStock + '-Trade Plan')

    # [tradePlanWorkbookSheet.write(0, x, '', empty_cell_format) for x in range(0,7,1)]
    #
    for col_num, value in enumerate(summaryRow.columns.values):
        if col_num > 12:
            tradePlanWorkbookSheet.write(4, col_num-12, value, trade_header_format)
            tradePlanWorkbookSheet.write(5, col_num-12, summaryRow.iloc[0,col_num], trade_text_format)
        elif col_num > 6:
            tradePlanWorkbookSheet.write(2, col_num-6, value, trade_header_format)
            tradePlanWorkbookSheet.write(3, col_num-6, summaryRow.iloc[0,col_num], trade_text_format)
        else:
            tradePlanWorkbookSheet.write(0, col_num, value, trade_header_format)
            tradePlanWorkbookSheet.write(1, col_num, summaryRow.iloc[0,col_num], trade_text_format)

    tradePlanWorkbookSheet.set_row(1, 20)
    tradePlanWorkbookSheet.set_row(3, 20)
    tradePlanWorkbookSheet.set_row(5, 20)

     # Format Earning data?
    # [tradePlanWorkbookSheet.write(0, x, '', empty_cell_format) for x in range(0,7,1)]
    # Expiry Text / Implied Vol
    # next Expiry dates
    tradePlanWorkbookSheet.write(7,1, expiryText, expiry_text_format)
    tradePlanWorkbookSheet.write(8, 1, "Next Expiry's ->", expiry_format)
    tradePlanWorkbookSheet.write(8, 2, 'Friday:  ' + dateUtils.getNextFridayExpiryFormat(), empty_expiryW_format)
    tradePlanWorkbookSheet.write(8, 3, "Monthly:  " + dateUtils.month3Format(dateUtils.getNextExpiryDate()), expiry_format)

    # [tradePlanWorkbookSheet.write(9, x, '', empty_expiryM_format) for x in range(2,4,2)]
    tradePlanWorkbookSheet.write(9, 2, '', empty_expiryW_format)
    tradePlanWorkbookSheet.write(9, 3, '', empty_expiryM_format)

    tradePlanWorkbookSheet.write(13, 0, "Today:  ", today_format)
    tradePlanWorkbookSheet.write(13, 1, dateUtils.getTodayStr(), today_format)
    tradePlanWorkbookSheet.write(13, 2, 'Strike', trade_header_format)
    tradePlanWorkbookSheet.write(13, 3, 'Price', trade_header_format)
    tradePlanWorkbookSheet.write(13, 4, 'IV', trade_header_format)
    tradePlanWorkbookSheet.write(13, 5, 'Volume', trade_header_format)
    # tradePlanWorkbookSheet.write(16, 6, 'IV', trade_header_format)
    tradePlanWorkbookSheet.write(13, 6, 'Time Executed', trade_header_format)

    tradePlanWorkbookSheet.write(14, 0, 'Open', open_format)
    tradePlanWorkbookSheet.write(14, 1, 'Call', call_label_format)
    tradePlanWorkbookSheet.write(15, 1, 'Put', put_label_format)

    [tradePlanWorkbookSheet.write(14, x, '', empty_cell_format) for x in range(2,7,1)]
    [tradePlanWorkbookSheet.write(15, x, '', empty_cell_format) for x in range(2,7,1)]
    [tradePlanWorkbookSheet.write(15, x, '', empty_cell_format) for x in range(2,7,1)]

    [tradePlanWorkbookSheet.write(16, x, '', empty_expiryM_format) for x in range(1, 7, 1)]
    tradePlanWorkbookSheet.set_row(16, 10)
    #
    tradePlanWorkbookSheet.write(17, 0, 'Close', close_format)
    tradePlanWorkbookSheet.write(17, 1, 'Call', trade_header_format)
    tradePlanWorkbookSheet.write(18, 1, 'Put', put_label_format)
    [tradePlanWorkbookSheet.write(17, x, '', empty_cell_format) for x in range(2,7,1)]
    [tradePlanWorkbookSheet.write(18, x, '', empty_cell_format) for x in range(2,7,1)]
    tradePlanWorkbookSheet.set_row(14, 40)
    tradePlanWorkbookSheet.set_row(15, 40)
    tradePlanWorkbookSheet.set_row(17, 40)
    tradePlanWorkbookSheet.set_row(18, 40)
    #
    tradePlanWorkbookSheet.set_tab_color('green')
    tradePlanWorkbookSheet.set_column('B:G', 22)
    # # Save excel
    writer.save()

    return aWebDriver


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

