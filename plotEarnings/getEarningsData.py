import sys

from localUtilities.ibUtils.buildCompanyFundamentalFromBarChart import plotEarningsMove

sys.path.append('/home/michael/jupyter/local-packages')

import numpy as np
import pandas as pd

import matplotlib
# Matplotlib renderers (there is an eponymous backend for each;
# these are non-interactive backends, capable of writing to a file):
# https://matplotlib.org/stable/users/explain/backends.html
# use Cario or AGG for png files
#
import matplotlib.pyplot as plt
from matplotlib.widgets import Cursor
import matplotlib.dates as mdates

#https://github.com/highfestiva/finplot
# todo: add import finplot as fplt - get interactive graphing

# mplfinance -
# matplotlib utilities for the visualization,
# and visual analysis, of financial data
# most common usage =======================
#     mpf.plot(data)
# where data is a Pandas DataFrame object
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

def getWeeklyExcelSummary(startday, theStock, mpl):

    # Get saved data Summary of companies
    companyEarningsWeek = startday + '/'
    companyListFile = 'SummaryWeekOf-' + startday + excelSuffix
    theFilePath = theBaseCompaniesDirectory + companyEarningsWeek + companyListFile
    # earningWeekDir = Path(theFilePath)
    #TODo Complete next
    # Complete the loop to get the theStock and then pass to getWeeklyStockTabSummary
    #updated to use mpl 12/31/21
    if mpl == True:
        x = getWeeklyStockTabSummary_mpl(theFilePath, theStock)
        return x
    else:
        x = getWeeklyStockTabSummary(theFilePath, theStock)
        return x

def getWeeklyStockTabSummary(theFilePath, theSymbol):
    #todo: why is this needed?

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

    #need to set up index with Datetime
    earningsDay =  excelPastEarningsDateDF[['Earnings_Date','Open','High','Low', 'Close',
                                                        'Volume','EPS_Estimate','Reported_EPS',
                                                        'Surprise(%)','EDFwd1DayClosePercentDelta',
                                                         'EDFwd4DayClosePercentDelta']]

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

    returnList = [earnings1DayMove_np, earnings4DayMove_np, earningsMdate_np,
                  earnings1DayCandlestick, earningsDayEPS, earningsDay]

    return returnList

def plotEarnings(earningsMdate_np, earnings1DayMove_np, earnings4DayMove_np, earningsDayEPS,
                 startday, theStock):

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
    fig, earningsMovePlt = plt.subplots(2,1, figsize=(15, 6))
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
    earningsEpsSuprisePlt.spines["left"].set_position(("axes", 1.06))
    # Having been created by twinx, earningsMovePlt has its frame off, so the line of its
    # detached spine is invisible.  First, activate the frame but make the patch
    # and spines invisible.
    make_patch_spines_invisible(earningsEpsSuprisePlt)
    # Second, show the right spine.
    earningsEpsSuprisePlt.spines["left"].set_visible(True)

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

    # lines2, labels2 = earningsEpsPlt.get_legend_handles_labels()
    # # build Legend for 2nd Xaxis
    # lines1, labels1 = earningsMovePlt.get_legend_handles_labels()

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
    #earningsMovePlt.set_ylim(bottom=ylimBottom, top=ylimTop, auto=True)

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

    xBarRepEPS = earningsEpsPlt.bar(earningsMdate_np+6, earningsDayEPS.Reported_EPS, width=4,
                                    label=ax2LegendReportedEPS, color=colorReportedEPS) #, alpha=0.5)
    xBarEstEPS = earningsEpsPlt.bar(earningsMdate_np-1, earningsDayEPS.EPS_Estimate, width=4,
                                    label=ax2LegendEstimatedEPS, color=colorEstimatedEPS) #, alpha=0.5)
    xBarSupEPS = earningsEpsSuprisePlt.bar(earningsMdate_np+12, earningsDayEPS['Surprise(%)'], width=4,
                                           label=ax2LegendSupriseEPS, color=colorSupriseEPS) #, alpha=0.5)

    lines = [label1Day[0],label4Day[0], horzLine, xBarEstEPS[0], xBarRepEPS[0], xBarSupEPS[0] ]
    lineLabel = [label1Day[0]._label, label4Day[0]._label,horzLine._label,  xBarEstEPS._label, xBarRepEPS._label, xBarSupEPS._label]
    # set legend placement - lower left - mrk 12/21/21
    earningsMovePlt.legend(lines, lineLabel,bbox_to_anchor=(0.02, 0.04))

    #cursor = Cursor(earningsMovePlt, useblit=True, color='red', linewidth=2) #, horizOn=True, vertOn=True, color='green')

    companyEarningsWeek =  startday  + '/rawData/'

    plotThisPNG = theBaseCompaniesDirectory +  companyEarningsWeek + theStock + '.png'
    plt.savefig(plotThisPNG)
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


