IB_API_HOST = "127.0.0.1"

# Connect to IB Gateway / Paper Trade 4002
#            TWS        / Paper Trade 7495
IB_PAPER_TRADE_PORT = 4002

#Client ID 0 will receive order status messages for its own (client ID 0) orders
# and also for orders submitted manually from TWS.
IB_API_CLIENTID_0 = 0

# Just another Client ID
# can be used as a start point for incremental IDs
IB_API_CLIENTID_1 = 1

# Puts / Calls
putRight = 'P'
callRight = 'C'
rights = [putRight, callRight]

# // Form Dropdown Data
# theSecurityTypes: any[] = ["STK", "IND", "OPT", "FUT", "FOP", "CASH", "BAG", "NEWS"];
# theExchangeTypes: any[] = ["SMART", "CBOE", "AMEX", "IDEAL", "ISLAND", "NYSE", "PHLX"];
# theTickTypes: any[] = ["LAST", "CLOSE", "BID", "ASK", "LOW", "HIGH"];