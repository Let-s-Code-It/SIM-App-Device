
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
Saving the last error to a file
"""
from App.Utils.ErrorLogger import ErrorLogger
ErrorLogger()




"""
Program logs in a file
"""
import os
import logging
from datetime import datetime
logDirectory = 'Data/logs'
if not os.path.exists(logDirectory):
    os.makedirs(logDirectory)
logging.basicConfig(filename=logDirectory+'/' + datetime.today().strftime('%Y-%m-%d') + '.log', format='%(asctime)s - [%(levelname)s]: %(message)s', level=logging.DEBUG)
logging.info('System starts')



"""
Checking md5 checksum of files to find out version
"""
from App.Utils.MD5Sum import MD5Sum
MD5Sum()



"""
After clicking Ctrl + C the program shuts down
"""
import signal
def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    os._exit(0)
signal.signal(signal.SIGINT, signal_handler)
print('Press Ctrl+C if you can close program')




"""
peak boot arguments
"""
from App.LaunchArguments import LaunchArgumentsInit, LaunchArguments
print(LaunchArgumentsInit())



"""
SQL Start
"""
from App.SQL import SQL
SQL.Init()


""" 
Web server start
"""
from App.Web import WebThread
WebThread.start()



"""
Socket client (connect to sim panel serwer) start
"""
from App.SocketClient import SocketClient
SocketClient.Connect()


"""
Reader start (Connect with SIM hat via USB/uart)
"""
from App.Reader import GetReader, CreateReader
CreateReader.run()


"""
Maintaining the main process
"""
import time
while True:
    time.sleep(1)

