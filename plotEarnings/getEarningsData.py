import sys
sys.path.append('/home/michael/jupyter/local-packages')

import numpy as np
import pandas as pd

import matplotlib
# Matplotlib renderers (there is an eponymous backend for each;
# these are non-interactive backends, capable of writing to a file):
# https://matplotlib.org/stable/users/explain/backends.html
# use Cario or AGG for png files
matplotlib.use('AGG')
import matplotlib.pyplot as plt
from matplotlib.widgets import Cursor
import matplotlib.dates as mdates

# mplfinance -
# matplotlib utilities for the visualization,
# and visual analysis, of financial data
# most common usage =======================
#     mpf.plot(data)
# where data is a Pandas DataFrame object
#
# containing Open, High, Low and Close data, with a Pandas DatetimeIndex.
import mplfinance as mpf
import mplcursors

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
    #print('in getWeeklyExcelSummary')

    # Get saved data Summary of companies
    companyEarningsWeek = startday + '/'
    companyListFile = 'SummaryWeekOf-' + startday + excelSuffix
    theFilePath = theBaseCompaniesDirectory + companyEarningsWeek + companyListFile
    # earningWeekDir = Path(theFilePath)
    #TODo Complete next
    # Complete the loop to get the theStock and then pass to getWeeklyStockTabSummary
    #updated to use mpl 12/31/21
    return getWeeklyStockTabSummary_mpl(theFilePath, theStock)

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
    earnings1DayMove_np = excelPastEarningsDateDF.EDFwd1DayClosePercentDelta.values*100
    earnings4DayMove_np = excelPastEarningsDateDF.EDFwd4DayClosePercentDelta.values*100

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

def plotEarnings(theCandleStickData, earningsMdate_np, earnings1DayMove_np, earnings4DayMove_np, earningsDayEPS, startday, theStock):

    # Set date formatter
    locator = mdates.AutoDateLocator()
    formatter = mdates.ConciseDateFormatter(locator)
    formatter.formats = ["%b-%d-%Y"]

    # Set colors and labels - Earnings Move ----------------
    color1DayStockMove = 'navy'
    color4DayStockMove = 'maroon'
    xLabel = 'Earnings Dates'
    xLabelColor = 'slategray'
    yLabelStockDeltaColor = color1DayStockMove
    yLabel1DayStockMove = 'Stock % Delta @ 1 Day Close Price'
    yLabel4DayStockMove = 'Stock % Delta @ 4 Day Close Price'
    yLabelStockDeltaTitle = 'Stock % Delta'
    ax1LegendLabel1Day = "1-Day % Move"
    ax1LegendLabel4Day = "4-Day % Move"
    zeroPointLabel = '@ $0.0 Move'

    # set title ----------------
    theTitle = theStock + '  -- 1-Day VS 4-Days Past Earnings $ Delta & EPS Estimate/Reported/Suprise'

    # Set colors and labels - EPS Move ----------------
    colorReportedEPS = 'forestgreen'
    colorEstimatedEPS = 'dodgerblue'
    colorSupriseEPS = "crimson"
    colorLabel = 'green'
    #'EPS_Estimate','Reported_EPS','Surprise(%) ----------------
    ax2LegendReportedEPS  = "Reported EPS"
    ax2LegendEstimatedEPS = "Estimated EPS"
    ax2LegendSupriseEPS   = "Surprise(%)"

    # setup plotting ----------------------------
    # single Plot for Earnings price moves // Main Plot
    fig, earningsMovePlt = plt.subplots(figsize=(15, 6))
    # instantiate a second axes that shares the same x-axis
    # Setup Plot for a second axes that shares the same x-axis for EPS
    earningsEpsPlt = earningsMovePlt.twinx()
    # Setup Plot for a third axes that shares the same x-axis for earning surprise
    earningsEpsSuprisePlt = earningsMovePlt.twinx()

