import unittest
from unittest import mock
import pifi.etc_io as etc_io
import os
import json

class EtcIOTests(unittest.TestCase):

    def test_nonexistant_get_default_ap_conf(self):
        f = mock.Mock(side_effect=FileNotFoundError('foo'))
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



def main():
    unittest.main()

if __name__ == '__main__':
    main()
