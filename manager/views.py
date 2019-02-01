import os
import json
import requests
import threading
from time import sleep
from datetime import date
from django.http import JsonResponse, HttpResponse
from core.attack import Attacking
from .models.Stack import Stack
from .models.Templates import Templates
from .models.Configs import VpnFiles
from core.daemon import get_config, personal_logging, logging
from core.checker import CheckFtp
from users.models.Users import Users

"""выполняет управление процессом атак:
добавляет, редактирует, удаляет

"""


def add_to_stack(request):
    if 'username' not in request.POST or 'token' not in request.POST or 'emails' not in request.POST or \
            'sender' not in request.POST or 'sender_password' not in request.POST or 'subject' not in request.POST or \
            'body_name' not in request.POST or 'method' not in request.POST or 'country' not in request.POST or \
            'description' not in request.POST:
        return JsonResponse({'response': 'field error'})
    try:
        the_user = Users.objects.get(username=request.POST['username'])
    except Users.DoesNotExist:
        return JsonResponse({'response': 'denied'})
    if request.POST['token'] != the_user.token:
        return JsonResponse({"response": "denied"})
    email_count = 0
    emls = request.POST['emails']
    emails = emls.split(",")
    for email in emails:
        email_count += 1
        new_stack = Stack()
        new_stack.sender = request.POST['sender']
        new_stack.sender_password = request.POST['sender_password']
        new_stack.email = email
        new_stack.subject = request.POST['subject']
        try:
            new_stack.body = Templates.objects.get(name=request.POST['body_name']).body
        except Templates.DoesNotExist:
            new_stack.body = request.POST['body_name']
        new_stack.method = request.POST['method']
        new_stack.date_add = date.today()
        new_stack.country = request.POST['country']
        new_stack.description = request.POST['description']
        new_stack.ftp_host = request.POST['host']
        new_stack.ftp_login = request.POST['user']
        new_stack.ftp_password = request.POST['pswd']
        new_stack.who_hacked = request.POST['username']
        new_stack.status = '0'
        new_stack.save()
        personal_logging(the_user.log_file, 'New attacking :' + email)
        del new_stack
    if email_count > 0:
        if get_config('attacking') == '0':
            atk = Attacking()
            atk.start()
        if get_config('checking_ftp') == '0':
            check = CheckFtp()
            check.start()
    logging('add_to_stack', '{0} added emails to stack.'.format(the_user.username))
    return JsonResponse({'response': 'ok', 'emails_add': email_count})


# TODO: доделать, пока хз что делает
def get_info_about_target(request):
    if 'username' not in request.GET or 'token' not in request.GET or 'email' not in request.GET:
        return JsonResponse({'response': 'filed error'})
    try:
        the_user = Users.objects.get(username=request.GET['username'])
    except Users.DoesNotExist:
        return JsonResponse({'response': 'denied'})
    if request.GET['token'] != the_user.token:
        return JsonResponse({"response": "denied"})
    eml = Stack.objects.get()
    return ''


def load_template(request):
    if 'username' not in request.POST or 'token' not in request.POST or 'name' not in request.POST or \
            'description' not in request.POST or 'template' not in request.POST:
        return JsonResponse({'response': 'filed error'})
    try:
        the_user = Users.objects.get(username=request.POST['username'])
    except Users.DoesNotExist:
        return JsonResponse({'response': 'denied'})
    if request.POST['token'] != the_user.token:
        return JsonResponse({"response": "denied"})
    template = Templates()
    template.name = request.POST['name']
    template.body = request.POST['template']
    template.description = request.POST['description']
    template.owner = request.POST['username']
    template.save()
    personal_logging(the_user.log_file, 'Add template: {0}'.format(request.POST['name']))
    logging('add_to_stack', '{0} added template {1} to templates.'.format(the_user.username, request.POST['name']))
    return JsonResponse({"response": "ok"})


def get_templates(request):
    if 'username' not in request.GET or 'token' not in request.GET:
        return JsonResponse({'response': 'filed error'})
    try:
        the_user = Users.objects.get(username=request.GET['username'])
    except Users.DoesNotExist:
        return JsonResponse({'response': 'denied'})
    if request.GET['token'] != the_user.token:
        return JsonResponse({"response": "denied"})
    try:
        templates = Templates.objects.all()
    except Templates.DoesNotExist:
        return JsonResponse({'response': 'no templates'})
    response = {'response': 'ok', 'count': templates.count()}
    records = []
    for template in templates:
        tmp_dic = {
            'name': template.name,
            'description': template.description,
            'body': template.body}
        records.append(tmp_dic)
        del tmp_dic
    response['templates'] = records
    return JsonResponse(response)


def add_vpn_to_bd(request):
    vpn_files = os.listdir('nord_vpn')
    for fl in vpn_files:
        if not VpnFiles.objects.filter(name=fl).exists():
            vpn = VpnFiles()
            vpn.name = fl
            vpn.path = os.path.join('nord_vpn', fl)
            vpn.save()
            del vpn
    return JsonResponse({"response": "ok"})


def check_ip(request):
    result = True
    ip = requests.get('https://api.ipify.org').text
    country = json.loads(requests.get('https://www.iplocate.io/api/lookup/' + ip).text)['country_code']
    if country != 'KZ':
        return HttpResponse(str(result))
    else:
        while True:
            result = False
            vpn = VpnFiles.objects.order_by('?').first()

            # vpn_master = VpnMaster()
            # vpn_master.start(vpn.name)
            vpn_name = os.path.join('nord_vpn', vpn.name)
            t = threading.Thread(target=check_vpn, args=(vpn_name,))
            t.start()
            print('ip: ' + os.getcwd())
            sleep(15)
            ip = requests.get('https://api.ipify.org').text
            country = json.loads(requests.get('https://www.iplocate.io/api/lookup/' + ip).text)['country_code']
            if country != 'KZ':
                result = True
                break
        return HttpResponse(str(result))


def check_vpn(vpn_name):
    print(vpn_name)
    script = 'sudo openvpn {0}'.format(vpn_name)
    print('script: ' + script)
    print('vpn: ' + os.getcwd())
    print(os.system("bash -c '%s'" % script))
    # sleep(3)
    # print(os.system("bash -c '%s'" % '1322'))
    return
