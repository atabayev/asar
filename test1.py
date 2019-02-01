import subprocess
import requests
import json
from time import sleep


def get_country():
    proc = subprocess.call(["sudo", "openvpn", "/home/asar/www/asar/nord_vpn/ar13.nordvpn.com.tcp443.ovpn"],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # with open('/home/asar/www/asar/logs/sss.txt', 'w') as fl:
    #     fl.write(proc.)
    #     fl.write(proc.stderr.decode('utf-8'))
    # proc1 = subprocess.run("sudo openvpn $FILE {0}".format(proc.stdout.decode('utf-8')), shell=True, )

    return 'ok'


print('okay')
get_country()
