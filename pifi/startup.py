# Wait a bit before starting
import time
time.sleep(5)

import NetworkManager

import uuid
import json

import pifi.nm_helper as nm
import pifi.var_io as var_io
import pifi.etc_io as etc_io

def main():
    pifi_conf_settings = etc_io.get_conf()

    # Expirimental dual wifi support
    ApModeDevice = NetworkManager.Device # Device used for AP mode
    ClientModeDevice = NetworkManager.Device # Device for connecting out

    for device in nm.managedAPCapableDevices():
        print("Using %s for AP mode support" % device.Interface)
        ApModeDevice = device
        break # Use first device for now

    if (ApModeDevice == NetworkManager.Device):
        print("ERROR: Could not get a AP capable device from NetworkManager")
        exit(2)

    for device in nm.managedWifiDevices():
        print("Using %s for wifi client mode" % device.Interface)
        ClientModeDevice = device
        break # Use first device for now

    if (ClientModeDevice == NetworkManager.Device):
        print("ERROR: Could not get a wifi client device to use from NetworkManager")
        exit(2)

    var_io.writeSeenSSIDs(nm.seenSSIDs([ClientModeDevice]))
 
    # Allow 30 seconds for network manager to sort itself out
    # time.sleep(30)

    if (ClientModeDevice.State == NetworkManager.NM_DEVICE_STATE_ACTIVATED):
        print("Client Device currently connected to: %s" 
            % ClientModeDevice.SpecificDevice().ActiveAccessPoint.Ssid)
        return
    else:
        print("Device is not connected to any network, Looking for pending connections")

        pending = var_io.readPendingConnections()
        # We can't use the generator directly because we want len, so we use list()
        availible_connections = list(nm.availibleConnections(ClientModeDevice, pending))

        if len(availible_connections) >= 1:
            # Use the best connection
            best_ap, best_con = nm.selectConnection(availible_connections)

            print("Connecting to %s" % best_con['802-11-wireless']['ssid'])
            NetworkManager.NetworkManager.AddAndActivateConnection(best_con, ClientModeDevice, best_ap)
            
            new_pending = var_io.readPendingConnections().remove(best_con)
            var_io.writePendingConnections(new_pending)
            return
		
        # If we reach this point, we gave up on Client mode
        print("No SSIDs from pending connections found, Starting AP mode")

        if pifi_conf_settings['delete_existing_ap_connections'] == False:
            print("Looking for existing AP mode connection")

            for connection in nm.existingAPConnections():
                print("Found existing AP mode connection, SSID: %s" % 
                    connection.GetSettings()['802-11-wireless']['ssid'])
                print("Initializing AP Mode")
                NetworkManager.NetworkManager.ActivateConnection(connection, ApModeDevice, "/")
                return # We don't acutally want to loop, just use the first iter
        else:
            for connection in nm.existingAPConnections():
                print("Deleting existing AP mode connection, SSID: %s" % 
                    connection.GetSettings()['802-11-wireless']['ssid'])
                connection.Delete()

        print("No existing AP mode connections found")
        print("Creating new default AP mode connection with config:")

        # Default AP mode connection
        settings = etc_io.get_default_ap_conf(ApModeDevice.HwAddress)
        print(json.dumps(settings, indent=1)) ## Pretty Print settings

        print("Initializing AP Mode")
        NetworkManager.NetworkManager.AddAndActivateConnection(settings, ApModeDevice, "/")
