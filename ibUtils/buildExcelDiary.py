
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
    # assuming Path is setup
    writer = pd.ExcelWriter(outExcelFile, engine='xlsxwriter')

    summaryWorkbook = writer.book
    fmt = summaryWorkbook.add_format()

    # Summary Sheet Name
    yahooEarningsDF.to_excel(writer, sheet_name='Summary Earnings')

    for i in range(0, len(yahooEarningsDF)):
        # get the symbol and transpose data to fit Horizontally, creat sheet
        aSymbol = yahooEarningsDF.loc[i,].Symbol
        theHeader = yahooEarningsDF.loc[i,].to_frame()
        theHeaderTransposed = theHeader.T
        theHeaderTransposed.to_excel(writer, sheet_name= aSymbol)

        inCsvFile_aSymbol = companyEarningsWeek + aSymbol + csvSuffix
        yahooEarningsDf_aSymbol = pd.read_csv(inCsvFile_aSymbol, index_col=0)
        startRow = 3

        yahooEarningsDF.at[i, "Earnings_Date"] = dateUtils.getDateFromISO8601(yahooEarningsDF.loc[i,].Earnings_Date)

        yahooEarningsDf_aSymbol.to_excel(writer, sheet_name= aSymbol,  startrow=startRow)

    # Convert the dataframe to an XlsxWriter Excel object.
    # yahooEarningDf.to_excel(writer, sheet_name='Week of ' + startday)

    # format Earnings_Date Column C Row to len(yahooEarningsDF)+1

    worksheet = writer.sheets['Summary Earnings']

    cellRowFormat = summaryWorkbook.add_format({'bold': True, 'bg_color': 'green'})
    cellColFormat = summaryWorkbook.add_format()
    cellColFormat.set_shrink()

    worksheet.set_column(0, 20, 15 ,cellColFormat)
    worksheet.set_row(0, 15, cellRowFormat)

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
