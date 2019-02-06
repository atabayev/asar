import datetime
import email
import imaplib
import os
from time import sleep
from zipfile import ZipFile

import psycopg2


def reform_date(in_date):
    tmp = in_date.strftime('%d.%m.%Y %H:%M')
    return datetime.datetime.strptime(tmp, '%d.%m.%Y %H:%M')


def crypt(value):
    crypted_value = value.swapcase()
    return crypted_value


def decrypt(value):
    decrypted_value = value.swapcase()
    return decrypted_value


def set_config(name, value):
    with psycopg2.connect(dbname='asar_db', user='asar_admin', password='aSaR14!q', host='127.0.0.1', port=5432) \
            as conn:
        with conn.cursor() as cursor:
            cursor.execute('UPDATE manager_configs SET value = %s WHERE name = %s', (value, name,))

        cursor.close()
        conn.commit()
    conn.close()
    return 'ok'


def get_config(name):
    with psycopg2.connect(dbname='asar_db', user='asar_admin', password='aSaR14!q', host='127.0.0.1', port=5432) \
            as conn:
        with conn.cursor() as cursor:
            cursor.execute('SELECT * FROM manager_configs WHERE name = %s', (name,))
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


def scan_email(the_email, emails_password, base_dir, last_msg_datetime):
    emails_zip = []
    tmp_dir = os.path.join(base_dir, 'tmp')
    first_time = True
    last_messages_date = last_msg_datetime
    try:
        imap_session = imaplib.IMAP4_SSL('imap.mail.ru')
    except Exception as e:
        return 'error connect with IMAP ' + str(e)
    try:
        result = imap_session.login(the_email, emails_password)
    except Exception as e:
        logging('scan_email', 'Error logging to {0}'.format(the_email))
        return 'PC', datetime.datetime.now()
    del result
    try:
        imap_session.select('INBOX')
    except Exception as e:
        logging('scan_email', 'Error select INBOX in {0}'.format(the_email))
        return 'NI', datetime.datetime.now()
    status, data = imap_session.uid('search', 'UNSEEN')
    unseen_messages = data[0].split()
    status, data = imap_session.uid('search', 'ALL')
    if status != 'OK':
        return 'NA', datetime.datetime.now()
    messages_id = data[0].split()
    for message_id in reversed(messages_id):
        attached_files = []
        logs_name = datetime.date.today().strftime('%m%d') + '_' + message_id.decode('utf-8') + '_' + the_email
        status, data = imap_session.uid('fetch', message_id, '(RFC822)')
        if status != 'OK':
            continue
        message = email.message_from_bytes(data[0][1])
        messages_date = reform_date(email.utils.parsedate_to_datetime(message['date']))
        if first_time:
            last_messages_date = messages_date
            first_time = False
        if messages_date <= last_msg_datetime:
            break
        subject = ''
        body_txt = ''
        body_html = ''
        email_from = ''
        email_to = ''
        email_cc = ''
        encoding = ''
        if 'from' in message:
            try:
                if message['From'][0:7].upper() == '=?WINDO':
                    encoding = 'cp1251'
                    tmp = email.header.decode_header(message['From'])
                    for i in range(1, len(tmp), 2):
                        email_from = email_from + email.header.decode_header(message['From'])[i - 1][0].decode(encoding) + \
                                     email.header.decode_header(message['From'])[i][0].decode(encoding) + ' '
                elif message['From'][0:7].upper() == '=?UTF-8':
                    encoding = 'utf-8'
                    tmp = email.header.decode_header(message['From'])
                    for i in range(1, len(tmp), 2):
                        email_from = email_from + email.header.decode_header(message['From'])[i - 1][0].decode(encoding) \
                                     + email.header.decode_header(message['From'])[i][0].decode(encoding) + ' '
                else:
                    encoding = ''
                    email_from = message['From']
            except Exception as e:
                logging('scan email', 'Ошибка {0}. ID: {1}'.format(e, message_id.decode('utf-8')))

        if 'To' in message:
            try:
                if message['To'][0:7].upper() == '=?WINDO':
                    encoding = 'cp1251'
                    tmp = email.header.decode_header(message['To'])
                    if len(tmp) == 1:
                        email_to = tmp[0][0]
                    else:
                        for i in range(1, len(tmp), 2):
                            email_to = email_to + email.header.decode_header(message['To'])[i - 1][0].decode('cp1251') \
                                       + email.header.decode_header(message['To'])[i][0].decode('cp1251') + ' '
                elif message['To'][0:7].upper() == '=?UTF-8':
                    encoding = 'utf-8'
                    tmp = email.header.decode_header(message['To'])
                    if len(tmp) == 1:
                        email_to = tmp[0][0]
                    else:
                        for i in range(1, len(tmp), 2):
                            email_to = email_to + email.header.decode_header(message['To'])[i - 1][0].decode('utf-8') \
                                       + email.header.decode_header(message['To'])[i][0].decode('utf-8') + ' '
                else:
                    email_to = message['To']
                    tmp = message['To']
                    if len(tmp) == 1:
                        email_to = tmp[0][0]
                    else:
                        for i in range(1, len(tmp), 2):
                            email_to = message['To']
            except Exception as e:
                logging('scan email', 'Ошибка {0}. ID: {1}'.format(e, message_id.decode('utf-8')))
        if 'Cc' in message:
            try:
                if message['Cc'][0:7].upper() == '=?WINDO':
                    encoding = 'cp1251'
                    tmp = email.header.decode_header(message['Cc'])
                    for i in range(1, len(tmp), 2):
                        email_cc = email_cc + email.header.decode_header(message['Cc'])[i - 1][0].decode('cp1251') + \
                                   email.header.decode_header(message['Cc'])[i][0].decode('cp1251') + ' '
                elif message['Cc'][0:7].upper() == '=?UTF-8':
                    encoding = 'utf-8'
                    tmp = email.header.decode_header(message['Cc'])
                    for i in range(1, len(tmp), 2):
                        email_cc = email_cc + email.header.decode_header(message['Cc'])[i - 1][0].decode('utf-8') + \
                                   email.header.decode_header(message['Cc'])[i][0].decode('utf-8') + ' '
                else:
                    email_cc = message['Cc']
                    tmp = email.header.decode_header(message['Cc'])
                    for i in range(1, len(tmp), 2):
                        email_cc = message['Cc']
            except Exception as e:
                logging('scan email', 'Ошибка {0}. ID: {1}'.format(e, message_id.decode('utf-8')))
        if 'Subject' in message:
            try:
                if message['Subject'][0:7].upper() == '=?WINDO':
                    encoding = 'cp1251'
                    subject = email.header.decode_header(message['Subject'])[0][0].decode('cp1251')
                elif message['Subject'][0:7].upper() == '=?UTF-8':
                    encoding = 'utf-8'
                    subject = email.header.decode_header(message['Subject'])[0][0].decode('utf-8')
                else:
                    subject = message['Subject']
            except Exception as e:
                logging('scan email', 'Ошибка {0}. ID: {1}'.format(e, message_id.decode('utf-8')))
        if encoding == '':
            encoding = 'utf-8'
        if message.is_multipart():
            for part in message.walk():
                if part.get_content_type() == 'text/plain' and not part.get_filename():
                    body_txt = part.get_payload(decode=True)
                    try:
                        body_txt = body_txt.decode(encoding)
                    except Exception as e:
                        logging('scan email', 'Ошибка в body_text decode: {0}. Message ID: {1}'
                                .format(e, message_id.decode('utf-8')))
                        body_txt = 'Ошибка кодировки'
                if part.get_content_type() == 'text/html':
                    body_html = part.get_payload(decode=True)
                    try:
                        body_html = body_html.decode(encoding)
                    except Exception as e:
                        logging('scan email', 'Ошибка в body_html decode: {0}. Message ID: {1]'
                                .format(e, message_id.decode('utf-8')))
                        body_txt = 'Ошибка кодировки'
                if part.get_filename():
                    file_name = email.header.decode_header(part.get_filename())[0][0]
                    if str(file_name)[1] == '\'':
                        try:
                            file_name = file_name.decode(encoding)
                        except Exception as e:
                            logging('scan email', 'Ошибка в file_name={0} decode: {1}. Message ID: {2}'
                                    .format(file_name, e, message_id.decode('utf-8')))
                            file_name = email.header.decode_header(part.get_filename())[0][0]
                    if not os.path.exists(tmp_dir):
                        os.makedirs(tmp_dir)
                    attach = os.path.join(tmp_dir, file_name)
                    with open(attach, 'wb') as fl:
                        fl.write(part.get_payload(decode=True))
                    fl.close()
                    attached_files.append(attach)
        body = body_txt
        if body_txt == '':
            body = body_html
        for_cc = ''
        if email_cc != '':
            for_cc = '\nКопия: ' + email_cc
        text_for_log = """
Письмо от: {0}
Кому: {1} {2}
Тема письма:  {3}            

Текст письма:
----------------------------------------------------------------
{4}
----------------------------------------------------------------
        """.format(email_from, email_to, for_cc, subject, body)
        if not os.path.exists(tmp_dir):
            os.makedirs(tmp_dir)
        with open(os.path.join(tmp_dir, logs_name + '.txt'), 'w', encoding='utf8') as fl:
            fl.write(text_for_log)
        fl.close()
        with ZipFile(os.path.join(base_dir, logs_name + '.zip'), 'w') as zf:
            for att in attached_files:
                zf.write(att, os.path.basename(att))
            zf.write(os.path.join(tmp_dir, logs_name + '.txt'), logs_name + '.txt')
        zf.close()
        emails_zip.append(os.path.join(base_dir, logs_name + '.zip'))
        if message_id in unseen_messages:
            imap_session.uid('store', message_id, '-FLAGS', '\Seen')
        for att in attached_files:
            os.remove(att)
        os.remove(os.path.join(tmp_dir, logs_name + '.txt'))
    imap_session.close()
    return 'OK', last_messages_date, emails_zip


