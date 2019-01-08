import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders


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
        return 'err. Ошибка аутентификации для {0} с паролем {1} при отправке {2}. Ошибка: {3}' \
            .format(sender, sender_password, atk_type, str(e))
    try:
        session.sendmail(sender, email, msg.as_string().encode('utf-8'))
    except Exception as e:
        return 'err. Ошибка: {0}, при отправке письма на почту {1} при отправке {2}'.format(str(e), email, atk_type)
    session.quit()
    return 'Успешная отправка {0}: {1}'.format(atk_type, email)


if __name__ == '__main__':
    result = send_fishing('smtp.mail.ru', 2525, 'garond@mail.ru', 'Ee060919515', 'E1dos@mail.ru', 'Тема',
                          '<html> Hello world!!! </html>')
