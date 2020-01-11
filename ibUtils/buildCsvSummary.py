import sys

sys.path.append('/home/michael/jupyter/local-packages')

import pandas as pd
import numpy as np

# Save the data
from pathlib import Path

theBaseCompaniesDirectory = '/home/michael/jupyter/earningDateData/Companies/'
csvSuffix = '.csv'


# create diary
# ============================================================================
def saveCsvSummary(yahooEarningsOfInterestDF, allYahooEarningsForWeekDF, startday):
    """
    This will save the data as CSV from the Yahoo Earnings Page scrape
    1) yahooEarningsOfInterestDF - Companies w/ liquidity defined as Open Option interest >6000 or so
    2) allYahooEarningsForWeekDF - all the companies that have earnings calls this week

    Parameters
    ----------
    yahooEarningsOfInterestDF : Companies w/ liquididty defined as Open Option interest >6000 or so
    allYahooEarningsForWeekDF : all the companies that have earnings calls this week
    startday : beginning of week

    Returns - nothing
    -------

    """

    # build the new directory path
    companyEarningsWeekDir = theBaseCompaniesDirectory + startday + '/'
    # make the directory if it does not exist / .mkdir does not return anything
    Path(companyEarningsWeekDir).mkdir(parents=True, exist_ok=True)

    # create file names as stings
    # All = all the earnings this week
    companyListFileAll = 'AllEarningsfromWeekOf-' + startday + csvSuffix
    # Interest = the companies with liquidity
    companyListFileInterest = 'EarningOfInterestforweekOf-' + startday + csvSuffix

    allPath = Path(companyEarningsWeekDir + companyListFileAll)
    interestPath = Path(companyEarningsWeekDir + companyListFileInterest)

    yahooEarningsOfInterestDF.to_csv(interestPath)
    allYahooEarningsForWeekDF.to_csv(allPath)

    return

#============================================================================
def createWeeklySummary(startday):
    print('in createWeeklySummary')
    # Get saved data
    companyEarningsWeek = startday + '/'
    companyListFile = 'EarningOfInterestforweekOf-' + startday + csvSuffix
    x = theBaseCompaniesDirectory + companyEarningsWeek
    earningWeekDir = Path(x)

    yahooEarningsDF = pd.read_csv(earningWeekDir / companyListFile, index_col=0)

    yahooEarningsDF = getVolAndUpdateMoveDelta(yahooEarningsDF, earningWeekDir)

    # Save Week Summary
    companySummaryListFile = 'SummaryOfWeek-' + startday + csvSuffix

    outCsvSummaryFile = theBaseCompaniesDirectory + companyEarningsWeek + companySummaryListFile
    yahooEarningsDF.to_csv(outCsvSummaryFile)

    return yahooEarningsDF


def getVolAndUpdateMoveDelta(yahooEarningsDF, earningWeekDir):
    print('in createWeekSummary')
    # Get % IV Delta
    yahooEarningsDF['IV_Delta'] = yahooEarningsDF.impliedVolatility - yahooEarningsDF.histVolatility
    yahooEarningsDF['IV_Delta'] = yahooEarningsDF['IV_Delta'].astype(float).map("{:.1%}".format)

    # For "Earnings Call Time" column remove all but "before" or "after"
    yahooEarningsDF['Earnings Call Time'] = yahooEarningsDF['Earnings Call Time'].str[:5]
    yahooEarningsDF.rename(columns={'Earnings Call Time': 'Time'}, inplace=True)

    yahooEarningsDF.histVolatility = yahooEarningsDF.histVolatility.astype(float).map("{:.1%}".format)
    yahooEarningsDF.impliedVolatility = yahooEarningsDF.impliedVolatility.astype(float).map("{:.1%}".format)

    return updateDiary(yahooEarningsDF, earningWeekDir) #returns updated yahooEarningsDF


