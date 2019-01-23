import json
import os
import requests
from time import sleep


def check_ip():
    result = True
    if json.loads(requests.get('https://www.iplocate.io/api/lookup/' +
                               requests.get('https://api.ipify.org').text).text)['country_code'] == 'KZ':
        return result
    else:
        result = False
        try:
            config_files = os.listdir('VPN_configs')
        except FileNotFoundError:
            print('check_ip', 'Нет файлов конфигураций для VPN')
            return False
        for config_file in config_files:
            script = 'openvpn --configure {0}'.format(config_file)
            os.system("bash -c '%s'" % script)
            sleep(15)
            if json.loads(requests.get('https://www.iplocate.io/api/lookup/' +
                                       requests.get('https://api.ipify.org').text).text)['country_code'] == 'KZ':
                result = True
                break
        return result
