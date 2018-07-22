"""
This module has helper methods for Network Manager that helps
keep the rest of the code simpler.

It wraps python-networkmanager.
"""

import NetworkManager

def checkCapablities(device_capabilities, capability):
    return device_capabilities & capability == capability


def is_wireless_device(device, NetworkManager=NetworkManager):
    return (device.DeviceType == NetworkManager.NM_DEVICE_TYPE_WIFI)

def is_ap_capable(device, NetworkManager=NetworkManager):
    wi_device = device.SpecificDevice()
    supports_ap = checkCapablities(wi_device.WirelessCapabilities,
        NetworkManager.NM_WIFI_DEVICE_CAP_AP)
    return supports_ap

def get_device_by_name(name, NetworkManager=NetworkManager):
    """
    Get device my the interface name.

    Does not yeild 'specific devices' call SpecificDevice() to get one.
    """
    return NetworkManager.NetworkManager.GetDeviceByIpIface(name)

def managedWifiDevices(NetworkManager=NetworkManager):
    """
    Generator that yields Wifi devices managed by NetworkManager.

    Does not yeild 'specific devices' call SpecificDevice() to get one.
    """
    for device in NetworkManager.NetworkManager.GetDevices():
        if is_wireless_device(device, NetworkManager=NetworkManager):
            yield device

def managedAPCapableDevices(NetworkManager=NetworkManager):
    """
    Generator that yields AP capable Wifi devices managed by NetworkManager.

    Does not yeild 'specific devices' call SpecificDevice() to get one.
    """
    for device in managedWifiDevices(NetworkManager=NetworkManager):
        if is_ap_capable(device, NetworkManager=NetworkManager):
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
    best = None
    for ap, con in availible_connections:
        if ap.Strength > max_strength:
            max_strength = ap.Strength
            best = (ap, con)

    if best is not None:
        return best
    else:
        raise ValueError("No connections in availible_connections could be found")

def existingAPConnections(NetworkManager=NetworkManager):
    for connection in NetworkManager.Settings.ListConnections():
        settings = connection.GetSettings()
        if '802-11-wireless' in settings:
            if settings['802-11-wireless']['mode'] == 'ap':
                yield connection

def existingConnections(NetworkManager=NetworkManager):
    for connection in NetworkManager.Settings.ListConnections():
        settings = connection.GetSettings()
        if '802-11-wireless' in settings:
            if settings['802-11-wireless']['mode'] != 'ap':
                yield connection

def select_devices(pifi_conf, NetworkManager=NetworkManager):
    """
    Select the ap mode device and client mode devices to use

    returns a tuple of (ap_device, client_device)
    """
    devices = list(managedWifiDevices(NetworkManager=NetworkManager))

    ap_device = None
    client_device = None

    # Fail immediately if no devices
    if len(devices) == 0:
        raise RuntimeError("No NetworkManager managed devices")

    # If a specific ap_device is specified, use it if it is ap capable
    if pifi_conf['ap_device'] != 'any':
        ap_device = get_device_by_name(pifi_conf['ap_device'], 
            NetworkManager=NetworkManager)

        assert is_ap_capable(ap_device, NetworkManager=NetworkManager), \
            "Specified ap_device %s is not ap capable" % pifi_conf['ap_device']

    # If a specific client_device is specified, use it if it is wireless
    if pifi_conf['client_device'] != 'any':
        client_device = get_device_by_name(pifi_conf['client_device'], 
            NetworkManager=NetworkManager)

        assert is_wireless_device(client_device, NetworkManager=NetworkManager), \
            "Specified client_device %s is not wireless" % pifi_conf['client_device']

    # If ap_device can be any, use the first one that isn't the same as client_device
    if pifi_conf['ap_device'] == 'any':
        for device in managedAPCapableDevices(NetworkManager=NetworkManager):
            ap_device = device
            if client_device is not None and (client_device.Interface == ap_device.Interface):
                continue
            else:
                break

    # If client_device can be any, use the first one that isn't the same as ap_device
    # If all are the same, use ay of them
    if pifi_conf['client_device'] == 'any':
        for device in devices:
            client_device = device
            if (client_device.Interface == ap_device.Interface):
                continue
            else:
                break

    if (ap_device is not None) and (client_device is not None):
        return (ap_device, client_device)