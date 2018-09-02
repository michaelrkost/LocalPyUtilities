# ======== Logging ================================================
import logging
import sys


# Level Numeric value
#    CRITICAL  50
#    ERROR     40
#    WARNING   30
#    INFO      20
#    DEBUG     10
#    NOTSET     0

def init_logger_singleton():
    global logger

    logger = logging.getLogger(name='PyOptionLogger')
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        '[%(asctime)s:%(module)s:%(lineno)s:%(levelname)s] %(message)s')

    streamhandler = logging.StreamHandler(sys.stdout)
    streamhandler.setLevel(logging.DEBUG)
    streamhandler.setFormatter(formatter)

    logger.addHandler(streamhandler)

    # To add a seperate handle for file
    # filehandler = logging.FileHandler('PyOptionLogger.log')
    # filehandler.setLevel(logging.DEBUG)
    # filehandler.setFormatter(formatter)
    #
    # logger.addHandler(filehandler)
