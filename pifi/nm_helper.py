"""
This module has helper methods for Network Manager that helps
keep the rest of the code simpler.

It wraps python-networkmanager.
"""

import NetworkManager

def checkCapablities(device_capabilities, capability):
    return device_capabilities & capability == capability

def managedWifiDevices():
    for device in NetworkManager.NetworkManager.GetDevices():
        if device.DeviceType == NetworkManager.NM_DEVICE_TYPE_WIFI:
            yield device

def managedAPCapableDevices():
    for device in managedWifiDevices():
        wi_device = device.SpecificDevice()
        supports_ap = checkCapablities(wi_device.WirelessCapabilities,
            NetworkManager.NM_WIFI_DEVICE_CAP_AP)
        if (supports_ap == True):
            yield device

def seenSSIDs(device):
    for ap in device.SpecificDevice().GetAccessPoints():
        yield ap.Ssid