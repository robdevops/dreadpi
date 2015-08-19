#!/usr/bin/python3

"""
energy.py - Energy module for dreadpi. Abstracts any knowledge of data sources from main program.

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


import configparser
import sys
import os
from lib import support
from lib import enlighten
from lib import pvoutput
from lib import external_script


CFG_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'dreadpi.cfg'))
CFG = configparser.ConfigParser()
CFG.read(CFG_FILE)


def get(DATA_SOURCE):

	"""
	Expects a data source. 
	Reads config file, and if appropriate config exists, drops priv then calls the applicable data collector.
	Returns a value in watts along with optional fields.
	"""

	support.drop_privileges()  # especially important for "external_script" in case of world writable configs.
	content_timestamp = None  # collectors should modify this where available.

	if DATA_SOURCE == "enlighten":

		try:
			SYS_ID = CFG['ENLIGHTEN']['sys_id']
			KEY = CFG['ENLIGHTEN']['key']
			USER_ID = CFG['ENLIGHTEN']['user_id']
		except KeyError:
			sys.exit("Error: Enlighten config not found.")

		watts, content_timestamp = enlighten.fetch(SYS_ID, KEY, USER_ID)

	elif DATA_SOURCE == "pvoutput":

		try:
			KEY = CFG['PVOUTPUT']['key']
			SYS_ID = CFG['PVOUTPUT']['sys_id']
		except KeyError:
			sys.exit("Error: PvOutput config not found.")

		watts, content_timestamp = pvoutput.fetch(KEY, SYS_ID)

	elif DATA_SOURCE == "external_script":

		try:
			COLLECTION_SCRIPT = CFG['EXTERNAL_SCRIPT']['collection_script']
		except KeyError:
			sys.exit("ERROR: collection_script not found in config.")

		watts = external_script.fetch(COLLECTION_SCRIPT)

	else:

		sys.exit("ERROR: No known energy source requested.")

	return watts, content_timestamp
