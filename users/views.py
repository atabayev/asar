import hashlib
from django.http import JsonResponse
from .models.Users import Users
from core.daemon import generate_token, personal_logging, logging

"""управление пользователями

"""


def auth(request):
    if 'Login' not in request.POST and 'password' not in request.POST:
        return JsonResponse({"response": "filed error"})
    username = request.POST['username'].lower()
    try:
        user = Users.objects.get(username=username)
    except Users.DoesNotExist:
        return JsonResponse({"response": "denied"})
    hash_pswd = hashlib.md5(request.POST['password'].encode('utf-8')).hexdigest()
    if hash_pswd != user.password:
        return JsonResponse({"response": "denied"})
    token = generate_token()
    user.token = token
    user.status = '1'
    user.save()
    personal_logging(user.log_file, 'Authorization!')
    return JsonResponse({"response": "ok", "username": username, "token": token})


def deauth(request):
    if 'Login' not in request.POST and 'password' not in request.POST:
        return JsonResponse({"response": "filed error"})
    username = request.POST['username'].lower()
    try:
        user = Users.objects.get(username=username)
    except Users.DoesNotExist:
        return JsonResponse({"response": "denied"})
    user.token = ''
    user.status = '0'
    user.save()
    personal_logging(user.log_file, 'Deauthorization!')
    return JsonResponse({"response": "ok"})


def reg(request):
    new_user = Users()
    new_user.username = request.POST['username'].lower()
    new_user.password = hashlib.md5(request.POST['password'].encode('utf-8')).hexdigest()
    new_user.log_file = request.POST['username'].lower() + '_log.log'
    new_user.save()
    personal_logging(new_user.log_file, 'Registration!')
    return JsonResponse({'response': 'ok'})