def updateDiary(yahooEarningsDF, earningWeekDir):
    print('in updateDiary')

    maxFwd4PercentDelta = []
    minFwd4PercentDelta = []
    maxFwd4PercentDeltaABS = []
    
    maxFwd1PercentDelta = []
    minFwd1PercentDelta = []
    maxFwd1PercentDeltaABS = []

    maxFwd1PriceDelta = []
    minFwd1PriceDelta = []
    maxFwd1PriceDeltaABS = []
    
    maxFwd4PriceDelta = []
    minFwd4PriceDelta = []
    maxFwd4PriceDeltaABS = []

    stdFwd4 = []
    sdtFwd1 = []

    varFwd4 = []
    varFwd1 = []

    meanFwd4 = []
    meanFwd1 = []

    medianFwd4 = []
    medianFwd1 = []

    # modeFwd4 = []
    # modeFwd1 = []

    for row in yahooEarningsDF.itertuples():
        aCompanyFile = row.Symbol + csvSuffix
        filePath = earningWeekDir / aCompanyFile
        print(filePath)
        ckForFile = Path(filePath)
        if ckForFile.is_file():
            # get CSV file with data
            anEarningWeeksCompany = pd.read_csv(earningWeekDir / aCompanyFile, index_col=0)
            # Calculate percent Delta for 4 Day movement
            maxFwd4PercentDelta.append(anEarningWeeksCompany['EDFwd4DayClosePercentDelta'].max())
            minFwd4PercentDelta.append(anEarningWeeksCompany['EDFwd4DayClosePercentDelta'].min())
            maxFwd4PercentDeltaABS.append(max(abs(anEarningWeeksCompany['EDFwd4DayClosePercentDelta'].min()),
                                        anEarningWeeksCompany['EDFwd4DayClosePercentDelta'].max()))

            # Calculate price Delta for 4 Day movement
            maxFwd4PriceDelta.append(anEarningWeeksCompany['EDDiffFwd4Close'].max())
            minFwd4PriceDelta.append(anEarningWeeksCompany['EDDiffFwd4Close'].min())
            maxFwd4PriceDeltaABS.append(max(abs(anEarningWeeksCompany['EDDiffFwd4Close'].min()),
                                        anEarningWeeksCompany['EDDiffFwd4Close'].max()))

            # Calculate percent Delta for 1 Day movement
            maxFwd1PercentDelta.append(anEarningWeeksCompany['EDFwd1DayClosePercentDelta'].max())
            minFwd1PercentDelta.append(anEarningWeeksCompany['EDFwd1DayClosePercentDelta'].min())
            maxFwd1PercentDeltaABS.append(max(abs(anEarningWeeksCompany['EDFwd1DayClosePercentDelta'].min()),
                                        anEarningWeeksCompany['EDFwd1DayClosePercentDelta'].max()))

            # Calculate price Delta for 1 Day movement
            maxFwd1PriceDelta.append(anEarningWeeksCompany['EDDiffFwd1Close'].max())
            minFwd1PriceDelta.append(anEarningWeeksCompany['EDDiffFwd1Close'].min())
            maxFwd1PriceDeltaABS.append(max(abs(anEarningWeeksCompany['EDDiffFwd1Close'].min()),
                                        anEarningWeeksCompany['EDDiffFwd1Close'].max()))

            stdFwd4.append(anEarningWeeksCompany['EDFwd4DayClosePercentDelta'].std())
            sdtFwd1.append(anEarningWeeksCompany['EDFwd1DayClosePercentDelta'].std())

            varFwd4.append(anEarningWeeksCompany['EDFwd4DayClosePercentDelta'].var())
            varFwd1.append(anEarningWeeksCompany['EDFwd1DayClosePercentDelta'].var())

            meanFwd4.append(anEarningWeeksCompany['EDFwd4DayClosePercentDelta'].mean())
            meanFwd1.append(anEarningWeeksCompany['EDFwd1DayClosePercentDelta'].mean())

            medianFwd4.append(anEarningWeeksCompany['EDFwd4DayClosePercentDelta'].median())
            medianFwd1.append(anEarningWeeksCompany['EDFwd1DayClosePercentDelta'].median())

            # modeFwd4.append(anEarningWeeksCompany['EDFwd4DayClosePercentDelta'].mode())
            # modeFwd1.append(anEarningWeeksCompany['EDFwd1DayClosePercentDelta'].mode())


        else: # no data add not a number / nan
            maxFwd4PercentDelta.append(np.nan)
            minFwd4PercentDelta.append(np.nan)
            maxFwd4PercentDeltaABS.append(np.nan)

            maxFwd1PercentDelta.append(np.nan)
            minFwd1PercentDelta.append(np.nan)
            maxFwd1PercentDeltaABS.append(np.nan)

            maxFwd1PriceDelta.append(np.nan)
            minFwd1PriceDelta.append(np.nan)
            maxFwd1PriceDeltaABS.append(np.nan)

            maxFwd4PriceDelta.append(np.nan)
            minFwd4PriceDelta.append(np.nan)
            maxFwd4PriceDeltaABS.append(np.nan)

            stdFwd4.append(np.nan)
            sdtFwd1.append(np.nan)

            stdFwd4.append(np.nan)
            sdtFwd1.append(np.nan)

            varFwd4.append(np.nan)
            varFwd1.append(np.nan)

            meanFwd4.append(np.nan)
            meanFwd1.append(np.nan)

            medianFwd4.append(np.nan)
            medianFwd1.append(np.nan)

            # modeFwd4.append(np.nan)
            # modeFwd1.append(np.nan)


    yahooEarningsDF['maxFwd4PercentDelta'] = maxFwd4PercentDelta
    yahooEarningsDF['minFwd4PercentDelta'] = minFwd4PercentDelta
    yahooEarningsDF['maxFwd4PercentDeltaABS'] = maxFwd4PercentDeltaABS

    yahooEarningsDF['maxFwd1PercentDelta'] = maxFwd1PercentDelta
    yahooEarningsDF['minFwd1PercentDelta'] = minFwd1PercentDelta
    yahooEarningsDF['maxFwd1PercentDeltaABS'] = maxFwd1PercentDeltaABS

    yahooEarningsDF['maxFwd1PriceDelta'] = maxFwd1PriceDelta
    yahooEarningsDF['minFwd1PriceDelta'] = minFwd1PriceDelta
    yahooEarningsDF['maxFwd1PriceDeltaABS'] = maxFwd1PriceDeltaABS

    yahooEarningsDF['maxFwd4PriceDelta'] = maxFwd4PriceDelta
    yahooEarningsDF['minFwd4PriceDelta'] = minFwd4PriceDelta
    yahooEarningsDF['maxFwd4PriceDeltaABS'] = maxFwd4PriceDeltaABS

    yahooEarningsDF['stdFwd4%'] = stdFwd4
    yahooEarningsDF['sdtFwd1%'] = sdtFwd1

    yahooEarningsDF['varFwd4%'] = varFwd4
    yahooEarningsDF['varFwd1%'] = varFwd1

    yahooEarningsDF['meanFwd4%'] = meanFwd4
    yahooEarningsDF['meanFwd1%'] = meanFwd1

    yahooEarningsDF['medianFwd4%'] = medianFwd4
    yahooEarningsDF['medianFwd1%'] = medianFwd1

    # yahooEarningsDF['modeFwd4%'] = modeFwd4
    # yahooEarningsDF['modeFwd1%'] = modeFwd1

    yahooEarningsDF = cleanUpFormats(yahooEarningsDF)

    return yahooEarningsDF


