from django.http import HttpResponse, JsonResponse


def index(request):
    if "token" not in request.GET:
        return JsonResponse({"response": "token error"})
    if request.GET["token"] == "111":
        answer = "1"
    else:
        answer = "2"
    return HttpResponse(answer)
