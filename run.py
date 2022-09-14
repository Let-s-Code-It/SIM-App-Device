

"""


!!!!!!!!!!!!!!!!!!!!!!!!!!!

IMORTANT !!!!

Use GetReader(), not reader.

Example:

GetReader().write(...)

!!!!!!!!!!!!!!!!!!!!!!!!!!!



"""

import signal
import os
def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    os._exit(0)
signal.signal(signal.SIGINT, signal_handler)
print('Press Ctrl+C if you can close program')


import time


from App.LaunchArguments import LaunchArgumentsInit, LaunchArguments
print(LaunchArgumentsInit())


from App.SQL import SQL
SQL.Init()

from App.Web import WebThread
WebThread.start()

"""
from App.SocketClient import SocketClientThread, SocketClientSend
SocketClientThread.start()
"""

from App.SocketClient import SocketClient
SocketClient.Connect()

from App.Reader import GetReader, CreateReader
CreateReader.run()
#if not GetReader().alive:
#    print("reader not alive")

#Reader.protocol.write("AT",lambda transport,data: print("TEST COMMAND"))


while True:
    time.sleep(1)


"""
with ReaderThread(serial_port, SerialReader) as reader:

    #time.sleep(20)
    #reader.write("+AT-O-CHUJ",lambda transport,data: print("Ależ chujem jebło"))

    time.sleep(20)
    #reader.write("AT+CMGF=1",lambda transport,data: print("Przygotowanie do wyslania SMS"))
    
    #reader.write("AT+COPS=?",lambda transport,data: print("Nadajniki GSM w poblizu"))

    #reader.write('AT+CMGS="'+UTF16.encode("884167733")+'"\n\r' + UTF16.encode("Hello 1") + chr(26), lambda transport, data: print("Wysylam SMS"))
    #reader.write('AT+CMGS="'+UTF16.encode("884167733")+'"\n\r' + UTF16.encode("Hello 2") + chr(26), lambda transport, data: print("Wysylam SMS"))
    #reader.write('AT+CMGS="'+UTF16.encode("884167733")+'"\n\r' + UTF16.encode("Hello 3") + chr(26), lambda transport, data: print("Wysylam SMS"))
    #reader.write('AT+CMGS="'+UTF16.encode("884167733")+'"\n\r' + UTF16.encode("Hello 4") + chr(26), lambda transport, data: print("Wysylam SMS"))

    
    while(1):
        time.sleep(10)
        #reader.write("AT+CGNSINF",lambda transport,data: print("Lokalizacja GPS"))
        try:
            SocketClientSend('keep alive', {'foo': 'bar'})
        except:
            print("Send socket message error...")
        
"""