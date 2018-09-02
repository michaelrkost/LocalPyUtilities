

def error200 (reqId, errorCode, errorString, contract):
    print("200 <<>> 200",reqId, errorCode, errorString, contract)

def error321 (reqId, errorCode, errorString, contract):
    print("321 <<>> 321")

def error10061(reqId, errorCode, errorString, contract):
    print("error10061 <<>> error10061")

errorDict = {
    200 : error200,
    321 : error321,
    10061 : error10061
}

def onError(reqId, errorCode, errorString, contract):
    # look at errorCode to see if warning or error
   if errorCode in errorDict:
        errorDict[errorCode](reqId, errorCode, errorString, contract)
   else:
       print('Error not in "Error Dictionary" => errorCode: ', errorCode,"   ", errorString,)

