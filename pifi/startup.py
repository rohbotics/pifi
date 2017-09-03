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

    ApModeDevice, ClientModeDevice = nm.select_devices(pifi_conf_settings)

    print("Using %s for AP mode support" % ApModeDevice.Interface)
    print("Using %s for wifi client mode" % ClientModeDevice.Interface)

    var_io.writeSeenSSIDs(nm.seenSSIDs([ClientModeDevice]))
 
    # Allow 30 seconds for network manager to sort itself out
    time.sleep(30)

    if (ClientModeDevice.State == NetworkManager.NM_DEVICE_STATE_ACTIVATED):
        print("Client Device currently connected to: %s" 
            % ClientModeDevice.SpecificDevice().ActiveAccessPoint.Ssid)
        return
    else:
        print("Device is not connected to any network, Looking for pending connections")

        pending = var_io.readPendingConnections()

        # Try to pick a connection to use, if none found, just continue
        try:
            # Use the best connection
            best_ap, best_con = nm.selectConnection(nm.availibleConnections(ClientModeDevice, pending))

            print("Connecting to %s" % best_con['802-11-wireless']['ssid'])
            NetworkManager.NetworkManager.AddAndActivateConnection(best_con, ClientModeDevice, best_ap)
            
            new_pending = var_io.readPendingConnections().remove(best_con)
            var_io.writePendingConnections(new_pending)
            return
        except ValueError:
            pass
		
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
