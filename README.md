# dreadpi
Demand Response Enabling Device (DRED) for Raspberry Pi.

Dreadpi enables automatic control of air conditioning DRM modes based on your current renewable power generation.
It achieves this by controlling a relay board connected to the RasPi GPIO pins.
This can reduce your grid energy consumption by better aligning your peak load with your peak generation.

Note: DRED is an AU/NZ standard (AS/NZS 4755).

Supported collectors:
* api.enphaseenergy.com (Enlighten API)
* pvoutput.org
* standalone script


#### REQUIREMENTS

* RasPi hardware (You'll be error-bombed if dreadpi can't access the broadcom chip)
* 2x Double Throw Relay module ($3 online) and leads ($1 online).
* Root access (for controlling the broadcom chip)
* Python 3.x
* RPi.GPIO Python 3 module (raspbian package "python3-rpi.gpio")

#### INSTALL

Installs to ./dreadpi/:
```
git clone https://github.com/solikeumyeah/dreadpi.git
```

#### TEST
```
sudo ./dreadpi/dreadpi.py
```

#### CONFIG

At minimum, a data source must be confgured. You'll need to obtain API keys and replace XXX values for the API collectors to work, but you can test with the default 'external_script' setting.
```
dreadpi.cfg
```


#### SCHEDULE

Creating an example cron which captures the last output to a file:
```
echo "*/5 * * * *     root    /root/dreadpi/dreadpi.py > /var/log/dreadpi.lastrun 2>&1" > /etc/cron.d/dreadpi
```
 
#### LOGGING

Critical errors:
````
/var/log/dreadpi.errorlog.txt
````
DRM states (for graphing purposes, states are expressed as a % of max energy use):
````
/var/log/dreadpi.plotlog.txt 
````


#### SECURITY

Because controlling the RasPi GPIO pins requires root access, The following restrictions have been implemented:
* Dreadpi runs all its collectors as the 'nobody' user.
* The external_script filename can not contain most special shell characters.
* Online APIs use hard coded URL prefixes.

Because API keys are read/write, and a potential privacy concern, your config should not be world readable (and obviously not world writeable):
````
sudo chmod 600 dreadpi/dreadpi.cfg
````


#### WIRING

Remove the jumper closing JD-VCC with VCC.

RasPi to relay control pins (low voltage side):	
* PIN1 (3V3)		-> VCC
* PIN2 (5V)  		-> JD-VCC
* PIN6 (GND)		-> GND
* PIN11 (GPIO17)	-> IN1
* PIN13 (GPIO27)	-> IN2
* PIN9 (GND)		-> GND (redundant)

Relay switch pins:
* RLA1-COM		->	DRM-COM.
* RLA2-COM		->	RLA1-NC.
* RLA1-NO		->	DRM2.
* RLA2-NO		->	DRM3.
* RLA2-NC 		-> 	(none) rest position aka drm0.

Disclaimer: This info is provided for educational purposes. I don't condone acting upon it. You should not mess around with high voltage. Your safety is your own responsibility.


#### CONTRIBUTE

You can easily add new collectors. Just drop a .py in the lib directory and have it return a value in watts.
Load it from energy.py like this:
```
from lib import <your collector>
```
And call it like this:
```
elif DATA_SOURCE == "<your collector>":
    watts = <your collector>.<your function>()
```
To be accepted upstream, also:
* Copy/Paste the logging block from another collector (requires import logging and import os).
* Pass your variables from dreadpi.cfg:
```
elif DATA_SOURCE == "<your collector>":
    watts = <your collector>.<your function>(USER, KEY, SYSID)
```
Ideally your collector would also:
* Return a POSIX content timestamp:
```
elif DATA_SOURCE == "<your collector>":
    watts, content_timestamp = <your collector>.<your function>(USER, KEY, SYSID)
```
* Perform exception handling and health warnings as per existing examples.
* Have well commented code.

Note: collectors must be able to run as 'nobody'.