def XXXXplotEarnings_mpl(theCandleStickData, pngPlotFileLocation, theStock,
                     startDay, earningDayList, outDays):
    #https://github.com/matplotlib/mplfinance/blob/master/examples/panels.ipynb

    #=================================================================================
    # Set colors and labels - Earnings Move ----------------
    color1DayStockMove = 'navy'
    color4DayStockMove = 'maroon'
    xLabel = 'Earnings Dates'
    xLabelColor = 'slategray'
    yLabelColor = 'indigo'
    yLabelStockDeltaColor = color1DayStockMove
    yLabel1DayStockMove = 'Stock % Delta @ 1 Day Close Price'
    yLabel4DayStockMove = 'Stock % Delta @ 4 Day Close Price'
    yLabelStockDeltaTitle = 'Stock % Delta'
    ax1LegendLabel1Day = "1-Day % Move"
    ax1LegendLabel4Day = "4-Day % Move"
    zeroPointLabel = '@ $0.0 Move'

    # set title ----------------
    theMplTitle = theStock + '  -- Stock at Earnings @ the Red dotted Line'
    theMoveTitle = theStock + '  -- 1-Day VS 4-Days Past Earnings $ Delta'
    theEPSTitle = theStock + '  -- EPS Estimate/Reported/Surprise'

    # Set colors and labels - EPS Move ----------------
    colorReportedEPS = 'forestgreen'
    colorEstimatedEPS = 'dodgerblue'
    colorSupriseEPS = "crimson"
    colorLabel = 'green'
    # 'EPS_Estimate','Reported_EPS','Surprise(%) ----------------
    ax2LegendReportedEPS = "Reported EPS"
    ax2LegendEstimatedEPS = "Estimated EPS"
    ax2LegendSupriseEPS = "Surprise(%)"

    #=================================================================================
    #setup chart stuff
    bar_width = 0.4
    theEDaysData = theCandleStickData[~theCandleStickData['Earnings_Date'].isna()]
    # =================================================================================
    # setup plotting ----------------------------
    # fig = mpf.plot(theCandleStickData, volume=True, type='candle', style='charles', title=theMplTitle,
    #                figsize=(15, 6), returnfig=True,  # addplot=plotEPS,
    #                vlines=dict(vlines=earningDayList, linestyle='dotted', colors='red', linewidths=.8),
    #                savefig=pngPlotFileLocation)

    # single Plot for Earnings price moves // Main Plot
    fig = mpf.figure( figsize=(7, 8))
    candleStickAx = fig.add_subplot(4,1,1)
    volumeAx      = fig.add_subplot(4,1,2)
    earningsAx    = fig.add_subplot(4,1,3)
    # =========================================================================================
    # set axes[1] titles/labels/ticks - Earnings Move ----------------------
    earningsAx.set_title(theMoveTitle)
    earningsAx.set_xlabel(xLabel, color=xLabelColor)
    earningsAx.set_ylabel(yLabelStockDeltaTitle, color=yLabelStockDeltaColor)
    earningsAx.tick_params(axis='y', labelcolor=yLabelStockDeltaColor)
    earningsAx.tick_params(axis='x', labelcolor=xLabelColor)

    # plot 1Day and 4Day move
    earningMovesDataList = plotEarningsMove(theStock, startDay)
    earningsMdate_np    = earningMovesDataList[0]
    earnings1DayMove_np = earningMovesDataList[1]
    earnings4DayMove_np = earningMovesDataList[2]
    earningsDayEPS      = earningMovesDataList[3]
    theEarningsDatalist = earningMovesDataList[4]

    # plotEarnings = [mpf.make_addplot(theCandleStickData[['EPS_Estimate']], ax=earningsAx, panel=3,
    #                 width=0.5,  type='bar', color= 'r', alpha=.5)]
    # earningsAx.plot(theEarningsDatalist, color=color4DayStockMove,
    #                label=ax1LegendLabel4Day, linestyle='-', marker='o', zorder=1)

    # mpf.plot(theCandleStickData, returnfig=True, #addplot= plotEarnings,
    #          ax=candleStickAx, volume=volumeAx, savefig=pngPlotFileLocation,
    #          vlines=dict(vlines=earningDayList, linestyle='dotted', colors='red', linewidths=.8),
    #          type='candle', style='charles')

    plotEarnings = [mpf.make_addplot(theCandleStickData, ax=candleStickAx,ylabel='OHLC Price'),
                    mpf.make_addplot(theCandleStickData,ax=volumeAx) ]

    mpf.plot(theCandleStickData, ax=candleStickAx, volume=volumeAx, returnfig=True, savefig=pngPlotFileLocation,
             vlines=dict(vlines=earningDayList, linestyle='dotted', colors='red', linewidths=.8),
             title=theMplTitle, figsize=(15, 6), type='candle', style='charles')

    # =========================================================================================
    mpf.show()


