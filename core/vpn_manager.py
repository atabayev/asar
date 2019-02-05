import os
import sys
from threading import Thread
from time import sleep
import subprocess
import requests
import json
from core.daemon import get_config, set_config, logging


class VpnManager(Thread):

    def __init__(self):
        Thread.__init__(self)

    def run(self):
        logging('VpnManager', 'Start')
        if get_config('vpn_manager') == '1':
            logging('VpnManager', 'return 1')
            return
        set_config('vpn_manager', '1')
        while True:
            try:
                country = get_country()
                logging('VpnManager', 'country = {0}'.format(country))
                if country == 'KZ':
                    set_config('vpn', '0')
                    logging('VpnManager', 'vpn=0')
                else:
                    set_config('vpn', '1')
                    logging('VpnManager', 'vpn=1')
                sleep(200)
            except Exception:
                logging('VpnManager', 'Error: {0}'.format(sys.exc_info()))


def get_country():
    country = 'KZ'
    if not os.path.isfile(os.path.join('bashes', 'MYIP.TXT')):
        return country
    with open(os.path.join('bashes', 'MYIP.TXT'), 'r') as fl:
        my_ip = fl.read().rstrip()
    if my_ip == '':
        return country
    country = my_ip.split(' ')[3].replace(',', '')
    return country
