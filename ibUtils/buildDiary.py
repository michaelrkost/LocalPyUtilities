
import sys
sys.path.append('/home/michael/jupyter/local-packages')

import pandas as pd
from localUtilities import dateUtils

import itertools
import datetime

from ib_insync import *

# create diary
#============================================================================
def create(startday):
    # Save the data
    from pathlib import Path
    theDirectory = '/home/michael/jupyter/earningDateData/'
    companySave = 'Companies/' + startday + '/'
    csvSuffix = '.csv'

    companyListFile = 'weekOf-' + startday + csvSuffix
    earningWeekDir = Path(theDirectory + companySave)

    yahooEarningsDF = pd.read_csv(earningWeekDir / companyListFile, index_col=0)

    # Get % IV Delta
    yahooEarningsDF['IV_Delta'] = yahooEarningsDF.impliedVolatility - yahooEarningsDF.histVolatility
    yahooEarningsDF['IV_Delta'] = yahooEarningsDF['IV_Delta'].astype(float).map("{:.2%}".format)

    # For "Earnings Call Time" column remove all but "before" or "after"
    yahooEarningsDF['Earnings Call Time'] = yahooEarningsDF['Earnings Call Time'].str[:5]
    yahooEarningsDF.rename(columns={'Earnings Call Time': 'Time'}, inplace=True)

    yahooEarningsDF.histVolatility = yahooEarningsDF.histVolatility.astype(float).map("{:.2%}".format)
    yahooEarningsDF.impliedVolatility = yahooEarningsDF.impliedVolatility.astype(float).map("{:.2%}".format)

    return updateDiary(yahooEarningsDF, csvSuffix, earningWeekDir)


def updateDiary(yahooEarningsDF, csvSuffix, earningWeekDir):

    maxPercentDelta = []
    minPercentDelta = []
    maxPercentDeltaABS = []

    for row in yahooEarningsDF.itertuples():
        aCompanyFile = row.Symbol + csvSuffix
        anEarningWeeksCompany = pd.read_csv(earningWeekDir / aCompanyFile, index_col=0)
        maxPercentDelta.append(anEarningWeeksCompany['Max%Delta'].max())
        minPercentDelta.append(anEarningWeeksCompany['Min%Delta'].min())
        maxPercentDeltaABS.append(max(abs(anEarningWeeksCompany['Min%Delta'].min()),
                                    anEarningWeeksCompany['Max%Delta'].max()))

    yahooEarningsDF['Max%Delta'] = maxPercentDelta
    yahooEarningsDF['Min%Delta'] = minPercentDelta
    yahooEarningsDF['Max%Move'] = maxPercentDeltaABS

    yahooEarningsDF['Max$Move'] = yahooEarningsDF['Max%Move'] * yahooEarningsDF['close']

    yahooEarningsDF['Max$MoveCl'] = yahooEarningsDF['close'] + yahooEarningsDF['Max$Move']
    yahooEarningsDF['Min$MoveCl'] = yahooEarningsDF['close'] - yahooEarningsDF['Max$Move']


    yahooEarningsDF['Max%Delta'] = yahooEarningsDF['Max%Delta'].map("{:.2%}".format)
    yahooEarningsDF['Min%Delta'] = yahooEarningsDF['Min%Delta'].map("{:.2%}".format)
    yahooEarningsDF['Max%Move'] = yahooEarningsDF['Max%Move'].map("{:.2%}".format)
    yahooEarningsDF['Max$Move'] = yahooEarningsDF['Max$Move'].astype(float).map("${:.2f}".format)
    yahooEarningsDF['Max$MoveCl'] = yahooEarningsDF['Max$MoveCl'].astype(float).map("${:.2f}".format)
    yahooEarningsDF['Min$MoveCl'] = yahooEarningsDF['Min$MoveCl'].astype(float).map("${:.2f}".format)

    # Shorten some Column names and format the column
    yahooEarningsDF.rename(columns={'avOptionVolume': 'OptVolume'}, inplace=True)
    yahooEarningsDF['OptVolume'] = yahooEarningsDF['OptVolume'].astype(int)

    yahooEarningsDF.rename(columns={'impliedVolatility': 'impVol'}, inplace=True)
    yahooEarningsDF.rename(columns={'impliedVolatility': 'impVol'}, inplace=True)

    yahooEarningsDF.rename(columns={'Expected_Range': 'Exp$Range'}, inplace=True)
    yahooEarningsDF['Exp$Range'] = yahooEarningsDF['Exp$Range'].astype(float).map("${:.2f}".format)

    yahooEarningsDF['close'] = yahooEarningsDF['close'].astype(float).map("${:.2f}".format)
    yahooEarningsDF['last'] = yahooEarningsDF['last'].astype(float).map("${:.2f}".format)

    # rearrange columns
    yahooEarningsDF = yahooEarningsDF[['Earnings_Date', 'Symbol', 'Company', 'Time', 'close', 'last',
           'OptVolume', 'histVolatility', 'impVol', 'IV_Delta',
           'Max%Delta', 'Min%Delta', 'Max%Move','Exp$Range',  'Max$Move', 'Max$MoveCl',
           'Min$MoveCl']]


    return yahooEarningsDF

