import logging
from logging.handlers import TimedRotatingFileHandler

def setup(name,filename):
    filename = "/vagrant/logs/" + filename
    logHandler = TimedRotatingFileHandler(filename,when="midnight",backupCount=5)
    logFormatter = logging.Formatter('%(asctime)s[%(threadName)s] %(message)s')
    logHandler.setFormatter( logFormatter )

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logHandler)
    logger.setLevel(logging.DEBUG)
    return logger

def getLogger(name):
    return logging.getLogger(name)




