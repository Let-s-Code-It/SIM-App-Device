import socketio
from threading import Thread
import time

from .SQL import SQL

from .Utils.SystemInfo import getSystemInfo

from .Device import Device

from .Logger import logger, defineLogToSocketFunction

from ..Config import __VERSION__

from .Utils.MD5Sum import MD5Sum

import json
import os
#sio = socketio.Client(logger=True, engineio_logger=True)
sio = socketio.Client(
    # reconnection_attempts=5,  # liczba prób ponownego połączenia
    # reconnection_delay=1,  # opóźnienie między próbami ponownego połączenia (w sekundach)
    # reconnection_delay_max=5,  # maksymalne opóźnienie między próbami ponownego połączenia (w sekundach)
    # randomization_factor=0.5  # wartość losowa używana do obliczania losowego opóźnienia między próbami (zakres od 0 do 1)
)

@sio.event(namespace='/device')
def connect():
    logger.debug("I'm connected!")
    logger.debug(sio.sid)

    auth = SQL.Get("socket_unique_auth_key")
    if auth != "":
        SocketClient.emit("login", auth)
    else: 
        SocketClient.emit("first login", SQL.Get("socket_unique_login_key"))

@sio.event(namespace='/device')
def connect_error(data):
    logger.debug("The connection failed!")

@sio.event(namespace='/device')
def disconnect():
    logger.debug("I'm disconnected!")
    # SocketClient.Logged = False
    # defineLogToSocketFunction(None)

    # SocketClient.Connect()


@sio.on('my message', namespace='/device')
def on_message(data):
    logger.debug(['I received a message!', data])

@sio.on('keep alive', namespace='/device')
def on_message(data):
    SocketClient.keepAliveLastSentTime = 0
    logger.debug(['Keep Alive response: ', data])



@sio.on('first login', namespace='/device')
def handle1(data):
    logger.debug(['Static login key from socket server: ', data])
    SQL.Set("socket_unique_auth_key", data['input'])
    SocketClient.emit("login", data['input'])

@sio.on('first login fail', namespace='/device')
def handle2(data):
    logger.debug("Invalid socket unique login key (first login)...")
    SocketClient.Logged = False

@sio.on('login', namespace='/device')
def handle3():
    logger.debug('Loggin success.')
    logger.info('Logged in to the socket server')
    logger.debug(getSystemInfo())
    SocketClient.Logged = True
    SocketClient.emit("device info", getSystemInfo())

    SocketClient.SendReadersInfo()
    
    defineLogToSocketFunction(SocketClient.LoggerLog)

@sio.on('login fail', namespace='/device')
def handle4(data):
    logger.debug("Invalid socket unique login key...")
    SocketClient.Logged = False

@sio.on('device data', namespace='/device')
def handle5(data):
    logger.debug("Your Device Name: " + data['friendly_name'])
    Device.Adopted = data['adopted']
    logger.debug(["Adopt Status: ", Device.Adopted, data])

@sio.on('send message', namespace='/device')
def handle6(data):
    logger.debug("sending a new message at the request of the sim app panel ")
    logger.debug(data)
    SocketClient.Readers[0].send_sms_from_panel(data)
    """SocketClient.Readers[0].send_sms(
        data['recipient'], 
        data['text'], 
        lambda transport: SocketClient.MessageSentSuccessfully(transport, data), 
        lambda transport, d: SocketClient.MessageNotSent(transport, d, data)
    )"""


@sio.on('*')
def catch_all(event, data):
    print(event)
    print(data)
    logger.debug("Undefined socket event: '" + event + "', with data: " + data)


AtLeastOnceConnected = False

start_socket_function_bool = False
# def start_socket():
#     global start_socket_function_bool
#     time.sleep(3)
#     if not sio.connected:
#         if not start_socket_function_bool:
#             start_socket_function_bool = True
#             #while(True):
#             try:
#                 logger.debug("start_socket - try")

#                 sio.connect( 
#                     SQL.Get("socket_address"), 
#                     namespaces=['/device'], 
#                     headers={"app-version": __VERSION__, 'app-version-sum': json.dumps(MD5Sum())},
#                     transports=['websocket']
#                     )

