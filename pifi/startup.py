# Wait a bit before starting
import time
time.sleep(5)

import NetworkManager

import uuid
import json

def getSeenSSIDs(device):
    aps = dict()

    for ap in device.SpecificDevice().GetAccessPoints():
        aps[ap.Ssid] = ap

    return aps

def writeSeenSSIDs(aps):
    target = open('/tmp/seen_ssids', 'w')
    target.truncate()

    for ssids in aps:
        target.write('%-30s \n' % (aps[ssids].Ssid))

def readPendingConnections():
    try:    
        pending_file = open('/etc/pifi_pending', 'r')
        return json.load(pending_file)
    except IOError:
        return dict()

def checkCapablities(device_capabilities, capability):
    return device_capabilities & capability == capability

def getAvailiblePendingConnection(seenSSIDs, pendingConnections):
    for ssid in seenSSIDs:
        for pcon in pendingConnections:
            if ssid == pcon['ssid']:
                return pcon

def main():
    ApModeDevice = NetworkManager.Device

    for device in NetworkManager.NetworkManager.GetDevices():
        if device.DeviceType != NetworkManager.NM_DEVICE_TYPE_WIFI:
            continue
        wi_device = device.SpecificDevice()
        supports_ap = checkCapablities(wi_device.WirelessCapabilities, 
            NetworkManager.NM_WIFI_DEVICE_CAP_AP)
        if (supports_ap == True):
            print "Network Mangager reports AP mode support on %s" % wi_device.HwAddress
            ApModeDevice = device

    if (ApModeDevice == NetworkManager.Device):
        print "ERROR: Network Manager reports no AP mode support on any managed device"
        exit(2)

    seenSSIDs = getSeenSSIDs(ApModeDevice)
    writeSeenSSIDs(seenSSIDs)
    pendingConnections = readPendingConnections()   
 
    # Allow 30 seconds for network manager to sort itself out
    time.sleep(30)

    if (ApModeDevice.State == 100):
        print("Device currently connected to: %s" 
            % ApModeDevice.SpecificDevice().ActiveAccessPoint.Ssid)
    else:
        print "Device is not connected to any network, Looking for pending connections"

        new_ap_connection = getAvailiblePendingConnection(seenSSIDs, pendingConnections)
        if new_ap_connection is not None:
            connection_uuid = str(uuid.uuid4())

            settings = {
                'connection': {
                    'id': new_ap_connection['ssid'],
                    'type': '802-11-wireless',
                    'autoconnect': True,
                    'uuid': connection_uuid
                },

                '802-11-wireless': {
                    'mode': 'infrastructure',
                    'security': '802-11-wireless-security',
                    'ssid': new_ap_connection['ssid']
                },

                '802-11-wireless-security': {
                    'key-mgmt': 'wpa-psk',
                    'psk': new_ap_connection['password']
                },

                'ipv4': {'method': 'auto'},
                'ipv6': {'method': 'auto'}
            }
            
            print "Connecting to %s" % new_ap_connection['ssid']
            NetworkManager.NetworkManager.AddAndActivateConnection(settings, ApModeDevice, "/")
            
            pendingConnections.remove(new_ap_connection) 
            pending_file = open('/etc/pifi_pending', 'w')
            pending_file.truncate()
            pending_file.write(json.dumps(pendingConnections))
            return
		
        print "No SSIDs assoicated with pending connections found, Starting AP mode"

        found_connection = False
        existing_connection = NetworkManager.Settings.Connection

        print "Looking for existing AP mode connection"
        for connection in NetworkManager.Settings.ListConnections():
            settings = connection.GetSettings()
            if '802-11-wireless' in settings:
                if settings['802-11-wireless']['mode'] == 'ap':
                  found_connection = True
                  existing_connection = connection
                  break

        if found_connection:
            print "Found existing AP mode connection, SSID: %s" % \
                existing_connection.GetSettings()['802-11-wireless']['ssid']

            print "Initializing AP Mode"
            NetworkManager.NetworkManager.ActivateConnection(existing_connection, ApModeDevice, existing_connection)
        else:
            print "No existing AP mode connections found"
            print "Creating new default AP mode connection"
            connection_uuid = str(uuid.uuid4())

            settings = {
                'connection': {
                    'id': 'Hotspot',
                    'type': '802-11-wireless',
                    'autoconnect': False,
                    'uuid': connection_uuid
                },

                '802-11-wireless': {
                    'mode': 'ap',
                    'security': '802-11-wireless-security',
                    'ssid': 'UbiquityRobot'
                },

                '802-11-wireless-security': {
                    'key-mgmt': 'wpa-psk',
                    'psk': 'robotseverywhere'
                },

                'ipv4': {'method': 'shared'},
                'ipv6': {'method': 'ignore'}
            }

            print "Initializing AP Mode"
            NetworkManager.NetworkManager.AddAndActivateConnection(settings, ApModeDevice, "/")
