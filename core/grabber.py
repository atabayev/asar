import imaplib
import datetime
from datetime import timedelta
import email
import os
from zipfile import ZipFile
from threading import Thread
from grabber.models.Emails import Emails


class Grabbing(Thread):

    def __init__(self):
        Thread.__init__(self)

    def run(self):
        grabbing()


def grabbing():
    emails = Emails.objects.all().filter(status='1')
    for eml in emails:
        today = datetime.date.today().strftime('%d.%m.%Y')
        directory = os.path.join('emails', today, eml.email)
        last_scan = datetime.datetime.strptime(eml.last_messages_datetime, '%d.%m.%Y %H:%M:%S')
        result, last_msg_date = scan_email(eml.email, eml.password, directory, last_scan)
        if result == 'OK':
            eml.last_scan_datetime = (datetime.datetime.now() + timedelta(hours=6))\
                .strftime('%d.%m.%Y %H:%M:%S')
            eml.last_messages_datetime = last_msg_date.strftime('%d.%m.%Y %H:%M:%S')
        else:
            if result == 'PC':
                eml.comment = 'Password changed. ' + last_msg_date.strftime('%d.%m.%Y %H:%M:%S')
                eml.status = '0'
            if result == 'NI':
                eml.comment = 'Can\' select inbox. ' + last_msg_date.strftime('%d.%m.%Y %H:%M:%S')
                eml.status = '-1'
            if result == 'NA':
                eml.comment = 'Can\' search ALL messages. ' + last_msg_date.strftime('%d.%m.%Y %H:%M:%S')
                eml.status = '-1'
        eml.save()


def scan_email(the_email, emails_password, base_dir, last_scan_date):
    first_time = True
    last_messages_date = last_scan_date
    try:
        imap_session = imaplib.IMAP4_SSL('imap.mail.ru')
    except Exception as e:
        return 'error connect with IMAP ' + str(e)
    try:
        result = imap_session.login(the_email, emails_password)
    except Exception as e:
        return 'PC', datetime.datetime.now()
    del result
    try:
        imap_session.select('INBOX')
    except Exception as e:
        return 'NI', datetime.datetime.now()

    status, data = imap_session.uid('search', 'UNSEEN')
    unseen_messages = data[0].split()

    status, data = imap_session.uid('search', 'ALL')
    if status != 'OK':
        return 'NA', datetime.datetime.now()
    messages_id = data[0].split()

    for message_id in reversed(messages_id):
        attached_files = []
        logs_name = datetime.date.today().strftime('%m%d') + '_' + \
            message_id.decode('utf-8') + '_' + the_email
        status, data = imap_session.uid('fetch', message_id, '(RFC822)')
        if status != 'OK':
            continue

        message = email.message_from_bytes(data[0][1])
        messages_date = email.utils.parsedate_to_datetime(message['date'][0:-6])
        if first_time:
            last_messages_date = messages_date
            first_time = False

        if messages_date < last_scan_date:
            break

        subject = ''
        body_txt = ''
        body_html = ''
        if message['from'][0:7] == '=?UTF-8':
            email_from_part_1 = email.header.decode_header(message['from'])[0][0].decode('utf-8')
            email_from_part_2 = email.header.decode_header(message['from'])[1][0].decode('utf-8')
        else:
            email_from_part_1 = message['from']
            email_from_part_2 = ''

        if message.is_multipart():
            subject = message['Subject']
            if message['Subject'][0:7] == '=?UTF-8':
                subject = email.header.decode_header(message['Subject'])[0][0].decode('utf-8')
            for part in message.walk():
                if part.get_content_type() == 'text/plain' and not part.get_filename():
                    body_txt = part.get_payload(decode=True)
                    body_txt = body_txt.decode('utf-8')
                    if not os.path.exists(base_dir):
                        os.makedirs(base_dir)
                if part.get_content_type() == 'text/html':
                    body_html = part.get_payload(decode=True)
                    body_html = body_html.decode('utf-8')
                    if not os.path.exists(base_dir):
                        os.makedirs(base_dir)
                if part.get_filename():
                    file_name = email.header.decode_header(part.get_filename())[0][0].decode(
                        'utf-8')
                    if not os.path.exists(base_dir):
                        os.makedirs(base_dir)
                    attach = os.path.join(base_dir, subject + '_' + file_name)
                    with open(attach, 'wb') as fl:
                        fl.write(part.get_payload(decode=True))
                    fl.close()
                    attached_files.append(attach)
        body = body_txt
        if body_txt == '':
            body = body_html
        text_for_log = """
Письмо от: {0} {1}
Тема письма:  {2}            
            
Текст письма:
================================================================
{3}
================================================================
        """.format(email_from_part_1, email_from_part_2, subject, body)
        with open(os.path.join(base_dir, logs_name + '.txt'), 'w') as fl:
            fl.write(text_for_log)
        fl.close()
        with ZipFile(os.path.join(base_dir, logs_name + '.zip'), 'w') as zf:
            for att in attached_files:
                zf.write(att, os.path.basename(att))
            zf.write(os.path.join(base_dir, logs_name + '.txt'), logs_name + '.txt')
        zf.close()
        if message_id in unseen_messages:
            imap_session.uid('store', message_id, '-FLAGS', '\Seen')
        for att in attached_files:
            os.remove(att)
        os.remove(os.path.join(base_dir, logs_name + '.txt'))
    imap_session.close()
    return 'OK', last_messages_date
