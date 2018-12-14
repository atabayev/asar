import requests
import json
import os

p = {
    'emails - list',
    'sender',
    'sender_password',
    'subject',
    'body',
    'method',
    'country',
    'description',
}


def main():
    base = 'http://localhost:8000/manager/1/'
    with open('/home/yel/Документы/templates/template1.html', 'r') as fl:
        text = fl.read()
    # emails = ['reciever.test1@bk.ru', 'reciever.test2@bk.ru', 'reciever.test3@bk.ru']
    # emails = ['reciever.test1@bk.ru', 'reciever.test2@bk.ru', 'reciever.test3@bk.ru', 'reciever.test4@bk.ru']
    emails = ['reciever.test1@bk.ru']
    data = {
        'token': 'sss',
        'sender': 'sender.test@bk.ru',
        'sender_password': 'Ee060919515',
        'subject': 'test-18-1',
        'body': text,
        'method': '1',
        'country': 'Mordor',
        'description': 'this is description',
        'emails': emails
    }
    r = requests.post(base, data=data)
    print(r.text)
    print('------------------------------------------------------')
    try:
        print(r.json())
    except ValueError:
        print('No json object')


if __name__ == '__main__':
    main()
