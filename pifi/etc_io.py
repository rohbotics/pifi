"""
This module handles all of the pifi files in /etc

For now this is just the default AP configuration
"""

#default_ap_path = "/etc/pifi/default_ap.em"
default_ap_path = "../default_ap.em"

import os
import em
import json
import uuid

def get_default_ap_conf(mac, open=open):
    try:
        with open(default_ap_path) as ap_conf_file:
            ap_conf = ap_conf_file.read()
            expanded_ap_conf = em.expand(ap_conf, {"mac": mac, "uuid_str": str(uuid.uuid4())})
            return json.loads(expanded_ap_conf)
    except FileNotFoundError:
        return {
            'connection': {
                'id': 'Pifi AP Mode',
                'type': '802-11-wireless',
                'autoconnect': False,
                'uuid': str(uuid.uuid4())
            },

            '802-11-wireless': {
                'mode': 'ap',
                'security': '802-11-wireless-security',
                'ssid': 'pifiAP_%4s' % mac.replace(":", "")[-4:]
            },

            '802-11-wireless-security': {
                'key-mgmt': 'wpa-psk',
                'psk': 'robotseverywhere'
            },

            'ipv4': {'method': 'shared'},
            'ipv6': {'method': 'ignore'}
        }
