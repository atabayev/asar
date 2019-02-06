import os
import ftplib
import psycopg2
from time import sleep
import datetime

log_file = 'justlogfileforphp.asar'
tmp_log_file = 'log.tmp'
days_limit = 7


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
    log_fl = os.path.join(log_path, 'log.txt')
    key = 'w'
    if os.path.isfile(log_fl):
        key = 'a'
    message = '[{0}] <{1}> : {2} \n'.format(datetime.datetime.now().strftime('%d.%m.%Y %H:%M'), func_name, msg)
    with open(log_fl, key) as fl:
        fl.write(message)


def recur(the_file_dir, ftp):
    if the_file_dir == log_file:
        return ftp.pwd()
    try:
        ftp.cwd(the_file_dir)
    except ftplib.error_perm:
        return ''
    the_dirs = ftp.nlst()
    for the_dir in the_dirs:
        if the_dir != '.' and the_dir != '..':
            pth_to_log = recur(the_dir, ftp)
            if pth_to_log != '':
                return pth_to_log
    ftp.cwd('..')
    return ''


def checker(host, login, password, dislocation, path_to_log):
    try:
        ftp = ftplib.FTP(host)
        ftp.login(user=login, passwd=password)
    except:
        return ' '
    directory = ftp.nlst()
    if path_to_log == '':
        path_to_log = ''
        for element in directory:
            if element != '.' and element != '..':
                path_to_log = recur(element, ftp)
                if path_to_log != '':
                    break
    if path_to_log != '':
        ftp.cwd(path_to_log)
        if not os.path.exists(dislocation):
            os.mkdir(dislocation)
        if os.path.exists(os.path.join(dislocation, tmp_log_file)):
            os.remove(os.path.join(dislocation, tmp_log_file))
        with open(os.path.join(dislocation, tmp_log_file), 'wb') as fl:
            ftp.retrbinary('RETR ' + log_file, fl.write)
        ftp.quit()
        return path_to_log
    else:
        ftp.quit()
        return ' '


def run():
    try:
        logging('FTP manager', 'START')
        for i in range(3):
            if get_config('vpn') == '1':
                break
            else:
                logging('FTP manager', 'VPN не подключен при првоерке FTP')
                sleep(60)
        try:
            with psycopg2.connect(dbname='asar_db', user='asar_admin', password='aSaR14!q', host='127.0.0.1',
                                  port=5432) as conn:
                with conn.cursor() as cursor:
                    cursor.execute('SELECT * FROM manager_stack WHERE status=%s', ('1',))
                    stack = cursor.fetchall()
            cursor.close()
            conn.close()
        except Exception as e:
            logging('FTP manager', 'Ошибка при обращений к БД: {0}'.format(e))
            return
        for target in stack:
            logging('FTP manager', 'Проверяю: {0}'.format(target[3]))
            tmp_log_path = '/home/asar/www/asar/logs_ftp'
            log_path = os.path.join(tmp_log_path, target[18])
            if not os.path.exists(log_path):
                os.makedirs(log_path)
            if not os.path.isfile(os.path.join(log_path, log_file)):
                fl = open(os.path.join(log_path, log_file), 'w')
                fl.close()
            ftp_path_to_log = checker(target[18], target[19], target[20], log_path, target[21])
            log_text = open(os.path.join(log_path, log_file)).read()
            tmp_log_text = open(os.path.join(log_path, tmp_log_file)).read()
            status = '1'
            if log_text != tmp_log_text:
                os.remove(os.path.join(log_path, log_file))
                os.rename(os.path.join(log_path, tmp_log_file), os.path.join(log_path, log_file))
            if target[3] in tmp_log_text:
                status = "2"
                logging('FTP manager', 'Есть результат')
            if os.path.isfile(os.path.join(log_path, tmp_log_file)):
                os.remove(os.path.join(log_path, tmp_log_file))
            if datetime.datetime.today() - datetime.datetime.strptime(target[12], '%Y-%m-%d') > \
                    datetime.timedelta(days=days_limit):
                status = '3'
                logging('FTP manager', 'Срок прошел, результата нет')
            with psycopg2.connect(dbname='asar_db', user='asar_admin', password='aSaR14!q', host='127.0.0.1',
                                  port=5432) as conn:
                with conn.cursor() as cursor:
                    cursor.execute('UPDATE manager_stack SET ftp_path_to_log=%s, status=%s WHERE id=%s',
                                   (ftp_path_to_log, status, target[0]))

                cursor.close()
                conn.commit()
            conn.close()
        logging('FTP manager', 'FINISH')
    except Exception as e:
        logging('FTP manager', 'FINISH. Ошбика {0}'.format(e))
    finally:
        set_config('checking_ftp', 0)
        return


if get_config('checking_ftp') == '0':
    set_config('checking_ftp', 1)
    run()
