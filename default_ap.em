{
    "connection": {
        "id": "Pifi AP Mode",
        "type": "802-11-wireless",
        "autoconnect": false,
        "uuid": "@(uuid_str)"
    },

    "802-11-wireless": {
        "mode": "ap",
        "security": "802-11-wireless-security",
        "ssid": "@(hostname)@(mac.replace(":", "")[-4:])"
    },

    "802-11-wireless-security": {
        "key-mgmt": "wpa-psk",
        "psk": "robotseverywhere"
    },

    "ipv4": {
        "method": "shared"
    },
    "ipv6": {
        "method": "ignore"
    }
}
