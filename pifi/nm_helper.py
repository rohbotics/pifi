"""
This module has helper methods for Network Manager that helps
keep the rest of the code simpler.

It wraps python-networkmanager.
"""

import NetworkManager

def checkCapablities(device_capabilities, capability):
    return device_capabilities & capability == capability

def managedWifiDevices(NetworkManager=NetworkManager):
    """
    Generator that yields Wifi devices managed by NetworkManager.

    Does not return 'specific devices' call SpecificDevice() to get one.
    """
    for device in NetworkManager.NetworkManager.GetDevices():
        if device.DeviceType == NetworkManager.NM_DEVICE_TYPE_WIFI:
            yield device

def managedAPCapableDevices(NetworkManager=NetworkManager):
    """
    Generator that yields AP capable Wifi devices managed by NetworkManager.

    Does not return 'specific devices' call SpecificDevice() to get one.
    """
    for device in managedWifiDevices(NetworkManager=NetworkManager):
        wi_device = device.SpecificDevice()
        supports_ap = checkCapablities(wi_device.WirelessCapabilities,
            NetworkManager.NM_WIFI_DEVICE_CAP_AP)
        if (supports_ap == True):
            yield device

def seenSSIDs(devices):
    for device in devices:
        for ap in device.SpecificDevice().GetAccessPoints():
            yield ap.Ssid

def availibleConnections(device, connections):
    access_points = device.SpecificDevice().GetAccessPoints()
    for ap in access_points:
        for con in connections:
            if ap.Ssid == con['802-11-wireless']['ssid']:
                yield (ap, con)

def selectConnection(availible_connections):
    """
    Select the best Access Point and connection based on signal strength

    Return a tuple of (AccessPoint, Connection)
    """
    max_strength = 0
    for ap, con in availible_connections:
        if ap.Strength > max_strength:
            max_strength = ap.Strength
            return (ap, con)
    raise RuntimeError("No connections in availible_connections could be found")

def existingAPConnections(NetworkManager=NetworkManager):
    for connection in NetworkManager.Settings.ListConnections():
        settings = connection.GetSettings()
        if '802-11-wireless' in settings:
            if settings['802-11-wireless']['mode'] == 'ap':
                yield connection
              