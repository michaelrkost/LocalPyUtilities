
import sys
from pathlib import Path
sys.path.append('/home/michael/jupyter/local-packages')

import pandas as pd

from localUtilities import dateUtils

theBaseCompaniesDirectory = '/home/michael/jupyter/earningDateData/Companies/'

csvSuffix = '.csv'
excelSuffix = '.xlsx'

# =============================================================================

def saveSummaryToExcel(yahooEarningsDF, startday ):
    """

    Parameters
    ----------
    yahooEarningsDF: the Yahoo earnings DF
    startday : Earnings week startday

    Returns
    -------

    """

    # Setup Excel output file
    companyEarningsWeek = theBaseCompaniesDirectory + startday + '/'
    outExcelFile = companyEarningsWeek + 'SummaryWeekOf-' + startday + excelSuffix

    # Create a Pandas Excel writer using XlsxWriter as the engine
    # assuming Path is setup to outExcelFile
    writer = pd.ExcelWriter(outExcelFile, engine='xlsxwriter')

    summaryWorkbook = writer.book
    fmt = summaryWorkbook.add_format()

    yahooEarningsDF.sort_values(by=['Symbol'], inplace=True)
    yahooEarningsDF = yahooEarningsDF.reset_index(drop=True)

    # create first tab as Summary Earnings
    # turn off the header so it can be formatted
    yahooEarningsDF.to_excel(writer, sheet_name='Summary Earnings')
    worksheet = writer.sheets['Summary Earnings']

    # number of Stocks / i.e. Rows in Summary Earnings Tab
    len_yahooEarningsDF = len(yahooEarningsDF)

    # write out each Stock Symbol info from the stock CSV file into an excel tab
    for i in range(0, len_yahooEarningsDF):
        # from yahooEarningsDF get the symbol and then transpose data to fit Horizontally, creat sheet
        # this is the Stock Tab top 3 rows that include Current Earnings info as well as other info like
        #     options volume, expected price changes, and delta price IV - etc
        aSymbol = yahooEarningsDF.loc[i,].Symbol
        theHeader = yahooEarningsDF.loc[i,].to_frame()
        theHeaderTransposed = theHeader.T
        theHeaderTransposed.to_excel(writer, sheet_name= aSymbol)

        inCsvFile_aSymbol = companyEarningsWeek + aSymbol + csvSuffix
        yahooEarningsDf_aSymbol = pd.read_csv(inCsvFile_aSymbol, index_col=0)
        # start adding to data to tab after the Current Earnings info - see above
        startRow = 3
        # get date
        yahooEarningsDF.at[i, "Earnings_Date"] = dateUtils.getDateFromISO8601(yahooEarningsDF.loc[i,].Earnings_Date)
        # add the data
        yahooEarningsDf_aSymbol.to_excel(writer, sheet_name= aSymbol,  startrow=startRow)


    # cellRowFormat = summaryWorkbook.add_format({'bold': True, 'bg_color': 'red'})  #hex ccffcc  / R:204 G: 255 B: 204
    # cellLtGreenFormat = summaryWorkbook.add_format({'bold': True, 'bg_color': '#CCFFCC'})
    # cellColFormat.set_shrink()
    #
    percentFormat  = summaryWorkbook.add_format({'num_format': '0.0%'})
    currencyFormat = summaryWorkbook.add_format({'num_format': '$#,##0.00'})

    worksheet.set_column('G:I', 10, percentFormat)
    worksheet.set_column('M:M', 10, currencyFormat)
    worksheet.set_column('N:O', 10, percentFormat)
    worksheet.set_column('P:T', 10, currencyFormat)

    # Close the Pandas Excel writer and output the Excel file.
    writer.save()

    return

def saveDiary2Excel(startday):

    companyEarningsWeek = theBaseCompaniesDirectory + startday + '/'

    # Get saved Summary data
    earningWeekDir = Path(companyEarningsWeek)

    # Save Week Summary
    companySummaryListFile = 'SummaryOfWeek-' + startday + csvSuffix

    # read in CSV summary file based on startday
    yahooEarningsDF = pd.read_csv(earningWeekDir / companySummaryListFile, index_col=0)

    # todo determine if we need Put/Call MinMaxVolsSav
    # save Put/Call Volumes to CSV files
    # getMinMaxVolsSaveAsCSV(ib, yahooEarningsDF, startday)
    # save the weeks earning Summary to Excel
    saveSummaryToExcel(yahooEarningsDF, startday)

    print('Done - buildExcelDiary-saveDiary2Excel........')

    return