def cleanUpFormats(yahooEarningsDF):

    # yahooEarningsDF['Max%Delta'] = yahooEarningsDF['Max%Delta'].map("{:.2%}".format)
    # yahooEarningsDF['Min%Delta'] = yahooEarningsDF['Min%Delta'].map("{:.2%}".format)
    # yahooEarningsDF['Max%Move'] = yahooEarningsDF['Max%Move'].map("{:.2%}".format)
    # yahooEarningsDF['Max%$MoveOnClose'] = yahooEarningsDF['Max%$MoveOnClose'].astype(float).map("${:.2f}".format)
    #
    # yahooEarningsDF['Max$MoveCl'] = yahooEarningsDF['Max$MoveCl'].astype(float).map("${:.2f}".format)
    # yahooEarningsDF['Min$MoveCl'] = yahooEarningsDF['Min$MoveCl'].astype(float).map("${:.2f}".format)

    yahooEarningsDF['maxFwd4PercentDelta']    = yahooEarningsDF['maxFwd4PercentDelta'].map("{:.2%}".format)
    yahooEarningsDF['minFwd4PercentDelta']    = yahooEarningsDF['minFwd4PercentDelta'].map("{:.2%}".format)
    yahooEarningsDF['maxFwd4PercentDeltaABS'] = yahooEarningsDF['maxFwd4PercentDeltaABS'].map("{:.2%}".format)

    yahooEarningsDF['maxFwd1PercentDelta']    = yahooEarningsDF['maxFwd1PercentDelta'].map("{:.2%}".format)
    yahooEarningsDF['minFwd1PercentDelta']    = yahooEarningsDF['minFwd1PercentDelta'].map("{:.2%}".format)
    yahooEarningsDF['maxFwd1PercentDeltaABS'] = yahooEarningsDF['maxFwd1PercentDeltaABS'].map("{:.2%}".format)

    yahooEarningsDF['maxFwd1PriceDelta']    = yahooEarningsDF['maxFwd1PriceDelta'].astype(float).map("${:.2f}".format)
    yahooEarningsDF['minFwd1PriceDelta']    = yahooEarningsDF['minFwd1PriceDelta'].astype(float).map("${:.2f}".format)
    yahooEarningsDF['maxFwd1PriceDeltaABS'] = yahooEarningsDF['maxFwd1PriceDeltaABS'].astype(float).map("${:.2f}".format)

    yahooEarningsDF['maxFwd4PriceDelta']    = yahooEarningsDF['maxFwd4PriceDelta'].astype(float).map("${:.2f}".format)
    yahooEarningsDF['minFwd4PriceDelta']    = yahooEarningsDF['minFwd4PriceDelta'].astype(float).map("${:.2f}".format)
    yahooEarningsDF['maxFwd4PriceDeltaABS'] = yahooEarningsDF['maxFwd4PriceDeltaABS'].astype(float).map("${:.2f}".format)

    yahooEarningsDF['stdFwd4%']    = yahooEarningsDF['stdFwd4%'].map("{:.2%}".format)
    yahooEarningsDF['sdtFwd1%']    = yahooEarningsDF['sdtFwd1%'].map("{:.2%}".format)

    yahooEarningsDF['varFwd4%']    = yahooEarningsDF['varFwd4%'].map("{:.2%}".format)
    yahooEarningsDF['varFwd1%']    = yahooEarningsDF['varFwd1%'].map("{:.2%}".format)

    yahooEarningsDF['meanFwd4%']   = yahooEarningsDF['meanFwd4%'].map("{:.2%}".format)
    yahooEarningsDF['meanFwd1%']   = yahooEarningsDF['meanFwd1%'].map("{:.2%}".format)

    yahooEarningsDF['medianFwd4%'] = yahooEarningsDF['medianFwd4%'].map("{:.2%}".format)
    yahooEarningsDF['medianFwd1%'] = yahooEarningsDF['medianFwd1%'].map("{:.2%}".format)

    # yahooEarningsDF['modeFwd4%']   = yahooEarningsDF['modeFwd4%'].map("{:.2%}".format)
    # yahooEarningsDF['modeFwd1%']   = yahooEarningsDF['modeFwd1%'].map("{:.2%}".format)

    # Shorten some Column names and format the column
    yahooEarningsDF.rename(columns={'PutFridayOpenInterest': 'PutOpenIntst'}, inplace=True)
    yahooEarningsDF.rename(columns={'CallFridayOpenInterest': 'CallOpenIntst'}, inplace=True)

    yahooEarningsDF['PutOpenIntst'] = yahooEarningsDF['PutOpenIntst'].astype(int)
    yahooEarningsDF['CallOpenIntst'] = yahooEarningsDF['CallOpenIntst'].astype(int)

    yahooEarningsDF.rename(columns={'impliedVolatility': 'impVol'}, inplace=True)
    yahooEarningsDF.rename(columns={'histVolatility': 'histVol'}, inplace=True)

    yahooEarningsDF.rename(columns={'Expected_Range': 'Exp$Range'}, inplace=True)
    yahooEarningsDF['Exp$Range'] = yahooEarningsDF['Exp$Range'].astype(float).map("${:.2f}".format)

    yahooEarningsDF['Close'] = yahooEarningsDF['Close'].astype(float).map("${:.2f}".format)
    yahooEarningsDF['Last'] = yahooEarningsDF['Last'].astype(float).map("${:.2f}".format)

    # rearrange columns
    yahooEarningsDF = yahooEarningsDF[['Symbol', 'Company', 'Earnings_Date', 'Time', 'Volume',
                                       'High', 'Low', 'Last', 'Open', 'Close', 'Last', 'histVol',
                                       'impVol', 'IV_Delta', 'Option_Volume', 'PutOpenIntst',
                                       'CallOpenIntst', 'Exp$Range', 'maxFwd4PercentDelta', 'minFwd4PercentDelta',
                                       'maxFwd4PercentDeltaABS', 'maxFwd1PercentDeltaABS', 'maxFwd1PercentDelta',
                                       'minFwd1PercentDelta', 'maxFwd1PriceDelta', 'minFwd1PriceDelta',
                                       'maxFwd1PriceDeltaABS', 'maxFwd4PriceDeltaABS', 'maxFwd4PriceDelta',
                                       'minFwd4PriceDelta', 'stdFwd4%', 'sdtFwd1%', 'varFwd4%', 'varFwd1%',
                                       'meanFwd4%', 'meanFwd1%', 'medianFwd4%', 'medianFwd1%']]

    return yahooEarningsDF