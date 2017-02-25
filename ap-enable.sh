cat <<EOM >/etc/network/interfaces
# interfaces(5) file used by ifup(8) and ifdown(8)
# Include files from /etc/network/interfaces.d:
source-directory /etc/network/interfaces.d

# The loopback network interface
auto lo
iface lo inet loopback

# Added by rPi Access Point Setup
allow-hotplug wlan0
iface wlan0 inet static
        address 10.0.0.1
        netmask 255.255.255.0
        network 10.0.0.0
        broadcast 10.0.0.255
EOM

echo "denyinterfaces wlan0" > /etc/dhcpcd.conf

systemctl enable hostapd.service
systemctl enable dnsmasq.service

