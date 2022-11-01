import socketio
from threading import Thread
import time

from .SQL import SQL

from .Utils.SystemInfo import getSystemInfo

from .Device import Device

import logging

sio = socketio.Client()

@sio.event(namespace='/device')
def connect():
    print("I'm connected!")

    auth = SQL.Get("socket_unique_auth_key")
    if auth != "":
        SocketClient.emit("login", auth)
    else: 
        SocketClient.emit("first login", SQL.Get("socket_unique_login_key"))

@sio.event(namespace='/device')
def connect_error(data):
    print("The connection failed!")

@sio.event(namespace='/device')
def disconnect():
    print("I'm disconnected!")
    SocketClient.Logged = False



@sio.event(namespace='/device')
def message(data):
    print(['I received a message!!!!', data])

@sio.on('my message', namespace='/device')
def on_message(data):
    print(['I received a message!', data])

@sio.on('keep alive', namespace='/device')
def on_message(data):
    print(['Keep Alive response: ', data])



@sio.on('first login', namespace='/device')
def on_message(data):
    print(['Static login key from socket server: ', data])
    SQL.Set("socket_unique_auth_key", data['input'])
    SocketClient.emit("login", data['input'])

@sio.on('first login fail', namespace='/device')
def on_message(data):
    print("Invalid socket unique login key (first login)...")
    SocketClient.Logged = False

@sio.on('login', namespace='/device')
def on_message():
    print('Loggin success.')
    logging.info('Logged in to the socket server')
    print(getSystemInfo())
    SocketClient.Logged = True
    SocketClient.emit("device info", getSystemInfo())

    SocketClient.SendReadersInfo();

@sio.on('login fail', namespace='/device')
def on_message(data):
    print("Invalid socket unique login key...")
    SocketClient.Logged = False

@sio.on('device data', namespace='/device')
def on_message(data):
    print("Your Device Name: " + data['friendly_name'])
    Device.Adopted = data['adopted']
    print("Adopt Status: ", Device.Adopted)

@sio.on('send message', namespace='/device')
def on_message(data):
    print("sending a new message at the request of the sim app panel ")
    print(data)
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
            print("Socket Connection Error!")
        except:
            print("Socket Error: Other....")
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

        print("Update Socket Login Key to: " + key)


    @staticmethod
    def UpdateAddress(address):
        
        SQL.Set("socket_address", address)

        print("Update Socket Path... " + address)


    @staticmethod
    def Reload():
        print("Reload SocketClient....")
        if sio.connected or AtLeastOnceConnected:
            print("Socket IO is connected: Trying to recconect after change key/address")
            sio.disconnect()

            SocketClient.Connect()

        else:
            print("Socket IO is disconnected: Update address/key updated. Please wait to reconnect.")

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
            print(["I cant send this message to socket :c Is disconnected", title, message])


    @staticmethod
    def SendReadersInfo():
        if(len(SocketClient.Readers) > 0):
            print(["sim cards", [SocketClient.Readers[0].info]])
            SocketClient.emit("update sim cards", [SocketClient.Readers[0].info])
        else:
            print("SendReadersInfo: No one Readers ready...")


    @staticmethod
    def MessageSentSuccessfully(message):
        print("----->Wiadomość sms wysłana pomyślnie")
        SocketClient.emit("message sent successfully", {
            "message": message,
        })

    @staticmethod
    def MessageNotSent(message, reason):
        print("----->Wadimość sms NIE wysłana z bledem '"+reason+"' ")
        
        SocketClient.emit("message not sent", {
            "message": message,
            "reason": reason
        })


    
