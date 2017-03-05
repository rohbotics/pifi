import NetworkManager

import uuid

def checkCapablities(device_capabilities, capability):
    return device_capabilities & capability == capability

ApModeDevice = NetworkManager.Device

for device in NetworkManager.NetworkManager.GetDevices():
    if device.DeviceType != NetworkManager.NM_DEVICE_TYPE_WIFI:
        continue
    wi_device = device.SpecificDevice()
    supports_ap = checkCapablities(wi_device.WirelessCapabilities, 
        NetworkManager.NM_WIFI_DEVICE_CAP_AP)
    if (supports_ap == True):
        print("Network Mangager reports AP mode support on %s" % wi_device.HwAddress)
        ApModeDevice = device

if (ApModeDevice == NetworkManager.Device):
    print("ERROR: Network Manager reports no AP mode support on any managed device")
    exit(2)

if (ApModeDevice.State == 100):
    print("Device currently connected to: %s" 
        % ApModeDevice.SpecificDevice().ActiveAccessPoint.Ssid)
else:
    print("Device is not connected to any network, Start AP mode")

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

    # NetworkManager.Settings.AddConnection(settings)

    # connection = NetworkManager.Settings.GetConnectionByUuid(connection_uuid)
    NetworkManager.NetworkManager.AddAndActivateConnection(settings, device, "/")