
import sys

sys.path.append('/home/michael/jupyter/local-packages')



# Doc is here: https://ib-insync.readthedocs.io/readme.html
from ib_insync import *
util.startLoop()

ib = IB()
# Connect to IB Gateway / Paper Trade 4002
#            TWS        / Paper Trade 7495
ib.connect('127.0.0.1', 4002, clientId=4)
