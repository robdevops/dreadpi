#!/usr/bin/python3

""" 
pvoutput.py - PVOutput collector for dreadpi.

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


def fetch(KEY, SYS_ID):

	"""
	Expects login key and system id for the PVOutput API.
	Returns the last known watts reading along with its timestamp.
	Also warns if the API limit is close.
	"""

	# secondary imports here to reduce startup time when this collector is unused.
	import sys
	import time
	import urllib.request
	import json
	from lib import support

	ERRORLOG.info("bleep bloop bleep...")

	# config validation
	if not (
		KEY and SYS_ID and
		support.is_hex(KEY) and
		support.is_int(SYS_ID) and
		len(KEY) == 40 and
		len(SYS_ID) < 10):
			sys.exit("Error: unexpected values in PVOutput config.")

	# setup
	URL = "http://pvoutput.org/service/r2/getstatus.jsp"
	request = urllib.request.Request(URL)
	request.add_header('X-Rate-Limit', '1')
	request.add_header('X-Pvoutput-Apikey', KEY)
	request.add_header('X-Pvoutput-SystemId', SYS_ID)

	# fetch
	try:
		response = urllib.request.urlopen(request)
	except urllib.error.URLError as err:
		sys.exit("Error talking to PvOutput: %s" % (err))

	# parse/compile body
	content = response.read().decode('utf-8')
	content = content.split(",")
	pv_keys = ['date', 'time', 'watt_hour_total', 'watts', 'watt_hour_used', 'watts_using', 'efficiency', 'temperature', 'voltage']
	content = dict(zip(pv_keys, content))

	# compile/parse headers
	headers = dict(response.info().items())
	limit_left = int(headers['X-Rate-Limit-Remaining'])
	limit_reset = float(headers['X-Rate-Limit-Reset'])
	limit_reset = time.strftime('%H:%M', time.localtime(limit_reset))

	# warn if we notice imminent API throttle
	if limit_left < 10:
		ERRORLOG.warn("WARNING: You are %s requests from the PVOutput API limit. Resets at %s." % (limit_left, limit_reset))

	# setup timestamp for later
	content_timestamp = content['date'] + content['time']
	content_timestamp = time.mktime(time.strptime(content_timestamp, "%Y%m%d%H:%M"))

	# result
	print(json.dumps(content, sort_keys=True, indent=4))
	watts = content['watts']

	return watts, content_timestamp


# logging
ERRORLOG_FILE = os.path.join(os.sep, 'var', 'log', 'dreadpi.errorlog.txt')
ERRORLOG_FH = logging.handlers.RotatingFileHandler(ERRORLOG_FILE, mode='a', maxBytes=1048576, backupCount=0)
ERRORLOG_FH.setFormatter(logging.Formatter(fmt="%(asctime)s\t%(name)s\t%(message)s"))
ERRORLOG = logging.getLogger(__name__)
ERRORLOG.addHandler(ERRORLOG_FH)
ERRORLOG_CH = logging.StreamHandler()
ERRORLOG_CH.setFormatter(logging.Formatter(fmt="%(name)s\t%(message)s"))
ERRORLOG.addHandler(ERRORLOG_CH)  # print the same thing to stderr
