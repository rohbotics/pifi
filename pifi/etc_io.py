"""
This module handles all of the pifi files in /etc

For now this is just the default AP configuration
"""

default_ap_path = "/etc/pifi/default_ap.em"
conf_path = "/etc/pifi/pifi.conf"

hostname_path = "/etc/hostname"
hosts_path = "/etc/hosts"

crda_path = "/etc/default/crda"

import os, sys
import em
import json, yaml
import uuid
import re

JSONDecodeError = ValueError
if sys.version_info[0] >= 3.5:
    JSONDecodeError = json.decoder.JSONDecodeError


def get_default_ap_conf(mac, open=open):
    hostname = "pifi"  # Default value
    try:
        hostname = get_hostname(open=open)
    except Exception as e:
        pass
    fallback_ap_conf = {
        "connection": {
            "id": "Pifi AP Mode",
            "type": "802-11-wireless",
            "autoconnect": False,
            "uuid": str(uuid.uuid4()),
        },
        "802-11-wireless": {
            "mode": "ap",
            "security": "802-11-wireless-security",
            "ssid": "%s%4s" % (hostname, mac.replace(":", "")[-4:]),
        },
        "802-11-wireless-security": {"key-mgmt": "wpa-psk", "psk": "robotseverywhere"},
        "ipv4": {"method": "shared"},
        "ipv6": {"method": "ignore"},
    }

    try:
        with open(default_ap_path) as ap_conf_file:
            ap_conf = ap_conf_file.read()
            expanded_ap_conf = em.expand(
                ap_conf,
                {"mac": mac, "uuid_str": str(uuid.uuid4()), "hostname": hostname},
            )
            ap_config = json.loads(expanded_ap_conf)

            ###
            # Work around for a bug in the default_ap config for some time
            # the autoconnect field was a string, instead of a bool, causing
            # Network manager to not be happy, this was shipped and as it is a
            # config file, it won't be fixed by updating, so this works around
            # that issue by making that part of the config a bool
            #
            # The fallback_ap mode configuration was always correct, and is also
            # always going to be fixed on update, so we only have to apply this
            # fixup on input coming in from the config file
            ###
            if "connection" in ap_config:
                if isinstance(ap_config["connection"]["autoconnect"], str):
                    tmp = ap_config["connection"]["autoconnect"].lower()
                    # We del so that we can reassign it as different type
                    del ap_config["connection"]["autoconnect"]
                    if tmp == "true":
                        ap_config["connection"]["autoconnect"] = True
                    else:
                        ap_config["connection"]["autoconnect"] = False
            return ap_config
    except FileNotFoundError:
        print(
            "WARN /etc/pifi/default_ap.em doesn't exist, using fallback configuration"
        )
        return fallback_ap_conf
    except (JSONDecodeError, NameError) as e:
        print(
            "WARN failed to parse /etc/pifi/default_ap.em, using fallback configuration"
        )
        print(e)
        return fallback_ap_conf


default_conf = {
    "delete_existing_ap_connections": True,
    "ap_device": "any",
    "client_device": "any",
    "status_led": None,
    "button_device_name": None,
}


def get_conf(open=open):
    try:
        with open(conf_path) as conf_file:
            conf = yaml.load(conf_file)
            if conf is None:
                print("WARN /etc/pifi/pifi.conf is empty, using default configuration")
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
    if line.startswith("127.") and "localhost" not in line:
        return line.replace(old_hostname, new_hostname)
    else:
        return line


def set_hostname(old_hostname, new_hostname, open=open):
    with open(hostname_path, "w+") as hostname_file:
        hostname_file.truncate()
        hostname_file.write("%s\n" % new_hostname)

    hosts_lines = []
    with open(hosts_path, "r+") as hosts_file:
        hosts_lines = hosts_file.readlines()
        hosts_lines = [
            change_hostline(old_hostname, new_hostname, line) for line in hosts_lines
        ]

    with open(hosts_path, "w") as hosts_file:
        hosts_file.writelines(hosts_lines)


def change_regdomain(line, country_code):
    if line.startswith("REGDOMAIN"):
        return "REGDOMAIN={}".format(country_code)
    else:
        return line


def set_country(country_code, open=open):
    crda_lines = []
    with open(crda_path, "r") as crda_file:
        crda_lines = crda_file.readlines()

    crda_lines = [change_regdomain(line, country_code) for line in crda_lines]

    with open(crda_path, "w") as crda_file:
        crda_file.writelines(crda_lines)
