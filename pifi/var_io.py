"""
This module handles all of the pifi files in /var

The files in /var are the pending connections file, and the seen SSIDs file
"""

# This file requires python3, due to better more detailed exceptions


seen_SSIDs_path = "/var/lib/pifi/seen_ssids"
pending_path = "/var/lib/pifi/pending"

# Used for debugging
# seen_SSIDs_path = "/tmp/pifi/seen_ssids"
# pending_path = "/tmp/pifi/pending"

import os
import json

def ensureDir(file_path):
    """
    Takes a path to a file, and creates the parent directory if it doen't exist.
    """
    directory = os.path.dirname(file_path)
    try: 
        os.makedirs(directory)
    except FileExistsError:
        pass

def readSeenSSIDs(open=open):
    """
    Returns a list of strings containg the ssids in seen_SSIDs_path.
    One line of the file is one ssid.
    """
    try:
        with open(seen_SSIDs_path) as seen_file:
            seen_ssids = seen_file.readlines()
            seen_ssids = [ssid.strip() for ssid in seen_ssids] 
            return seen_ssids
    except FileNotFoundError:
        return list()

def writeSeenSSIDs(ssids, open=open, ensureDir=ensureDir):
    """
    Takes a list of ssids and writes them to seen_SSIDs_path.
    One ssid per line.
    """
    ensureDir(seen_SSIDs_path)
    with open(seen_SSIDs_path, 'w+') as seen_file:
        seen_file.truncate()
        for ssid in ssids:
            seen_file.write('%s\n' % (ssid))

def readPendingConnections(open=open):
    """
    Returns a list parsed from the json in the file pending_path.
    """
    try:
        with open(pending_path, 'r') as pending_file:
            try:
                pending_connections = json.load(pending_file)
            except ValueError:
                print ("WARN failed to decode json in %s, ignoring" % pending_path)
                return list()
            if not isinstance(pending_connections, list):
                raise ValueError("%s does not contain a json list" % pending_path)
            return pending_connections
    except FileNotFoundError:
        return list()

def writePendingConnections(pending, open=open, ensureDir=ensureDir):
    """
    Takes a list of dicts and writes the json representation to pending_path.
    """
    ensureDir(pending_path)
    with open(pending_path, 'w+') as pending_file:
        pending_file.seek(0)  # rewind
        if pending is not None:
            json.dump(pending, pending_file)
        else:
            json.dump(list(), pending_file)
        pending_file.truncate()