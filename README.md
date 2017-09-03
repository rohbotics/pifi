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
* Scan for visible access points, and save the SSIDs to `/var/lib/pifi/seen_ssids`
* Go through any pending connections in `/var/lib/pifi/pending`, and see if any are visable
* If any of the pending connections are visible, connect to them, and remove them from pending
* Otherwise look for an existing AP mode definiton and start it
* If there is no existing AP mode definition create one with the configuration in `/etc/pifi/default_ap.em` (SSID:'UbiquityRobot{LAST_4_OF_MAC_ADDRESS}' and password:'robotseverywhere')

## Connecting to a network while in AP mode
Connect to the Robot's wifi (default UbiquityRobot{LAST_4_OF_MAC_ADDRESS}, password robotseverywhere) on your laptop. 

SSH into the robot with `ssh ubuntu@10.42.0.1`. 

Once logged into the robot, run `sudo pifi add WIFI_SSID PASSWORD`, and reboot `sudo reboot`.

Your robot should now be connected to your network.  

## Installation
The recommended way to install is from debs. The apt source at https://packages.ubiquityrobotics.com/ has the packages.

If that source is configured on your system, simply run `sudo apt install pifi`.

To install from source, run `sudo python3 setup.py install` in the pifi directory after cloning the repo.

## Configuration
The settings of the default AP that pifi creates are configurable. `/etc/pifi/default_ap.em` contains and empy template of the json that represents the connection settings.

The varibles passed into the template are the MAC address of the device (mac), and a newly generated UUIDv4 (uuid_str).

This is the default configuration:
```
{
    "connection": {
        "id": "Pifi AP Mode",
        "type": "802-11-wireless",
        "autoconnect": "False",
        "uuid": "@(uuid_str)"
    },

    "802-11-wireless": {
        "mode": "ap",
        "security": "802-11-wireless-security",
        "ssid": "UbiquityRobot@(mac.replace(":", "")[-4:])"
    },

    "802-11-wireless-security": {
        "key-mgmt": "wpa-psk",
        "psk": "robotseverywhere"
    },

    "ipv4": {
        "method": "shared"
    },
    "ipv6": {
        "method": "ignore"
    }
}
```

Empy uses the template format `@()` with python expressions inside of the parenthesis.

The `mac.replace(":", "")[-4:]` gets the last 4 digits of the MAC address after removing colons.

## Dependencies
Note: Don't worry about dependencies if you are installing from debs, they will be installed automatically.

This package depends on python3-networkmanager and python3-docopt.

python3-networkmanager is not availible in the standard ubuntu/debian repos, so you will have install it from `pip3 install python-networkmanager`, or use the debian package from https://packages.ubiquityrobotics.com/. More info [here](debian/build-dependencies.md)

