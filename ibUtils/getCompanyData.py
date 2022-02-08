
import sys
sys.path.append('/home/michael/jupyter/local-packages')

from localUtilities import dateUtils, config
import numpy
import pandas as pd
import yahoo_fin.stock_info as si

def getHistoricEpsData(aStock):
    """
    Get the Historic EPS Data for aStock

    """
    # Get the Earnings History for aStock
    historicEpsDF = pd.DataFrame.from_dict(si.get_earnings_history(aStock))
    # drop superfluous columns
    historicEpsDF.drop(['startdatetimetype', 'timeZoneShortName', 'gmtOffsetMilliSeconds', 'quoteType'],
                     axis=1, inplace=True)
    # Update the "Earnings_Date" date str from "2022-01-25T00:00:00.000Z" to "2022-01-25"
    historicEpsDF['startdatetime'] = historicEpsDF['startdatetime'].map(lambda a: a.split("T", 1)[0])
    # now set as dateTime
    historicEpsDF['startdatetime'] = historicEpsDF['startdatetime'].map(lambda a: dateUtils.getDateFromISO8601(a))
    # Update the column names
    historicEpsDF.rename(columns={ "ticker": "Symbol", "companyshortname": "Company", "startdatetime": 'Earnings_Date',
        "startdatetimetype": "Earnings Call Time", "epsestimate": 'EPS_Estimate', "epsactual": "Reported_EPS",
        "epssurprisepct": "Surprise(%)" }, inplace = True)

    # Drop any future Earnings info
    historicEpsDF = historicEpsDF.drop(historicEpsDF[historicEpsDF['Earnings_Date'] > dateUtils.getTodayDateTime()].index)

    # sort the DF on "Earnings_Date"
    # use "ignore_index=True" as the default is False
    #   If True, the resulting axis will be labeled 0, 1, …, n - 1
    historicEpsDF = historicEpsDF.sort_values(by='Earnings_Date', ascending=False, ignore_index=True)

    # just keep the needed maxQtrs
    historicEpsDF = historicEpsDF.head(config.maxQtrs)

    # return the DF
    return historicEpsDF
