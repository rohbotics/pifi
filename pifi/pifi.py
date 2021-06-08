"""
pifi

Usage:
  pifi status
  pifi add <ssid> [<password>]
  pifi remove [-y] <ssid>
  pifi list seen
  pifi list pending
  pifi set-hostname <hostname>
  pifi rescan [-y]
  pifi --version

Options:
  -h --help    Show this help
  --version    Show pifi version
  -y           Bypass any prompting

"""
import argparse
import time
import uuid
import sys
import socket

import NetworkManager

import pifi.nm_helper as nm
import pifi.var_io as var_io
import pifi.etc_io as etc_io
import pifi.startup as startup
from pifi.version import __version__


def query_yes_no(question, default="no"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == "":
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' " "(or 'y' or 'n').\n")


def status(argv, nm=nm):
    devices = 0

    for ApModeDevice in nm.managedAPCapableDevices():
        devices += 1
        print("Network Mangager reports AP mode support on %s" % ApModeDevice.Interface)
        if ApModeDevice.State != 100:
            print("Device is not activated")
            exit(0)
        current_connection = ApModeDevice.GetAppliedConnection(0)
        if (
            "mode" in current_connection[0]["802-11-wireless"]
            and current_connection[0]["802-11-wireless"]["mode"] == "ap"
        ):
            print("Device is currently acting as an Access Point")
        else:
            ssid = current_connection[0]["802-11-wireless"]["ssid"]
            ssid = bytearray([ord(byte) for byte in ssid])
            print("Device is connected to %s" % ssid.decode("utf-8"))

    if devices == 0:
        print("ERROR: Network Manager reports no AP mode support on any managed device")
        exit(2)


def add(argv, var_io=var_io):
    parser = argparse.ArgumentParser(
        description="Add a network to connect to on the next reboot/rescan"
    )
    parser.add_argument("ssid")
    parser.add_argument("password", nargs="?")
    args = parser.parse_args(argv)

    ssid = args.ssid
    password = args.password

    if etc_io.get_hostname() == "ubiquityrobot":
        print(
            "WARN: Please use `pifi set-hostname` to change the hostname before connecting"
        )

    pending = var_io.readPendingConnections()

    if password is not None:
        new_connection = {
            "connection": {
                "id": str(ssid),
                "type": "802-11-wireless",
                "autoconnect": True,
                "uuid": str(uuid.uuid4()),
            },
            "802-11-wireless": {
                "mode": "infrastructure",
                "security": "802-11-wireless-security",
                "ssid": ssid,
            },
            "802-11-wireless-security": {
                "key-mgmt": "wpa-psk",  # We only support WPA2-PSK networks for now
                "psk": password,
            },
            "ipv4": {"method": "auto"},
            "ipv6": {"method": "auto"},
        }

    else:
        new_connection = {
            "connection": {
                "id": str(ssid),
                "type": "802-11-wireless",
                "autoconnect": True,
                "uuid": str(uuid.uuid4()),
            },
            "802-11-wireless": {"mode": "infrastructure", "ssid": ssid},
            "ipv4": {"method": "auto"},
            "ipv6": {"method": "auto"},
        }

    print("Added connection %s, will attempt to connect to it on future reboots" % ssid)
    pending.append(new_connection)

    try:
        var_io.writePendingConnections(pending)
    except PermissionError:
        print(
            "Error writing to /var/lib/pifi/pending, make sure you are running with sudo"
        )


def remove(argv):
    parser = argparse.ArgumentParser(
        description="Remove a network from both pending and current connections"
    )
    parser.add_argument("ssid")
    parser.add_argument("-y", action="store_true")
    args = parser.parse_args(argv)

    ssid = args.ssid
    skip_prompt = args.y

    for device in nm.managedWifiDevices():
        if device.State == NetworkManager.NM_DEVICE_STATE_ACTIVATED:
            current_connection = device.GetAppliedConnection(0)
            # SSID returned as list of bytes
            if ssid == b"".join(
                current_connection[0]["802-11-wireless"]["ssid"]
            ).decode("utf-8"):
                print("WARN: Connection is currently active")
                print("WARN: Deleting can disrupt existing SSH connetions")

                # If skip_prompt is true, short circuit the if, otherwise go into the query
                if not skip_prompt and not query_yes_no("Continue Removal?"):
                    return

    pending = var_io.readPendingConnections()
    for con in pending:
        if ssid == con["802-11-wireless"]["ssid"]:
            pending.remove(con)

    try:
        var_io.writePendingConnections(pending)
    except PermissionError:
        print(
            "Error writing to /var/lib/pifi/pending, make sure you are running with sudo"
        )
        return

    for con in nm.existingConnections():
        settings = con.GetSettings()
        if ssid == settings["802-11-wireless"]["ssid"]:
            pass
            con.Delete()


def list_command(argv):
    list_parser = argparse.ArgumentParser(
        description="List either seen or pending connections"
    )
    list_parser.add_argument("list")
    args = list_parser.parse_args(argv)

    if args.list == "seen":
        for ssid in var_io.readSeenSSIDs():
            print(ssid)
    if args.list == "pending":
        for con in var_io.readPendingConnections():
            try:
                print(con["802-11-wireless"]["ssid"])
            except KeyError:
                print(
                    "WARN: Found non wireless pending connection: %s"
                    % con["connection"]["id"]
                )


def set_hostname(argv):
    parser = argparse.ArgumentParser(description="Set a new hostname")
    parser.add_argument("hostname")
    args = parser.parse_args(argv)
    new_hostname = args.hostname

    old_hostname = etc_io.get_hostname()
    print("Changing hostname from %s to %s" % (old_hostname, new_hostname))

    try:
        etc_io.set_hostname(old_hostname, new_hostname)
        socket.sethostname(new_hostname)
    except PermissionError:
        print(
            "Error writing to /etc/hosts or /etc/hostname, make sure you are running with sudo"
        )
    except OSError:
        print(
            "Error writing to /etc/hosts or /etc/hostname, make sure you are running with sudo"
        )


def rescan(argv):
    parser = argparse.ArgumentParser(
        description="Stop AP mode and rescan for known networks, start AP mode again if none found"
    )
    parser.add_argument("-y", action="store_true")
    args = parser.parse_args(argv)

    skip_prompt = args.y

    pifi_conf_settings = etc_io.get_conf()
    ApModeDevice, ClientModeDevice = nm.select_devices(pifi_conf_settings)

    if ApModeDevice.State != 100:
        print("AP Device is not active")
    else:
        current_connection = ApModeDevice.GetAppliedConnection(0)
        if (
            "mode" in current_connection[0]["802-11-wireless"]
            and current_connection[0]["802-11-wireless"]["mode"] == "ap"
        ):
            print(
                "Device is currently acting as an Access Point, Rescanning requires turning this off"
            )
            print("This will disrupt any SSH connections")

            # If skip_prompt is true, short circuit the if, otherwise go into the query
            if not skip_prompt and not query_yes_no("Continue?"):
                return
            ApModeDevice.Disconnect()

    print("Waiting for wifi rescan")
    time.sleep(30)
    try:
        var_io.writeSeenSSIDs(nm.seenSSIDs([ClientModeDevice]))
    except PermissionError:
        print("Error writing to /var/lib/pifi/seen_ssids, continuing")

    if ClientModeDevice.State == NetworkManager.NM_DEVICE_STATE_ACTIVATED:
        print(
            "Connected to: %s"
            % ClientModeDevice.SpecificDevice().ActiveAccessPoint.Ssid
        )
        return

    print("Device is not connected to any network, Looking for pending connections")
    pending = var_io.readPendingConnections()

    # Try to pick a connection to use, if none found, just continue
    try:
        # Use the best connection
        best_ap, best_con = nm.selectConnection(
            nm.availibleConnections(ClientModeDevice, pending)
        )

        print("Connecting to %s" % best_con["802-11-wireless"]["ssid"])
        NetworkManager.NetworkManager.AddAndActivateConnection(
            best_con, ClientModeDevice, best_ap
        )

        new_pending = var_io.readPendingConnections().remove(best_con)
        var_io.writePendingConnections(new_pending)
        return
    except ValueError:
        pass

    # If we reach this point, we gave up on Client mode
    print("No SSIDs from pending connections found")
    startup.start_ap_mode(pifi_conf_settings, ApModeDevice, ClientModeDevice)


def set_country(argv):
    parser = argparse.ArgumentParser(description="Set your country ")
    parser.add_argument("ISO_country_code")
    args = parser.parse_args(argv)

    try:
        etc_io.set_country(args.ISO_country_code)
    except PermissionError:
        print("Error writing to /etc/default/crda, make sure you are running with sudo")
    except OSError:
        print("Error writing to /etc/default/crda, make sure you are running with sudo")


def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser(usage=__doc__)
    parser.add_argument("command", help="Subcommand to run")

    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s {version}".format(version=__version__),
    )
    args = parser.parse_args(argv[:1])

    commands = {
        "status": status,
        "add": add,
        "remove": remove,
        "set-hostname": set_hostname,
        "set-country": set_country,
        "rescan": rescan,
        "list": list_command,
    }

    if args.command in commands:
        commands[args.command](argv[1:])
