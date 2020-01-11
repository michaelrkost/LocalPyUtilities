import sys
sys.path.append('/home/michael/jupyter/local-packages')

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Save the data
from pathlib import Path

theBaseCompaniesDirectory = '/home/michael/jupyter/earningDateData/Companies/'
csvSuffix = '.csv'
excelSuffix = '.xlsx'


def getWeeklyExcelSummary(startday, theStock):
    print('in getWeeklyExcelSummary')

    # Get saved data Summary of companies
    companyEarningsWeek = startday + '/'
    companyListFile = 'SummaryWeekOf-' + startday + excelSuffix
    theFilePath = theBaseCompaniesDirectory + companyEarningsWeek + companyListFile
    # earningWeekDir = Path(theFilePath)
#TODo Complete next
# Complete the loop to get the theStock and then pass to getWeeklyStockTabSummary

    return getWeeklyStockTabSummary(theFilePath, theStock)


def getWeeklyStockTabSummary(theFilePath, theSymbol):



    # Get theSymbol excel TAB and put in DF
    excelEarningsDateDF = pd.read_excel(theFilePath, theSymbol)

    # From theSymbol excel TAB separate out the current earnings line from the past earning lines from Excel
    excelCurrentEarningsDateDF = excelEarningsDateDF.iloc[0:1, ]
    excelPastEarningsDateDF = excelEarningsDateDF.iloc[2:, ]

    # pull out the headers then save the remaining Past Earnings DF
    headers = excelPastEarningsDateDF.iloc[0]
    excelPastEarningsDateDF = pd.DataFrame(excelPastEarningsDateDF.values[1:], columns=headers)

    # reindex new DF
    excelPastEarningsDateDF.reindex

    # create to np array to display in matplotlib!!!!
    earningsMdate_np = excelPastEarningsDateDF.Earnings_Date.values
    earnings1DayMove_np = excelPastEarningsDateDF.EDFwd1DayClosePercentDelta.values
    earnings4DayMove_np = excelPastEarningsDateDF.EDFwd4DayClosePercentDelta.values

#need to set up index with Datetime
    earnings1DayCandlestick =  excelPastEarningsDateDF[['Earnings_Date','Open','High','Low', 'Close', 'Volume']]
    # # earnings1DayCandlestick["Date"] = earnings1DayCandlestick.Earnings_Date.map.to_datetime()
    # earnings1DayCandlestick = pd.to_datetime(earnings1DayCandlestick['Earnings_Date'] )#+ ' ' + earnings1DayCandlestick['time'], format=format)
    # earnings1DayCandlestick = earnings1DayCandlestick.set_index('Earnings_Date', drop=False)
    earnings1DayCandlestick.set_index(pd.DatetimeIndex(earnings1DayCandlestick['Earnings_Date']))
    # earnings1DayCandlestick.reindex

    # Convert date string to a datenum using dateutil.parser.parse().
    earningsMdate_np = mdates.datestr2num(earningsMdate_np)  # np.core.defchararray.rstrip(earningsDate_np, 10))

    returnList = [earnings1DayMove_np, earnings4DayMove_np, earningsMdate_np, earnings1DayCandlestick]

    return returnList

def plotEarnings(earningsMdate_np, earnings1DayMove_np, earnings4DayMove_np, theStock):
    locator = mdates.AutoDateLocator()
    formatter = mdates.ConciseDateFormatter(locator)
    formatter.formats = ["%b-%d-%Y"]

    color1DayStockMove = 'tab:blue'
    color4DayStockMove = 'darkorange'
    xLabel = 'Earnings Dates'
    xLabelColor = 'maroon'
    yLabelColor = 'darkgreen'
    yLabel1DayStockMove = 'Stock % Delta @ 1 Day Close Price'
    yLabel4DayStockMove = 'Stock % Delta @ 4 Day Close Price'
    yLabel = 'Stock % Delta'
    ax1LegendLabel1Day = "1-Day % Move"
    ax1LegendLabel4Day = "4-Day % Move"
    zeroPointLabel = '@ 0.0'

    # single Plot
    # theStock = excelPastEarningsDateDF.iloc[0,0]
    fig, ax1 = plt.subplots(figsize=(15, 6))

    theTitle = theStock + '  -- 1-Day VS 4-Days / Past Earnings $ Delta'

    ax1.set_title(theTitle)

    ax1.set_xlabel(xLabel, color=xLabelColor)
    ax1.set_ylabel(yLabel, color=yLabelColor)
    ax1.tick_params(axis='y', labelcolor=yLabelColor)
    ax1.tick_params(axis='x', labelcolor=xLabelColor)

    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%b-%d-%Y"))

    ax1.plot(earningsMdate_np, earnings1DayMove_np, color=color1DayStockMove,
             label=ax1LegendLabel1Day, linestyle='--', marker='o')
    ax1.plot(earningsMdate_np, earnings4DayMove_np, color=color4DayStockMove,
             label=ax1LegendLabel4Day, linestyle='-', marker='D')
    plt.axhline(y=0, color='gold', linestyle=':', label=zeroPointLabel)

    # build Legend for 2 Xaxis
    lines1, labels1 = ax1.get_legend_handles_labels()
    # lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(bbox_to_anchor=(1.1, 1.1))

    # fig.autofmt_xdate()
    # plt.show()