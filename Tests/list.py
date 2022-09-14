import serial.tools.list_ports

ports = serial.tools.list_ports.comports()
for port in ports:
	print(port[0], port[1], port[2])