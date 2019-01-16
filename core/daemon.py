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
