"""
This module handles all of the pifi files in /var

The files in /var are the pending connections file, and the seen SSIDs file
"""

# This file uses python3 features, python3 is required

seen_SSIDs_path = "/var/lib/pifi/seen_ssids"
pending_path = "/var/lib/pifi/pending"

import os

def ensureDir(file_path):
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

def writeSeenSSIDs(aps):
    try:
        with open(seen_SSIDs_path, 'w+') as seen_file:
            seen_file.truncate()
            for ssids in aps:
                seen_file.write('%-30s \n' % (aps[ssids].Ssid))
    except FileNotFoundError:
        ensureDir(pending_path)

def readPendingConnections():
    try:
        with open(pending_path, 'r') as pending_file:
            return json.load(pending_file)
    except FileNotFoundError:
        return list()

def writePendingConnections(pending):
    try:
        with open(pending_path, 'w+') as pending_file:
            pending_file.seek(0)  # rewind
            json.dump(pending, pending_file)
            pending_file.truncate()
    except FileNotFoundError:
        ensureDir(pending_path)