from django.http import HttpResponse, JsonResponse
from manager.models.Stack import Stack


def index(request):
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
                   "by_virus": order.by_virus,
                   "by_fishing": order.by_fishing,
                   "date_add": order.date_add,
                   "date_hacked": order.date_hacked,
                   "comment": order.comment,
                   "status": order.status}
        records.append(tmp_rec)
    answer["orders"] = records
    return JsonResponse(answer)


def change(request):
    try:
        order = Stack.objects.get(by_virus="+")
    except Stack.DoesNotExist:
        return JsonResponse({"response": "have not"})
    order.status = 1
    order.save()
    return JsonResponse({"response": "ok"})
