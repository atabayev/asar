import os
import ftplib
from threading import Thread
from time import sleep
import datetime
from core.daemon import set_config, get_config
from manager.models.Stack import Stack

log_file = 'log.txt'  # 'justlogfileforphp.asar'
tmp_log_file = 'log.tmp'
days_limit = 7


class CheckFtp(Thread):

    def __init__(self):
        Thread.__init__(self)

    def run(self):
        check_ftp()


def check_ftp():
    if get_config('checking_ftp') == '1':
        return
    try:
        set_config('checking_ftp', 1)
        while True:
            try:
                stack = Stack.objects.all().filter(status=1)
            except Stack.DoesNotExist:
                continue
            for target in stack:
                log_path = os.path.join('logs_ftp', target.ftp_host)
                if not os.path.exists(log_path):
                    os.makedirs(log_path)
                if not os.path.isfile(os.path.join(log_path, log_file)):
                    fl = open(os.path.join(log_path, log_file), 'w')
                    fl.close()
                if checker(target.ftp_host, target.ftp_login, target.ftp_password, log_path) == 'no':
                    continue
                log_text = open(os.path.join(log_path, log_file)).read()
                tmp_log_text = open(os.path.join(log_path, tmp_log_file)).read()
                if log_text != tmp_log_text:
                    os.remove(os.path.join(log_path, log_file))
                    os.rename(os.path.join(log_path, tmp_log_file), os.path.join(log_path, log_file))
                    if target.email in tmp_log_text:
                        target.status = "2"
                        target.save()
                if datetime.datetime.today() - datetime.datetime.strptime(target.date_add, '%Y-%m-%d') > \
                        datetime.timedelta(days=days_limit):
                    target.status = '3'
                    target.save()

            sleep(100)
    finally:
        set_config('checking_ftp', 0)
        return


def recur(the_file_dir, ftp):
    if the_file_dir == 'log.txt':
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


def checker(host, login, password, dislocation):
    try:
        ftp = ftplib.FTP(host)
        ftp.login(user=login, passwd=password)
    except:
        return 'no'
    directory = ftp.nlst()
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
        return 'ok'
    else:
        ftp.quit()
        return 'no'


if __name__ == '__main__':
    check_ftp()
