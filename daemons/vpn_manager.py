#!/usr/bin/env python3
import os
import psycopg2
from datetime import datetime


def set_config(name, value):
    with psycopg2.connect(dbname='asar_db', user='asar_admin', password='aSaR14!q', host='127.0.0.1', port=5432) \
            as conn:
        with conn.cursor() as cursor:
            cursor.execute('UPDATE manager_configs SET value=%s WHERE name=%s', (value, name,))

    cursor.close()
    conn.close()
    return 'ok'


def get_config(name):
    with psycopg2.connect(dbname='asar_db', user='asar_admin', password='aSaR14!q', host='127.0.0.1', port=5432) \
            as conn:
        with conn.cursor() as cursor:
            cursor.execute('SELECT * FROM manager_configs WHERE name=%s', (name,))
            record = cursor.fetchone()
    cursor.close()
    conn.close()
    return record[2]


def logging(func_name, msg):
    log_path = '/home/asar/www/asar/logs'
    if not os.path.exists(log_path):
        os.mkdir(log_path)
    log_file = os.path.join(log_path, 'log.txt')
    key = 'w'
    if os.path.isfile(log_file):
        key = 'a'
    message = '[{0}] <{1}> : {2} \n'.format(datetime.now().strftime('%d.%m.%Y %H:%M'), func_name, msg)
    with open(log_file, key) as fl:
        fl.write(message)


bash_path = '/home/asar/www/asar/bashes'
try:
    country = 'KZ'
    if os.path.isfile(os.path.join(bash_path, 'MYIP.TXT')):
        with open(os.path.join(bash_path, 'MYIP.TXT'), 'r') as fl:
            my_ip = fl.read().rstrip()
        if my_ip != '':
            country = my_ip.split(' ')[3].replace(',', '')
    if country == 'KZ':
        set_config('vpn', '0')
    else:
        set_config('vpn', '1')
except Exception as e:
    print('1')
    logging('VpnManager', 'Error: {0}'.format(e))
