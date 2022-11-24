import sqlite3
import os

import time

import threading

from .Logger import logger

from ..Config import __APPLICATION_DATA__, __DEFAULT_CONTROLLER_SOCKET__, __APPLICATION_DATABASE_PATH__

lock = threading.Lock()




CONFIG_PREFIX = "device_1_"

class SQL():

	conn = None

	c = None

	RequestInQueue = False


	@staticmethod
	def Init():

		SQL.conn = sqlite3.connect(__APPLICATION_DATABASE_PATH__, check_same_thread=False)
		SQL.c = SQL.conn.cursor()

		logger.debug("DB CONNECTED")

		if os.stat(__APPLICATION_DATABASE_PATH__).st_size == 0:
			logger.debug("Configure data base...")
			SQL.c.execute('CREATE TABLE sms (row_id INTEGER PRIMARY KEY, number, text, date, time)')
			SQL.c.execute('CREATE TABLE mms (row_id INTEGER PRIMARY KEY, number, date, time, unique_id, file BLOB, file_type, file_name)')
			SQL.c.execute('CREATE TABLE incomming_calls (row_id INTEGER PRIMARY KEY, number, status, date, time)')

			SQL.c.execute('CREATE TABLE config (row_id INTEGER PRIMARY KEY, name, value, date)')
			SQL.c.execute('CREATE UNIQUE INDEX name ON config(name)')

			SQL.conn.commit()

			SQL.Set('socket_address', __DEFAULT_CONTROLLER_SOCKET__)

	"""
	@staticmethod
	def QueueWait():
		while(SQL.RequestInQueue):
			time.sleep(0.3)
		
		SQL.RequestInQueue = True
	"""
	@staticmethod
	def execute(sql, ar=None):

		try:
			lock.acquire(True)

			#SQL.QueueWait()

			SQL.c.execute(sql, ar)
			SQL.conn.commit()

			#SQL.RequestInQueue = False

		finally:
			lock.release()


	@staticmethod
	def select(sql, ar=None):

		try:

			lock.acquire(True)

			#SQL.QueueWait()

			#print(["SQL SELECT -> ", sql, ar])

			SQL.c.execute(sql, ar)

			R = SQL.c.fetchall()

			#SQL.RequestInQueue = False
		finally:
			lock.release()
			return R



	@staticmethod
	def Set(key, value):
		t = time.time()
		SQL.execute("INSERT OR replace INTO config VALUES (null, ?, ?, ?)", (CONFIG_PREFIX + key, value, t))

	@staticmethod
	def Get(key):
		r = SQL.select("SELECT value FROM config WHERE name = ?", [CONFIG_PREFIX  + key])
		if r:
			return r[0][0]
		return ""




	@staticmethod
	def add_sms(number, text, date, t):
		SQL.execute("INSERT INTO sms VALUES (null, ?, ?, ?, ?)", (number , text , date, t))