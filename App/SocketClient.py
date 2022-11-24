import socketio
from threading import Thread
import time

from .SQL import SQL

from .Utils.SystemInfo import getSystemInfo

from .Device import Device

from .Logger import logger, defineLogToSocketFunction

sio = socketio.Client()

@sio.event(namespace='/device')
def connect():
    logger.debug("I'm connected!")

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
    SocketClient.Logged = False

    defineLogToSocketFunction(None)



@sio.event(namespace='/device')
def message(data):
    logger.debug(['I received a message!!!!', data])

@sio.on('my message', namespace='/device')
def on_message(data):
    logger.debug(['I received a message!', data])

@sio.on('keep alive', namespace='/device')
def on_message(data):
    logger.debug(['Keep Alive response: ', data])



@sio.on('first login', namespace='/device')
def on_message(data):
    logger.debug(['Static login key from socket server: ', data])
    SQL.Set("socket_unique_auth_key", data['input'])
    SocketClient.emit("login", data['input'])

@sio.on('first login fail', namespace='/device')
def on_message(data):
    logger.debug("Invalid socket unique login key (first login)...")
    SocketClient.Logged = False

@sio.on('login', namespace='/device')
def on_message():
    logger.debug('Loggin success.')
    logger.info('Logged in to the socket server')
    logger.debug(getSystemInfo())
    SocketClient.Logged = True
    SocketClient.emit("device info", getSystemInfo())

    SocketClient.SendReadersInfo()
    
    defineLogToSocketFunction(SocketClient.LoggerLog)

@sio.on('login fail', namespace='/device')
def on_message(data):
    logger.debug("Invalid socket unique login key...")
    SocketClient.Logged = False

@sio.on('device data', namespace='/device')
def on_message(data):
    logger.debug("Your Device Name: " + data['friendly_name'])
    Device.Adopted = data['adopted']
    logger.debug(["Adopt Status: ", Device.Adopted, data])

@sio.on('send message', namespace='/device')
def on_message(data):
    logger.debug("sending a new message at the request of the sim app panel ")
    logger.debug(data)
    SocketClient.Readers[0].send_sms_from_panel(data)
    """SocketClient.Readers[0].send_sms(
        data['recipient'], 
        data['text'], 
        lambda transport: SocketClient.MessageSentSuccessfully(transport, data), 
        lambda transport, d: SocketClient.MessageNotSent(transport, d, data)
    )"""




AtLeastOnceConnected = False

def start_socket():
    while(True):
        try:
            sio.connect( SQL.Get("socket_address"), namespaces=['/device'] )
            AtLeastOnceConnected = True
            break
        except socketio.exceptions.ConnectionError:
            logger.debug("Socket Connection Error!")
        except:
            logger.debug("Socket Error: Other....")
        finally:
            time.sleep(10)



"""
def SocketClientSend(title, message):
    sio.emit(title, message) #TODO! EXAMPLE!
"""

class SocketClient:


    Logged = False

    Readers = []

    @staticmethod
    def Connect():
        SocketClientThread = Thread(target=start_socket)
        SocketClientThread.start()

    @staticmethod
    def UpdateLoginKey(key):
        
        SQL.Set("socket_unique_login_key", key)
        SQL.Set("socket_unique_auth_key", "")

        logger.debug("Update Socket Login Key to: " + key)


    @staticmethod
    def UpdateAddress(address):
        
        SQL.Set("socket_address", address)

        logger.debug("Update Socket Path... " + address)


    @staticmethod
    def Reload():
        logger.debug("Reload SocketClient....")
        if sio.connected or AtLeastOnceConnected:
            logger.debug("Socket IO is connected: Trying to recconect after change key/address")
            sio.disconnect()

            SocketClient.Connect()

        else:
            logger.debug("Socket IO is disconnected: Update address/key updated. Please wait to reconnect.")

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

        try:
            return sio.emit(title, message, namespace='/device')
        except socketio.exceptions.BadNamespaceError:
            logger.debug(["I cant send this message to socket :c Is disconnected", title, message])


    @staticmethod
    def SendReadersInfo():
        if(len(SocketClient.Readers) > 0):
            logger.debug(["sim cards", [SocketClient.Readers[0].info]])
            SocketClient.emit("update sim cards", [SocketClient.Readers[0].info])
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

