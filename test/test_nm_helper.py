import unittest
from unittest import mock
from io import StringIO
import os, sys

sys.modules['NetworkManager'] = mock.MagicMock()
import pifi.nm_helper as nm_helper

class NMHelperTests(unittest.TestCase):

    def test_managed_wifi_devices_no_devices(self):
        nm = mock.MagicMock()
        nm.configure_mock(**{'NetworkManager.GetDevices.return_value': list()})

        generator = nm_helper.managedWifiDevices(NetworkManager=nm)
        with self.assertRaises(StopIteration):
            next(generator)

    def test_managed_wifi_devices_no_wifi_devices(self):
        dev = mock.MagicMock()
        dev.configure_mock(**{'DeviceType' : 0})

        nm = mock.MagicMock()
        nm.configure_mock(**{'NetworkManager.GetDevices.return_value': [dev],
                     'NM_DEVICE_TYPE_WIFI' : 2
                    })

        generator = nm_helper.managedWifiDevices(NetworkManager=nm)
        with self.assertRaises(StopIteration):
            next(generator)

    def test_managed_wifi_devices_one_wifi_device(self):
        dev = mock.MagicMock()
        dev.configure_mock(**{'DeviceType' : 2})

        nm = mock.MagicMock()
        nm.configure_mock(**{'NetworkManager.GetDevices.return_value': [dev],
                             'NM_DEVICE_TYPE_WIFI' : 2
                            })

        generator = nm_helper.managedWifiDevices(NetworkManager=nm)

        self.assertEqual(dev, next(generator))

        with self.assertRaises(StopIteration):
            next(generator)

    def test_managed_ap_devices_no_devices(self):
        nm = mock.MagicMock()
        nm.configure_mock(**{'NetworkManager.GetDevices.return_value': list(),
                             'NM_DEVICE_TYPE_WIFI' : 2
                            })

        generator = nm_helper.managedWifiDevices(NetworkManager=nm)

        with self.assertRaises(StopIteration):
            next(generator)

    def test_managed_ap_devices_no_ap_devices(self):
        wi_dev = mock.MagicMock()
        wi_dev.configure_mock(**{'WirelessCapabilities' : 200})

        dev = mock.MagicMock()
        dev.configure_mock(**{'DeviceType' : 2,
                               'SpecificDevice.return_value': wi_dev
                             })

        nm = mock.MagicMock()
        nm.configure_mock(**{'NetworkManager.GetDevices.return_value': [dev],
                             'NM_DEVICE_TYPE_WIFI' : 2,
                             'NM_WIFI_DEVICE_CAP_AP' : 100
                            })

        generator = nm_helper.managedAPCapableDevices(NetworkManager=nm)

        with self.assertRaises(StopIteration):
            next(generator)

    def test_managed_ap_devices_one_ap_device(self):
        wi_dev = mock.MagicMock()
        wi_dev.configure_mock(**{'WirelessCapabilities' : 100})

        dev = mock.MagicMock()
        dev.configure_mock(**{'DeviceType' : 2,
                               'SpecificDevice.return_value': wi_dev
                             })

        nm = mock.MagicMock()
        nm.configure_mock(**{'NetworkManager.GetDevices.return_value': [dev],
                             'NM_DEVICE_TYPE_WIFI' : 2,
                             'NM_WIFI_DEVICE_CAP_AP' : 100
                            })

        generator = nm_helper.managedAPCapableDevices(NetworkManager=nm)

        self.assertEqual(dev, next(generator))

        with self.assertRaises(StopIteration):
            next(generator)

def main():
    unittest.main()

if __name__ == '__main__':
    main()
