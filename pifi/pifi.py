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
from docopt import docopt

import NetworkManager
import json
import os

import pifi.nm_helper as nm
import pifi.var_io as var_io

def status():
    ApModeDevice = NetworkManager.Device

    for device in nm.managedAPCapableDevices():
        wi_device = device.SpecificDevice()
        print("Network Mangager reports AP mode support on %s" % wi_device.HwAddress)
        ApModeDevice = device
        current_connection = ApModeDevice.GetAppliedConnection(0)
        if current_connection[0]['802-11-wireless']['mode'] == "ap":
            print("Device is currently acting as an Access Point")
        else:
            ssid = current_connection[0]['802-11-wireless']['ssid']
            ssid = bytearray([ord(byte) for byte in ssid])
            print("Device is connected to %s" % ssid.decode("utf-8"))

    if (ApModeDevice == NetworkManager.Device):
        print("ERROR: Network Manager reports no AP mode support on any managed device")
        exit(2)

def add(ssid, password):
    try:
        pending = var_io.readPendingConnections()
        pending.append({'ssid' : ssid, 'password' : password})
        var_io.writePendingConnections(pending)
    except PermissionError:
        print("Error writing to /var/lib/pifi/pending, make sure you are running with sudo")

def list_seen():
    with open('/tmp/seen_ssids') as seen_file:
        print(seen_file.read(), end='')

def list_pending():
    with open('/etc/pifi_pending') as pending_file:    
        pending = json.load(pending_file)
        for connection in pending:
            print(connection['ssid'])

def main():
    arguments = docopt(__doc__, version='pifi version 0.1.3')
    
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
