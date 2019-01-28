import os
import json
import random
import hashlib
import requests
from time import sleep
from datetime import datetime
from manager.models.Configs import Configs

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
    with open('logs.txt', key) as fl:
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
        return
    config.value = value
    config.save()


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


# TODO: Проверить
def check_ip():
    result = True
    if json.loads(requests.get('https://www.iplocate.io/api/lookup/' +
                               requests.get('https://api.ipify.org').text).text)['country_code'] == 'KZ':
        set_config('status', '1')
        return result
    else:
        result = False
        os.rem
        # try:
        #     config_files = os.listdir('VPN_configs')
        # except FileNotFoundError:
        #     logging('check_ip', 'Нет файлов конфигураций для VPN')
        #     return False
        # for config_file in config_files:
        #     script = 'openvpn --configure {0}'.format(config_file)
        #     os.system("bash -c '%s'" % script)
        script = 'nordvpn c'
        for i in range(3):
            os.system("bash -c '%s'" % script)
            sleep(15)
            if json.loads(requests.get('https://www.iplocate.io/api/lookup/' +
                                       requests.get('https://api.ipify.org').text).text)['country_code'] == 'KZ':
                result = True
                set_config('status', '0')
                break
        return result
