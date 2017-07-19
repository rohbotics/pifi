"""
pifi

Usage:
  pifi status
  pifi add <ssid> <password>
  pifi list seen
  pifi list pending
  pifi --version

Options:
  -h --help    Show this help
  --version    Show pifi version

"""
from __future__ import print_function
from docopt import docopt

import NetworkManager
import json
import os

def checkCapablities(device_capabilities, capability):
    return device_capabilities & capability == capability

def status():
    ApModeDevice = NetworkManager.Device

    for device in NetworkManager.NetworkManager.GetDevices():
        if device.DeviceType != NetworkManager.NM_DEVICE_TYPE_WIFI:
            continue
        wi_device = device.SpecificDevice()
        supports_ap = checkCapablities(wi_device.WirelessCapabilities,
            NetworkManager.NM_WIFI_DEVICE_CAP_AP)
        if (supports_ap == True):
            print("Network Mangager reports AP mode support on %s" % wi_device.HwAddress)
            ApModeDevice = device

    if (ApModeDevice == NetworkManager.Device):
        print("ERROR: Network Manager reports no AP mode support on any managed device")
        exit(2)
    
    current_connection = ApModeDevice.GetAppliedConnection(0)
    if current_connection[0]['802-11-wireless']['mode'] == "ap":
        print("Device is currently acting as an Access Point")
    else:
        print("Device is connected to %s" % ''.join(current_connection[0]['802-11-wireless']['ssid']))

def add(ssid, password):
    if not os.path.isfile("/etc/pifi_pending"):
        try:
            with open('/etc/pifi_pending', 'w+') as pending_file:
                json.dump([], pending_file)
        except IOError as e:
            print("Error creating /etc/pifi_pending, make sure you are running with sudo") 

    try:
        with open('/etc/pifi_pending', 'r+') as pending_file:    
            pending = json.load(pending_file)
            pending.append({'ssid' : ssid, 'password' : password})
            pending_file.seek(0)  # rewind
            json.dump(pending, pending_file)
            pending_file.truncate()
    except IOError as e:
        print("Error appending to /etc/pifi_pending, make sure you are running with sudo") 

def list_seen():
    with open('/tmp/seen_ssids') as seen_file:
        print(seen_file.read(), end='')

def list_pending():
    with open('/etc/pifi_pending') as pending_file:    
        pending = json.load(pending_file)
        for connection in pending:
            print(connection['ssid'])

def main():
    arguments = docopt(__doc__, version='Pifi Version 0.1.3')
    
    if arguments['status']:
        status()
    if arguments['add']:
        if '<password>' in arguments:
            add(arguments['<ssid>'], arguments['<password>'])
        else:
            add(arguments['<ssid>'], None)
    if arguments['list'] and arguments['seen']:
        list_seen()
    if arguments['list'] and arguments['pending']:
        list_pending()
