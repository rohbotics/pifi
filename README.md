# pifi
Wifi tools for Robots with Raspberry Pis

Currently this is a script that runs at bootup and does the following:
* Determine if there is Wifi device capable of access point mode
* Scan for visable access points, and save the SSIDs to `/tmp/seen_ssids`
* Go through any pending connections in `/etc/pifi_pending`, and see if any are visable
* If any of the pending connections are visable, connect to them, and remove them from pending
* Otherwise look for an existing AP mode definiton and start it
* If there is no existing AP mode definition create one with SSID:'UbiquityRobot' and password:'robotseverywhere'

## Installation
The recommended way to install is from debs. The apt source at https://packages.ubiquityrobotics.com/ has the packages.

If that source is configured on your system, simply run `sudo apt install pifi`.

## Dependencies
Note: Don't worry about dependancies if you are installing from debs, they will be installed automatically.

This package depends on python-networkmanager.

## Connecting to a network while in AP mode
Add a connection to the JSON file `/etc/pifi_pending` manually for now.

This is an example:
```
[
{"ssid" : "EXAMPLE_WIFI", "password" : "WIFI_PASSWORD"}
]
