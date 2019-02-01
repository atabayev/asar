import os
import ftplib
import random
from threading import Thread
from time import sleep
import datetime
from core.daemon import set_config, get_config, logging
from manager.models.Stack import Stack

'''
    Проверяет log файл на FTP сервере и если отличает от скаченного log файла(означает что есть новые данные), 
    то скачивает и заменяет его.
'''

log_file = 'justlogfileforphp.asar'
tmp_log_file = 'log.tmp'
days_limit = 7


class CheckFtp(Thread):

    def __init__(self):
        Thread.__init__(self)

    def run(self):
        if get_config('checking_ftp') == '1':
            return
        set_config('checking_ftp', 1)
        logging('check_ftp', 'START')
        try:
            while True:
                logging('check_ftp', 'while True:')
                while True:
                    if get_config('vpn') == '1':
                        break
                    else:
                        logging('check_ftp', 'not check_ip()')
                        sleep(60)
                try:
                    stack = Stack.objects.all().filter(status=1)
                except Stack.DoesNotExist:
                    continue
                for target in stack:
                    logging('CheckFtp', target.email)
                    log_path = os.path.join('logs_ftp', target.ftp_host)
                    if not os.path.exists(log_path):
                        os.makedirs(log_path)
                    if not os.path.isfile(os.path.join(log_path, log_file)):
                        fl = open(os.path.join(log_path, log_file), 'w')
                        fl.close()
                    target.ftp_path_to_log = checker(target.ftp_host, target.ftp_login, target.ftp_password,
                                                     log_path, target.ftp_path_to_log)
                    log_text = open(os.path.join(log_path, log_file)).read()
                    tmp_log_text = open(os.path.join(log_path, tmp_log_file)).read()
                    if log_text != tmp_log_text:
                        os.remove(os.path.join(log_path, log_file))
                        os.rename(os.path.join(log_path, tmp_log_file), os.path.join(log_path, log_file))
                        if target.email in tmp_log_text:
                            target.status = "2"
                    else:
                        if os.path.isfile(os.path.join(log_path, tmp_log_file)):
                            os.remove(os.path.join(log_path, tmp_log_file))
                    if datetime.datetime.today() - datetime.datetime.strptime(target.date_add, '%Y-%m-%d') > \
                            datetime.timedelta(days=days_limit):
                        target.status = '3'
                    target.save()
                sleep(random.randint(300, 600))
        finally:
            set_config('checking_ftp', 0)
            return


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


if __name__ == '__main__':
    check_ftp()
