from django.http import JsonResponse
from manager.models.Stack import Stack
from core.daemon import get_config
from core.grab_manager import GrabManager
from core.attack import Attacking
from core.checker import CheckFtp


def all_records(request):
    if "token" not in request.GET:
        return JsonResponse({"response": "token error"})
    if request.GET["token"] != "111":
        return JsonResponse({"response": "access denied"})
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
    if get_config('grab_management') == '0':
        grab_manager = GrabManager()
        grab_manager.start()
    if get_config('attacking') == '0':
        atk = Attacking()
        atk.start()
    if get_config('checking_ftp') == '0':
        check = CheckFtp()
        check.start()
    return JsonResponse(answer)


def new_record(request):
    if "token" not in request.GET:
        return JsonResponse({"response": "token error"})
    if request.GET["token"] != "111":
        return JsonResponse({"response": "access denied"})
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
    if get_config('grab_management') == '0':
        grab_manager = GrabManager()
        grab_manager.start()
    if get_config('attacking') == '0':
        atk = Attacking()
        atk.start()
    if get_config('checking_ftp') == '0':
        check = CheckFtp()
        check.start()
    return JsonResponse(answer)

