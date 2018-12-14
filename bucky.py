from email import encoders
from email.mime.base import MIMEBase
from tkinter import *
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from html.parser import HTMLParser
from tkinter import messagebox
from string import Template
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from tkinter import ttk
from threading import Event, Thread
from tkinter import filedialog
import smtplib
import tkinter.messagebox
# import the smtplib module. It should be included in Python by default
import smtplib
# import necessary packages
# import urlopen
import requests
import psycopg2
import time
import sys
import chardet
import atexit
import ntpath


# Вытягивает имя из страницы Мой мир
class TitleParser(HTMLParser):
    def error(self, message):
        pass

    def __init__(self):
        HTMLParser.__init__(self)
        self.match = False
        self.title = ''

    def handle_starttag(self, tag, attributes):
        self.match = True if tag == 'title' else False

    def handle_data(self, data):
        if self.match:
            self.title = data
            self.match = False


# Вытягивает имя из страницы Мой мир
def get_username(username, domain):
    url = "http://my.mail.ru/" + domain + "/" + username
    # print(url)
    firstname = ""

    try:

        # html_string = urlopen(url)

        url = requests.get(url)
        html_string = url.text

        parser = TitleParser()
        parser.feed(html_string)
        # print(parser.title.split()[0])

        firstname = parser.title.split()[0]

        # if firstname == u"Менің":# and firstname == "Мой"
        #     firstname = "Noname"

    except Exception as e:
        log = str(datetime.now()) + " Error:#1" + str(e.args)
        file = open("logs.txt", mode="a", encoding="utf-8")
        file.write(log + "\n")
        file.close()
        print("Error#1: " + str(e.args))

    return firstname


MY_ADDRESS = ''
PASSWORD = ''


# Вытаскивает получателей из файла mycontacts.txt
def get_receivers(filename):
    names = []
    emails = []
    number_of_text_files = []
    try:
        with open(filename, mode='r', encoding='utf-8') as contacts_file:
            for a_contact in contacts_file:
                if 2 is len(a_contact.split()):
                    # print("len 2")
                    username = get_username(a_contact.split()[0].split("@")[0],
                                            a_contact.split()[0].split("@")[1].split(".")[0])
                    # messagebox.showinfo("Contact", username)
                    names.append(username)
                    emails.append(a_contact.split()[0])
                    number_of_text_files.append(a_contact.split()[1])
                if 3 is len(a_contact.split()):
                    # print("len 2")
                    names.append(a_contact.split()[1])
                    emails.append(a_contact.split()[0])
                    number_of_text_files.append(a_contact.split()[2])
            contacts_file.close()
    except Exception as e:
        log = str(datetime.now()) + " Error#2:" + str(e.args)
        file = open("logs.txt", mode="a", encoding="utf-8")
        file.write(log + "\n")
        file.close()
        print("Error#2: " + str(e.args))

    return names, emails, number_of_text_files


# Вытаскивает получателей из БД
def get_receivers_db():
    names = []
    emails = []

    # !/usr/bin/python2.4
    #
    # Small script to show PostgreSQL and Pyscopg together
    #

    try:
        conn = psycopg2.connect("dbname='postgres' user='kira' host='localhost' password='password'")
        print("I am able to connect to the database")

    except:
        print("I am unable to connect to the database")

    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT mycontacts.first_name, emails.email FROM mycontacts INNER JOIN emails ON mycontacts.id = emails.id")
    except:
        print("I can't SELECT from mycontacts")

    rows = cur.fetchall()
    print("\nRows: \n")

    for row in rows:
        print("   ", row[0] + " " + row[1])
        a_contact = row[0] + " " + row[1]
        if 1 is len(a_contact.split()):
            username = get_username(a_contact.split()[0].split("@")[0],
                                    a_contact.split()[0].split("@")[1].split(".")[0])
            messagebox.howinfo("Contact", username)
            names.append(username)
            emails.append(a_contact.split()[0])

        else:
            names.append(a_contact.split()[0])
            emails.append(a_contact.split()[1])

    return names, emails