def plotEarnings_mpl(theCandleStickData, pngPlotFileLocation, aStock, earningDayList, outDays):
#   ********************************************************
#   plotEarnings_mpl-WorkingWith-MPL-    Jan10-22
#   ********************************************************

    theTitle = aStock + '  -- Stock at Earnings @ Red dotted Line'
    bar_width = 0.4
    theED_Data = theCandleStickData[~theCandleStickData['Earnings_Date'].isna()]

    # After plotting the data find the maximum absolute value between the min and max axis values.
    # Then set the min and max limits of the axis to the negative and positive (respectively)
    # of that value.
    # get the y data Max for ylimit
    yabs_maxEPSPlt, yabs_maxEPSSupr, yabs_DayMoveClose = get_ED_ylim(theED_Data)
    # ylim= where the value must be a len=2 tuple (min,max).
    earningsEpsPltSet_ylim        = (-yabs_maxEPSPlt, yabs_maxEPSPlt)
    earningsEpsSuprisePltSet_ylim = (-yabs_maxEPSSupr, yabs_maxEPSSupr)
    earningsMovePltSet_ylim       = (-yabs_DayMoveClose, yabs_DayMoveClose)

    # Add dotted line for $0 - Price move ----------------------
    # ylim((bottom, top))  # set the ylim to bottom, top
    # matplotlib/mplfinance ---workaround till
    #     Feature Request: HLines on AddPlot #204
    #     https://github.com/matplotlib/mplfinance/issues/204
    # for now need a hline=0
    theEPS0line = [0] * theCandleStickData.shape[0] # hline=0

    # # Configure the axes
    # ax1 = fig.add_subplot(4, 1, (1, 2))
    # ax2 = fig.add_subplot(4, 1, 3, sharex=ax1)
    # ax3 = fig.add_subplot(4, 1, 4, sharex=ax1)


    # set styles
    styleMPF = mpf.make_mpf_style(base_mpf_style = 'charles', edgecolor='grey')

    plotEPS = [ mpf.make_addplot(theCandleStickData[['EPS_Estimate']], ylabel='EPS_Estimate',
                                 width=0.5, type='scatter', color='r', marker='<', panel=2, alpha=.2,
                                 ylim=earningsEpsPltSet_ylim),

                mpf.make_addplot(theCandleStickData[['Reported_EPS']], ylabel='Reported_EPS', y_on_right=False,
                                 width=0.5,  type='scatter', color='g', marker='>', panel=2, alpha=.2,
                                 ylim=earningsEpsPltSet_ylim),

                mpf.make_addplot(theCandleStickData[['Surprise(%)']], ylabel='Surprise(%)',
                                 width=0.5,  type='scatter', color= 'b', marker='D', panel=2, alpha=.2,
                                 ylim=earningsEpsSuprisePltSet_ylim),

                mpf.make_addplot(theEPS0line, linestyle='dotted', panel=2, width=1, color='orange'),
                mpf.make_addplot(theEPS0line, linestyle='dotted', panel=3, width=1, color='orange'),

                mpf.make_addplot(theCandleStickData['EDFwd1DayClosePercentDelta'], ylabel='1Day Fwd Close',
                                 alpha=.5, panel=3, type='scatter',  marker='3', color='pink',
                                 ylim=earningsMovePltSet_ylim),

                mpf.make_addplot(theCandleStickData['EDFwd4DayClosePercentDelta'], ylabel='4Day Fwd Close',
                                 alpha=.5, panel=3, type='scatter',  marker='4',color='y',
                                 ylim=earningsMovePltSet_ylim),
                mpf.make_addplot(theCandleStickData['Volume'], type='bar', panel=1, ylabel='Tweet',
                                 y_on_right=False)]


    fig, axlist = mpf.plot(theCandleStickData, volume=True, type='candle', title=theTitle, style=styleMPF,
                           figsize=(18, 10), addplot=plotEPS, returnfig=True, panel_ratios=(8,3,4,4),
                           vlines=dict(vlines=earningDayList,linestyle='dotted', colors='red', linewidths=.8),
                           savefig=pngPlotFileLocation)

    # axlist[0].xaxis.set_major_formatter(formatter)
    mpf.show()

