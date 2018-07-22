"""
pifi

Usage:
  pifi status
  pifi add <ssid> [<password>]
  pifi remove <ssid>
  pifi list seen
  pifi list pending
  pifi set-hostname <hostname>
  pifi --version

Options:
  -h --help    Show this help
  --version    Show pifi version

"""
from docopt import docopt

import NetworkManager
import json
import os, sys, socket

import pifi.nm_helper as nm
import pifi.var_io as var_io
import pifi.etc_io as etc_io

import uuid


def query_yes_no(question, default="no"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")


def status(nm=nm):
    devices = 0

    for ApModeDevice in nm.managedAPCapableDevices():
        devices += 1
        print("Network Mangager reports AP mode support on %s" % ApModeDevice.Interface)
        if ApModeDevice.State != 100:
            print("Device is not activated")
            exit(0)
        current_connection = ApModeDevice.GetAppliedConnection(0)
        if current_connection[0]['802-11-wireless']['mode'] == "ap":
            print("Device is currently acting as an Access Point")
        else:
            ssid = current_connection[0]['802-11-wireless']['ssid']
            ssid = bytearray([ord(byte) for byte in ssid])
            print("Device is connected to %s" % ssid.decode("utf-8"))

    if (devices == 0):
        print("ERROR: Network Manager reports no AP mode support on any managed device")
        exit(2)

def add(ssid, password, var_io=var_io):
    if etc_io.get_hostname() == "ubiquityrobot":
        print("WARN: Please use `pifi set-hostname` to change the hostname before connecting")

    pending = var_io.readPendingConnections()

    if password is not None:
        new_connection = {
                'connection': {
                    'id': str(ssid),
                    'type': '802-11-wireless',
                    'autoconnect': True,
                    'uuid': str(uuid.uuid4())
                },

                '802-11-wireless': {
                    'mode': 'infrastructure',
                    'security': '802-11-wireless-security',
                    'ssid': ssid
                },

                '802-11-wireless-security': {
                    'key-mgmt': 'wpa-psk', # We only support WPA2-PSK networks for now
                    'psk': password
                },

                'ipv4': {'method': 'auto'},
                'ipv6': {'method': 'auto'}
        }

    else:
        new_connection = {
                'connection': {
                    'id': str(ssid),
                    'type': '802-11-wireless',
                    'autoconnect': True,
                    'uuid': str(uuid.uuid4())
                },

                '802-11-wireless': {
                    'mode': 'infrastructure',
                    'ssid': ssid
                },

                'ipv4': {'method': 'auto'},
                'ipv6': {'method': 'auto'}
        }


    pending.append(new_connection)

    try:
        var_io.writePendingConnections(pending)
    except PermissionError:
        print("Error writing to /var/lib/pifi/pending, make sure you are running with sudo")

def remove(ssid):
    for device in nm.managedWifiDevices():
        if device.State == NetworkManager.NM_DEVICE_STATE_ACTIVATED:
            current_connection = device.GetAppliedConnection(0)
            # SSID returned as list of bytes
            if ssid == b''.join(current_connection[0]['802-11-wireless']['ssid']).decode("utf-8"):
                print("WARN: Connection is currently active")
                print("WARN: Deleting can disrupt existing SSH connetions")
                if query_yes_no("Continue Deletion?") == False:
                    return

    pending = var_io.readPendingConnections()
    for con in pending:
        if ssid == con['802-11-wireless']['ssid']:
            pending.remove(con)

    try:
        var_io.writePendingConnections(pending)
    except PermissionError:
        print("Error writing to /var/lib/pifi/pending, make sure you are running with sudo")
        return

    for con in nm.existingConnections():
        settings = con.GetSettings()
        if ssid == settings['802-11-wireless']['ssid']:
            con.Delete()


def list_seen():
    for ssid in var_io.readSeenSSIDs():
        print(ssid)

def list_pending():
    for con in var_io.readPendingConnections():
        try:
            print(con['802-11-wireless']['ssid'])
        except KeyError:
            print("WARN: Found non wireless pending connection: %s" % 
                    con['connection']['id'])


def set_hostname(new_hostname):
    old_hostname = etc_io.get_hostname()
    print("Changing hostname from %s to %s" % (old_hostname, new_hostname))

    try:
        etc_io.set_hostname(old_hostname, new_hostname)
        socket.sethostname(new_hostname)
    except PermissionError:
        print("Error writing to /etc/hosts or /etc/hostname, make sure you are running with sudo")
    except OSError:
        print("Error writing to /etc/hosts or /etc/hostname, make sure you are running with sudo")

def main(argv=sys.argv[1:]):
    arguments = docopt(__doc__, argv=argv, version='pifi version 0.5.3')
    
    if arguments['status']:
        status()
    if arguments['add']:
        if '<password>' is not None:
            add(arguments['<ssid>'], arguments['<password>'])
        else:
            add(arguments['<ssid>'], None)
    if arguments['remove']:
        if '<password>' is not None:
            remove(arguments['<ssid>'])    
    if arguments['list'] and arguments['seen']:
        list_seen()
    if arguments['list'] and arguments['pending']:
        list_pending()
    if arguments['set-hostname']:
        set_hostname(arguments['<hostname>'])
