import sys
sys.path.append('/home/michael/jupyter/local-packages')

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
from matplotlib.widgets import Cursor

import matplotlib.dates as mdates

import mplcursors

import matplotlib
#matplotlib.use('Agg')

# Save the data
from pathlib import Path

theBaseCompaniesDirectory = '/home/michael/jupyter/earningDateData/Companies/'
csvSuffix = '.csv'
excelSuffix = '.xlsx'

def make_patch_spines_invisible(ax):
    ax.set_frame_on(True)
    ax.patch.set_visible(False)
    for sp in ax.spines.values():
        sp.set_visible(False)

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
    # add the headers to DF
    excelPastEarningsDateDF = pd.DataFrame(excelPastEarningsDateDF.values[1:], columns=headers)

    # reindex new DF
    excelPastEarningsDateDF.reindex

    # create to np array to display in matplotlib!!!!
    # Past earnings
    earningsMdate_np = excelPastEarningsDateDF.Earnings_Date.values
    earnings1DayMove_np = excelPastEarningsDateDF.EDFwd1DayClosePercentDelta.values
    earnings4DayMove_np = excelPastEarningsDateDF.EDFwd4DayClosePercentDelta.values

    #need to set up index with Datetime
    earnings1DayCandlestick =  excelPastEarningsDateDF[['Earnings_Date','Open','High','Low', 'Close', 'Volume']]
    # Get EPS data
    earningsDayEPS =  excelPastEarningsDateDF[['Earnings_Date','EPS_Estimate','Reported_EPS','Surprise(%)']]

    earnings1DayCandlestick.set_index(pd.DatetimeIndex(earnings1DayCandlestick['Earnings_Date']))
    earningsDayEPS.set_index(pd.DatetimeIndex(earningsDayEPS['Earnings_Date']))

    # Convert date string to a datenum using dateutil.parser.parse().
    earningsMdate_np = mdates.datestr2num(earningsMdate_np)  # np.core.defchararray.rstrip(earningsDate_np, 10))

    returnList = [earnings1DayMove_np, earnings4DayMove_np, earningsMdate_np, earnings1DayCandlestick, earningsDayEPS]

    return returnList

def plotEarnings(earningsMdate_np, earnings1DayMove_np, earnings4DayMove_np, earningsDayEPS, theStock):

    # Set date formatter
    locator = mdates.AutoDateLocator()
    formatter = mdates.ConciseDateFormatter(locator)
    formatter.formats = ["%b-%d-%Y"]

    # Set colors and labels  Earnings Move ----------------
    color1DayStockMove = 'navy'
    color4DayStockMove = 'darkorange'
    xLabel = 'Earnings Dates'
    xLabelColor = 'slategray'
    yLabelStockDeltaColor = color4DayStockMove
    yLabel1DayStockMove = 'Stock % Delta @ 1 Day Close Price'
    yLabel4DayStockMove = 'Stock % Delta @ 4 Day Close Price'
    yLabelStockDeltaTitle = 'Stock % Delta'
    ax1LegendLabel1Day = "1-Day % Move"
    ax1LegendLabel4Day = "4-Day % Move"
    zeroPointLabel = '@ $0.0 Move'

    # set title
    theTitle = theStock + '  -- 1-Day VS 4-Days Past Earnings $ Delta & EPS Estimate/Reported/Suprise'

    # Set colors and labels  EPS Move
    colorReportedEPS = 'forestgreen'
    colorEstimatedEPS = 'dodgerblue'
    colorSupriseEPS = 'firebrick'
    colorLabel = 'green'
    #,'EPS_Estimate','Reported_EPS','Surprise(%)
    ax2LegendReportedEPS  = "Reported EPS"
    ax2LegendEstimatedEPS = "Estimated EPS"
    ax2LegendSupriseEPS   = "Surprise(%)"

    # setup plotting ----------------------------
    # single Plot for Earnings price moves // Main Plot
    fig, earningsMovePlt = plt.subplots(figsize=(15, 6))
    # Setup Plot for a second axes that shares the same x-axis for EPS
    earningsEpsPlt = earningsMovePlt.twinx()
    # Setup Plot for a third axes that shares the same x-axis for earning surprise
    earningsEpsSuprisePlt = earningsMovePlt.twinx()

