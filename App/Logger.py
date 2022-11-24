import logging
import sys
import os
from datetime import datetime
import time

from ..Config import __APPLICATION_DATA__



def defineLogToSocketFunction(d):
    print(" defineLogToSocketFunction ----> ", d)
    LogsToSocket.defineSocketFunction(d)


class LogsToSocket:
    socketFunction = None
    queue = []

    @staticmethod
    def defineSocketFunction(d):
        LogsToSocket.socketFunction = d
        if d != None:
            for data in  LogsToSocket.queue:
                data = LogsToSocket.queue.pop(0)
                LogsToSocket.socketFunction(data)
            LogsToSocket.queue = []

    @staticmethod
    def add(record, message):

        data = {
            "message": message,
            "level": record.levelname,
            "date": record.asctime,
            "time": int(time.time())
        }

        if LogsToSocket.socketFunction != None:
            LogsToSocket.socketFunction(data)
        else:
            LogsToSocket.queue.append(data)





class LoggerHandler(logging.StreamHandler):
    def emit(self, record):
        try:
            msg = self.format(record)
            stream = self.stream
            
            LogsToSocket.add(record, msg)
            #SocketClient.LoggerLog(msg)
            #print([record.levelname, record.asctime])
            
            #stream.write(msg)
            #stream.write(self.terminator)

            #self.flush()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)

def setup_custom_logger(name):
    formatter = logging.Formatter(fmt='%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    
    logDirectory = __APPLICATION_DATA__ + '/logs'
    if not os.path.exists(logDirectory):
        os.makedirs(logDirectory)

    logFile = logDirectory+'/' + datetime.today().strftime('%Y-%m-%d_%H:%M:%S') + '.log'
    print("Log file: " + logFile)
    
    handler = logging.FileHandler(logFile, mode='w')
    handler.setFormatter(formatter)
    screen_handler = logging.StreamHandler(stream=sys.stdout)
    screen_handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    logger.addHandler(screen_handler)

    loggerAddon = LoggerHandler()
    logger.addHandler(loggerAddon)

    return logger


logger = setup_custom_logger('SIM_App_Device')