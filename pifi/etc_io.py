"""
This module handles all of the pifi files in /etc

For now this is just the default AP configuration
"""

default_ap_path = "/etc/pifi/default_ap.em"
conf_path = "/etc/pifi/pifi.conf"

hostname_path = "/etc/hostname"
hosts_path = "/etc/hosts"

#default_ap_path = "../default_ap.em"
#conf_path = "../pifi.conf"

import os, sys
import em
import json, yaml
import uuid
import re

JSONDecodeError = ValueError
if sys.version_info[0] >= 3.5:
    JSONDecodeError = json.decoder.JSONDecodeError

def get_default_ap_conf(mac, open=open):
    hostname = "pifi" # Default value
    try:
        hostname = get_hostname(open=open)
    except Exception as e:
        pass
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
            'ssid': '%s%4s' % (hostname, mac.replace(":", "")[-4:])
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
            expanded_ap_conf = em.expand(ap_conf, {
                "mac": mac, 
                "uuid_str": str(uuid.uuid4()), 
                "hostname": hostname
                }
            )
            return json.loads(expanded_ap_conf)
    except FileNotFoundError:
        print("WARN /etc/pifi/default_ap.em doesn't exist, using fallback configuration")
        return fallback_ap_conf
    except (JSONDecodeError, NameError) as e:
        print("WARN failed to parse /etc/pifi/default_ap.em, using fallback configuration")
        print(e)
        return fallback_ap_conf


default_conf = \
{
    'delete_existing_ap_connections' : True,
    'ap_device' : 'any',
    'client_device' : 'any',
    'status_led' : None
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

def get_hostname(open=open):
    with open(hostname_path) as hostname_file:
        return hostname_file.read().strip()


def change_hostline(old_hostname, new_hostname, line):
    if line.startswith("127.") and 'localhost' not in line:
        return line.replace(old_hostname, new_hostname)
    else:
        return line

def set_hostname(old_hostname, new_hostname, open=open):
    with open(hostname_path, 'w+') as hostname_file:
        hostname_file.truncate()
        hostname_file.write('%s\n' % new_hostname)

    hosts_lines = []
    with open(hosts_path, 'r+') as hosts_file:
        hosts_lines = hosts_file.readlines()
        hosts_lines = [change_hostline(old_hostname, new_hostname, line) for line in hosts_lines]

    with open(hosts_path, 'w') as hosts_file:
        hosts_file.writelines(hosts_lines)