#=========================================================================================

    # Offset the right spine of Suprise ---------------------------
    # The ticks and label have already been
    # placed on the right by twinx above.
    earningsEpsSuprisePlt.spines["right"].set_position(("axes", 1.05))
    # Having been created by twinx, earningsMovePlt has its frame off, so the line of its
    # detached spine is invisible.  First, activate the frame but make the patch
    # and spines invisible.
    make_patch_spines_invisible(earningsEpsSuprisePlt)
    # Second, show the right spine.
    earningsEpsSuprisePlt.spines["right"].set_visible(True)

    # set titles/labels/ticks ----------------------
    earningsMovePlt.set_title(theTitle)
    # Set labels
    earningsMovePlt.set_xlabel(xLabel, color=xLabelColor)
    earningsMovePlt.set_ylabel(yLabelStockDeltaTitle, color=yLabelStockDeltaColor)
    earningsEpsPlt.set_ylabel('EPS', color=colorLabel)
    earningsEpsSuprisePlt.set_ylabel('Suprise %', color=colorSupriseEPS)
    # Set tick
    earningsMovePlt.tick_params(axis='y', labelcolor=yLabelStockDeltaColor)
    earningsMovePlt.tick_params(axis='x', labelcolor=xLabelColor)
    earningsEpsPlt.tick_params(axis='y', labelcolor=colorLabel)
    earningsEpsSuprisePlt.tick_params(axis='y', labelcolor=colorSupriseEPS)

    lines2, labels2 = earningsEpsPlt.get_legend_handles_labels()
    # build Legend for 2nd Xaxis
    lines1, labels1 = earningsMovePlt.get_legend_handles_labels()

    # set xaxis format -------------------------------
    earningsMovePlt.xaxis.set_major_formatter(mdates.DateFormatter("%b-%d-%Y"))
    fig.autofmt_xdate()

    plt.grid(color=colorSupriseEPS) # not needed at this point

    # plot 1Day and 4Day move
    label1Day = earningsMovePlt.plot(earningsMdate_np, earnings1DayMove_np, color=color1DayStockMove,
             label=ax1LegendLabel1Day, linestyle='--', marker='o')
    label4Day = earningsMovePlt.plot(earningsMdate_np, earnings4DayMove_np, color=color4DayStockMove,
             label=ax1LegendLabel4Day, linestyle='-', marker='o')

    # Add dotted line for $0 - Price move
    horzLine = earningsMovePlt.axhline(y=0, color='navy', linestyle=':', label=zeroPointLabel)

    xBar1 = earningsEpsPlt.bar(earningsMdate_np+6, earningsDayEPS.Reported_EPS, 4, label=ax2LegendReportedEPS, color=colorReportedEPS)
    xBar2 = earningsEpsPlt.bar(earningsMdate_np-1, earningsDayEPS.EPS_Estimate, 4, label=ax2LegendEstimatedEPS, color=colorEstimatedEPS)
    xBar3 = earningsEpsSuprisePlt.bar(earningsMdate_np+12, earningsDayEPS['Surprise(%)'], 4, label=ax2LegendSupriseEPS, color=colorSupriseEPS)

    lines = [label1Day[0],label4Day[0], horzLine, xBar2[0], xBar1[0], xBar3[0]]
    lineLabel = [label1Day[0]._label, label4Day[0]._label,horzLine._label,  xBar2._label, xBar1._label, xBar3._label]
    # set legend to top right
    earningsMovePlt.legend(lines, lineLabel,bbox_to_anchor=(0.96, 0.02))

    #cursor = Cursor(earningsMovePlt, useblit=True, color='red', linewidth=2) #, horizOn=True, vertOn=True, color='green')

    plt.show()

