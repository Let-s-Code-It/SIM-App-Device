import argparse

LaunchArguments = {}

def LaunchArgumentsInit():
	global LaunchArguments
	parser = argparse.ArgumentParser()
	parser.add_argument('--webport', help='Port from WebServer (default 8098)', default=8098, type=int)

	parser.add_argument('--authorization', help='0 - does not require logging in, 1 - requires logging in to the site, 2 - requires logging in every time the engine is started (default: 1)', default=1, type=int)
	parser.add_argument('--password', help='Password for logging in to the website (default: admin)', default='admin', type=str)

	parser.add_argument('--dir', help='Local folder with your application data', default=None, type=str)
	
	LaunchArguments = parser.parse_args()
	return LaunchArguments