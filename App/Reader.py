from serial import Serial, SerialException
from serial.threaded import ReaderThread


from .SIM800.SerialReader import SerialReader

from .SQL import SQL


from threading import Thread

import time

from .SQL import SQL

import serial.tools.list_ports

Reader = None

from .Logger import logger

logger.debug("Reader.py - LOADED")

def start_reader():

	global Reader

	TryOtherPorts = True

	PortName = SQL.Get('port_name')
	PortFriendlyName = SQL.Get('port_friendly_name')

	while(True):
		try:
			serial_port = Serial(PortName, baudrate=115200)
			Reader = ReaderThread(serial_port, SerialReader)

			Reader.start()
			Reader._connection_made.wait()

			logger.debug("Serial port READY.")

			while Reader.is_alive():
				#logger.debug("ReaderThread (SIM): Is alive :)")
				GetReader().protocol.loop()
			
			logger.debug("ReaderThread is DEAD :c")

			#serial_port.close()
			break

		except SerialException:
			Reader = None
			logger.debug(" !!! ---> Reader not created! (wrong serial port)")

			if TryOtherPorts and PortFriendlyName != "":
				for port in serial.tools.list_ports.comports():
					if port[1] == PortFriendlyName:
						PortName = port[0]
						logger.debug("Serial port connection error: Trying other port -> " + PortName + "("+port[1]+")")
						return

			PortName = SQL.Get('port_name')

		finally:
			time.sleep(10)



def GetReader():
	global Reader
	return Reader


CreateReader = Thread(target=start_reader)


