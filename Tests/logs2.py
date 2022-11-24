import logging
import sys


class LoggerHandler(logging.StreamHandler):
    def emit(self, record):
        try:
            msg = self.format(record)
            stream = self.stream

            #print([record.levelname, record.asctime])
            
            #stream.write(msg)
            #stream.write(self.terminator)

            self.flush()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)

def setup_custom_logger(name):
    formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s',
                                  datefmt='%Y-%m-%d %H:%M:%S')
    handler = logging.FileHandler('log.txt', mode='w')
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
logger.info('This is a message!')

logger.debug('Debug message :)')