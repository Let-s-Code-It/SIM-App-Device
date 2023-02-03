from serial.threaded import ReaderThread, Protocol
from collections import namedtuple
import time

from .AppHandler import AppHandler

from ..Utils.UTF16 import UTF16

from ..SocketClient import SocketClient

from ..SQL import SQL

QueuedCommand = namedtuple('QueuedCommand', ['value', 'callback'])

from ..Logger import logger



class SerialReader(Protocol):
    """
    Serial port reader customized to communicate with SIM800
    """

    TERMINATOR = b'\r\n'

    def __init__(self):
        """
        Initialize default data and event handlers
        """
        self.transport = None

        self.InitSimInProgress = False

        SocketClient.Readers.append(self)

        self.init()

    def init(self, restored=False):

        print('-')
        print('-')
        print('-')
        print('-')
        print('-')
        print('-')
        print('-')
        print('-')
        print('-')
        print('-')
        print('-')
        print('-')
        print('-')
        print('-')
        print('-')

        self.Ready = False

        self.queue = []
        self.callbacks = {}
        self.handler = AppHandler(self)
        self.last_command = None
        self.next_response_callback = None
        
        self.buffer = None

        self.connection_confirmed = restored

        self.FirstLoop = True

        self.simCardDetected = True

        self.PinCodeRequired = False

        self.availablePinAttempts = None

        self.sms_queue_from_panel = []

        self.serial_number = ''
        self.my_phone_number = ''

        if restored:
            self.emit("serial connection confirmed")

        self.reconfigure()

    def GetInfo(self):
        return {
            'my_phone_number': self.my_phone_number,
            'port_name': SQL.Get('port_name'),
            'port_friendly_name': SQL.Get('port_friendly_name'),
            'serial_number': self.serial_number,
            'serial_port_responds': self.connection_confirmed,
            'sim_card_detected': self.simCardDetected,
            'pin_code_required': self.PinCodeRequired,
            'serial_port_ready': self.Ready
        }

    def emit(self, title, message={}):
        message['sim'] = self.GetInfo()
        return SocketClient.emit(title, message)

    def bind_event(self, event, callback):
        """
        Bind new handler for given event
        """

        logger.debug('bind_event')
        if event not in self.callbacks:
            self.callbacks[event] = [callback]
        else:
            self.callbacks[event].append(callback)

    def write(self, data, callback=None):
        """
        Add new queued command
        """

        logger.debug("New queued command (" + data +  ")")
        if not callback:
            def callback(transport):
                return None

        self.queue.append(QueuedCommand(data, callback))

        if self.transport:
            logger.debug("send_queued in write")
            self.send_queued()

    def writeOne(self, data, callback=None):
        if not any(item.value == data for item in self.queue):
            self.write(data, callback)

    def writeAbsolutely(self, data, callback=None):
        
        logger.debug("Absolute sending of the command: " + data)
        
        self.next_response_callback = callback
        self.last_command = data
        self.transport.write(str.encode(data) + b'\n')

    def reconfigure(self):
        """
        Reconfigure SIM800 with our default settings
        """

        logger.debug('reconfigure')


        #self.write('\x1A', lambda transport,data: print("CTRL+z"))


 
        # self.write("ATE0")

        # return


        self.check_connection()


        self.write("ATE0", lambda transport, data: logger.debug(
            "hide send at command on response"))
        self.write("AT", lambda transport, data: logger.debug("AT callback :)"))
        self.write("ATZ", lambda transport, data: logger.debug("Factory reset"))

        self.write("AT+CFUN=1,1", lambda transport, data: time.sleep(5))

        self.write("ATE0", lambda transport, data: logger.debug(
            "hide send at command on response"))

        self.write("AT+CMEE=2", lambda transport, data: logger.debug("Show errors"))

        #self.write("AT+CPIN?", lambda transport, data: self.simCardInserted(data))
        self.write("AT+CPIN?")

        
    def check_connection(self):
        self.write("AT", lambda transport, data: transport.confirm_connection()) 
    def confirm_connection(self):
        self.connection_confirmed = True
        self.emit("serial connection confirmed")
        logger.debug("Connection confirmed")

    def configure_apn(self):
        #configure mms
        self.write("AT+CMMSINIT", lambda transport, data: logger.debug(""))

        if SQL.Get('url_mms_center'):
            self.write(
                'AT+CMMSCURL="' + SQL.Get('url_mms_center') + '"',
                lambda transport,
                data: logger.debug(""))

        self.write("AT+CMMSCID=1", lambda transport, data: logger.debug(""))


        if SQL.Get('ip_mms_proxy') and SQL.Get('port_mms_proxy'):
            self.write(
                'AT+CMMSPROTO="' + SQL.Get('ip_mms_proxy') + '", ' + SQL.Get('port_mms_proxy'),
                lambda transport,
                data: logger.debug(""))

        """self.write(
            'AT+SAPBR=3,1,"Contype","mms"',
            lambda transport,
            data: print(""))"""

        if SQL.Get('apn_name'):
            self.write(
                'AT+SAPBR=3,1,"APN","' + SQL.Get('apn_name') + '"',
                lambda transport,
                data: logger.debug(""))

    def connection_made(self, transport):
        """
        Serial port connection made
        """

        logger.debug('connection_made')
        self.transport = transport


        #CTRL+Z
        self.transport.write(str.encode('\x1A'))
        time.sleep(1)

        

        logger.debug("send_queued in connection_made")
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

        self.next_response_callback = queued_command.callback

        self.last_command = queued_command
        self.transport.write(str.encode(queued_command.value) + b'\n')
        
        logger.debug("Command sended: " + queued_command.value )
        
        #^^^^^^^
        #self.next_response_callback = queued_command.callback
        
        logger.debug("SENT QUEUED COMMAND (" + queued_command.value +  ")")
        time.sleep(1)

        return True

    def answered(self, lines):
        """
        Check if serial already answered to our last command
        """

        if self.next_response_callback:
            logger.debug([line for line in lines if self.is_error(line)])
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

        logger.debug("New serial data received...")

        logger.debug(data)
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
            logger.debug("send_queued in data_received (if len(lines) == 0)")
            self.send_queued()
            return
            
        #print("Received: \n\t" + '\n\t'.join(lines) + "\n")
        logger.debug("data_Received: \n\t" + '\n\t'.join(lines) + "\n")

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

            print(parts)

            if len(parts) > 1:
                action = parts[0]
                data = parts[1]
            else:
                #data = parts[0]
                action = parts[0]

            if action in self.callbacks:
                for callback in self.callbacks[action]:
                    callback(self, data.strip())
            else:
                logger.debug("No callback defined for action '" + action + "'")

        logger.debug("send_queued in data_received")
        self.send_queued()

    def send_sms(self, number, text):
        logger.debug(["SEND SMS HANDLER", number, text])
        self.write('AT+CMGS="'+UTF16.encode(number)+'"\n\r' + UTF16.encode(text) + chr(26) )

    def send_sms_from_panel(self, message):
        self.sms_queue_from_panel.append({
            "message": message
        })
        self.send_sms(message['recipient'], message['text'])

    def stop(self):
        logger.debug("stop function - todo...")
        #self.transport.terminate()

    def loop(self):
        #necessarily at the beginning!!
        time.sleep(10)

        if not self.connection_confirmed:
            logger.debug("Connection with serial port not confirmed!!")
            self.writeAbsolutely("AT", lambda transport, data: self.init(restored=True))
            if self.FirstLoop:
                self.FirstLoop = False
                self.simCardDetected = False
                self.emit("serial connection not confirmed")
        elif not self.simCardDetected:
            if not self.InitSimInProgress:
                self.InitSimInProgress = True
                logger.debug("Check sim card status again....")
                self.writeOne("AT+CFUN=1,1", lambda transport, data: self.InitSim(data))
                #self.writeOne("AT+CPIN?", lambda transport, data: print("TEST -> CPIN", data))
            else:
                logger.debug("Check sim card - loop blocked, becouse init sim card in progress :)")
        elif self.Ready:
            #check signal strength
            self.writeOne("AT+CSQ")

        #socket keep alive
        self.keepAlive()
        
        logger.debug("Reader loop :)")

    def keepAlive(self):
        if not SocketClient.IsConnected():
            SocketClient.keepAliveLastSentTime = 0
        elif SocketClient.keepAliveLastSentTime == 0 or (time.time() - SocketClient.keepAliveLastSentTime) < 120:
            if SocketClient.keepAliveLastSentTime == 0:
                SocketClient.keepAliveLastSentTime = time.time()
            logger.debug("Keep alive time: " + str(time.time() - SocketClient.keepAliveLastSentTime))
            self.emit("keep alive")
        else:
            SocketClient.keepAliveLastSentTime = 0
            SocketClient.Disconnect()
            SocketClient.Connect()
            logger.info("Socket restart - keep alive limit...")

    def noSimCard(self):
        logger.debug("noSimCard method...")
        self.simCardDetected = False
        self.InitSimInProgress = False
        self.emit("sim card not detected")

    def InitSim(self, data):
        time.sleep(10)

        self.write("ATE0", lambda transport, data: logger.debug(
            "hide send at command on response"))

        self.write("AT+CMEE=2", lambda transport, data: logger.debug("Show errors"))

        self.write("AT+CPIN?")

    def ActionAfterSimCardReady(self):
        logger.debug("SIM CARD READY :)")

        self.simCardDetected = True
        self.PinCodeRequired = False

        self.emit("sim card detected")

        #self.write('AT+CLCK="SC",1,"1234",1')

        # Before (mode=1, text):
        #   self.queue.append(QueuedCommand('AT+CMGDA="DEL ALL"', lambda
        #       transport, data: print("Dell All SMS fro memory"))
        # Below is the same, but with mode=0 (numbers)
        self.write(
            'AT+CMGDA=6',
            lambda transport,
            data: logger.debug("Dell All SMS fro memory"))

        """
        Save Device serial number
        """
        self.write("AT+GSN", AppHandler.save_serial_number)


        """
        End call if exist
        """
        self.write(
            "ATH",
            lambda transport,
            data: logger.debug("End call ( if exist ;) )"))


        """
        Disable Automatic connection reception
        """
        self.write("ATS0=0", lambda transport, data: logger.debug(
            "Automatic connection reception - FALSE"))


        """
        Define Tone Dialing
        """
        self.write(
            "AT+DDET=1,100,0,0",
            lambda transport,
            data: logger.debug("Tone Dialling"))
        

        """
        Incomming call ringtone volume -> 0
        """
        self.write("AT+CRSL=0", lambda transport, data: logger.debug("Call volume 0"))

        
        """
        show data about caller  - phone number etc
        """
        self.write("AT+CLIP=1", lambda transport, data: logger.debug("Caller info"))


        """
        specific SMS text format
        """
        self.write(
            'AT+CSCS="UCS2"',
            lambda transport,
            data: logger.debug("encoding the message to UCS2"))

        #self.write("AT+CNUM", lambda transport, data: print("SIM phone number"))
        self.write("AT+CNUM")

        
        self.write("AT+CMGF=1", lambda transport, data: logger.debug(""))
        self.write(
            "AT+CSAS=0",
            lambda transport,
            data: logger.debug("for CSMP work..."))
        self.write(
            "AT+CSMP=17,167,2,25",
            lambda transport,
            data: logger.debug("utf8 etc...."))
        self.write(
            "AT+CUSD=1",
            lambda transport,
            data: logger.debug("card operator message"))

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

        #self.write("ATD*101#;", lambda transport, data: logger.debug("Reading USSD..."))

        """ Dont remove this command - its verifications :)"""
        self.write("AT", AppHandler.Ready )

    def PinCodeNeeded(self):
        self.simCardDetected = True
        #self.PinCodeRequired = True
        self.emit("sim card detected")
        
        self.write('AT+SPIC')

    def SaveRemainingPinOrPukAttempts(self, pin1, pin2, puk1, puk2):
        logger.debug("availablePinAttempts:" + pin1)
        self.availablePinAttempts = pin1

        if pin1 == '3':
            logger.debug("you have the maximum number of attempts to enter the pin code")
            saved_pin = SQL.Get('pin_code')
            if len(saved_pin) > 1:
                logger.debug("Trying to use pin code: " + saved_pin)
                return self.UsePinCode(saved_pin)
            else:
                logger.error("you have not saved your pin code")
        else:
            logger.error("You do not have the maximum number of pin code attempts available")

        self.PinCodeRequired = True

        self.emit("pin code required")

    def SavePinCode(self, pin):
        SQL.Set("pin_code", pin )
        logger.debug("Save pin code: " + pin)

        if self.availablePinAttempts != None and self.PinCodeRequired:
            logger.debug("i'm trying to unlock with the pin you just typed in the form")
            self.UsePinCode(pin)

    def UsePinCode(self, pin):
        logger.debug("UsePinCode -> " + pin)
        self.write('AT+CPIN="' + pin + '"')