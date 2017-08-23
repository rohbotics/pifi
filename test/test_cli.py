import unittest
from unittest import mock
from io import StringIO
import os, sys

sys.modules['NetworkManager'] = mock.MagicMock()
import pifi.pifi as pifi

class NMHelperTests(unittest.TestCase):

    def test_add_one_insecure_connection_empty_list(self):
        var = mock.MagicMock()
        var.configure_mock(**{'readPendingConnections.return_value': list()})

        pifi.add('Foo', None, var_io=var)

        var.readPendingConnections.assert_called_once_with()
        written_connection = var.writePendingConnections.call_args[0][0][0]
        del written_connection['connection']['uuid']

        expected_connection = {
                'connection': {
                    'id': 'Foo',
                    'type': '802-11-wireless',
                    'autoconnect': True
                },

                '802-11-wireless': {
                    'mode': 'infrastructure',
                    'ssid': 'Foo'
                },

                'ipv4': {'method': 'auto'},
                'ipv6': {'method': 'auto'}
        }
        
        self.assertEqual(written_connection, expected_connection)

    def test_add_one_secure_connection_empty_list(self):
        var = mock.MagicMock()
        var.configure_mock(**{'readPendingConnections.return_value': list()})

        pifi.add('Foo', 'bar', var_io=var)

        var.readPendingConnections.assert_called_once_with()
        written_connection = var.writePendingConnections.call_args[0][0][0]
        del written_connection['connection']['uuid']

        expected_connection = {
            'connection': {
                'id': 'Foo',
                'type': '802-11-wireless',
                'autoconnect': True,
            },

            '802-11-wireless': {
                'mode': 'infrastructure',
                'security': '802-11-wireless-security',
                'ssid': 'Foo'
            },

            '802-11-wireless-security': {
                'key-mgmt': 'wpa-psk', # We only support WPA2-PSK networks for now
                'psk': 'bar'
            },

            'ipv4': {'method': 'auto'},
            'ipv6': {'method': 'auto'}
        }
        
        self.assertEqual(written_connection, expected_connection)

    def test_add_one_secure_connection_permission_denied(self):
        var = mock.MagicMock()
        var.configure_mock(**{'writePendingConnections.side_effect': PermissionError})

        pifi.add('Foo', 'bar', var_io=var) # Only checking for no exceptions

    def test_add_one_secure_connection_existing_list(self):
        existing_connection = {'Baz' : 'qux'}

        var = mock.MagicMock()
        var.configure_mock(**{'readPendingConnections.return_value': [existing_connection]})

        pifi.add('Foo', 'bar', var_io=var)

        var.readPendingConnections.assert_called_once_with()
        written_connections = var.writePendingConnections.call_args[0][0]
        del written_connections[1]['connection']['uuid']

        expected_connection = {
            'connection': {
                'id': 'Foo',
                'type': '802-11-wireless',
                'autoconnect': True,
            },

            '802-11-wireless': {
                'mode': 'infrastructure',
                'security': '802-11-wireless-security',
                'ssid': 'Foo'
            },

            '802-11-wireless-security': {
                'key-mgmt': 'wpa-psk', # We only support WPA2-PSK networks for now
                'psk': 'bar'
            },

            'ipv4': {'method': 'auto'},
            'ipv6': {'method': 'auto'}
        }
        
        self.assertEqual(written_connections, [existing_connection, expected_connection])


def main():
    unittest.main()

if __name__ == '__main__':
    main()
