from serial.threaded import ReaderThread, Protocol
from collections import namedtuple
import time

from .AppHandler import AppHandler

from ..Utils.UTF16 import UTF16

from ..SocketClient import SocketClient

from ..SQL import SQL

QueuedCommand = namedtuple('QueuedCommand', ['value', 'callback'])

import logging



class SerialReader(Protocol):
    """
    Serial port reader customized to communicate with SIM800
    """

    TERMINATOR = b'\r\n'

    def __init__(self):
        """
        Initialize default data and event handlers
        """

        self.queue = []
        self.callbacks = {}
        self.handler = AppHandler(self)
        self.last_command = None
        self.next_response_callback = None
        self.transport = None
        self.buffer = None

        self.connection_confirmed = False

        self.info = {
            'my_phone_number': '',
            'port_name': SQL.Get('port_name'),
            'port_friendly_name': SQL.Get('port_friendly_name'),
            'serial_number': ''
        }

        self.sms_queue_from_panel = []

        self.reconfigure()

    def bind_event(self, event, callback):
        """
        Bind new handler for given event
        """

        print('bind_event')
        if event not in self.callbacks:
            self.callbacks[event] = [callback]
        else:
            self.callbacks[event].append(callback)

    def write(self, data, callback=None):
        """
        Add new queued command
        """

        print("New queued command (" + data +  ")")
        if not callback:
            def callback(transport):
                return None

        self.queue.append(QueuedCommand(data, callback))

        if self.transport:
            logging.debug("send_queued in write")
            self.send_queued()

    def reconfigure(self):
        """
        Reconfigure SIM800 with our default settings
        """

        print('reconfigure')


        #self.write('\x1A', lambda transport,data: print("CTRL+z"))


 
        # self.write("ATE0")

        # return



        self.check_connection()


        self.write("ATE0", lambda transport, data: print(
            "hide send at command on response"))
        self.write("AT", lambda transport, data: print("AT callback :)"))
        self.write("ATZ", lambda transport, data: print("Factory reset"))
        self.write("AT+CFUN=1,1", lambda transport, data: time.sleep(5))

        self.write("ATE0", lambda transport, data: print(
            "hide send at command on response"))

        self.write("AT+CMEE=2", lambda transport, data: print("Show errors"))
        self.write("AT+CPIN?", lambda transport, data: print("PIN/SIM status"))

        # Before (mode=1, text):
        #   self.queue.append(QueuedCommand('AT+CMGDA="DEL ALL"', lambda
        #       transport, data: print("Dell All SMS fro memory"))
        # Below is the same, but with mode=0 (numbers)
        self.write(
            'AT+CMGDA=6',
            lambda transport,
            data: print("Dell All SMS fro memory"))

        self.write("AT+GSN", AppHandler.save_serial_number)
        
        #self.write("AT+CNUM", lambda transport, data: print("SIM phone number"))
        self.write("AT+CNUM")
        
        self.write(
            "ATH",
            lambda transport,
            data: print("End call ( if exist ;) )"))
        self.write("ATS0=0", lambda transport, data: print(
            "Automatic connection reception - FALSE"))
        self.write(
            "AT+DDET=1,100,0,0",
            lambda transport,
            data: print("Tone Dialling"))
        self.write("AT+CRSL=0", lambda transport, data: print("Call volume 0"))
        self.write("AT+CLIP=1", lambda transport, data: print("Caller info"))
        self.write(
            'AT+CSCS="UCS2"',
            lambda transport,
            data: print("encoding the message to UCS2"))
        self.write("AT+CMGF=1", lambda transport, data: print(""))
        self.write(
            "AT+CSAS=0",
            lambda transport,
            data: print("for CSMP work..."))
        self.write(
            "AT+CSMP=17,167,2,25",
            lambda transport,
            data: print("utf8 etc...."))
        self.write(
            "AT+CUSD=1",
            lambda transport,
            data: print("card operator message"))

        # Configure GPS
        
        """
        self.write("AT+CGNSPWR=1", lambda transport, data: print(""))
        self.write("AT+CGATT=1", lambda transport, data: print(""))
        self.write(
            'AT+SAPBR=3,1,"CONTYPE","GPRS"',
            lambda transport,
            data: print(""))
        self.write('AT+CGNSSEQ="RMC"', lambda transport, data: print(""))
        self.write("AT+CGPSRST=0", lambda transport, data: print(""))
        """

        self.configure_apn()

        self.write("ATD*101#;", lambda transport, data: print("Reading USSD..."))




        """ Dont remove this command - its verifications :)"""
        self.write("AT", AppHandler.Ready )
        
    def check_connection(self):
        self.write("AT", lambda transport, data: transport.confirm_connection()) 
    def confirm_connection(self):
        self.connection_confirmed = True

    def configure_apn(self):
        #configure mms
        self.write("AT+CMMSINIT", lambda transport, data: print(""))

        if SQL.Get('url_mms_center'):
            self.write(
                'AT+CMMSCURL="' + SQL.Get('url_mms_center') + '"',
                lambda transport,
                data: print(""))

        self.write("AT+CMMSCID=1", lambda transport, data: print(""))


        if SQL.Get('ip_mms_proxy') and SQL.Get('port_mms_proxy'):
            self.write(
                'AT+CMMSPROTO="' + SQL.Get('ip_mms_proxy') + '", ' + SQL.Get('port_mms_proxy'),
                lambda transport,
                data: print(""))

        """self.write(
            'AT+SAPBR=3,1,"Contype","mms"',
            lambda transport,
            data: print(""))"""

        if SQL.Get('apn_name'):
            self.write(
                'AT+SAPBR=3,1,"APN","' + SQL.Get('apn_name') + '"',
                lambda transport,
                data: print(""))

    def connection_made(self, transport):
        """
        Serial port connection made
        """

        print('connection_made')
        self.transport = transport

        logging.debug("send_queued in connection_made")
        self.send_queued()

    def send_queued(self):
        """
        Send next queued command if possible
        """

        if self.next_response_callback:
            return False

        if len(self.queue) == 0:
            return False

        queued_command = self.queue.pop(0)
        self.last_command = queued_command
        self.transport.write(str.encode(queued_command.value) + b'\n')
        
        logging.debug("Command sended: " + queued_command.value )
        
        self.next_response_callback = queued_command.callback
        print("SENT QUEUED COMMAND (" + queued_command.value +  ")")
        time.sleep(1)

        return True

    def answered(self, lines):
        """
        Check if serial already answered to our last command
        """

        if self.next_response_callback:
            print([line for line in lines if self.is_error(line)])
            if 'OK' in lines:
                if self.next_response_callback.__code__.co_argcount == 2:
                    index = lines.index('OK')
                    self.next_response_callback(self, lines[:index])
                    lines = lines[index+1:]
                else:
                    self.next_response_callback(self)
                    lines.remove('OK')

                self.next_response_callback = None
            elif len([line for line in lines if self.is_error(line)]) > 0:
                self.next_response_callback = None
            else:
                return (False, lines)

        return (True, lines)


    def is_error(self, line):
        """
        Check if line is some kind of error
        """

        action = line.split(':', 1)[0]
        if action[0] == '+' and action[-6:] == ' ERROR':
            return True
        return False


    def data_received(self, data):
        """
        New serial data received
        """

        print(data)
        if b'\xFF' in data:
            return
        self.buffer = ('' if self.buffer is None else self.buffer)
        try:
            self.buffer = self.buffer + data.decode('utf-8')
        except ValueError:
            pass

        if SerialReader.TERMINATOR not in data[-len(
                SerialReader.TERMINATOR):]:
            return

        self.buffer = self.buffer.strip()
        lines = [line.strip() for line in self.buffer.split(
            SerialReader.TERMINATOR.decode('utf-8')) if len(line.strip()) > 0]

        has_answered, lines = self.answered(lines)
        if not has_answered:
            return

        self.buffer = None

        if len(lines) == 0:
            logging.debug("send_queued in data_received (if len(lines) == 0)")
            self.send_queued()
            return
            
        print("Received: \n\t" + '\n\t'.join(lines) + "\n")
        logging.debug("data_Received: \n\t" + '\n\t'.join(lines) + "\n")

        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if len(line) == 0:
                continue

            j = i + 1
            while j < len(lines):
                if lines[j].strip()[0] == '+':
                    break
                j = j + 1

            line = '\n'.join(lines[i:j])
            i = j
            print(line)

            parts = line.split(':', 1)
            data = ""
            action = ""

            if len(parts) > 1:
                action = parts[0]
                data = parts[1]
            else:
                data = parts[0]

            if action in self.callbacks:
                for callback in self.callbacks[action]:
                    callback(self, data)
            else:
                print("No callback defined for action '" + action + "'")

        logging.debug("send_queued in data_received")
        self.send_queued()

    def send_sms(self, number, text):
        print(["SEND SMS HANDLER", number, text])
        self.write('AT+CMGS="'+UTF16.encode(number)+'"\n\r' + UTF16.encode(text) + chr(26) )

    def send_sms_from_panel(self, message):
        self.sms_queue_from_panel.append({
            "message": message
        })
        self.send_sms(message['recipient'], message['text'])

    def stop(self):
        print("stop function - todo...")
        #self.transport.terminate()
        