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
    1) yahooEarningsOfInterestDF - Companies w/ liquidity defined as Open Option interest >500 or so
    2) allYahooEarningsForWeekDF - all the companies that have earnings calls this week

    Parameters
    ----------
    yahooEarningsOfInterestDF : Companies w/ liquidity defined as Open Option interest > 500 or so
    allYahooEarningsForWeekDF : all the companies that have earnings calls this week
    startday : beginning of week

    Returns - nothing
    -------

    """

    # build the new directory path
    companyEarningsWeekDir = theBaseCompaniesDirectory + startday + '/rawData/'
    # make the directory if it does not exist / .mkdir does not return anything
    Path(companyEarningsWeekDir).mkdir(parents=True, exist_ok=True)

    # create file names as stings
    # All = all the earnings this week
    companyListFileAll = 'AllEarningsfromWeekOf-' + startday + csvSuffix
    # Interest = the companies with liquidity
    companyListFileInterest = 'EarningOfInterestforweekOf-' + startday + csvSuffix

    allPath = Path(companyEarningsWeekDir + companyListFileAll)
    interestPath = Path(companyEarningsWeekDir + companyListFileInterest)

    # ***** keep all the data - see if we need the data later in the process **********
    # yahooEarningsOfInterestDF = yahooEarningsOfInterestDF[['Symbol', 'Company', 'Earnings_Date',  'Earnings Call Time', 'High',
    #    'Open', 'Volume', 'Option_Volume', 'Low', 'Close', 'histVolatility',
    #    'impliedVolatility', 'Expected_Range']]

    yahooEarningsOfInterestDF.to_csv(interestPath)
    allYahooEarningsForWeekDF.to_csv(allPath)

    return

#============================================================================
def createWeeklySummary(startday):
    print('in createWeeklySummary')
    # Get saved data
    companyEarningsWeek = startday + '/rawData/'
    companyListFile = 'EarningOfInterestforweekOf-' + startday + csvSuffix
    earningsWeekPath = theBaseCompaniesDirectory + companyEarningsWeek
    earningWeekDir = Path(earningsWeekPath)

    yahooEarningsDF = pd.read_csv(earningWeekDir / companyListFile, index_col=0)

    yahooEarningsDF = getVolAndUpdateMoveDelta(yahooEarningsDF, earningWeekDir)

    # Save Week Summary
    companySummaryListFile = 'SummaryOfWeek-' + startday + csvSuffix
    # Weekly Summary only w/out the specific aStock tabs
    outCsvSummaryFile = theBaseCompaniesDirectory + companyEarningsWeek + companySummaryListFile
    yahooEarningsDF.to_csv(outCsvSummaryFile)

    return yahooEarningsDF


def getVolAndUpdateMoveDelta(yahooEarningsDF, earningWeekDir):
    print('in createWeekSummary // getVolAndUpdateMoveDelta() lenYahhDF', len(yahooEarningsDF))
    # Get % IV Delta
    yahooEarningsDF['IV_Delta'] = yahooEarningsDF.impliedVolatility - yahooEarningsDF.histVolatility

    # For "Earnings Call Time" column remove all but "before" or "after"
    yahooEarningsDF['Earnings Call Time'] = yahooEarningsDF['Earnings Call Time'].str[:5]
    yahooEarningsDF.rename(columns={'Earnings Call Time': 'Time'}, inplace=True)

    return updateDiary(yahooEarningsDF, earningWeekDir) #returns updated yahooEarningsDF


def updateDiary(yahooEarningsDF, earningWeekDir):
    print('in updateDiary')

    maxFwd4PercentDelta = []
    minFwd4PercentDelta = []
    maxFwd4PercentDeltaABS = []

    maxFwd4PriceDelta = []
    minFwd4PriceDelta = []
    maxFwd4PriceDeltaABS = []

    maxFwd1PercentDelta = []
    minFwd1PercentDelta = []
    maxFwd1PercentDeltaABS = []

    maxFwd1PriceDelta = []
    minFwd1PriceDelta = []
    maxFwd1DayABSPriceDelta = []

    maxBak4PriceDelta = []
    minBak4PriceDelta = []
    maxBak4PriceDeltaABS = []

    maxBak1PercentDelta = []
    minBak1PercentDelta = []
    maxBak1PercentDeltaABS = []

    maxBak1PriceDelta = []
    minBak1PriceDelta = []
    maxBak1DayABSPriceDelta = []

    maxBak4PercentDelta = []
    minBak4PercentDelta = []
    maxBak4PercentDeltaABS = []

    stdFwd4 = []
    stdFwd1 = []
    std25Fwd1 = []
    stdFwd1Fwd4 = []

    varFwd4 = []
    varFwd1 = []

    meanFwd4 = []
    meanFwd1 = []

    medianFwd4 = []
    medianFwd1 = []

    anElse = 1
    for row in yahooEarningsDF.itertuples():
        print(row.Symbol)
        aCompanyFile = row.Symbol + csvSuffix
        filePath = earningWeekDir / aCompanyFile
        print("  filePath:  ", filePath, '\n')
        ckForFile = Path(filePath)
        if ckForFile.is_file():
            # get company's CSV file with data
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
            maxFwd1DayABSPriceDelta.append(max(abs(anEarningWeeksCompany['EDDiffFwd1Close'].min()),
                                        anEarningWeeksCompany['EDDiffFwd1Close'].max()))

            # Calculate percent Delta for Bak4 Day movement
            maxBak4PercentDelta.append(anEarningWeeksCompany['EDBak4DayClosePercentDelta'].max())
            minBak4PercentDelta.append(anEarningWeeksCompany['EDBak4DayClosePercentDelta'].min())
            maxBak4PercentDeltaABS.append(max(abs(anEarningWeeksCompany['EDBak4DayClosePercentDelta'].min()),
                                        anEarningWeeksCompany['EDBak4DayClosePercentDelta'].max()))

            # Calculate price Delta for Bak4 Day movement
            maxBak4PriceDelta.append(anEarningWeeksCompany['EDDiffBak4Close'].max())
            minBak4PriceDelta.append(anEarningWeeksCompany['EDDiffBak4Close'].min())
            maxBak4PriceDeltaABS.append(max(abs(anEarningWeeksCompany['EDDiffBak4Close'].min()),
                                        anEarningWeeksCompany['EDDiffBak4Close'].max()))

            # Calculate percent Delta for Bak1 Day movement
            maxBak1PercentDelta.append(anEarningWeeksCompany['EDBak1DayClosePercentDelta'].max())
            minBak1PercentDelta.append(anEarningWeeksCompany['EDBak1DayClosePercentDelta'].min())
            maxBak1PercentDeltaABS.append(max(abs(anEarningWeeksCompany['EDBak1DayClosePercentDelta'].min()),
                                        anEarningWeeksCompany['EDBak1DayClosePercentDelta'].max()))

            # Calculate price Delta for Bak1 Day movement
            maxBak1PriceDelta.append(anEarningWeeksCompany['EDDiffBak1Close'].max())
            minBak1PriceDelta.append(anEarningWeeksCompany['EDDiffBak1Close'].min())
            maxBak1DayABSPriceDelta.append(max(abs(anEarningWeeksCompany['EDDiffBak1Close'].min()),
                                        anEarningWeeksCompany['EDDiffBak1Close'].max()))


            stdFwd4.append(anEarningWeeksCompany['EDFwd4DayClosePercentDelta'].std())
            stdFwd1.append(anEarningWeeksCompany['EDFwd1DayClosePercentDelta'].std())
            std25Fwd1.append(anEarningWeeksCompany['EDFwd1DayClosePercentDelta'].std()*2.5)

            stdFwd1Fwd4_concat = pd.concat([anEarningWeeksCompany['EDFwd1DayClosePercentDelta'], anEarningWeeksCompany['EDFwd4DayClosePercentDelta']])
            stdFwd1Fwd4.append(stdFwd1Fwd4_concat.std())

            varFwd4.append(anEarningWeeksCompany['EDFwd4DayClosePercentDelta'].var())
            varFwd1.append(anEarningWeeksCompany['EDFwd1DayClosePercentDelta'].var())

            meanFwd4.append(anEarningWeeksCompany['EDFwd4DayClosePercentDelta'].mean())
            meanFwd1.append(anEarningWeeksCompany['EDFwd1DayClosePercentDelta'].mean())

            medianFwd4.append(anEarningWeeksCompany['EDFwd4DayClosePercentDelta'].median())
            medianFwd1.append(anEarningWeeksCompany['EDFwd1DayClosePercentDelta'].median())

        else: # no data add not a number / nan
            print( "   *** No data @ row Index  = ", row.Index, "\n")
            #row.Index = row.Index +1
            anElse = anElse + 1

            maxFwd4PercentDelta.append(np.nan)
            minFwd4PercentDelta.append(np.nan)
            maxFwd4PercentDeltaABS.append(np.nan)

            maxFwd1PercentDelta.append(np.nan)
            minFwd1PercentDelta.append(np.nan)
            maxFwd1PercentDeltaABS.append(np.nan)

            maxFwd1PriceDelta.append(np.nan)
            minFwd1PriceDelta.append(np.nan)
            maxFwd1DayABSPriceDelta.append(np.nan)

            maxFwd4PriceDelta.append(np.nan)
            minFwd4PriceDelta.append(np.nan)
            maxFwd4PriceDeltaABS.append(np.nan)

            maxBak4PercentDelta.append(np.nan)
            minBak4PercentDelta.append(np.nan)
            maxBak4PercentDeltaABS.append(np.nan)

            maxBak4PriceDelta.append(np.nan)
            minBak4PriceDelta.append(np.nan)
            maxBak4PriceDeltaABS.append(np.nan)

            maxBak1PercentDelta.append(np.nan)
            minBak1PercentDelta.append(np.nan)
            maxBak1PercentDeltaABS.append(np.nan)

            maxBak1PriceDelta.append(np.nan)
            minBak1PriceDelta.append(np.nan)
            maxBak1DayABSPriceDelta.append(np.nan)

            stdFwd4.append(np.nan)
            stdFwd1.append(np.nan)
            stdFwd1Fwd4.append(np.nan)
            std25Fwd1.append(np.nan)

            varFwd4.append(np.nan)
            varFwd1.append(np.nan)

            meanFwd4.append(np.nan)
            meanFwd1.append(np.nan)

            medianFwd4.append(np.nan)
            medianFwd1.append(np.nan)

    yahooEarningsDF['maxFwd4PercentDelta'] = maxFwd4PercentDelta
    yahooEarningsDF['minFwd4PercentDelta'] = minFwd4PercentDelta
    yahooEarningsDF['maxFwd4PercentDeltaABS'] = maxFwd4PercentDeltaABS

    yahooEarningsDF['maxFwd1PercentDelta'] = maxFwd1PercentDelta
    yahooEarningsDF['minFwd1PercentDelta'] = minFwd1PercentDelta
    yahooEarningsDF['maxFwd1PercentDeltaABS'] = maxFwd1PercentDeltaABS

    yahooEarningsDF['maxFwd1PriceDelta'] = maxFwd1PriceDelta
    yahooEarningsDF['minFwd1PriceDelta'] = minFwd1PriceDelta
    yahooEarningsDF['max1DayABS$Delta'] = maxFwd1DayABSPriceDelta

    yahooEarningsDF['maxFwd4PriceDelta'] = maxFwd4PriceDelta
    yahooEarningsDF['minFwd4PriceDelta'] = minFwd4PriceDelta
    yahooEarningsDF['maxFwd4PriceDeltaABS'] = maxFwd4PriceDeltaABS

    yahooEarningsDF['maxBak4PercentDelta'] = maxBak4PercentDelta
    yahooEarningsDF['minBak4PercentDelta'] = minBak4PercentDelta
    yahooEarningsDF['maxBak4PercentDeltaABS'] = maxBak4PercentDeltaABS

    yahooEarningsDF['maxBak4PriceDelta'] = maxBak4PriceDelta
    yahooEarningsDF['minBak4PriceDelta'] = minBak4PriceDelta
    yahooEarningsDF['maxBak4PriceDeltaABS'] = maxBak4PriceDeltaABS

    yahooEarningsDF['maxBak1PercentDelta'] = maxBak1PercentDelta
    yahooEarningsDF['minBak1PercentDelta'] = minBak1PercentDelta
    yahooEarningsDF['maxBak1PercentDeltaABS'] = maxBak1PercentDeltaABS

    yahooEarningsDF['maxBak1PriceDelta'] = maxBak1PriceDelta
    yahooEarningsDF['minBak1PriceDelta'] = minBak1PriceDelta
    yahooEarningsDF['maxBak1DayABSPriceDelta'] = maxBak1DayABSPriceDelta

    yahooEarningsDF['stdFwd4%'] = stdFwd4
    yahooEarningsDF['stdFwd1%'] = stdFwd1
    yahooEarningsDF['stdFwd1$TimesClose'] = (yahooEarningsDF['stdFwd1%'] * yahooEarningsDF['Close'])
    yahooEarningsDF['std25Fwd1%'] = std25Fwd1
    yahooEarningsDF['std25Fwd1$TimesClose'] = (yahooEarningsDF['std25Fwd1%'] * yahooEarningsDF['Close'])
    # yahooEarningsDF['std25Fwd1MinusClose'] = yahooEarningsDF['Close'] - yahooEarningsDF['std25Fwd1%TimesClose']
    # yahooEarningsDF['std25Fwd1PlusClose']  = yahooEarningsDF['Close'] + yahooEarningsDF['std25Fwd1%TimesClose']
    yahooEarningsDF['ABSFwd1MinusClose'] = yahooEarningsDF['Close'] - yahooEarningsDF['max1DayABS$Delta']
    yahooEarningsDF['ABSFwd1PlusClose']  = yahooEarningsDF['Close'] + yahooEarningsDF['max1DayABS$Delta']

    # std25Fwd1.append(anEarningWeeksCompany['EDFwd1DayClosePercentDelta'].std() * 2.5)
    # std25TimesClose.append(std25Fwd1 * anEarningWeeksCompany['Close'])
    # # TODO -- Fix this
    # # std25MinusClose.append(anEarningWeeksCompany['Close']-(std25Fwd1*anEarningWeeksCompany['Close']))
    # # std25PlusClose.append(anEarningWeeksCompany['Close']+(std25Fwd1*anEarningWeeksCompany['Close']))
    # # TODO -- Fix this
    # # std25MinusClose.append(anEarningWeeksCompany['Close']-(std25Fwd1*anEarningWeeksCompany['Close']))
    # # std25PlusClose.append(anEarningWeeksCompany['Close']+(std25Fwd1*anEarning
    # yahooEarningsDF['std25TimesClose'] = std25TimesClose

    yahooEarningsDF['stdFwd1Fwd4%'] = stdFwd1Fwd4
    yahooEarningsDF['varFwd4%'] = varFwd4
    yahooEarningsDF['varFwd1%'] = varFwd1

    yahooEarningsDF['meanFwd4%'] = meanFwd4
    yahooEarningsDF['meanFwd1%'] = meanFwd1

    yahooEarningsDF['medianFwd4%'] = medianFwd4
    yahooEarningsDF['medianFwd1%'] = medianFwd1

    yahooEarningsDF = cleanUpColumns(yahooEarningsDF)

    return yahooEarningsDF


def cleanUpColumns(yahooEarningsDF):

    # Shorten some Column names and format the column
    # todo remove Open interest
    # yahooEarningsDF.rename(columns={'PutFridayOpenInterest': 'PutOpenIntst'}, inplace=True)
    # yahooEarningsDF.rename(columns={'CallFridayOpenInterest': 'CallOpenIntst'}, inplace=True)
    # yahooEarningsDF['PutOpenIntst'] = yahooEarningsDF['PutOpenIntst'].astype(int)
    # yahooEarningsDF['CallOpenIntst'] = yahooEarningsDF['CallOpenIntst'].astype(int)

    yahooEarningsDF.rename(columns={'impliedVolatility': 'impVol'}, inplace=True)
    yahooEarningsDF.rename(columns={'histVolatility': 'histVol'}, inplace=True)

    yahooEarningsDF.rename(columns={'Expected_Range': 'Exp$Range'}, inplace=True)


    # Format DF columns as we just need to show the data


    yahooEarningsDF['stdFwd1%'] = yahooEarningsDF['stdFwd1%'].round(4).map("{:.2%}".format)
    yahooEarningsDF['std25Fwd1%'] = yahooEarningsDF['std25Fwd1%'].round(4).map("{:.2%}".format)
    yahooEarningsDF['std25Fwd1$TimesClose'] = yahooEarningsDF['std25Fwd1$TimesClose'].map("${:.2f}".format)
    yahooEarningsDF['stdFwd1$TimesClose'] = yahooEarningsDF['stdFwd1$TimesClose'].map("${:.2f}".format)
    yahooEarningsDF['Exp$Range'] = yahooEarningsDF['Exp$Range'].map("${:.2f}".format)
    yahooEarningsDF['Close'] = yahooEarningsDF['Close'].map("${:.2f}".format)
    yahooEarningsDF['max1DayABS$Delta'] = yahooEarningsDF['max1DayABS$Delta'].round(2).map("${:.2f}".format)
    yahooEarningsDF['ABSFwd1MinusClose'] = yahooEarningsDF['ABSFwd1MinusClose'].round(2).map("${:.2f}".format)
    yahooEarningsDF['ABSFwd1PlusClose'] = yahooEarningsDF['ABSFwd1PlusClose'].round(2).map("${:.2f}".format)

    yahooEarningsDF['impVol'] = yahooEarningsDF['impVol'].round(2).map("{:.0%}".format)
    yahooEarningsDF['histVol'] = yahooEarningsDF['histVol'].round(2).map("{:.0%}".format)
    yahooEarningsDF['IV_Delta'] = yahooEarningsDF['IV_Delta'].round(2).map("{:.0%}".format)



    # rearrange columns
    # yahooEarningsDF = yahooEarningsDF[['Symbol', 'Company', 'Earnings_Date','Time', 'Close', 'Volume',
    #                                    'histVol','impVol', 'IV_Delta', 'Option_Volume',
    #                                    'Exp$Range', 'stdFwd1%', 'std25Fwd1%',
    #                                    'Close', 'max1DayABS$Delta','stdFwd1$TimesClose', 'std25Fwd1$TimesClose','ABSFwd1MinusClose', 'ABSFwd1PlusClose']]
    yahooEarningsDF = yahooEarningsDF[['Symbol', 'Company', 'Earnings_Date','Time', 'Close', 'Volume',
                                       'histVol','impVol', 'IV_Delta', 'Option_Volume',
                                       'Exp$Range', 'stdFwd1%', 'std25Fwd1%',
                                       'Close', 'max1DayABS$Delta','stdFwd1$TimesClose', 'std25Fwd1$TimesClose','ABSFwd1MinusClose', 'ABSFwd1PlusClose',
                                       'maxBak4PercentDelta', 'minBak4PercentDelta', 'maxBak4PercentDeltaABS', 'maxBak4PriceDelta', 'minBak4PriceDelta',
                                       'maxBak4PriceDeltaABS', 'maxBak1PercentDelta', 'minBak1PercentDelta', 'maxBak1PercentDeltaABS', 'maxBak1PriceDelta',
                                       'minBak1PriceDelta', 'maxBak1DayABSPriceDelta']]

    return yahooEarningsDF