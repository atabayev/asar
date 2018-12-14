from os.path import isfile
from datetime import datetime
from manager.models.Configs import Configs

fishing_attack_results = {
    '0': 'Успешно отправлено: ',
    '1': 'Ошибка создания MIMEMultipart msg. ',
    '2': 'Ошибка подключения к хосту. ',
    '3': 'Ошибка аутентификации для отправителя',
    '4': ''
}


def logging(func_name, msg):
    key = 'w'
    if isfile('logs.txt'):
        key = 'a'
    message = '[{0}] <{1}> : {2} \n'.format(datetime.now().strftime('%d.%m.%Y %H:%M'), func_name, msg)
    with open('logs.txt', key) as fl:
        fl.write(message)


def get_config(name):
    try:
        return Configs.objects.get(name=name).value
    except Configs.DoesNotExist:
        logging('get_config', 'err. Не существует значения {0} в таблице Configs'.format(name))
        return '0'


def set_config(name, value):
    try:
        config = Configs.objects.get(name=name)
    except Configs.DoesNotExist:
        logging('set_config', 'err. Не существует значения {0} в таблице Configs'.format(name))
        return
    config.value = value
    config.save()