def plot_Earnings_EPS_DayMove(theCandleStickData, earningsMdate_np, earnings1DayMove_np, earnings4DayMove_np,
                              earningsDayEPS, startday, theStock):

    # Set colors and labels - Earnings Move ----------------
    color1DayStockMove = 'navy'
    color4DayStockMove = 'maroon'
    xLabel = 'Earnings Dates'
    xLabelColor = 'slategray'
    yLabelColor = 'indigo'
    yLabelStockDeltaColor = color1DayStockMove
    yLabel1DayStockMove = 'Stock % Delta @ 1 Day Close Price'
    yLabel4DayStockMove = 'Stock % Delta @ 4 Day Close Price'
    yLabelStockDeltaTitle = 'Stock % Delta'
    ax1LegendLabel1Day = "1-Day % Move"
    ax1LegendLabel4Day = "4-Day % Move"
    zeroPointLabel = '@ $0.0 Move'

    # set title ----------------
    theMoveTitle = theStock + '  -- 1-Day VS 4-Days Past Earnings $ Delta'
    theEPSTitle = theStock + '  -- EPS Estimate/Reported/Surprise'

    # Set colors and labels - EPS Move ------------
    # ----
    colorReportedEPS = 'forestgreen'
    colorEstimatedEPS = 'dodgerblue'
    colorSupriseEPS = "crimson"
    colorLabel = 'green'
    # 'EPS_Estimate','Reported_EPS','Surprise(%) ----------------
    ax2LegendReportedEPS = "Reported EPS"
    ax2LegendEstimatedEPS = "Estimated EPS"
    ax2LegendSupriseEPS = "Surprise(%)"

    # setup plotting ----------------------------
    # single Plot for Earnings price moves // Main Plot
    fig = mpf.figure(theCandleStickData, volume=True, style='yahoo', figsize=(15, 10))
    axCandleStick = fig.add_subplot(4, 1, 1)
    axVolume      = fig.add_subplot(4, 1, 2)
    axEPS         = fig.add_subplot(4, 1, 3)
    axMove        = fig.add_subplot(4, 1, 4)
    # Setup Plot for a another y-axes that shares the same x-axis for earning surprise
    earningsEpsSurprisePlt = axEPS.twinx()
    # =========================================================================================
    # set the spacing between subplots
    plt.subplots_adjust(left=0.1, bottom=0.1, right=0.9,top=0.9,wspace=2,hspace=1)
    # =========================================================================================
    # set titles/labels/ticks - EPS --------------------------------------------
    axEPS.set_title(theEPSTitle)
    axEPS.set_xlabel(xLabel, color=xLabelColor)
    axEPS.set_ylabel('EPS', color=colorLabel)
    axEPS.tick_params(axis='y', labelcolor=colorLabel)

    #make_patch_spines_invisible(earningsEpsSuprisePlt)
    earningsEpsSurprisePlt.set_ylabel('EPS Suprise %', color=colorSupriseEPS)
    earningsEpsSurprisePlt.tick_params(axis='y', labelcolor=colorSupriseEPS)

    # set axes[1] titles/labels/ticks - Earnings Move ----------------------
    axMove.set_title(theMoveTitle)
    axMove.set_xlabel(xLabel, color=xLabelColor)
    axMove.set_ylabel(yLabelStockDeltaTitle, color=yLabelStockDeltaColor)
    axMove.tick_params(axis='y', labelcolor=yLabelStockDeltaColor)
    axMove.tick_params(axis='x', labelcolor=xLabelColor)

    # =============================================================================================
    # find plot high/low boundary limits to center the 0 yAxis in the figure
    # for Surprise EPS
    aDayMinSup = np.round(np.nanmin(earningsDayEPS['Surprise(%)']), 2)
    aDayMaxSup = np.round(np.nanmax(earningsDayEPS['Surprise(%)']), 2)

    # Get Min/Max for EPS
    aDayMinRT = np.round(np.nanmin(earningsDayEPS.Reported_EPS), 2)
    aDayMaxRT = np.round(np.nanmax(earningsDayEPS.Reported_EPS), 2)
    aDayMinESP = np.round(np.nanmin(earningsDayEPS.EPS_Estimate), 2)
    aDayMaxESP = np.round(np.nanmax(earningsDayEPS.EPS_Estimate), 2)

    # # After plotting the data find the maximum absolute value between the min and max axis values.
    # # Then set the min and max limits of the axis to the negative and positive (respectively) of that value.
    yabs_maxMoveSupr = max(abs(aDayMinSup), abs(aDayMaxSup))
    earningsEpsSurprisePlt.set_ylim(ymin=-yabs_maxMoveSupr, ymax=yabs_maxMoveSupr)

    yabs_maxMoveEPS = max(abs(aDayMinRT), abs(aDayMaxRT), abs(aDayMinESP), abs(aDayMaxESP))
    axEPS.set_ylim(ymin=-yabs_maxMoveEPS, ymax=yabs_maxMoveEPS)

    # ========================================================================================

    # # Add dotted line for $0 - Price move ----------------------
    axMove.axhline(y=0, color='pink', linestyle=':', label=zeroPointLabel, zorder=1)
    axEPS.axhline(y=0, color='pink', linestyle=':', label=zeroPointLabel, zorder=1)

    axEPS.bar(earningsMdate_np + 6, earningsDayEPS.Reported_EPS, width=4,
               label=ax2LegendReportedEPS, color=colorReportedEPS, alpha=0.5)
    axEPS.bar(earningsMdate_np - 1, earningsDayEPS['EPS_Estimate'], width=4,
               label=ax2LegendEstimatedEPS, color=colorEstimatedEPS, alpha=0.5)
    axEPS.bar(earningsMdate_np + 12, earningsDayEPS['Surprise(%)'], 4,
                                           label=ax2LegendSupriseEPS, color=colorSupriseEPS, alpha=0.5)

    # ========================================================================================
    # plot 1Day and 4Day move
    axMove.plot(earningsMdate_np, earnings1DayMove_np, color=color1DayStockMove,
                            label=ax1LegendLabel1Day, linestyle='--', marker='o', zorder=1)
    axMove.plot(earningsMdate_np, earnings4DayMove_np, color=color4DayStockMove,
                            label=ax1LegendLabel4Day, linestyle='-', marker='o', zorder=1)
    for xc in zip(earningsMdate_np):
        axMove.axvline(x=xc, color='orange',linestyle='--', lw=1)
        axEPS.axvline(x=xc, color='orange',linestyle='--', lw=1)
    # ========================================================================================
    # Set date formatter
    xtick_locator = mdates.AutoDateLocator()
    xtick_formatter = mdates.ConciseDateFormatter(xtick_locator)
    xtick_formatter.formats = ["%b-%d-%Y"]

    # set xaxis format -------------------------------
    axCandleStick.xaxis.set_major_formatter(mdates.DateFormatter("%b-%d-%Y"))
    axVolume.xaxis.set_major_formatter(mdates.DateFormatter("%b-%d-%Y"))

    # set xTicks to Earnings Day
    axEPS.xaxis.set_major_formatter(mdates.DateFormatter("%b-%d-%Y"))
    axEPS.set_xticks(earningsMdate_np)
    axMove.xaxis.set_major_formatter(mdates.DateFormatter("%b-%d-%Y"))
    axMove.set_xticks(earningsMdate_np)

    # axCandleStick.vlines(earningsDayEPS["Earnings_Date"].tolist(), 0, 1, linestyles='dashed', colors='red')

    print('earningsMdate_np:  \n', earningsMdate_np)

    #print('axCandleStick.axes.Axes.get_xticks():  ', axCandleStick.axes.Axes.get_xticks() )
    # ========================================================================================

    companyEarningsWeek = startday + '/rawData/'
    #mpf.plot(theCandleStickData, ax=axs[3], volume=axs[4])
    plotThisPNG = theBaseCompaniesDirectory + companyEarningsWeek + theStock + '.png'
    aList=earningsDayEPS["Earnings_Date"].tolist()
    mpf.plot(theCandleStickData,ax=axCandleStick,volume=axVolume,xrotation=10,type='candle',
             vlines=dict(vlines=aList,linewidths=(1,2,3)))

    plt.savefig(plotThisPNG)
    plt.close(fig)



