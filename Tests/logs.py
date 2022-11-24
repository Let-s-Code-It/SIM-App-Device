import logging
class LoggerHandler(logging.StreamHandler):
    def emit(self, record):
        try:
            msg = self.format(record)
            stream = self.stream
            stream.write(msg)
            stream.write(self.terminator)

            self.flush()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)
if __name__ == '__main__':
    import time
    loggerAddon = LoggerHandler()
    console  = logging.StreamHandler()  

    logger = logging.getLogger('test')
    logger.setLevel(logging.DEBUG) 
    logger.addHandler(loggerAddon)

    logging.basicConfig(filename='logging.log', format='%(asctime)s - [%(levelname)s]: %(message)s', level=logging.DEBUG)

    logger.info('test1')
    for i in range(3):
        logger.debug('remaining %d seconds', i)
        time.sleep(1)
    logger.info('test2')