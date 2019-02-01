from django.http import JsonResponse, HttpResponse
from manager.models.Stack import Stack
from core.daemon import logging
from core.start_daemons import StartDaemons
from core.tester import Tester
from users.models.Users import Users


def all_records(request):
    if "token" not in request.GET or "username" not in request.GET:
        return JsonResponse({"response": "field error"})
    try:
        the_user = Users.objects.get(username=request.GET['username'])
    except Users.DoesNotExist:
        return JsonResponse({'response': 'denied'})
    if request.GET['token'] != the_user.token:
        return JsonResponse({"response": "denied"})
    answer = {"response": "ok"}
    try:
        orders = Stack.objects.all()
    except Stack.DoesNotExist:
        return JsonResponse({"response": "stack error"})
    records = []
    for order in orders:
        tmp_rec = {"email": order.email,
                   "country": order.country,
                   "description": order.description,
                   "method": order.method,
                   "by_virus": order.by_virus,
                   "by_fishing": order.by_fishing,
                   "date_add": order.date_add,
                   "date_hacked": order.date_hacked,
                   "comment": order.comment,
                   "status": order.status}
        records.append(tmp_rec)
    answer["orders"] = records
    return JsonResponse(answer)


def start_daemons(request):
    if "token" not in request.POST or "username" not in request.POST:
        return JsonResponse({"response": "field error"})
    try:
        the_user = Users.objects.get(username=request.POST['username'])
    except Users.DoesNotExist:
        return JsonResponse({'response': 'denied'})
    if request.POST['token'] != the_user.token:
        return JsonResponse({"response": "denied"})
    daemons = StartDaemons()
    daemons.start()
    return HttpResponse('ok')


def new_record(request):
    if "token" not in request.GET or "username" not in request.GET:
        return JsonResponse({"response": "field error"})
    try:
        the_user = Users.objects.get(username=request.GET['username'])
    except Users.DoesNotExist:
        return JsonResponse({'response': 'denied'})
    if request.GET['token'] != the_user.token:
        return JsonResponse({"response": "denied"})
    answer = {"response": "ok"}
    try:
        orders = Stack.objects.all().filter(status=0)
    except Stack.DoesNotExist:
        return JsonResponse({"response": "stack error"})
    records = []
    for order in orders:
        tmp_rec = {"email": order.email,
                   "country": order.country,
                   "description": order.description,
                   "method": order.method,
                   "by_virus": order.by_virus,
                   "by_fishing": order.by_fishing,
                   "date_add": order.date_add,
                   "date_hacked": order.date_hacked,
                   "comment": order.comment,
                   "status": order.status}
        records.append(tmp_rec)
    answer["orders"] = records
    logging('new_record', 'new record')
    return JsonResponse(answer)


def check_connect(request):
    return HttpResponse('ok')


def tester(request):
    test = Tester()
    test.start()
    return HttpResponse('ok')