def get_ED_ylim(earningsDayEPS):
    # =============================================================================================

    # find plot high/low boundary limits to center the 0 yAxis in the figure
    # for EPS Data
    aDayMinREPS = np.round(np.nanmin(earningsDayEPS.Reported_EPS), 2)
    aDayMaxREPS = np.round(np.nanmax(earningsDayEPS.Reported_EPS), 2)
    aDayMinSup  = np.round(np.nanmin(earningsDayEPS['Surprise(%)']), 2)
    aDayMaxESP  = np.round(np.nanmax(earningsDayEPS.EPS_Estimate), 2)
    # for EPS Surprise
    aDayMaxSup = np.round(np.nanmax(earningsDayEPS['Surprise(%)']), 2)
    aDayMinESP = np.round(np.nanmin(earningsDayEPS.EPS_Estimate), 2)
    #for days 1 & 4 Day Move data
    a1DayMaxClose = np.round(np.nanmax(earningsDayEPS.EDFwd1DayClosePercentDelta), 2)
    a1DayMinClose = np.round(np.nanmin(earningsDayEPS.EDFwd1DayClosePercentDelta), 2)
    a4DayMaxClose = np.round(np.nanmax(earningsDayEPS.EDFwd4DayClosePercentDelta), 2)
    a4DayMinClose = np.round(np.nanmin(earningsDayEPS.EDFwd4DayClosePercentDelta), 2)


    #After plotting the data find the maximum absolute value between the min and max axis values.
    # Plotting EPS ymin/ymax we need all the data from Rreported and Estimated
    # Then set the min and max limits of the axis to the negative and positive (respectively) of that value.
    yabs_maxEPSPlt    = max(abs(aDayMinESP),abs(aDayMaxESP),abs(aDayMaxREPS),abs(aDayMinREPS))
    yabs_maxEPSSupr   = max(abs(aDayMinSup),abs(aDayMaxSup))
    yabs_DayMoveClose = max(abs(a1DayMaxClose), abs(a1DayMinClose),
                            abs(a4DayMaxClose), abs(a4DayMinClose))

    # print('earningsDayEPS 1st and last:  \n\n', earningsDayEPS.iloc[0].Earnings_Date, '\n',
    #       earningsDayEPS.iloc[-1].Earnings_Date, '\n\n' )

    return yabs_maxEPSPlt, yabs_maxEPSSupr, yabs_DayMoveClose