#=========================================================================================

    # Offset the right spine of Suprise ---------------------------
    # The ticks and label have already been
    # placed on the right by twinx above.
    # needs double parens to work -> (("axes", 1.06))
    earningsEpsSuprisePlt.spines["right"].set_position(("axes", 1.06))
    # Having been created by twinx, earningsMovePlt has its frame off, so the line of its
    # detached spine is invisible.  First, activate the frame but make the patch
    # and spines invisible.
    make_patch_spines_invisible(earningsEpsSuprisePlt)
    # Second, show the right spine.
    earningsEpsSuprisePlt.spines["right"].set_visible(True)

    # set titles/labels/ticks ----------------------
    earningsMovePlt.set_title(theTitle)
    # Set labels ----------------------
    earningsMovePlt.set_xlabel(xLabel, color=xLabelColor)
    earningsMovePlt.set_ylabel(yLabelStockDeltaTitle, color=yLabelStockDeltaColor)
    earningsEpsPlt.set_ylabel('EPS', color=colorLabel)
    earningsEpsSuprisePlt.set_ylabel('EPS Suprise %', color=colorSupriseEPS)
    # Set tick ----------------------
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

    #plt.grid(color=colorSupriseEPS) # grid not needed at this point

    # plot 1Day and 4Day move
    label1Day = earningsMovePlt.plot(earningsMdate_np, earnings1DayMove_np, color=color1DayStockMove,
             label=ax1LegendLabel1Day, linestyle='--', marker='o', zorder=1)
    label4Day = earningsMovePlt.plot(earningsMdate_np, earnings4DayMove_np, color=color4DayStockMove,
             label=ax1LegendLabel4Day, linestyle='-', marker='o', zorder=1)
    # =============================================================================================

    # find plot high/low boundary limits to center the 0 yAxis in the figure
    aDayMinRT = np.round(np.nanmin(earningsDayEPS.Reported_EPS), 2)
    aDayMaxRT = np.round(np.nanmax(earningsDayEPS.Reported_EPS), 2)
    aDayMinSup = np.round(np.nanmin(earningsDayEPS['Surprise(%)']), 2)
    aDayMaxSup = np.round(np.nanmax(earningsDayEPS['Surprise(%)']), 2)
    aDayMinESP = np.round(np.nanmin(earningsDayEPS.EPS_Estimate), 2)
    aDayMaxESP = np.round(np.nanmax(earningsDayEPS.EPS_Estimate), 2)

    # print("aDayMinRT: ", aDayMinRT, 'aDayMaxRT: ', aDayMaxRT)
    # print("aDayMinESP: ", aDayMinESP, "aDayMaxESP: ", aDayMaxESP)
    # print("aDayMinSup: ", aDayMinSup, 'aDayMaxSup: ', aDayMaxSup)
    # earningsMovePlt.set_ylim(bottom=ylimBottom, top=ylimTop, auto=True)

    #After plotting the data find the maximum absolute value between the min and max axis values.
    # Then set the min and max limits of the axis to the negative and positive (respectively) of that value.
    yabs_maxEPSPlt = max(abs(aDayMinESP),abs(aDayMaxESP),abs(aDayMinRT),abs(aDayMaxRT))
    earningsEpsPlt.set_ylim(ymin=-yabs_maxEPSPlt, ymax=yabs_maxEPSPlt)

    yabs_maxMoveSupr = max(abs(aDayMinSup),abs(aDayMaxSup))
    earningsEpsSuprisePlt.set_ylim(ymin=-yabs_maxMoveSupr, ymax=yabs_maxMoveSupr)

    yabs_maxMovePlt = abs(max(earningsMovePlt.get_ylim(), key=abs))
    earningsMovePlt.set_ylim(ymin=-yabs_maxMovePlt, ymax=yabs_maxMovePlt)
    # print("yabs_maxMoveSupr:  ", earningsEpsSuprisePlt.get_ylim(),'   ', yabs_maxMoveSupr)

    # Add dotted line for $0 - Price move ----------------------
    horzLine = earningsMovePlt.axhline(y=0, color='navy', linestyle=':', label=zeroPointLabel, zorder=1)

    xBarRepEPS = earningsEpsPlt.bar(earningsMdate_np+6, earningsDayEPS.Reported_EPS, width=4, label=ax2LegendReportedEPS, color=colorReportedEPS, alpha=0.5)
    xBarEstEPS = earningsEpsPlt.bar(earningsMdate_np-1, earningsDayEPS.EPS_Estimate, width=4, label=ax2LegendEstimatedEPS, color=colorEstimatedEPS, alpha=0.5)
    xBarSupEPS = earningsEpsSuprisePlt.bar(earningsMdate_np+12, earningsDayEPS['Surprise(%)'], 4, label=ax2LegendSupriseEPS, color=colorSupriseEPS, alpha=0.5)

    lines = [label1Day[0],label4Day[0], horzLine, xBarEstEPS[0], xBarRepEPS[0], xBarSupEPS[0] ]
    lineLabel = [label1Day[0]._label, label4Day[0]._label,horzLine._label,  xBarEstEPS._label, xBarRepEPS._label, xBarSupEPS._label]
    # set legend placement - lower left - mrk 12/21/21
    earningsMovePlt.legend(lines, lineLabel,bbox_to_anchor=(0.02, 0.04))

    #cursor = Cursor(earningsMovePlt, useblit=True, color='red', linewidth=2) #, horizOn=True, vertOn=True, color='green')

    companyEarningsWeek =  startday  + '/rawData/'

    plotThis = theBaseCompaniesDirectory +  companyEarningsWeek + theStock + '.png'
    plt.savefig(plotThis)
    plt.close(fig)

