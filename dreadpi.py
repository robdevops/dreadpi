#!/usr/bin/python3

"""
dreadpi.py - DreadPi - Demand Response Enabling Device (DRED) for Raspberry Pi.

Electricity bill reduction by signalling air conditioner DRM based on your renewable energy output.
See README for details.

Copyright 2015 Robert Stevens

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

"""


import sys
import os
import socket
import logging
import logging.handlers
import time
import configparser
import json  # this instance as a pretty printer
import RPi.GPIO as GPIO
from lib import energy
from lib import support

# logging is noisy to configure :/
LOGFORMAT = logging.Formatter(fmt="%(asctime)s\t%(message)s")
ERRORLOG_FILE=os.path.join(os.sep, 'var', 'log', 'dreadpi.errorlog.txt')
ERRORLOG_FH = logging.handlers.RotatingFileHandler(ERRORLOG_FILE, mode='a', maxBytes=1048576, backupCount=0)
ERRORLOG_FH.setFormatter(LOGFORMAT)
ERRORLOG = logging.getLogger('errorlog')
ERRORLOG.addHandler(ERRORLOG_FH)
ERRORLOG_CH = logging.StreamHandler()
ERRORLOG.addHandler(ERRORLOG_CH)  # print the same thing to stderr
PLOTLOG_FILE = os.path.join(os.sep, 'var', 'log', 'dreadpi.plotlog.txt')
PLOTLOG_FH = logging.handlers.RotatingFileHandler(PLOTLOG_FILE, mode='a', maxBytes=5242880, backupCount=2)
PLOTLOG_FH.setFormatter(LOGFORMAT)
PLOTLOG = logging.getLogger('statelog')
PLOTLOG.addHandler(PLOTLOG_FH)
PLOTLOG.setLevel(logging.INFO)


def main():

	""" main program in a function as per module convention """

	# show previous state
	pins_before = [GPIO.input(p) for p in PIN_ORDER]
	drm = drm_get(pins_before)
	pin_values = dict(zip(PIN_ORDER, pins_before))
	print("Previous pin states: (DRM%s)" % (drm))
	print(json.dumps(pin_values, sort_keys=True, indent=4))

	# fetch energy reading
	watts, content_timestamp = energy.get(DATA_SOURCE)

	# validate energy reading
	try:
		watts = int(watts)
	except ValueError:
		abort("ERROR: energy reading: %s is not a number. Aborting with DRM0." % (watts))

	if watts < 0:
		abort("ERROR: invalid energy reading: %s. Aborting with DRM0." % (watts))

	# check freshness if applicable
	if content_timestamp:
		freshness_check(content_timestamp)

	# mode select
	if watts >= 0 and watts < THRESHOLD_LOW:
		print("Energy: %s W. DRM2 desired." % (watts))
		GPIO.output(PIN_ORDER, (1, 0))
		PLOTLOG.info(50)

	elif watts >= THRESHOLD_LOW and watts < THRESHOLD_HIGH:
		print("Energy: %s W. DRM3 desired." % (watts))
		GPIO.output(PIN_ORDER, (0, 1))
		PLOTLOG.info(75)

	elif watts >= THRESHOLD_HIGH:
		print("Energy: %s W. DRM0 desired." % (watts))
		GPIO.output(PIN_ORDER, (0, 0))
		PLOTLOG.info(100)

	else:
		abort("ERROR: fell through main logic! Aborting with DRM0. Watts is: %s" % (watts))

	# show changes if applicable
	pins_after = [GPIO.input(p) for p in PIN_ORDER]
	if pins_before != pins_after:
		drm = drm_get(pins_after)
		pin_values = dict(zip(PIN_ORDER, pins_after))
		print("Confirming new pin states: (DRM%s)." % (drm))
		print(json.dumps(pin_values, sort_keys=True, indent=4))


def freshness_check(content_timestamp):

	""" expects a POSIX timestamp, warns if it's old. """

	if support.is_posix_time(content_timestamp):
		now = time.time()
		freshness = now - content_timestamp
		if freshness < 0:
			ERRORLOG.warn("WARNING: Freshness is negative. Crossing timezones/incorrect time on local/source system(s).")
		elif freshness > FRESHNESS_TIME:
			abort("Energy source data is {0:.1f} mins old. Aborting with DRM0.".format(freshness / 60))
	else: 
		ERRORLOG.warn("Can't check timestamp; not in POSIX format.")


def drm_get(io_current):

	""" expects a list of GPIO pins, returns user friendly DRM representation """

	if io_current == [1, 0]:
		return 2
	elif io_current == [0, 1]:
		return 3
	elif io_current == [0, 0]:
		return 0
	else:
		abort("ERROR: unknown pin state: %s" % (io_current))


def abort(reason):

	""" 
	Shutdown process for critical failures.
	Requires a reason.
	"""

	ERRORLOG.error("%s" % (reason))
	GPIO.output(PIN_ORDER, (0, 0))
	PLOTLOG.info(100)
	sys.exit()


## setup ##

# config
CFG_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), 'dreadpi.cfg'))
CFG = configparser.ConfigParser()
CFG.read(CFG_FILE)
ME = os.path.basename(__file__)

try:
	THRESHOLD_LOW = int(CFG['MAIN']['THRESHOLD_LOW'])
	THRESHOLD_HIGH = int(CFG['MAIN']['THRESHOLD_HIGH'])
	PIN_ORDER = list(int(p) for p in CFG['HARDWARE']['pin_order'].split())
	DATA_SOURCE = CFG['MAIN']['data_source']
	FRESHNESS_TIME = int(CFG['MAIN']['freshness_time'])
except KeyError:
	sys.exit("Error: Basic config missing.")
if not (
	THRESHOLD_LOW and THRESHOLD_HIGH and PIN_ORDER and
	THRESHOLD_LOW > 0 and
	THRESHOLD_HIGH > THRESHOLD_LOW and
	len(PIN_ORDER) == 2):
		sys.exit("Error: Failed basic config check.")


# am I already running?
global LOCK_SOCKET  # global else garbage collected
LOCK_SOCKET = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
try:
	LOCK_SOCKET.bind('\0' + ME)
except socket.error:
	ERRORLOG.error("ERROR: Another instance is running. Aborting.")
	sys.exit()


# Initiate hardware
GPIO.setwarnings(False)  # required because our pin state persists between runs.
GPIO.setmode(GPIO.BOARD)
GPIO.setup(PIN_ORDER, GPIO.OUT)


if __name__ == '__main__':
	main()
