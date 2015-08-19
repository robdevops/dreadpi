#!/usr/bin/python3

""" 
support.py - Support module for dreadpi. Provides some basic reusable functions for other modules.

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


def is_hex(HEX_MAYBE):

	""" Checks if a string could be expressed in hexidecimal. """

	try:
		int(HEX_MAYBE, 16)
		return True
	except ValueError:
		return False


def is_int(INTEGER_MAYBE):

	""" Checks if a string could be expressed as an integer. '"""

	try:
		int(INTEGER_MAYBE)
		return True
	except ValueError:
		return False


def is_posix_time(POSIX_TIME_MAYBE):
	
	""" Checks if a string matches POSIX time format """

	# secondary imports here to reduce startup time when this function is unused.
	import time
	
	try:
		time.localtime(POSIX_TIME_MAYBE)
		return True
	except ValueError:
		return False


def ex_cmd(COMMAND_LINE):

	"""
	Quotes and executes an external command in Python's safest way.
	Returns exit code, stdout, stderr.
	"""

	# secondary imports here to reduce startup time when this function is unused.
	import shlex
	from subprocess import Popen, PIPE

	quoted_command = shlex.split(COMMAND_LINE)
	proc = Popen(quoted_command, stdout=PIPE, stderr=PIPE)

	stdout, stderr = proc.communicate()
	exitcode = proc.returncode

	stdout = stdout.decode('utf-8')
	stdout = stdout.strip()

	stderr = stderr.decode('utf-8')
	stderr = stderr.strip()

	return exitcode, stdout, stderr


def drop_privileges(uid_name='nobody', gid_name='nogroup'):
	
	""" Drops privs to 'nobody' user for the lifetime of the calling module. """

	# secondary imports here to reduce startup time when this function is unused.
	import os
	import pwd
	import grp

	desired_gid = grp.getgrnam(gid_name).gr_gid
	desired_uid = pwd.getpwnam(uid_name).pw_uid

	os.setgroups([])
	os.setgid(desired_gid)
	os.setuid(desired_uid)