def getWeeklyStockTabSummary_mpl(theFilePath, theSymbol):

    # Get theSymbol excel TAB and put in DF
    excelEarningsDateDF = pd.read_excel(theFilePath, theSymbol)

    # From theSymbol excel TAB separate out the current earnings line
    # from the past earning lines from Excel
    excelCurrentEarningsDateDF = excelEarningsDateDF.iloc[0:1, ]
    excelPastEarningsDateDF = excelEarningsDateDF.iloc[2:, ]

    # pull out the headers then save the remaining Past Earnings DF
    headers = excelPastEarningsDateDF.iloc[0]
    # add the headers to DF
    excelPastEarningsDateDF = pd.DataFrame(excelPastEarningsDateDF.values[1:], columns=headers)

    # reindex new DF
    excelPastEarningsDateDF.reindex

    # create to np array to display in mpl!!!!
    # Past earnings
    # earningsMdate_np = excelPastEarningsDateDF.Earnings_Date.values
    # earnings1DayMove_np = excelPastEarningsDateDF.EDFwd1DayClosePercentDelta.values*100
    # earnings4DayMove_np = excelPastEarningsDateDF.EDFwd4DayClosePercentDelta.values*100

    #need to set up index with Datetime
    earningsDay =  excelPastEarningsDateDF[['Earnings_Date','Open','High','Low', 'Close',
                                                        'Volume','EPS_Estimate','Reported_EPS',
                                                        'Surprise(%)','EDFwd1DayClosePercentDelta',
                                                         'EDFwd4DayClosePercentDelta']]
    earningsDay['EDFwd1DayClosePercentDelta'] \
        = earningsDay['EDFwd1DayClosePercentDelta'].map(lambda a: round((a*100),2))
    earningsDay['EDFwd4DayClosePercentDelta'] \
        = earningsDay['EDFwd4DayClosePercentDelta'].map(lambda a: round((a*100),2))
    # Get EPS data
    # earningsDayEPS =  excelPastEarningsDateDF[['Earnings_Date','EPS_Estimate','Reported_EPS','Surprise(%)']]
    #
    # earnings1DayCandlestick.set_index(pd.DatetimeIndex(earnings1DayCandlestick['Earnings_Date']))
    # earningsDayEPS.set_index(pd.DatetimeIndex(earningsDayEPS['Earnings_Date']))
    #
    # # Convert date string to a datenum using dateutil.parser.parse().
    # earningsMdate_np = mdates.datestr2num(earningsMdate_np)  # np.core.defchararray.rstrip(earningsDate_np, 10))
    #
    # returnList = [earnings1DayMove_np, earnings4DayMove_np, earningsMdate_np, earnings1DayCandlestick, earningsDayEPS]

    return earningsDay


def plotEarnings_mpl(theCandleStickData, pngPlotFileLocation, aStock, earningDayList, outDays):


    theTitle = aStock + '  -- 1-Day VS 4-Days Past Earnings $ Delta & EPS Estimate/Reported/Suprise'

    # setup the plot
    plotEPS = [ mpf.make_addplot(theCandleStickData[['EPS_Estimate']], type='bar', color= 'r', panel=2),
                mpf.make_addplot(theCandleStickData[['Reported_EPS']], type='bar', color= 'g', panel=2),
                mpf.make_addplot(theCandleStickData[['Surprise(%)']],  type='bar', color= 'b', panel=2)]

    mpf.plot(theCandleStickData,vlines=dict(vlines=earningDayList, colors=('r')))

    mpf.plot(theCandleStickData, volume=True, type='candle', style='charles', title=theTitle,
             addplot=plotEPS, figsize=(20, 10), savefig=pngPlotFileLocation)\
        # ,
        #      vlines=dict(vlines=outDays, colors=('c','g', 'c'), linewidths=1))


