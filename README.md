# dreadpi
Demand Response Enabling Device (DRED) for Raspberry Pi.


INTRO

Dreadpi enables automatic control of air conditioning DRM modes based on your current renewable power generation.
It achieves this by controlling a relay board connected to the RasPi GPIO pins.
This can reduce your grid energy consumption by better aligning your peak load with your peak generation.

Supported collectors:
api.enphaseenergy.com
pvoutput.org
standalone script


SYSTEM REQUIREMENTS

* RasPi hardware (dreadpi will throw errors if it can't access the broadcom chip)
* 2x Double Throw Relay module ($3 online) and leads ($1 online).
* Root access (for controlling the broadcom chip)
* Python 3.x
* RPi.GPIO Python Module (raspbian package "python3-rpi.gpio")


CONFIG

At minimum, a data source must be confgured in /root/dreadpi/dreadpi.cfg


SCHEDULE

* echo "*/5 * * * *     root    /root/dreadpi.py > dreadpi.lastrun 2>&1" > /etc/cron.d/dreadpi

 
LOGGING

Critical errors:	/var/log/dreadpi.errorlog.txt
DRM states:	/var/log/dreadpi.plotlog.txt (expressed as a % of max energy use: DRM0/2/3=100/50/75%)


SECURITY

Because controlling the RasPi GPIO pins requires root access, The following restrictions have been implemented:
* Dreadpi runs all its collectors as the 'nobody' user.
* The external_script filename can not contain most special shell characters.
* Online APIs use hard coded URL prefixes.

Because API keys are read/write, your config should not be world readable (and obviously not world writeable):
	* sudo chmod 600 /root/dreadpi/dreadpi.cfg


WIRING

(a) Remove the jumper closing JD-VCC with VCC.

(b) RasPi to relay control pins (low voltage side):	
PIN1 (3V3)		  -> VCC
PIN2 (5V)  		  -> JD-VCC
PIN6 (GND)		  -> GND
PIN11 (GPIO17)	-> IN1
PIN13 (GPIO27)  -> IN2
PIN9 (GND)		  -> GND (redundant)

(c) Relay switch pins:
RLA1-COM		->	DRM-COM.
RLA2-COM		->	RLA1-NC.
RLA1-NO		  ->	DRM2.
RLA2-NO		  ->	DRM3.
RLA2-NC 		-> 	(none) rest position aka drm0.


CONTRIBUTE

Collectors:
You can easily add new collectors. Just drop a .py in the lib directory and have it return a value in watts.
Load it from energy.py like this:
	from lib import <your collector>
	
And call it from energy.py like this:
	elif DATA_SOURCE == "<your collector>":
		watts = <your collector>.<your function>()

To be accepted upstream, also:
* Copy/Paste the logging block from another collector.
* Have energy.py pass your variables from the existing config:
	watts = <your collector>.<your function>(USER, KEY, SYSID)

Ideally your collector would also:
* Return a POSIX content timestamp:
	watts, content_timestamp = <your collector>.<your function>(USER, KEY, SYSID)
* Perform exception handling and health warnings as per existing examples.
* Have well commented code.

Note: collectors must be able to run as 'nobody'.

