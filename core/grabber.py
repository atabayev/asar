from time import sleep
import imaplib
import datetime
import email
import os
from zipfile import ZipFile
from threading import Thread
from grabber.models.Emails import Emails, Zips
from core.daemon import decrypt, reform_date, set_config, get_config

'''
    Скачивает письма и создает архив по формату.
'''


class Grabbing(Thread):

    def __init__(self):
        Thread.__init__(self)

    def run(self):
        if get_config('grabbing') == '1':
            return
        set_config('grabbing', '1')
        while True:
            if get_config('vpn') == '1':
                break
            else:
                sleep(60)
        emails = Emails.objects.all().filter(status='1')
        today = datetime.date.today().strftime('%d.%m.%Y')
        directory = os.path.join('emails', today)
        for eml in emails:
            if not os.path.exists(directory):
                os.makedirs(directory)
            last_messages_datetime = datetime.datetime.strptime(eml.last_messages_datetime, '%d.%m.%Y %H:%M')
            if not check_ip():
                set_config('grabbing', '0')
                continue
            result, last_msg_dt, zips = scan_email(eml.email, decrypt(eml.password), directory, last_messages_datetime)
            for a_zip in zips:
                zip_file = Zips()
                zip_file.name = os.path.basename(a_zip)
                zip_file.path = a_zip
                zip_file.save()
            if result == 'OK':
                eml.last_scan_datetime = datetime.datetime.now().strftime('%d.%m.%Y %H:%M')
                eml.last_messages_datetime = (last_msg_dt + datetime.timedelta(hours=3)).strftime('%d.%m.%Y %H:%M')
            else:
                if result == 'PC':
                    eml.comment = 'Password changed. ' + last_msg_dt.strftime('%d.%m.%Y %H:%M:%S')
                    eml.status = '0'
                if result == 'NI':
                    eml.comment = 'Can\' select inbox. ' + last_msg_dt.strftime('%d.%m.%Y %H:%M:%S')
                    eml.status = '-1'
                if result == 'NA':
                    eml.comment = 'Can\' search ALL messages. ' + last_msg_dt.strftime('%d.%m.%Y %H:%M:%S')
                    eml.status = '-1'
            eml.save()
        set_config('grabbing', '0')


def scan_email(the_email, emails_password, base_dir, last_scan_date):
    emails_zip = []
    dates = []
    tmp_dir = 'tmp'
    first_time = True
    last_messages_date = last_scan_date
    try:
        imap_session = imaplib.IMAP4_SSL('imap.mail.ru')
    except Exception as e:
        return 'error connect with IMAP ' + str(e)
    try:
        result = imap_session.login(the_email, emails_password)
    except:
        return 'PC', datetime.datetime.now()
    del result
    try:
        imap_session.select('INBOX')
    except:
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
        dt_list = message['date'].split(' ')
        messages_time_zone = dt_list[len(dt_list) - 1]
        if messages_time_zone[2] == 'T':
            time_zone = 6
        elif messages_time_zone[2] == 'S':
            time_zone = 3
        else:
            time_zone = 6 - int(messages_time_zone[2])
        messages_date = reform_date(email.utils.parsedate_to_datetime(message['date'])) + \
                        datetime.timedelta(hours=time_zone)
        dates.append(message['date'] + ' ' + str(time_zone) + ' ' + messages_date.strftime('%d.%m.%Y %H:%M'))
        if first_time:
            last_messages_date = messages_date
            first_time = False
        if messages_date < last_scan_date:
            break
        subject = ''
        body_txt = ''
        body_html = ''
        email_from = ''
        email_to = ''
        email_cc = ''
        if 'from' in message:
            if message['From'][0:7] == '=?UTF-8':
                tmp = email.header.decode_header(message['From'])
                for i in range(1, len(tmp), 2):
                    email_from = email_from + email.header.decode_header(message['From'])[i - 1][0].decode('utf-8') + \
                                 email.header.decode_header(message['From'])[i][0].decode('utf-8') + ' '
            else:
                email_from = message['From']
                # tmp = email.header.decode_header(message['from'])
                # for i in range(0, len(tmp), 2):
                #     email_from = message['from']
        if 'To' in message:
            if message['To'][0:7] == '=?UTF-8':
                tmp = email.header.decode_header(message['To'])
                for i in range(1, len(tmp), 2):
                    email_to = email_to + email.header.decode_header(message['To'])[i - 1][0].decode('utf-8') + \
                               email.header.decode_header(message['To'])[i][0].decode('utf-8') + ' '
            else:
                email_to = message['To']
                # tmp = message['To']
                # for i in range(1, len(tmp), 2):
                #     email_to = message['To']
        if 'Cc' in message:
            if message['Cc'][0:7] == '=?UTF-8':
                tmp = email.header.decode_header(message['Cc'])
                for i in range(1, len(tmp), 2):
                    email_cc = email_cc + email.header.decode_header(message['Cc'])[i - 1][0].decode('utf-8') + \
                               email.header.decode_header(message['Cc'])[i][0].decode('utf-8') + ' '
            else:
                email_cc = message['Cc']
                # tmp = email.header.decode_header(message['Cc'])
                # for i in range(1, len(tmp), 2):
                #     email_cc = message['Cc']
        if 'Subject' in message:
            subject = message['Subject']
            if message['Subject'][0:7].upper() == '=?UTF-8':
                subject = email.header.decode_header(message['Subject'])[0][0].decode('utf-8')
        if message.is_multipart():
            for part in message.walk():
                if part.get_content_type() == 'text/plain' and not part.get_filename():
                    body_txt = part.get_payload(decode=True)
                    try:
                        body_txt = body_txt.decode('utf-8')
                    except UnicodeDecodeError:
                        body_txt = 'Ошибка кодировки'
                if part.get_content_type() == 'text/html':
                    body_html = part.get_payload(decode=True)
                    try:
                        body_html = body_html.decode('utf-8')
                    except UnicodeDecodeError:
                        body_txt = 'Ошибка кодировки'
                if part.get_filename():
                    file_name = email.header.decode_header(part.get_filename())[0][0]
                    try:
                        file_name = file_name.decode('utf-8')
                    except AttributeError:
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
    with open('times.txt', 'w', encoding='utf-8') as fl:
        fl.write("\n".join(dates))
    fl.close()
    return 'OK', last_messages_date, emails_zip
