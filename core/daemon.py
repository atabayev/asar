import os
import json
import random
import hashlib
import requests
import subprocess
from time import sleep
from datetime import datetime
from manager.models.Configs import Configs, VpnFiles

'''
    Дополнительный помощник: записывает логи, проверяет конфиги с БД, шифровнание, генерация токенов.
'''

fishing_attack_results = {
    '0': 'Успешно отправлено: ',
    '1': 'Ошибка создания MIMEMultipart msg. ',
    '2': 'Ошибка подключения к хосту. ',
    '3': 'Ошибка аутентификации для отправителя',
    '4': ''
}


def logging(func_name, msg):
    if not os.path.exists('logs'):
        os.mkdir('logs')
    log_file = os.path.join('logs', 'log.txt')
    key = 'w'
    if os.path.isfile(log_file):
        key = 'a'
    message = '[{0}] <{1}> : {2} \n'.format(datetime.now().strftime('%d.%m.%Y %H:%M'), func_name, msg)
    with open(log_file, key) as fl:
        fl.write(message)


def personal_logging(log_file_name, msg):
    if not os.path.exists('logs'):
        os.mkdir('logs')
    log_file = os.path.join('logs', log_file_name)
    key = 'w'
    if os.path.isfile(log_file):
        key = 'a'
    message = '[{0}] :> {1} \n'.format(datetime.now().strftime('%d.%m.%Y %H:%M'), msg)
    with open(log_file, key) as fl:
        fl.write(message)


def get_config(name):
    try:
        return Configs.objects.get(name=name).value
    except Configs.DoesNotExist:
        config = Configs()
        config.name = name
        config.value = "0"
        config.save()
        logging('get_config', 'err. Не существует значения {0} в таблице Configs'.format(name))
        del config
        return '0'


def set_config(name, value):
    try:
        config = Configs.objects.get(name=name)
    except Configs.DoesNotExist:
        config = Configs()
        config.name = name
        config.value = value
        config.save()
        logging('set_config', 'Создана запись {0} с значением {1} в таблице Configs'.format(name, value))
        del config
        return
    config.value = value
    config.save()
    del config
    return


def crypt(value):
    crypted_value = value.swapcase()
    return crypted_value


def decrypt(value):
    decrypted_value = value.swapcase()
    return decrypted_value


def reform_date(in_date):
    tmp = in_date.strftime('%d.%m.%Y %H:%M')
    return datetime.strptime(tmp, '%d.%m.%Y %H:%M')


def generate_token():
    random.seed()
    random_res = random.uniform(1000000, 9999999)
    result = hashlib.md5(str(random_res).encode('utf-8')).hexdigest()
    return result


# def check_ip():
#     logging('>>>>> CHECK_IP', 'start')
#     log1 = open('info.txt', 'a')
#     log1.write('\n')
#     log1.write('---------------------\n')
#     subprocess.Popen("./info", stdout=log1, stderr=log1, shell=True)
#     log1.close()
#     logging('>>>>> CHECK_IP', 'wrote info.txt')
#     result = True
#     ip = requests.get('https://api.ipify.org').text
#     logging('>>>>> CHECK_IP', 'IP: ' + ip)
#     country = json.loads(requests.get('https://www.iplocate.io/api/lookup/' + ip).text)['country_code']
#     logging('>>>>> CHECK_IP', 'страна: '+country)
#     if country != 'KZ':
#         return result
#     else:
#         result = False
#         if not os.path.exists('VPN_LOG_FILE.txt'):
#             with open('VPN_LOG_FILE.txt', 'w') as fl:
#                 fl.write('')
#         while True:
#             # vpn = VpnFiles.objects.order_by('?').first()
#             # vpn_name = os.path.join('nord_vpn', vpn.name)
#
#             # proc = Popen('sudo ' + script + ' ' + vpn_name, shell=True, stdout=True)
#             # print(proc)
#             # vpn_conn = VpnConnection(vpn_name)
#             # vpn_conn.start()
#             # t = threading.Thread(target=check_vpn, args=vpn.name)
#             # t.start()
#             logging('>>>>> CHECK_IP', 'страна: ' + country + '. Подключаюсь к VPN')
#             logging('>>>>> CHECK_IP', os.getcwd())
#             log = open('VPN_LOG_FILE.txt', 'a')
#             log.write(' ----------------------------------------------------------------------- ')
#             log.write(' ----------------------------------------------------------------------- ')
#             subprocess.Popen("./start_vpn", stdout=log, stderr=log)
#             sleep(10)
#             log.close()
#             ip = requests.get('https://api.ipify.org').text
#             country = json.loads(requests.get('https://www.iplocate.io/api/lookup/' + ip).text)['country_code']
#             logging('check_ip', 'После плделючения к VPN, страна: ' + country)
#             print(country)
#             if country != 'KZ':
#                 result = True
#                 # del vpn
#                 break
#             # del vpn
#         return result
#
#
# def check_vpn(vpn_name):
#     sc = 'sudo -s openvpn {0}'.format(os.path.join('nord_vpn', vpn_name))
#     os.system("bash -c '%s'" % sc)
#     return
