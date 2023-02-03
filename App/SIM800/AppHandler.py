from ..Utils.UTF16 import UTF16

from ..SQL import SQL

import time

from ..SocketClient import SocketClient

from ..Logger import logger

class AppHandler:
    """
    Class with handlers to events emitted by SerialReader
    """

    def __init__(self, reader):
        """
        Initialize reader and bind callbacks to specified events
        """

        self.reader = reader

        self.reader.bind_event("+CUSD", AppHandler.new_ussd_code)

        self.reader.bind_event("+CMTI", AppHandler.new_msg_incoming)

        self.reader.bind_event("+CMGR", AppHandler.sms_reading)

        self.reader.bind_event("+CNUM", AppHandler.save_my_phone_number)

        self.reader.bind_event("+CMS ERROR", AppHandler.cms_error)
        self.reader.bind_event("+CME ERROR", AppHandler.cms_error)

        self.reader.bind_event("+CMGS", AppHandler.message_sent)

        self.reader.bind_event("NORMAL POWER DOWN", AppHandler.ReaderShutDown)

        self.reader.bind_event("+CSQ", AppHandler.SignalStrength)

        self.reader.bind_event("+CLIP", AppHandler.Ring)

        self.reader.bind_event("+CPIN", AppHandler.cpin)
        
        self.reader.bind_event("+SPIC", AppHandler.RemainingPinOrPukAttempts)



    @staticmethod
    def Ready(transport, data):
        logger.debug("Reader Ready.")
        transport.Ready = True
        #SocketClient.Readers.append(transport)
        
        transport.emit("serial ready")

        """
        Todo ;)
        """
        #SocketClient.SendReadersInfo()


    @staticmethod
    def new_ussd_code(transport, data):
        """
        New ussd code event handler
        """

        logger.debug("NEW USSD CODE :)")
        l = data.split('"')
        if len(l) > 1:
            msg = l[1]
            message = UTF16.decode(msg)
            logger.debug(message)

            transport.emit("ussd received", {
                "data": {
                    "message": message
                }
            })

        else:
            logger.debug("USSD PROBLEM:")
            logger.debug(data)

    @staticmethod
    def new_msg_incoming(transport, data):
        """
        New message (SMS/MMS) received handler
        """

        parts = data.split(",")
        sms_id = parts[1]

        if len(parts) > 2 and "MMS PUSH" in parts[2]:

            logger.debug("NEW MMS INCOMING: " + sms_id)
            logger.debug(parts)
            #return
            if parts[4] != '2' or parts[3] != '2' :
                logger.debug("MMS ostatni argumnet jest inny niz 2: " + parts[4])
                return

            transport.write("AT+SAPBR=1,1", lambda transport,
            data: time.sleep(2))
            transport.write("AT+SAPBR=2,1", lambda transport,
            data: time.sleep(2))
            transport.write("AT+CMMSRECV=" + sms_id)
        else:
            logger.debug("NEW SMS INCOMING: " + sms_id)
            transport.write("AT+CMGR=" + sms_id)

    @staticmethod
    def sms_reading(transport, data):
        """
        Reading sms
        """
        data = data.split('"')
        number = UTF16.decode(data[3].strip())
        date = data[7].replace("'", "")
        t = int(time.time())

        if len(data) >= 8:
            msg = data[8]
            if ord(data[8][0]) == 10:
                msg = msg[1:]
            msg = UTF16.decode(msg)
        else:
            msg = "[EMPTY_MESSAGE]"

        logger.debug("Reading sms...")
        logger.debug(data)
        logger.debug(number)
        logger.debug(date)
        logger.debug(t)
        logger.debug(msg)

        transport.write('AT+CMGDA="DEL READ"', lambda transport, data: logger.debug("Delete all read messages"))

        SQL.add_sms(number, msg, date, t)


        transport.emit("sms received", {
            "data": {
                "from": number,
                "date": date,
                "text": msg,
                "time": t
            }
        })


    @staticmethod
    def cms_error(transport, data):
        """
        Handler for errors
        """

        logger.error('CMS/CME: ' + data + '(after ' + transport.last_command.value + ')')

        if data == "SIM not inserted":
            logger.debug("Sim card not detected...")
            transport.noSimCard()
        elif data == "SIM failure":
            logger.debug("SIM fail... ?!")
            transport.noSimCard()
        elif data == "incorrect password":
            logger.error("Invalid pin code!")
            transport.PinCodeNeeded()

        #transport.last_command.callbackError(transport, data)
        AppHandler.update_message_status_if_exist(transport, False, data)


    @staticmethod
    def save_my_phone_number(transport, data):
        l = data.split('"')
        logger.debug("Save my phone number...")
        logger.debug(l)
        transport.my_phone_number = l[3]

    @staticmethod
    def save_serial_number(transport, data):
        logger.debug(["Serial number", data])
        transport.serial_number = data[0]

    @staticmethod
    def message_sent(transport, data):
        AppHandler.update_message_status_if_exist(transport, True)

    @staticmethod
    def update_message_status_if_exist(transport, success, reason=None):
        if(len(transport.sms_queue_from_panel) > 0):
            data = transport.sms_queue_from_panel.pop(0)
            if(success):
                SocketClient.MessageSentSuccessfully(data['message'])
            else:
                SocketClient.MessageNotSent(data['message'], reason)

    @staticmethod
    def ReaderShutDown(transport, data):
        raise Exception("the device announced that it turned off...")

    @staticmethod
    def SignalStrength(transport, data):
        rssi, ber = data.split(",")

        rssi = int(rssi)

        # <rssi>
        # 0 -115 dBm or less
        # 1 -111 dBm
        # 2...30 -110... -54 dBm
        # 31 -52 dBm or greater
        # 99 not known or not detectable
        
        # <ber> (in percent):
        # 0...7 As RXQUAL values in the table in GSM 05.08 [20] subclause 7.2.4
        # 99 Not known or not detectable

        if rssi == 0:
            db = -115
        elif rssi == 1:
            db = -111
        elif 2 <= rssi <= 30:
            db = -110 + (rssi - 2)
        elif rssi == 31:
            db = -52
        elif rssi == 99:
            #db = "not known or not detectable"
            db = None
        else:
            db = None

        logger.debug("Signal Strength is: " + str(db) + "dBm")

        transport.emit("signal strength", {
            "data": {
                "rssi": db,
                "ber": ber
            }
        })

    @staticmethod
    def Ring(transport, data):

        d = data.split(",")
        logger.debug(d)
        
        #	+CLIP: "+48884167733",145,"",0,"",0
        #145 - incomming call
        # 0 - caller waiting...

        phone = d[0][1:-1]

        logger.debug("Incoming call: " + phone)

        transport.writeOne("AT+CHUP",  lambda transport, data: transport.emit("incoming call rejected", {
            "data": {
                "phone": phone,
            }
        }))


        transport.emit("incoming call", {
            "data": {
                "phone": phone,
            }
        })
    
    @staticmethod
    def cpin(transport, data):
        logger.debug("CPIN Command:")

        transport.InitSimInProgress = False

        if data == "READY":
            transport.ActionAfterSimCardReady()
        elif data == "NOT READY":
            logger.debug("the sim card has been removed")
            transport.noSimCard()
        elif data == "SIM PIN":
            logger.info("PIN Code Required!")
            transport.PinCodeNeeded()
        elif data == "SIM PUK":
            raise Exception("The sim card requires a PUK code. Remove the card, put it in the phone and enter the puk code and preferably remove the pin code.")
        else:
            logger.debug("unknown sim CPIN message: " + data)
            raise Exception("The sim card returned an unknown error, prompting us to stop the application. This error is: '" + data + "'. If you can, contact your administrator and describe the problem. I will be happy to correct it.")

    @staticmethod
    def RemainingPinOrPukAttempts(transport, data):
        logger.debug("RemainingPinOrPukAttempts:")
        d = data.split(",")
        logger.debug(d)

        [pin1, pin2, puk1, puk2] = d
        transport.SaveRemainingPinOrPukAttempts(pin1, pin2, puk1, puk2)




        
