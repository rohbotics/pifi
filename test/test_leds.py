import unittest
from unittest import mock
import pifi.leds as leds
import os

class LEDTests(unittest.TestCase):

    def test_one_led_blink(self):
        f = mock.mock_open()
        leds.blink('/led0', open=f)
        self.assertIn(mock.call('/led0/trigger', 'w+'), f.mock_calls)
        self.assertIn(mock.call().write('timer'), f.mock_calls)
        self.assertIn(mock.call('/led0/delay_on', 'w+'), f.mock_calls)
        self.assertIn(mock.call('/led0/delay_off', 'w+'), f.mock_calls)

    def test_multiple_led_blink(self):
        f = mock.mock_open()
        leds.blink(('/led0', '/led1'), open=f)
        self.assertIn(mock.call('/led0/trigger', 'w+'), f.mock_calls)
        self.assertIn(mock.call().write('timer'), f.mock_calls)
        self.assertIn(mock.call('/led0/delay_on', 'w+'), f.mock_calls)
        self.assertIn(mock.call('/led0/delay_off', 'w+'), f.mock_calls)
        self.assertIn(mock.call('/led1/trigger', 'w+'), f.mock_calls)
        self.assertIn(mock.call().write('timer'), f.mock_calls)
        self.assertIn(mock.call('/led1/delay_on', 'w+'), f.mock_calls)
        self.assertIn(mock.call('/led1/delay_off', 'w+'), f.mock_calls)

    def test_one_led_off(self):
        f = mock.mock_open()
        leds.off('/led0', open=f)
        self.assertIn(mock.call('/led0/brightness', 'w+'), f.mock_calls)
        self.assertIn(mock.call().write('0'), f.mock_calls)

    def test_multiple_led_off(self):
        f = mock.mock_open()
        leds.off(('/led0', '/led1'), open=f)
        self.assertIn(mock.call('/led0/brightness', 'w+'), f.mock_calls)
        self.assertIn(mock.call('/led1/brightness', 'w+'), f.mock_calls)
        self.assertIn(mock.call().write('0'), f.mock_calls)

    def test_one_led_on(self):
        f = mock.mock_open()
        leds.on('/led0', open=f)
        self.assertIn(mock.call('/led0/brightness', 'w+'), f.mock_calls)
        self.assertIn(mock.call().write('0'), f.mock_calls)
        self.assertIn(mock.call().write('255'), f.mock_calls)

    def test_multiple_led_on(self):
        f = mock.mock_open()
        leds.on(('/led0', '/led1'), open=f)
        self.assertIn(mock.call('/led0/brightness', 'w+'), f.mock_calls)
        self.assertIn(mock.call('/led1/brightness', 'w+'), f.mock_calls)
        self.assertIn(mock.call().write('255'), f.mock_calls)

def main():
    unittest.main()

if __name__ == '__main__':
    main()
