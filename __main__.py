
"""
Created by Karol Sójka
Let's Code It
www.letscode.it
kontakt@letscode.it
2022

"""




"""
!!!!!!!!!!!!!!!!!!!!!!!!!!!

IMORTANT !!!!

Use GetReader(), not reader.

Example:

GetReader().write(...)

!!!!!!!!!!!!!!!!!!!!!!!!!!!

"""




"""
peak boot arguments
"""
from .App.LaunchArguments import LaunchArgumentsInit, LaunchArguments
LaunchArgumentsInit()



"""
configuration of application paths, etc.
"""
from .Config import __APPLICATION_DATA__



"""
Saving the last error to a file
"""
from .App.Utils.ErrorLogger import ErrorLogger




"""
Program logs in a file
"""

import logging
from datetime import datetime



"""
Checking md5 checksum of files to find out version
"""
from .App.Utils.MD5Sum import MD5Sum



"""
After clicking Ctrl + C the program shuts down
"""
import signal
import os
def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    os._exit(0)



"""
SQL Start
"""
from .App.SQL import SQL



""" 
Web server start
"""
from .App.Web import WebThread




"""
Socket client (connect to sim panel serwer) start
"""
from .App.SocketClient import SocketClient



"""
Reader start (Connect with SIM hat via USB/uart)
"""
from .App.Reader import GetReader, CreateReader



"""
Maintaining the main process
"""
import time




if __name__ == "__main__":
	ErrorLogger()


	logDirectory = __APPLICATION_DATA__ + '/logs'
	if not os.path.exists(logDirectory):
	    os.makedirs(logDirectory)
	logging.basicConfig(filename=logDirectory+'/' + datetime.today().strftime('%Y-%m-%d') + '.log', format='%(asctime)s - [%(levelname)s]: %(message)s', level=logging.DEBUG)
	logging.info('System starts')


	MD5Sum()


	signal.signal(signal.SIGINT, signal_handler)
	print('Press Ctrl+C if you can close program')


	SQL.Init()


	WebThread.start()


	SocketClient.Connect()


	CreateReader.run()


	while True:
		time.sleep(1)