#                 AtLeastOnceConnected = True
#                 logger.debug("Socket: sio.connect method succesfully")
#                 #break
#             except socketio.exceptions.ConnectionError:
#                 logger.error("Socket Connection Error!")
#                 SocketClient.Disconnect()
#             except Exception as e:
#                 logger.error("Socket Error: Other... ")
#                 logger.error(e)
#                 SocketClient.Disconnect()
#             finally:
#                 logger.debug("start_socket - finally method")
#                 #time.sleep(10)
#             start_socket_function_bool = False
#         else:
#             logger.debug("double start_socket function blocked")
#     else:
#         logger.debug("start_socket function blocked - socket is connected")

def start_socket():
    start_success = False
    #SocketClient.whileEstablishingAConnection = True
    while not start_success:
        try:
            logger.debug("start_socket - try")

            sio.connect( 
                SQL.Get("socket_address"), 
                namespaces=['/device'], 
                headers={"app-version": __VERSION__, 'app-version-sum': json.dumps(MD5Sum())},
                transports=['websocket']
            )
            start_success = sio.connected
            logger.debug("Socket: sio.connect method succesfully")
        except socketio.exceptions.ConnectionError:
            logger.error("Socket Connection Error!")
        except Exception as e:
            logger.error("Socket Error: Other... ")
            logger.error(e)
        finally:
            time.sleep(5)
            logger.debug("start_socket - finally method")
            # if start_success:
            #     SocketClient.whileEstablishingAConnection = False
            # else:
            #logger.error("Critical! start_socket try again by loop ...")


    



"""
def SocketClientSend(title, message):
    sio.emit(title, message) #TODO! EXAMPLE!
"""

class SocketClient:


    Logged = False

    Readers = []

    keepAliveLastSentTime = 0

    whileEstablishingAConnection = False

    @staticmethod
    def Connect():
        # if SocketClient.whileEstablishingAConnection:
        #     logger.debug("SocketConnection.Connection - break")
        #     return

        SocketClientThread = Thread(target=start_socket)
        SocketClientThread.start()
        #start_socket()

    @staticmethod
    def UpdateLoginKey(key):
        
        SQL.Set("socket_unique_login_key", key)
        SQL.Set("socket_unique_auth_key", "")

        logger.debug("Update Socket Login Key to: " + key)


    @staticmethod
    def UpdateAddress(address):
        
        SQL.Set("socket_address", address)

        logger.debug("Update Socket Path... " + address)


    # @staticmethod
    # def Disconnect(force=False):
    #     logger.debug("SocketClient.Disconnect() method")

    #     if force:
    #         logger.debug("Force disconnect!")
    #         #sio.eio.disconnect()

    #     sio.disconnect()

    #     SocketClient.Logged = False
    #     defineLogToSocketFunction(None)

    # @staticmethod
    # def Reload():
    #     logger.debug("Reload SocketClient....")
    #     if sio.connected or AtLeastOnceConnected:
    #         logger.debug("Socket IO is connected: Trying to recconect after change key/address")
    #         sio.disconnect()

    #         SocketClient.Connect()

    #     else:
    #         logger.debug("Socket IO is disconnected: Update address/key updated. Please wait to reconnect.")
    #         SocketClient.Connect()

    @staticmethod
    def IsConnected():
        return sio.connected


    @staticmethod
    def emit(title, message):
        """
        if sio.connected:
            return sio.emit(title, message)
        else:
            print(["I cant send this message to socket :c Is disconnected", title, message])
        """
        #print("emit", title, message)

        try:
            return sio.emit(title, message, namespace='/device')
        except socketio.exceptions.BadNamespaceError as err:
            logger.debug(["I cant send this message to socket :c Is disconnected", title, message, err])
            #SocketClient.Reload()


    @staticmethod
    def SendReadersInfo():
        if(len(SocketClient.Readers) > 0):
            logger.debug(["sim cards", [SocketClient.Readers[0].GetInfo()]])
            SocketClient.emit("update sim cards", [SocketClient.Readers[0].GetInfo()])
        else:
            logger.debug("SendReadersInfo: No one Readers ready...")


    @staticmethod
    def MessageSentSuccessfully(message):
        logger.debug("----->Wiadomość sms wysłana pomyślnie")
        SocketClient.emit("message sent successfully", {
            "message": message,
        })

    @staticmethod
    def MessageNotSent(message, reason):
        logger.debug("----->Wadimość sms NIE wysłana z bledem '"+reason+"' ")
        
        SocketClient.emit("message not sent", {
            "message": message,
            "reason": reason
        })

    @staticmethod
    def LoggerLog(data):
        SocketClient.emit("logger log", data)

