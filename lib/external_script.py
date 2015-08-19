#!/usr/bin/python3

""" 
external_script.py - External_script collector for dreadpi.

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


def fetch(COLLECTION_SCRIPT):

	"""
	Expects an executable command, returns its output, warning of non-zero exit status and stderr.
	Also tries to be shell safe by whitelisting only common characters.
	It does not invoke a shell, but the argument still could.
	"""

	# secondary imports here to reduce startup time when this collector is unused.
	import sys
	import re
	from lib import support

	ERRORLOG.info("capacitors charging...")

	if not COLLECTION_SCRIPT:
		sys.exit("ERROR: collection_script is an empty value.")

	if re.search('[^A-Za-z0-9 _\-\.\/]', COLLECTION_SCRIPT):
		sys.exit("ERROR: collection_script may only contain A-z 0-9 _ - / .")

	# fetch
	exitcode, watts, stderr = support.ex_cmd(COLLECTION_SCRIPT)

	if exitcode != 0:
		ERRORLOG.warn("WARNING: %s return code: %s" % (COLLECTION_SCRIPT, exitcode))
	if stderr:
		ERRORLOG.warn("WARNING: %s returned: %s" % (COLLECTION_SCRIPT, stderr))

	return watts


# logging
ERRORLOG_FILE = os.path.join(os.sep, 'var', 'log', 'dreadpi.errorlog.txt')
ERRORLOG_FH = logging.handlers.RotatingFileHandler(ERRORLOG_FILE, mode='a', maxBytes=1048576, backupCount=0)
ERRORLOG_FH.setFormatter(logging.Formatter(fmt="%(asctime)s\t%(name)s\t%(message)s"))
ERRORLOG = logging.getLogger(__name__)
ERRORLOG.addHandler(ERRORLOG_FH)
ERRORLOG_CH = logging.StreamHandler()
ERRORLOG_CH.setFormatter(logging.Formatter(fmt="%(name)s\t%(message)s"))
ERRORLOG.addHandler(ERRORLOG_CH)  # print the same thing to stderr