def run():
    logging('Grab manager', 'START')
    try:
        while True:
            if get_config('vpn') == '1':
                break
            else:
                logging('Grab manager', 'VPN не подключен при првоерке FTP')
                sleep(60)
        with psycopg2.connect(dbname='asar_db', user='asar_admin', password='aSaR14!q', host='127.0.0.1', port=5432) \
                as conn:
            with conn.cursor() as cursor:
                cursor.execute('SELECT * FROM grabber_emails WHERE status=%s', ('1',))
                emails = cursor.fetchall()
        cursor.close()
        conn.close()
        tmp_directory = '/home/asar/www/asar/emails'
        if not os.path.exists(tmp_directory):
            os.makedirs(tmp_directory)
        today = datetime.date.today().strftime('%d.%m.%Y')
        directory = os.path.join(tmp_directory, today)
        if not os.path.exists(directory):
            os.makedirs(directory)
        for eml in emails:
            last_messages_datetime = datetime.datetime.strptime(eml[4], '%d.%m.%Y %H:%M')
            while True:
                if get_config('vpn') == '1':
                    break
                else:
                    logging('Grab manager', 'VPN не подключен при првоерке FTP')
                    sleep(45)
            result, last_msg_dt, zips = scan_email(eml[1], decrypt(eml[2]), directory, last_messages_datetime)
            with psycopg2.connect(dbname='asar_db', user='asar_admin', password='aSaR14!q', host='127.0.0.1',
                                  port=5432) as conn:
                with conn.cursor() as cursor:
                    cursor.execute('SELECT max(id) FROM grabber_zips')
                    max_id = 0
                    tmp = cursor.fetchone()
                    if tmp[0] is not None:
                        max_id = tmp[0]
                    for a_zip in zips:
                        max_id += 1
                        cursor.execute('INSERT INTO grabber_zips (id, name, path) VALUES (%s, %s, %s)',
                                       (max_id, os.path.basename(a_zip), a_zip,))
                cursor.close()
                conn.commit()
            conn.close()
            last_scan_dt = eml[3]
            last_mess_dt = eml[4]
            comment = eml[6]
            status = eml[5]
            if result == 'OK':
                last_scan_dt = datetime.datetime.now().strftime('%d.%m.%Y %H:%M')
                last_mess_dt = last_msg_dt.strftime('%d.%m.%Y %H:%M')
            else:
                if result == 'PC':
                    comment = 'Password changed. ' + last_msg_dt.strftime('%d.%m.%Y %H:%M:%S')
                    status = '0'
                if result == 'NI':
                    comment = 'Can\' select inbox. ' + last_msg_dt.strftime('%d.%m.%Y %H:%M:%S')
                    status = '-1'
                if result == 'NA':
                    comment = 'Can\' search ALL messages. ' + last_msg_dt.strftime('%d.%m.%Y %H:%M:%S')
                    status = '-1'
            with psycopg2.connect(dbname='asar_db', user='asar_admin', password='aSaR14!q', host='127.0.0.1',
                                  port=5432) as conn:
                sql = """UPDATE grabber_emails SET last_scan_datetime = %s, last_messages_datetime = %s, 
                         comment = %s, status = %s WHERE id = %s"""
                with conn.cursor() as cursor:
                    cursor.execute(sql, (last_scan_dt, last_mess_dt, comment, status, eml[0]))
                cursor.close()
                conn.commit()
            conn.close()
            # eml.save()
        set_config('grabbing', '0')
        logging('Grab manager', 'FINISH')
    except Exception as e:
        logging('Grab manager', 'FINISH. Ошибка : {0}'.format(e))
        set_config('grabbing', '0')


if get_config('grabbing') == '0':
    set_config('grabbing', '1')
    run()
