#!/usr/bin/python3

""" 
enlighten.py - Enlighten collector for dreadpi.

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


import logging
import os
import logging.handlers


def fetch(SYS_ID, KEY, USER_ID):

	"""
	Expects login details and system id for the Enlighten API.
	Returns the last known watts reading along with its timestamp.
	Also warns of abnormal system health.
	"""

	# secondary imports here to reduce startup time when this collector is unused.
	import sys
	import urllib.request
	import json
	from lib import support

	ERRORLOG.info("whir whir...")

	# config validation
	if not (
		SYS_ID and KEY and USER_ID and
		support.is_int(SYS_ID) and
		support.is_hex(KEY) and
		support.is_hex(USER_ID) and
		len(SYS_ID) < 10 and
		len(KEY) == 32 and
		len(USER_ID) == 18):
			sys.exit("Unexpected values in Enlighten config. Aborting.")

	# setup
	URL = "https://api.enphaseenergy.com/api/v2/systems/" + SYS_ID + "/summary?key=" + KEY + "&user_id=" + USER_ID
	request = urllib.request.Request(URL)

	# fetch
	try:
		response = urllib.request.urlopen(request)
	except urllib.error.URLError as err:
		sys.exit("Error talking to Enighten: %s" % (err))

	# parse
	result = response.read().decode('utf-8')
	result = json.loads(result)

	# warn if we notice poor system health
	if result['status'] != "normal":
		ERRORLOG.warn("WARNING: Enlighten reports status: %s " % (result['status']))

	# setup timestamp for later
	content_timestamp = result['last_report_at']

	# result
	print(json.dumps(result, sort_keys=True, indent=4))
	watts = str(result['current_power'])

	return watts, content_timestamp


ERRORLOG_FILE = os.path.join(os.sep, 'var', 'log', 'dreadpi.errorlog.txt')
ERRORLOG_FH = logging.handlers.RotatingFileHandler(ERRORLOG_FILE, mode='a', maxBytes=1048576, backupCount=0)
ERRORLOG_FH.setFormatter(logging.Formatter(fmt="%(asctime)s\t%(name)s\t%(message)s"))
ERRORLOG = logging.getLogger(__name__)
ERRORLOG.addHandler(ERRORLOG_FH)
ERRORLOG_CH = logging.StreamHandler()
ERRORLOG_CH.setFormatter(logging.Formatter(fmt="%(name)s\t%(message)s"))
ERRORLOG.addHandler(ERRORLOG_CH)  # print the same thing to stderr
