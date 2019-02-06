#!/bin/bash
country=$(geoiplookup $(wget -O - -q icanhazip.com))
GEO_IP="GeoIP Country Edition: KZ, Kazakhstan"
if [ "$country" == "$GEO_IP" ]
then
    FILE=$(find /home/asar/www/asar/nord_vpn/ -type f | shuf -n 1)
    sudo openvpn $FILE > /home/asar/www/asar/bashes/VPN_STAT.TXT &
fi
sleep 10s
geoiplookup $(wget -O - -q icanhazip.com) > /home/asar/www/asar/bashes/MYIP.TXT
sleep 10s
/usr/bin/python3 /home/asar/www/asar/daemons/vpn_manager.py
