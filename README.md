# pifi
Wifi provisioning tools for robots with Raspberry Pis.

[![Build Status](https://travis-ci.org/rohbotics/pifi.svg?branch=master)](https://travis-ci.org/rohbotics/pifi)
[![Coverage Status](https://coveralls.io/repos/github/rohbotics/pifi/badge.svg?branch=master)](https://coveralls.io/github/rohbotics/pifi?branch=master)

Pifi uses network manager to do the heavy lifting under the hood.

The command line tool is `pifi`:
```
Usage:
  pifi status                 Shows if the robot is in AP mode or connected to a network
  pifi add <ssid> <password>  Adds a connection to scan/connect to on bootup (needs sudo)
  pifi list seen              Lists the SSIDs that see seen during bootup
  pifi list pending           Lists the SSIDs that still need to configured in NetworkManager
  pifi --version              Prints the version of pifi on your system

Options:
  -h --help    Show a help message
  --version    Show pifi version
```

Pifi runs a script at boot up that does the following:
* Determine if there is Wifi device capable of access point mode
* Scan for visable access points, and save the SSIDs to `/var/lib/pifi/seen_ssids`
* Go through any pending connections in `/var/lib/pifi/pending`, and see if any are visable
* If any of the pending connections are visable, connect to them, and remove them from pending
* Otherwise look for an existing AP mode definiton and start it
* If there is no existing AP mode definition create one with SSID:'UbiquityRobot' and password:'robotseverywhere'

## Connecting to a network while in AP mode
Connect to the Robot's wifi (default UbiquityRobot, password robotseverywhere) on your laptop. 

SSH into the robot with `ssh ubuntu@10.42.0.1`. 

Once logged into the robot, run `sudo pifi add WIFI_SSID PASSWORD`, and reboot `sudo reboot`.

Your robot should now be connected to your network.  

## Installation
The recommended way to install is from debs. The apt source at https://packages.ubiquityrobotics.com/ has the packages.

If that source is configured on your system, simply run `sudo apt install pifi`.

To install from source, run `sudo python3 setup.py install` in the pifi directory after cloning the repo.

## Dependencies
Note: Don't worry about dependencies if you are installing from debs, they will be installed automatically.

This package depends on python3-networkmanager and python3-docopt.

python3-networkmanager is not availible in the standard ubuntu repos, so you will have install it from `pip3 install python-networkmanager`, or use the debian package from https://packages.ubiquityrobotics.com/.

