from .App.LaunchArguments import LaunchArguments



import os
__APPLICATION_PATH__ = os.path.dirname(__file__)

if LaunchArguments.dir:
	__APPLICATION_DATA__ = LaunchArguments.dir
else:
	__APPLICATION_DATA__ = os.path.join(__APPLICATION_PATH__, "Data")


if not os.path.exists(__APPLICATION_DATA__):
	os.makedirs(__APPLICATION_DATA__)


print("application data file path", __APPLICATION_DATA__)


__APPLICATION_MD5SUM__ = os.path.join(__APPLICATION_PATH__, 'md5sum.txt')
__APPLICATION_DATABASE_PATH__ = os.path.join(__APPLICATION_DATA__, "sim.db")

__DEFAULT_CONTROLLER_SOCKET__ 	= 'https://panel.sim-app.ovh/engine'
__PYPI_PACKAGE_NAME__ 			= 'lci-sim-app-device'
__AUTHOR_PAGE__ 				= 'https://github.com/Let-s-Code-It/SIM-App-Device'
__HOW_TO_UPDATE_PAGE__			= 'https://github.com/Let-s-Code-It/SIM-App-Device'

import importlib_metadata as metadata
try:
	__VERSION__ = metadata.version(__PYPI_PACKAGE_NAME__)
except:
	__VERSION__ = "0.0.0"

__CONSOLE_LOGS_PATH__ = os.path.join(__APPLICATION_DATA__, 'logs')

"""
ENV FILE
"""
from dotenv import load_dotenv
load_dotenv()

__SERIAL_LOOP_ENABLED__ = os.getenv('SerialLoopEnabled', '1') == '1'


__WEB_PORT__ = LaunchArguments.webport


__ADMIN_AUTHORIZATION_ENABLED__ = LaunchArguments.authorization
__ADMIN_PASSWORD__ = LaunchArguments.password if LaunchArguments.password != '' else os.getenv('AdminPassword', '') if os.getenv('AdminPassword', '') != '' else 'admin'

from time import time
__LAUNCH_DATE__ = time()