# Читает шаблоны
def read_template(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as template_file:
            template_file_content = template_file.read()
            template_file.close()
        return Template(template_file_content)
    except Exception as e:
        log = str(datetime.now()) + " Error#3:" + str(e.args)
        file = open("logs.txt", mode="a", encoding="utf-8")
        file.write(log + "\n")
        file.close()
        print("Error#3: " + str(e.args))


def read_login(filename):
    try:
        login = ""
        password = ""
        with open(filename, 'r', encoding='utf-8') as smtp_file:
            for smtp in smtp_file:
                if 2 is len(smtp.split()):
                    login = smtp.split()[0]
                    password = smtp.split()[1]
                    return login, password
            smtp_file.close()
            return login, password
    except Exception as e:
        log = str(datetime.now()) + " Error#4:" + str(e.args)
        file = open("logs.txt", mode="a", encoding="utf-8")
        file.write(log + "\n")
        file.close()
        print("Error#4: " + str(e.args))


# Вытаскивает получателей из файла mycontacts.txt
names, emails, texts = get_receivers('mycontacts.txt')  # read contacts
# names, emails = get_receivers_db()  # read contacts

# Читает шаблоны
message_template = read_template('message.txt')

# Читает логин и пароль отправителя из файла smtp.txt
MY_ADDRESS, PASSWORD = read_login('smtp.txt')

log = "\n" + str(datetime.now()) + " Start as:" + MY_ADDRESS
print(log)
file = open("logs.txt", mode="a", encoding="utf-8")
file.write(log + "\n")
file.close()


# numbers, files = read_namefiles('files.txt')

def get_files(filename):
    files = []
    try:
        print("Reading list of files:")
        with open(filename, mode='r', encoding='utf-8') as number_file:
            for a_file in number_file:
                if 3 is len(a_file.split(".")):
                    # messagebox.showinfo("Contact", username)
                    files.append(a_file.split("\n")[0])
            number_file.close()
    except Exception as e:
        log = str(datetime.now()) + " Error#21:" + str(e.args)
        file = open("logs.txt", mode="a", encoding="utf-8")
        file.write(log + "\n")
        file.close()
        print("Error#2: " + str(e.args))

    return files


def get_senders(filename):
    senders = []
    try:
        print("Reading list of senders:")
        with open(filename, mode='r', encoding='utf-8') as number_file:
            for a_file in number_file:
                if 2 is len(a_file.split(" ")):
                    # messagebox.showinfo("Contact", username)
                    senders.append(a_file.split("\n")[0])
            number_file.close()
    except Exception as e:
        log = str(datetime.now()) + " Error#21:" + str(e.args)
        file = open("logs.txt", mode="a", encoding="utf-8")
        file.write(log + "\n")
        file.close()
        print("Error#2: " + str(e.args))

    return senders


def main():
    try:
        # set up the SMTP server
        # s = smtplib.SMTP(host='smtp.mail.ru', port=2525)
        # s.starttls()
        # s.login(mail_entry.get(), pass_entry.get())
        status['text'] = "processing..."

        # Проверяет совпадает ли введенный логин и пароль отправителя с данными в файле smtp.txt
        if MY_ADDRESS + " " + PASSWORD is not mail_entry.get() + " " + pass_entry.get():
            file = open("smtp.txt", mode="a")
            log = str(datetime.now()) + " Login as:" + mail_entry.get()
            print(log)
            status['text'] = log
            file.seek(0)  # <- This is the missing piece
            file.truncate()
            file.write(mail_entry.get() + " " + pass_entry.get() + "\n")
            file.close()

        # print(attachment)

        # Проверка стоит ли галочка
        is_hidden = var.get()
        print(is_hidden)
        # если не стоит
        if not var.get():
            counts = 0
            counter = 0
            # For each contact, send the email:

            # print(str(next_time) + " time " + str(minutes) + " minutes sent")
            #
            # print(str(minutes) + " minutes before\n")

            if files_lb.size() == 0:
                status_msg = "No files are in listbox"
                messagebox.showinfo("Attention", status_msg)
                status['text'] = status_msg
                return

            time_to_change = 0
            change = 0

            for name, email, text in zip(names, emails, texts):

                try:
                    if counts == int(count_entry.get()):
                        status_msg = "Please, wait " + interval_entry.get() + " minute(s)..."
                        print(status_msg)
                        # messagebox.showinfo("Wait!", status_msg)
                        status['text'] = status_msg
                        time.sleep(60 * int(interval_entry.get()))
                        counts = 0

                        counts += 1

                        # set up the SMTP server
                        s = smtplib.SMTP(host='smtp.mail.ru', port=2525)
                        s.starttls()

                        msg = MIMEMultipart('alternative')  # create a message

                        # print("Sender is one")
                        # s.login(mail_entry.get(), pass_entry.get())
                        # msg['From'] = mail_entry.get()

                        status_msg = ""
                        if senders_lb.size() == 0:
                            status_msg = "Sender is one"
                            print(status_msg)
                            s.login(mail_entry.get(), pass_entry.get())
                            msg['From'] = mail_entry.get()
                        else:
                            status_msg = "Sender is " + senders[change].split()[0]
                            print(status_msg)
                            s.login(senders[change].split()[0], senders[change].split()[1])
                            msg['From'] = senders[change].split()[0]
                            time_to_change += 1
                        if time_to_change == int(time_to_change_entry.get()):
                            change += 1
                            time_to_change = 0
                        if change == len(senders):
                            change = 0

                        filename = ""
                        for el in files_lb.get(0, END):
                            number = el.split(".")[0]
                        if int(float(number)) == int(text):
                            filename = el.split(".")[1] + "." + el.split(".")[2]

                        if filename is "":
                            status_msg = "File was not selected"
                            print(status_msg)
                            messagebox.showinfo("Attention", status_msg)
                            status['text'] = status_msg
                            return

                        bom = bomType(filename)
                        attachment = open(filename, 'r', encoding=bom, errors='ignore')
                        msg.attach(MIMEText(attachment.read(), 'html'))

                        attachment.close()

                        del attachment

                        # add in the actual person name to the message template
                        # message =  MIMEText(message_template, 'html').substitute()# PERSON_NAME=nammessage_template

                        # Prints out the message body for our sake

                        # setup the parameters of the message
                        msg['To'] = email
                        msg['Subject'] = theme_entry.get()

                        # add in the message body
                        # msg.attach(msg.as_string())

                        # send the message via the server set up earlier.
                        s.send_message(msg)

                        del msg

                        counter += 1
                        log = str(datetime.now()) + " " + str(counter) + " Sent to " + email + " Filename: " + filename

                        print(log)

                        # messagebox.showinfo(status_msg, log)
                        status['text'] = status_msg

                        file = open("logs.txt", mode="a", encoding="utf-8")

                        file.write(log + "\n")

                        file.close()
                        s.quit()

                        del s

                except Exception as e:
                    log = str(datetime.now()) + " Error#5:" + str(e.args)
                    file = open("logs.txt", mode="a", encoding="utf-8")
                    file.write(log + "\n")
                    file.close()
                    print("Error#5: " + str(e.args))
                    pass

        else:
            counts = 0
            counter = 0
            # For each contact, send the email:

            # print(str(next_time) + " time " + str(minutes) + " minutes sent")
            #
            # print(str(minutes) + " minutes before\n")

            if files_lb.size() == 0:
                status_msg = "No files are in listbox"
                # messagebox.showinfo("Attention", status_msg)
                status['text'] = status_msg
                return

            time_to_change = 0
            change = 0

            names_str = ",".join(names)
            emails_str = ",".join(emails)

            try:
                if counts == int(count_entry.get()):
                    status_msg = "Please, wait " + interval_entry.get() + " minute(s)..."
                    print(status_msg)
                # messagebox.showinfo("Wait!", status_msg)
                status['text'] = status_msg
                time.sleep(60 * int(interval_entry.get()))
                counts = 0

                counts += 1

                # set up the SMTP server
                s = smtplib.SMTP(host='smtp.mail.ru', port=2525)
                s.starttls()

                msg = MIMEMultipart('alternative')  # create a message

                # print("Sender is one")
                # s.login(mail_entry.get(), pass_entry.get())
                # msg['From'] = mail_entry.get()

                status_msg = ""
                if senders_lb.size() == 0:
                    status_msg = "Sender is one"
                    print(status_msg)
                    s.login(mail_entry.get(), pass_entry.get())
                    msg['From'] = mail_entry.get()
                else:
                    status_msg = "Sender is " + senders[change].split()[0]
                    print(status_msg)
                    s.login(senders[change].split()[0], senders[change].split()[1])
                    msg['From'] = senders[change].split()[0]
                    time_to_change += 1
                if time_to_change == int(time_to_change_entry.get()):
                    change += 1
                    time_to_change = 0
                if change == len(senders):
                    change = 0

                filename = ""
                for el in files_lb.get(0, END):
                    number = el.split(".")[0]
                if int(float(number)) == int(texts[1]):
                    filename = el.split(".")[1] + "." + el.split(".")[2]

                if filename is "":
                    status_msg = "File was not selected"
                    print(status_msg)
                    # messagebox.showinfo("Attention", status_msg)
                    status['text'] = status_msg
                    return

                bom = bomType(filename)

                attachment = open(filename, 'r', encoding=bom, errors='ignore')
                msg.attach(MIMEText(attachment.read(), 'html'))
                attachment.close()

                del attachment

                # add in the actual person name to the message template
                # message =  MIMEText(message_template, 'html').substitute()# PERSON_NAME=nammessage_template

                # Prints out the message body for our sake

                # setup the parameters of the message
                msg['To'] = emails_str
                msg['Subject'] = theme_entry.get()

                # add in the message body
                # msg.attach(msg.as_string())

                # send the message via the server set up earlier.
                s.send_message(msg)

                del msg

                counter += 1
                log = str(datetime.now()) + " " + str(counter) + " Sent to " + emails_str + " Filename: " + filename

                print(log)

                # messagebox.showinfo(status_msg, log)
                status['text'] = status_msg

                file = open("logs.txt", mode="a", encoding="utf-8")

                file.write(log + "\n")

                file.close()
                s.quit()

                del s

            except Exception as e:
                log = str(datetime.now()) + " Error#5:" + str(e.args)
                file = open("logs.txt", mode="a", encoding="utf-8")
                file.write(log + "\n")
                file.close()
                print("Error#5: " + str(e.args))
                pass
                # Terminate the SMTP session and close the connection
                # s.quit()

        file2 = open("files.txt", mode="a", encoding='utf-8')

        # file2.truncate(0)
        # file2.seek(0)  # <- This is the missing piece
        open("files.txt", "w", encoding='utf-8').close()

        i = 0
        while i < files_lb.size():
            file2.write(files_lb.get(i) + '\n')
            i = i + 1

        file2.close()

        status_msg = "Sent"
        messagebox.showinfo("Messages", "Sent!")
        print(status_msg)

        # messagebox.showinfo("", status_msg)
        status['text'] = status_msg

    except  Exception as e:
        log = str(datetime.now()) + " Error#6:" + str(e.args)
        file = open("logs.txt", mode="a", encoding="utf-8")
        file.write(log + "\n")
        file.close()
        print("Error#6: " + str(e.args))


def send_template():
    try:
        # set up the SMTP server
        s = smtplib.SMTP(host='smtp.mail.ru', port=2525)
        s.starttls()
        s.login(mail_entry.get(), pass_entry.get())

        if MY_ADDRESS + " " + PASSWORD is not mail_entry.get() + " " + pass_entry.get():
            file = open("smtp.txt", mode="a")

            log = str(datetime.now()) + " Login as:" + mail_entry.get()

            print(log)

            file.seek(0)  # <- This is the missing piece
            file.truncate()

            file.write(mail_entry.get() + " " + pass_entry.get() + "\n")

            file.close()

        is_hidden = var.get()
        print(is_hidden)
        # Проверка стоит ли галочка
        if not var.get():
            counts = 0
            counter = 0
            # For each contact, send the email:

            for name, email, text in zip(names, emails, texts):
                # messagebox.showinfo("Contact", email)
                try:
                    if counts == int(count_entry.get()):
                        print("Please, wait, the timer is working...")
                        time.sleep(60 * int(interval_entry.get()))
                        counts = 0

                    counts += 1

                    # set up the SMTP server
                    s = smtplib.SMTP(host='smtp.mail.ru', port=2525)
                    s.starttls()
                    s.login(mail_entry.get(), pass_entry.get())

                    msg = MIMEMultipart()  # create a message

                    filename = attachment_text.cget("text")  # attachment_button.

                    if filename:
                        attachment = open(filename, 'rb')

                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload((attachment).read())
                        encoders.encode_base64(part)
                        part.add_header('Content-Disposition', "attachment; filename= %s" % ntpath.basename(filename))

                        msg.attach(part)

                        attachment.close()

                        del attachment

                    message_temp = MIMEText(Template(template_text.get("1.0", END)).substitute(PERSON_NAME=name),
                                            'plain')

                    msg.attach(message_temp)

                    counter += 1
                    log = str(datetime.now()) + " " + str(counter) + " Sent to " + email + " Filename: " + ""

                    print(log)

                    file = open("logs.txt", mode="a", encoding="utf-8")

                    file.write(log + "\n")

                    file.close()

                    # setup the parameters of the message
                    msg['From'] = mail_entry.get()
                    msg['To'] = email
                    msg['Subject'] = theme_entry.get()

                    # add in the message body
                    # msg.attach(msg.as_string())

                    # send the message via the server set up earlier.
                    s.send_message(msg)
                    del msg

                except Exception as e1:
                    log = str(datetime.now()) + " Error#51:" + str(e1.args)
                    file = open("logs.txt", mode="a", encoding="utf-8")
                    file.write(log + "\n")
                    file.close()
                    print("Error#5: " + str(e1.args))
                    pass
            # Terminate the SMTP session and close the connection
            s.quit()

        else:
            counts = 0
            counter = 0
            # For each contact, send the email:

            names_str = ",".join(names)
            emails_str = ",".join(emails)

            # //texts_str in
            # //zip(, texts):

            try:
                if counts == int(count_entry.get()):
                    print("Please, wait, the timer is working...")
                    time.sleep(60 * int(interval_entry.get()))
                    counts = 0

                counts += 1

                # set up the SMTP server
                s = smtplib.SMTP(host='smtp.mail.ru', port=2525)
                s.starttls()
                s.login(mail_entry.get(), pass_entry.get())

                msg = MIMEMultipart()  # create a message

                filename = attachment_text.cget("text")  # attachment_button.
                if filename:
                    attachment = open(filename, 'rb')

                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload((attachment).read())
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition', "attachment; filename= %s" % ntpath.basename(filename))

                    msg.attach(part)

                    attachment.close()

                    del attachment

                message_temp = Template(template_text.get("1.0", END))

                if names[counts]:
                    message_temp = MIMEText(Template(template_text.get("1.0", END)).substitute(PERSON_NAME=names[counts]),
                                            'plain')

                msg.attach(message_temp)

                counter += 1
                log = str(datetime.now()) + " " + str(counter) + " Sent to " + emails_str + " Filename: " + ""

                print(log)

                file = open("logs.txt", mode="a", encoding="utf-8")

                file.write(log + "\n")

                file.close()

                # setup the parameters of the message
                msg['From'] = mail_entry.get()
                msg['Bcc'] = emails_str
                msg['Subject'] = theme_entry.get()

                # add in the message body
                # msg.attach(msg.as_string())

                # send the message via the server set up earlier.
                s.send_message(msg)
                del msg

                # Terminate the SMTP session and close the connection
                s.quit()

            except  Exception as e2:
                log = str(datetime.now()) + " Error#52:" + str(e2.args)
                file = open("logs.txt", mode="a", encoding="utf-8")
                file.write(log + "\n")
                file.close()
                print("Error#5: " + str(e2.args))
                pass

        print("Sent")
        messagebox.showinfo("Messages", "Sent!")

    except  Exception as e3:
        log = str(datetime.now()) + " Error#6:" + str(e3.args)
        file = open("logs.txt", mode="a", encoding="utf-8")
        file.write(log + "\n")
        file.close()
        print("Error#6: " + str(e3.args))


# def send_attachment():
#     try:
#         # set up the SMTP server
#         s = smtplib.SMTP(host='smtp.mail.ru', port=2525)
#         s.starttls()
#         s.login(mail_entry.get(), pass_entry.get())
#
#         if MY_ADDRESS + " " + PASSWORD is not mail_entry.get() + " " + pass_entry.get():
#             file = open("smtp.txt", mode="a")
#
#             log = str(datetime.now()) + " Login as:" + mail_entry.get()
#
#             print(log)
#
#             file.seek(0)  # <- This is the missing piece
#             file.truncate()
#
#             file.write(mail_entry.get() + " " + pass_entry.get() + "\n")
#
#             file.close()
#
#         # print(attachment)
#
#         counts = 0
#         counter = 0
#         # For each contact, send the email:
#
#         for name, email, text in zip(names, emails, texts):
#
#             try:
#                 if counts == int(count_entry.get()):
#                     print("Please, wait, the timer is working...")
#                     time.sleep(60 * int(interval_entry.get()))
#                     counts = 0
#
#                 counts += 1
#
#                 # set up the SMTP server
#                 s = smtplib.SMTP(host='smtp.mail.ru', port=2525)
#                 s.starttls()
#                 s.login(mail_entry.get(), pass_entry.get())
#
#                 msg = MIMEMultipart()  # create a message
#
#                 filename = attachment_text.cget("text")  # attachment_button.
#
#                 attachment = open(filename, 'rb')
#
#                 part = MIMEBase('application', 'octet-stream')
#                 part.set_payload((attachment).read())
#                 encoders.encode_base64(part)
#                 part.add_header('Content-Disposition', "attachment; filename= %s" % filename)
#
#                 msg.attach(part)
#
#                 attachment.close()
#
#                 del attachment
#
#                 counter += 1
#                 log = str(datetime.now()) + " " + str(counter) + " Sent attached file to " + email + " Filename: " + ""
#
#                 print(log)
#
#                 file = open("logs.txt", mode="a", encoding="utf-8")
#
#                 file.write(log + "\n")
#
#                 file.close()
#
#                 # setup the parameters of the message
#                 msg['From'] = mail_entry.get()
#                 msg['To'] = email
#                 msg['Subject'] = theme_entry.get()
#
#                 # add in the message body
#                 # msg.attach(msg.as_string())
#
#                 # send the message via the server set up earlier.
#                 s.send_message(msg)
#                 del msg
#
#             except  Exception as ex:
#                 log = str(datetime.now()) + " Error#5:" + str(ex.args)
#                 file = open("logs.txt", mode="a", encoding="utf-8")
#                 file.write(log + "\n")
#                 file.close()
#                 print("Error#5: " + str(ex.args))
#                 pass
#         # Terminate the SMTP session and close the connection
#         s.quit()
#
#         print("Sent")
#         messagebox.showinfo("Messages", "Sent!")
#
#     except Exception as e:
#         log = str(datetime.now()) + " Error#6:" + str(e.args)
#         file = open("logs.txt", mode="a", encoding="utf-8")
#         file.write(log + "\n")
#         file.close()
#         print("Error#6: " + str(e.args))


def add():
    try:
        if "" is not file_name_entry.get():
            text = file_name_entry.get()  # files_lb.size() + 1) + "." +
            if text in files_lb.get(0, END):
                print("Listbox already contains such a value")
                return
            else:
                files_lb.insert(END, text)
        # files_lb.insert(END, file_name_entry.get())

    except Exception as e:
        log = str(datetime.now()) + " Error#7:" + str(e.args)
        file = open("logs.txt", mode="a", encoding="utf-8")
        file.write(log + "\n")
        file.close()
        print("Error#7" + str(e.args))


def remove():
    try:
        # global things
        # Delete from Listbox
        # selection = files_lb.curselection()[0]
        files_lb.delete(files_lb.curselection())
        # # Delete from list that provided it
        # value = eval(files_lb.get(selection[0]))
        # ind = things.index(value)
        # del (things[ind])
        # print(things)
    except Exception as e:
        log = str(datetime.now()) + " Error#8:" + str(e.args)
        file = open("logs.txt", mode="a", encoding="utf-8")
        file.write(log + "\n")
        file.close()
        print("Error#8: " + str(e.args))


if int(sys.version[0]) != 3:
    print('Aborted: Python 3.x required')
    sys.exit(1)


def bomType(file):
    try:
        rawdata = open(file, 'rb').read()
        result = chardet.detect(rawdata)
        charenc = result['encoding']
        # print(charenc)
        return charenc
    # f = open(file, 'rb')
    # b = f.read(4)
    # f.close()

    # if (b[0:3] == b'\xef\xbb\xbf'):
    #    return "utf8"

    # Python automatically detects endianess if utf-16 bom is present
    # write endianess generally determined by endianess of CPU
    # if ((b[0:2] == b'\xfe\xff') or (b[0:2] == b'\xff\xfe')):
    #    return "utf16"

    # if ((b[0:5] == b'\xfe\xff\x00\x00')
    #          or (b[0:5] == b'\x00\x00\xff\xfe')):
    #    return "utf32"

    # If BOM is not provided, then assume its the codepage
    #     used by your operating system
    # return "windows-1251"
    # For the Russian its: windows-1251

    except Exception as e:
        log = str(datetime.now()) + " Error#9:" + str(e.args)
        file = open("logs.txt", mode="a", encoding="utf-8")
        file.write(log + "\n")
        file.close()
        print("Error#9: " + str(e.args))


def call_repeatedly(interval, func, *args):
    stopped = Event()

    def loop():
        while not stopped.wait(interval):  # the first call is in `interval` secs
            func(*args)

    Thread(target=loop).start()
    return stopped.set


def goodbye(name, adjective):
    try:
        log = str(datetime.now()) + " Logout:" + MY_ADDRESS

        file = open("logs.txt", mode="a", encoding="utf-8")

        file.write(log + "\n")

        file.close()

        print('Goodbye, %s, it was %s to meet you.' % (name, adjective))

    except Exception as e:
        log = str(datetime.now()) + " Error#9:" + str(e.args)
        file = open("logs.txt", mode="a", encoding="utf-8")
        file.write(log + "\n")
        file.close()
        print("Error#9: " + str(e.args))


def my_file():
    file = filedialog.askopenfile(mode="r", initialdir="/", title="select file",
                                  filetypes=(("all files", "*.*"), ("text files", "*.txt")))
    if file:
        template_text.delete(1.0, END)
        template_text.insert(1.0, file.read())
        file.close()

    # open the selected txt file with notepad to read the content


def my_attachment_file():
    file = filedialog.askopenfile(mode="r", initialdir="/", title="select file",
                                  filetypes=(("all files", "*.*"), ("text files", "*.txt")))
    if file:
        attachment_text['text'] = file.name
        file.close()

    # open the selected txt file with notepad to read the content


def ShowChoice():
    choosen = v.get()
    if choosen == 0:
        button.pack()
        interval_label.pack()
        interval_entry.pack()
        count_label.pack()
        count_entry.pack()
        file_name.pack()
        file_name_entry.pack()
        files_lb.pack()
        button2.pack()
        button3.pack()

        #        template_person_label.pack_forget()

        #        template_person_entry.pack_forget()
        #        hidden_senders_check.pack_forget()
        template_text.place_forget()
        template_button.pack_forget()

        send_template_button.pack_forget()
        #        send_attachment_button.pack_forget()
        attachment_text.pack_forget()
        attachment_button.pack_forget()

    if choosen == 1:
        button.pack_forget()
        send_template_button.pack()

        file_name.pack_forget()
        file_name_entry.pack_forget()
        interval_label.pack_forget()
        interval_entry.pack_forget()
        count_label.pack_forget()
        count_entry.pack_forget()
        files_lb.pack_forget()
        button2.pack_forget()
        button3.pack_forget()

        #        template_person_label.pack()

        #        template_person_entry.pack()
        #        hidden_senders_check.pack()
        template_text.place(x=230, y=230, height=300, width=600)

        template_button.pack()

        # send_attachment_button.pack()
        attachment_text.pack()
        attachment_button.pack()

    if choosen == 2:
        button.pack_forget()

        send_template_button.pack_forget()
        # send_attachment_button.pack_forget()
        attachment_text.pack_forget()
        attachment_button.pack_forget()

        interval_label.pack_forget()
        interval_entry.pack_forget()
        count_label.pack_forget()
        count_entry.pack_forget()
        file_name.pack_forget()
        file_name_entry.pack_forget()
        files_lb.pack_forget()
        button2.pack_forget()
        button3.pack_forget()

        #        template_person_label.pack_forget()

        #        template_person_entry.pack_forget()
        #        hidden_senders_check.pack_forget()
        template_text.place_forget()
        template_button.pack_forget()


root = Tk()

root.title('Emailer')

root.geometry('500x700')

# mainframe = ttk.Frame(root, padding="3 3 12 12")
# mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
# mainframe.columnconfigure(0, weight=1)
# mainframe.rowconfigure(0, weight=1)

status = Label(root, text="processing…", bd=1, relief=SUNKEN, anchor=W)

# topframe = frame(root)

receivers_label = Label(text="Receivers:")

from_senders = Label(text="Senders: ")

from_mail = Label(text="From: ")

from_pass = Label(text="Password: ")

mail_entry = Entry()
mail_entry.insert(0, MY_ADDRESS)
mail_entry.focus()

pass_entry = Entry()
pass_entry.insert(0, PASSWORD)

files = get_files('files.txt')  # read list of files with numbers

files_lb = Listbox(root)

if 1 <= len(files):
    for f in files:
        files_lb.insert(END, f)

senders_lb = Listbox(root)

senders = get_senders('senders.txt')  # read list of files with numbers

if 1 <= len(senders):
    for s in senders:
        senders_lb.insert(END, s.split()[0])

atexit.register(goodbye, MY_ADDRESS, 'nice')

to_text = Label(text="To: ")

receivers_entry = Text(root, height=5, width=20)

scroll1 = Scrollbar(root, command=receivers_entry.yview)

for name, email, text in zip(names, emails, texts):
    receivers_entry.insert('1.0', email + " " + text + "\n")

receivers_entry.configure(yscrollcommand=scroll1.set)
receivers_entry.tag_configure('bold_italics',
                              font=('Verdana', 12, 'bold', 'italic'))
receivers_entry.tag_configure('big',
                              font=('Verdana', 24, 'bold'))
receivers_entry.tag_configure('color',
                              foreground='blue',
                              font=('Tempus Sans ITC', 14))

receivers_entry.tag_configure('groove',
                              relief=GROOVE,
                              borderwidth=2)

receivers_entry.tag_bind('bite',
                         '<1>',
                         lambda e, t=receivers_entry: t.insert(END, "Text"))

theme_text = Label(text="Theme:")

theme_entry = Entry()

# text = Text(root, height=20, width=20)
#
# # message_temp_sub = MIMEText(message_template.substitute(PERSON_NAME="PERSON_NAME"), 'plain')
# # text.insert('1.0', message_temp_sub)
#
# scroll = Scrollbar(root, command=text.yview)
#
# text.configure(yscrollcommand=scroll.set)
# text.tag_configure('bold_italics',
#                    font=('Verdana', 12, 'bold', 'italic'))
# text.tag_configure('big',
#                    font=('Verdana', 24, 'bold'))
# text.tag_configure('color',
#                    foreground='blue',
#                    font=('Tempus Sans ITC', 14))
#
# text.tag_configure('groove',
#                    relief=GROOVE,
#                    borderwidth=2)
#
# text.tag_bind('bite',
#               '<1>',
#               lambda e, t=text: t.insert(END, "Text"))

button = Button(text="Send html", command=main)

send_template_button = Button(text="Send template", command=send_template)

# send_attachment_button = Button(text="Send attachment", command=send_attachment)

button2 = Button(text="Add", command=add)

button3 = Button(text="Remove", command=remove)

file_name = Label(text="File name: ")

file_name_entry = Entry()

time_to_change_label = Label(text="Time to change sender, after: ")

choose_a_module_label = Label(text="""Choose a module:""")

time_to_change_entry = Entry()
time_to_change_entry.insert(0, str(len(senders)))

interval_label = Label(text="Interval, min: ")

count_label = Label(text="Number of  messages: ")

interval_entry = Entry()
interval_entry.insert(0, "1")

count_entry = Entry()
count_entry.insert(0, "1")

# messagebox.showinfo("Messages", "Sent")

time_to_change_label.place(x=10, y=10)
time_to_change_entry.place(x=10, y=30)

from_mail.place(x=10, y=50)
mail_entry.place(x=10, y=70)

from_pass.place(x=10, y=90)
pass_entry.place(x=10, y=110)

from_senders.place(x=10, y=130)
# from_senders.pack()

senders_lb.place(x=10, y=150)
# senders_lb.pack()

choose_a_module_label.place(x=10, y=320)

theme_text.pack()
theme_entry.pack()

receivers_label.place(x=10, y=460)
# to_text.pack()
receivers_entry.place(x=10, y=480)

# template_person_label = Label(root, text="Person name")

# template_person_entry = Entry(root, text="PERSON_NAME")
# template_button.grid(row=1, column=0)

var = BooleanVar()
hidden_senders_check = Checkbutton(root, text="One time message", variable=var)
hidden_senders_check.pack()
state = var.get()

template_text = Text(root)
# message_temp_sub = MIMEText(message_template.substitute(PERSON_NAME="PERSON_NAME"), 'plain')
template_text.insert("1.0", message_template.substitute(PERSON_NAME="PERSON_NAME"))
# template_label.grid(row=0, column=0)
template_button = Button(root, text="Open template file", command=my_file)

# template_button.grid(row=1, column=0)

attachment_text = Label(root)

attachment_button = Button(root, text="Attach file", command=my_attachment_file)

v = tkinter.IntVar()
v.set(0)  # initializing the choice, i.e. Python

types = [
    ("html", 1),
    ("Template", 2),
]

x = 320
for val, type in enumerate(types):
    x = x + 20
    tkinter.Radiobutton(
        text=type,
        padx=20,
        variable=v,
        command=ShowChoice,
        value=val).place(x=10, y=x)  # .pack(anchor=tkinter.W)
#    radio_button


# text.pack(side=LEFT)
# scroll.pack(side=RIGHT, fill=Y)

button.pack()

interval_label.pack()
interval_entry.pack()
count_label.pack()
count_entry.pack()

file_name.pack()
file_name_entry.pack()

files_lb.pack()
button2.pack()
button3.pack()

status.pack(side=BOTTOM, fill=X)

root.mainloop()
