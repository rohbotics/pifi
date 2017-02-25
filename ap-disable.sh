systemctl disable hostapd.service
systemctl disable dnsmasq.service

cat <<EOM >/etc/network/interfaces
# interfaces(5) file used by ifup(8) and ifdown(8)
# Include files from /etc/network/interfaces.d:
source-directory /etc/network/interfaces.d

# The loopback network interface
auto lo
iface lo inet loopback
EOM

echo "" > /etc/dhcpcd.conf

