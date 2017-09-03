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

    def test_nonexistant_conf(self):
        f = mock.Mock(side_effect=FileNotFoundError('foo'))
        conf = etc_io.get_conf(open=f)
        self.assertIsInstance(conf, dict)

    def test_good_conf(self):
        f = mock.mock_open(read_data=yaml.dump({'delete_existing_ap_connections' : True}))
        conf = etc_io.get_conf(open=f)
        self.assertIsInstance(conf, dict)
        self.assertEqual(conf, {'delete_existing_ap_connections' : True})

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

def main():
    unittest.main()

if __name__ == '__main__':
    main()
