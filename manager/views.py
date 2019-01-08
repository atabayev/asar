from datetime import date
from django.http import JsonResponse
from core.attack import Attacking
from .models.Stack import Stack
from core.daemon import get_config

# Create your views here.
"""выполняет управление процессом атак:
добавляет, редактирует, удаляет

"""


def add_to_stack(request):
    if 'token' not in request.POST:
        return JsonResponse({'response': 'no token'})
    if 'emails' not in request.POST or 'sender' not in request.POST or 'sender_password' not in request.POST or \
            'subject' not in request.POST or 'body' not in request.POST or 'method' not in request.POST or \
            'country' not in request.POST or 'description' not in request.POST:
        return JsonResponse({'response': 'no actual fields'})
    email_count = 0
    emls = request.POST['emails']
    emails = emls.split(",")
    for email in emails:
        if Stack.objects.filter(email=email).exists():
            continue
        email_count += 1
        new_stack = Stack()
        new_stack.sender = request.POST['sender']
        new_stack.sender_password = request.POST['sender_password']
        new_stack.email = email
        new_stack.subject = request.POST['subject']
        new_stack.body = request.POST['body']
        new_stack.method = request.POST['method']
        new_stack.date_add = date.today()
        new_stack.country = request.POST['country']
        new_stack.description = request.POST['description']
        new_stack.status = '0'
        new_stack.save()
        del new_stack
    if email_count > 0:
        if get_config('attacking') is '0':
            atk = Attacking()
            atk.start()
    return JsonResponse({'response': 'add: ' + str(email_count) + ' emails'})


def edit_from_stack(request):
    if 'emails' not in request.POST or 'sender' not in request.POST or 'sender_password' not in request.POST or \
            'subject' not in request.POST or 'body' not in request.POST or 'method' not in request.POST or \
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
    new_stack.body = request.POST['body']
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
