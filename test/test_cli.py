import unittest
from unittest import mock
from io import StringIO
import os, sys

sys.modules['NetworkManager'] = mock.MagicMock()
import pifi.pifi as pifi

class pifiCommandlineTests(unittest.TestCase):

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

    def test_status_no_devices_exit(self):
        managedAPCapableDevices = mock.MagicMock(side_effect=StopIteration)
        nm_mock = mock.MagicMock(**{'managedAPCapableDevices()' : managedAPCapableDevices})

        with self.assertRaises(SystemExit) as cm:
            pifi.status(nm=nm_mock)

        self.assertEqual(cm.exception.code, 2)

    def test_status_inactive_device(self):
        dev1 = mock.MagicMock(**{'Interface' : 'Foo', 'State' : 0})
        managedAPCapableDevices = mock.MagicMock(**{'return_value' : [dev1]})
        nm_mock = mock.MagicMock(**{'managedAPCapableDevices' : managedAPCapableDevices})

        with self.assertRaises(SystemExit) as cm:
            pifi.status(nm=nm_mock)

        self.assertEqual(cm.exception.code, 0)

    def test_ap_active_device(self):
        current_connection = [{'802-11-wireless' : {'mode' : 'ap'}}]
        dev1 = mock.MagicMock(**{'Interface' : 'Foo', 'State' : 0, 
                                'GetAppliedConnection.return_value': current_connection})

        managedAPCapableDevices = mock.MagicMock(**{'return_value' : [dev1]})
        nm_mock = mock.MagicMock(**{'managedAPCapableDevices' : managedAPCapableDevices})

        with self.assertRaises(SystemExit) as cm:
            pifi.status(nm=nm_mock)

        self.assertEqual(cm.exception.code, 0)

    def test_simple_cli_parse(self):
        del sys.modules['pifi.pifi']
        import pifi.pifi as tmp_pifi
        s = mock.MagicMock()
        tmp_pifi.status = s
        a = mock.MagicMock()
        tmp_pifi.add = a
        ls = mock.MagicMock()
        tmp_pifi.list_seen = ls
        lp = mock.MagicMock()
        tmp_pifi.list_pending = lp
        sh = mock.MagicMock()
        tmp_pifi.set_hostname = sh

        tmp_pifi.main(argv=['status'])
        self.assertIn(mock.call(), s.mock_calls)
        tmp_pifi.main(argv=['list', 'seen'])
        self.assertIn(mock.call(), ls.mock_calls)
        tmp_pifi.main(argv=['list', 'pending'])
        self.assertIn(mock.call(), lp.mock_calls)

    def test_args_cli_parse(self):
        del sys.modules['pifi.pifi']
        import pifi.pifi as tmp_pifi
        s = mock.MagicMock()
        tmp_pifi.status = s
        a = mock.MagicMock()
        tmp_pifi.add = a
        ls = mock.MagicMock()
        tmp_pifi.list_seen = ls
        lp = mock.MagicMock()
        tmp_pifi.list_pending = lp
        sh = mock.MagicMock()
        tmp_pifi.set_hostname = sh

        tmp_pifi.main(argv=['set-hostname', 'foo'])
        self.assertIn(mock.call('foo'), sh.mock_calls)
        tmp_pifi.main(argv=['set-hostname', 'bar'])
        self.assertIn(mock.call('bar'), sh.mock_calls)

        tmp_pifi.main(argv=['add', 'foo', 'bar'])
        self.assertIn(mock.call('foo', 'bar'), a.mock_calls)
        tmp_pifi.main(argv=['add', 'bar'])
        self.assertIn(mock.call('bar', None), a.mock_calls)


def main():
    unittest.main()

if __name__ == '__main__':
    main()
