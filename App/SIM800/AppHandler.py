from ..Utils.UTF16 import UTF16

from ..SQL import SQL

import time

from ..SocketClient import SocketClient

import logging

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



    @staticmethod
    def Ready(transport, data):
        print("Reader Ready.")
        transport.Ready = True
        SocketClient.Readers.append(transport)
        SocketClient.SendReadersInfo()


    @staticmethod
    def new_ussd_code(transport, data):
        """
        New ussd code event handler
        """

        print("NEW USSD CODE :)")
        l = data.split('"')
        if len(l) > 1:
            msg = l[1]
            message = UTF16.decode(msg)
            print(message)

            SocketClient.emit("ussd received", {
                "sim": transport.info,
                "data": {
                    "message": message
                }
            })

        else:
            print("USSD PROBLEM:")
            print(data)

    @staticmethod
    def new_msg_incoming(transport, data):
        """
        New message (SMS/MMS) received handler
        """

        parts = data.split(",")
        sms_id = parts[1]

        if len(parts) > 2 and "MMS PUSH" in parts[2]:

            print("NEW MMS INCOMING: " + sms_id)
            print(parts)
            #return
            if parts[4] != '2' or parts[3] != '2' :
                print("MMS ostatni argumnet jest inny niz 2: " + parts[4])
                return

            transport.write("AT+SAPBR=1,1", lambda transport,
            data: time.sleep(2))
            transport.write("AT+SAPBR=2,1", lambda transport,
            data: time.sleep(2))
            transport.write("AT+CMMSRECV=" + sms_id)
        else:
            print("NEW SMS INCOMING: " + sms_id)
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

        print("Reading sms...")
        print(data)
        print(number)
        print(date)
        print(t)
        print(msg)

        transport.write('AT+CMGDA="DEL READ"', lambda transport, data: print("Delete all read messages"))

        SQL.add_sms(number, msg, date, t)


        SocketClient.emit("sms received", {
            "sim": transport.info,
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

        print("Blont: " + data + ", po wykonaniu: " + transport.last_command.value + " :)")

        logging.error('CMS/CME: ' + data + '(after ' + transport.last_command.value + ')')

        #transport.last_command.callbackError(transport, data)
        AppHandler.update_message_status_if_exist(transport, False, data)


    @staticmethod
    def save_my_phone_number(transport, data):
        l = data.split('"')
        print("Save my phone number...")
        print(l)
        transport.info['my_phone_number'] = l[3]

    @staticmethod
    def save_serial_number(transport, data):
        print(["Serial number", data])
        transport.info['serial_number'] = data[0]

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