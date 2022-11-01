import threading 
import sys
import traceback
import os 
from datetime import datetime
import logging
from ...Config import __APPLICATION_DATA__
"""
If any process returns an error while the application is running, 
the program will end and an error file will be created 
in the default folder Data/errors/.
"""

def ErrorLogger():
    
    logDirectory = __APPLICATION_DATA__ + '/errors'
    
    if not os.path.exists(logDirectory):
        os.makedirs(logDirectory)

    original_init = threading.Thread.__init__
    def patched_init(self, *args, **kwargs):
        #print("thread init'ed")
        original_init(self, *args, **kwargs)
        original_run = self.run
        def patched_run(*args, **kw):
            try:
                original_run(*args, **kw)
            except:
                sys.excepthook(*sys.exc_info())
                logging.info("The program ended after an error.")

                fp = open(os.path.join(logDirectory, datetime.today().strftime('%Y-%m-%d %H:%M:%S') + '.txt'), 'w')
                fp.write(traceback.format_exc())
                fp.close()

                fp = open(os.path.join(logDirectory, 'last.txt'), 'w')
                fp.write(traceback.format_exc())
                fp.close()

                print('-'*60)

                os._exit(0)
        self.run = patched_run
    threading.Thread.__init__ = patched_init
