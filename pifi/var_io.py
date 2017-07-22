"""
This module handles all of the pifi files in /var

The files in /var are the pending connections file, and the seen SSIDs file
"""

# This file uses python3 features, python3 is required

seen_SSIDs_path = "/var/lib/pifi/seen_ssids"
pending_path = "/var/lib/pifi/pending"

import os
import json

def ensureDir(file_path):
    directory = os.path.dirname(file_path)
    try: 
        os.makedirs(directory)
    except FileExistsError:
        pass

def readSeenSSIDs():
    try:
        with open(seen_SSIDs_path) as seen_file:
            seen_ssids = seen_file.readlines()
            seen_ssids = [ssid.strip() for ssid in seen_ssids] 
            return seen_ssids
    except FileNotFoundError:
        return list()

def writeSeenSSIDs(ssids):
    ensureDir(seen_SSIDs_path)
    with open(seen_SSIDs_path, 'w+') as seen_file:
        seen_file.truncate()
        for ssid in ssids:
            seen_file.write('%-30s \n' % (ssid))

def readPendingConnections():
    try:
        with open(pending_path, 'r') as pending_file:
            return json.load(pending_file)
    except FileNotFoundError:
        return list()

def writePendingConnections(pending):
    ensureDir(pending_path)
    with open(pending_path, 'w+') as pending_file:
        pending_file.seek(0)  # rewind
        json.dump(pending, pending_file)
        pending_file.truncate()