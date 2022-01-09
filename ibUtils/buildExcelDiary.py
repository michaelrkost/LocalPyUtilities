
import sys
from pathlib import Path
sys.path.append('/home/michael/jupyter/local-packages')

import pandas as pd
import os.path

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
    startday : Earnings week startDay

    Returns
    -------

    """

    # Setup Excel output file
    companyEarningsWeek = theBaseCompaniesDirectory + startday + '/rawData/'
    outExcelFile = theBaseCompaniesDirectory + startday + '/' + 'SummaryWeekOf-' + startday + excelSuffix

    # Create a Pandas Excel writer using XlsxWriter as the engine
    # assuming Path is setup to outExcelFile
    writer = pd.ExcelWriter(outExcelFile, engine='xlsxwriter')

    summaryWorkbook = writer.book
    fmt = summaryWorkbook.add_format()

    # Set up index so to ultimately order Tabs
    yahooEarningsDF.sort_values(by=['Symbol'], inplace=True)
    yahooEarningsDF = yahooEarningsDF.reset_index(drop=True)

    # create first tab as Summary Earnings
    # turn off the header so it can be formatted
    # Trim summary columns
    summaryYahooEarningsDF = yahooEarningsDF.copy(deep=True)
    summaryYahooEarningsDF = setSummaryYahooDF(summaryYahooEarningsDF)
    # Save to Excel w/out index
    summaryYahooEarningsDF.to_excel(writer, sheet_name='Summary Earnings', index=False)
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
        if Path(inCsvFile_aSymbol).is_file():
            yahooEarningsDf_aSymbol = pd.read_csv(inCsvFile_aSymbol, index_col=0)
        else:
            continue
        # start adding to data to tab after the Current Earnings info - see above
        startRow = 3
        # get date
        yahooEarningsDF.at[i, "Earnings_Date"] = dateUtils.getDateFromISO8601(yahooEarningsDF.loc[i,].Earnings_Date)
        # add the data
        yahooEarningsDf_aSymbol.to_excel(writer, sheet_name= aSymbol,  startrow=startRow)
        aSymboWorksheet = writer.sheets[aSymbol]
        aSymboWorksheet.set_column('A:V', 15)
        aSymboWorksheet.set_column('N:U', 40)



    # cellRowFormat = summaryWorkbook.add_format({'bold': True, 'bg_color': 'red'})  #hex ccffcc  / R:204 G: 255 B: 204
    # cellLtGreenFormat = summaryWorkbook.add_format({'bold': True, 'bg_color': '#CCFFCC'})
    # cellColFormat.set_shrink()
    #
    percentFormat  = summaryWorkbook.add_format({'num_format': '0.00%','align': 'center'})
    currencyFormat = summaryWorkbook.add_format({'num_format': '$#,##0.00', 'align': 'center'})
    date_str_format = summaryWorkbook.add_format({'align': 'center'})

    header_format = summaryWorkbook.add_format({'num_format': '0','align': 'center',
                                                'bold': True, 'font_color': 'navy', 'border': 2,
                                                'valign': 'vcenter', 'fg_color': '#D7E4BC',})

    worksheet.set_column('A:A', 10)
    worksheet.set_column('B:B', 35)
    worksheet.set_column('C:C', 12, date_str_format)
    worksheet.set_column('D:D', 10, date_str_format)
    worksheet.set_column('E:E', 10, currencyFormat)
    worksheet.set_column('F:F', 15)
    worksheet.set_column('G:I', 10, percentFormat)
    worksheet.set_column('J:K', 12, currencyFormat)

    #Format headers -- need to get value then update
    for col_num, value in enumerate(summaryYahooEarningsDF.columns.values):
        worksheet.write(0, col_num, value, header_format)

    # Close the Pandas Excel writer and output the Excel file.
    writer.save()

    return

def saveDiary2Excel(startday):

    companyEarningsWeekCSVfile = theBaseCompaniesDirectory + startday + '/rawData/'

    # Get saved CSV Summary data
    earningWeekDir = Path(companyEarningsWeekCSVfile)

    # Save Week Summary
    companySummaryListFile = 'SummaryOfWeek-' + startday + csvSuffix

    # read in CSV summary file based on startDay
    yahooEarningsDF = pd.read_csv(earningWeekDir / companySummaryListFile, index_col=0)

    # todo determine if we need Put/Call MinMaxVolsSav
    # save Put/Call Volumes to CSV files
    # getMinMaxVolsSaveAsCSV(ib, yahooEarningsDF, startDay)
    # save the weeks earning Summary to Excel
    saveSummaryToExcel(yahooEarningsDF, startday)

    # print('Done - buildExcelDiary-saveDiary2Excel........')

    return

def setSummaryYahooDF(summaryYahooEarningsDF):
    # shorten some column names
    summaryYahooEarningsDF.rename(columns={'max1DayABS$Delta': 'Abs$Delta'}, inplace=True)
    summaryYahooEarningsDF.rename(columns={'Earnings_Date': 'Earnings'}, inplace=True)
    summaryYahooEarningsDF.rename(columns={'Option_Volume': 'OptionVolume'}, inplace=True)
    summaryYahooEarningsDF.rename(columns={'IV_Delta': 'VolDelta'}, inplace=True)

    # Get a new Summary DF
    # sumYahooEarningsDF[...].copy() - So not to do operation on slice of DF but actual DF
    # Will not get warning:
    #   "A value is trying to be set on a copy of a slice from a DataFrame."
    sumYahooEarningsDF = summaryYahooEarningsDF[['Symbol', 'Company', 'Earnings', 'Time', 'Close',
                                       'OptionVolume', 'histVol','impVol', 'VolDelta',
                                       'Exp$Range', 'Abs$Delta']].copy()

    # change Earnings from string '2019-08-19' to datetime
    sumYahooEarningsDF['Earnings'] = sumYahooEarningsDF['Earnings'].apply(dateUtils.getDateFromISO8601)
    # change Earning Time to isAfter to provide sort with Before Earnings First then After then TAS
    sumYahooEarningsDF.loc[sumYahooEarningsDF['Time'] == 'After', 'Time'] = 'isAfter'

    # sort by Earnings Date then Time // Before isAfter
    sumYahooEarningsDF = sumYahooEarningsDF.sort_values(by=['Earnings', 'Time'])

    #  Change to Earning Date Format: "Mon, Jul 06"
    sumYahooEarningsDF['Earnings'] = sumYahooEarningsDF['Earnings'].apply(dateUtils.getDayFormat)


    return sumYahooEarningsDF