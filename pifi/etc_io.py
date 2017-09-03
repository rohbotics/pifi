"""
This module handles all of the pifi files in /etc

For now this is just the default AP configuration
"""

default_ap_path = "/etc/pifi/default_ap.em"
conf_path = "/etc/pifi/pifi.conf"

default_ap_path = "../default_ap.em"
conf_path = "../pifi.conf"

import os
import em
import json, yaml
import uuid

def get_default_ap_conf(mac, open=open):
    fallback_ap_conf = \
    {
        'connection': {
            'id': 'Pifi AP Mode',
            'type': '802-11-wireless',
            'autoconnect': False,
            'uuid': str(uuid.uuid4())
        },

        '802-11-wireless': {
            'mode': 'ap',
            'security': '802-11-wireless-security',
            'ssid': 'UbiquityRobot%4s' % mac.replace(":", "")[-4:]
        },

        '802-11-wireless-security': {
            'key-mgmt': 'wpa-psk',
            'psk': 'robotseverywhere'
        },

        'ipv4': {'method': 'shared'},
        'ipv6': {'method': 'ignore'}
    }

    try:
        with open(default_ap_path) as ap_conf_file:
            ap_conf = ap_conf_file.read()
            expanded_ap_conf = em.expand(ap_conf, {"mac": mac, "uuid_str": str(uuid.uuid4())})
            return json.loads(expanded_ap_conf)
    except FileNotFoundError:
        print("WARN /etc/pifi/default_ap.em doesn't exist, using fallback configuration")
        return fallback_ap_conf
    except (json.decoder.JSONDecodeError, NameError) as e:
        print("WARN failed to parse /etc/pifi/default_ap.em, using fallback configuration")
        print(e)
        return fallback_ap_conf


default_conf = \
{
    'delete_existing_ap_connections' : False
}

def get_conf(open=open):
    try:
        with open(conf_path) as conf_file:
            conf = yaml.load(conf_file)
            if (conf is None):
                print('WARN /etc/pifi/pifi.conf is empty, using default configuration')
                return default_conf

            for key, value in default_conf.items():
                if key not in conf:
                    conf[key] = value

            return conf
    except FileNotFoundError:
        print("WARN /etc/pifi/pifi.conf doesn't exist, using default configuration")
        return default_conf
    except yaml.parser.ParserError:
        print("WARN failed to parse /etc/pifi/pifi.conf, using default configuration")
        return default_conf