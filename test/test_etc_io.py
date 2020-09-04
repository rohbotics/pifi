import unittest
from unittest import mock
import pifi.etc_io as etc_io
import os
import json, yaml

class EtcIOTests(unittest.TestCase):

    def test_nonexistant_get_default_ap_conf(self):
        f = mock.Mock(side_effect=FileNotFoundError('foo'))
        conf = etc_io.get_default_ap_conf('AF:BF:CF:0F:1F:2F', open=f)
        self.assertIsInstance(conf, dict)
        self.assertEqual(conf['802-11-wireless']['mode'], 'ap')

    def test_bad_json_get_default_ap_conf(self):
        f = mock.mock_open(read_data='{"Foo" : f"')
        conf = etc_io.get_default_ap_conf('AF:BF:CF:0F:1F:2F', open=f)
        self.assertIsInstance(conf, dict)
        self.assertEqual(conf['802-11-wireless']['mode'], 'ap')

    def test_bad_template_get_default_ap_conf(self):
        f = mock.mock_open(read_data='{"Foo" : "@(foo)"}')
        conf = etc_io.get_default_ap_conf('AF:BF:CF:0F:1F:2F', open=f)
        self.assertIsInstance(conf, dict)
        self.assertEqual(conf['802-11-wireless']['mode'], 'ap')

    def test_pure_json_get_default_ap_conf(self):
        f = mock.mock_open(read_data=json.dumps({'Foo' : 'Bar'}))
        conf = etc_io.get_default_ap_conf('AF:BF:CF:0F:1F:2F', open=f)
        self.assertIsInstance(conf, dict)
        self.assertEqual(conf, {'Foo' : 'Bar'})

    def test_templated_json_get_default_ap_conf(self):
        f = mock.mock_open(read_data='{"Foo" : "@(mac)"}')
        conf = etc_io.get_default_ap_conf('AF:BF:CF:0F:1F:2F', open=f)
        self.assertIsInstance(conf, dict)
        self.assertEqual(conf, {'Foo' : 'AF:BF:CF:0F:1F:2F'})

    ### 
    # Tests for work around for a bug in the default_ap config for some time
    # the autoconnect field was a string, instead of a bool, causing
    # Network manager to not be happy, this was shipped and as it is a
    # config file, it won't be fixed by updating, so this works around 
    # that issue
    ###
    def test_pure_json_autoconnect_string_to_bool_false(self):
        data = """
        {
            "connection": {
                "id": "Pifi AP Mode",
                "type": "802-11-wireless",
                "autoconnect": "False",
                "uuid": "foo-bar-foo-bar"
            }
        }
        """

        f = mock.mock_open(read_data=data)
        conf = etc_io.get_default_ap_conf('AF:BF:CF:0F:1F:2F', open=f)
        self.assertIsInstance(conf['connection']['autoconnect'], bool)
        self.assertEqual(conf['connection']['autoconnect'], False)
        self.assertIsInstance(conf, dict)

    def test_pure_json_autoconnect_string_to_bool_true(self):
        data = """
        {
            "connection": {
                "id": "Pifi AP Mode",
                "type": "802-11-wireless",
                "autoconnect": "True",
                "uuid": "foo-bar-foo-bar"
            }
        }
        """

        f = mock.mock_open(read_data=data)
        conf = etc_io.get_default_ap_conf('AF:BF:CF:0F:1F:2F', open=f)
        self.assertIsInstance(conf['connection']['autoconnect'], bool)
        self.assertEqual(conf['connection']['autoconnect'], True)
        self.assertIsInstance(conf, dict)

    def test_pure_json_autoconnect_bool(self):
        data = """
        {
            "connection": {
                "id": "Pifi AP Mode",
                "type": "802-11-wireless",
                "autoconnect": false,
                "uuid": "foo-bar-foo-bar"
            }
        }
        """

        f = mock.mock_open(read_data=data)
        conf = etc_io.get_default_ap_conf('AF:BF:CF:0F:1F:2F', open=f)
        self.assertIsInstance(conf['connection']['autoconnect'], bool)
        self.assertEqual(conf['connection']['autoconnect'], False)
        self.assertIsInstance(conf, dict)     

        data = """
        {
            "connection": {
                "id": "Pifi AP Mode",
                "type": "802-11-wireless",
                "autoconnect": true,
                "uuid": "foo-bar-foo-bar"
            }
        }
        """

        f = mock.mock_open(read_data=data)
        conf = etc_io.get_default_ap_conf('AF:BF:CF:0F:1F:2F', open=f)
        self.assertIsInstance(conf['connection']['autoconnect'], bool)
        self.assertEqual(conf['connection']['autoconnect'], True)
        self.assertIsInstance(conf, dict)   
    

    def test_nonexistant_conf(self):
        f = mock.Mock(side_effect=FileNotFoundError('foo'))
        conf = etc_io.get_conf(open=f)
        self.assertIsInstance(conf, dict)

    def test_good_conf(self):
        f = mock.mock_open(read_data=yaml.dump({'delete_existing_ap_connections' : True}))
        conf = etc_io.get_conf(open=f)
        self.assertIsInstance(conf, dict)
        expected = etc_io.default_conf
        expected.update({'delete_existing_ap_connections' : True})
        self.assertEqual(conf, expected)

    def test_incomplete_conf(self):
        f = mock.mock_open(read_data=yaml.dump({'Foo' : 'Bar'}))
        conf = etc_io.get_conf(open=f)
        self.assertIsInstance(conf, dict)
        expected = etc_io.default_conf
        expected.update({'Foo': 'Bar'})
        self.assertEqual(conf, expected)

    def test_empty_conf(self):
        f = mock.mock_open(read_data='')
        conf = etc_io.get_conf(open=f)
        self.assertIsNot(conf, None)
        self.assertIsInstance(conf, dict)
        self.assertEqual(conf, etc_io.default_conf)

    def test_bad_conf(self):
        f = mock.mock_open(read_data=': fd')
        conf = etc_io.get_conf(open=f)
        self.assertIsNot(conf, None)
        self.assertIsInstance(conf, dict)
        self.assertEqual(conf, etc_io.default_conf)

    def test_setcountry(self):
        input_data = """# Set REGDOMAIN to a ISO/IEC 3166-1 alpha2 country code so that iw(8) may set
# the initial regulatory domain setting for IEEE 802.11 devices which operate
# on this system.
#
# Governments assert the right to regulate usage of radio spectrum within
# their respective territories so make sure you select a ISO/IEC 3166-1 alpha2
# country code suitable for your location or you may infringe on local
# legislature. See `/usr/share/zoneinfo/zone.tab' for a table of timezone
# descriptions containing ISO/IEC 3166-1 alpha2 country codes.

REGDOMAIN="""

        expected_out = """# Set REGDOMAIN to a ISO/IEC 3166-1 alpha2 country code so that iw(8) may set
# the initial regulatory domain setting for IEEE 802.11 devices which operate
# on this system.
#
# Governments assert the right to regulate usage of radio spectrum within
# their respective territories so make sure you select a ISO/IEC 3166-1 alpha2
# country code suitable for your location or you may infringe on local
# legislature. See `/usr/share/zoneinfo/zone.tab' for a table of timezone
# descriptions containing ISO/IEC 3166-1 alpha2 country codes.

REGDOMAIN=US"""

        f = mock.mock_open(read_data=input_data)
        etc_io.set_country("US", f)
        handle = f()
        handle.writelines.assert_called_once_with(expected_out.splitlines(keepends=True))

def main():
    unittest.main()

if __name__ == '__main__':
    main()
