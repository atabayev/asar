import os
import mimetypes
import datetime
from wsgiref.util import FileWrapper
from django.http import HttpResponse, JsonResponse, StreamingHttpResponse
from core.grabber import Grabbing
from core.daemon import crypt, get_config, set_config
from core.grab_manager import GrabManager, ClearZips
from grabber.models.Emails import Emails, Zips

"""
    grabber   
"""


def get_emails(request):
    if "token" not in request.GET:
        return JsonResponse({"response": "token error"})
    if request.GET["token"] != "111":
        return JsonResponse({"response": "access denied"})
    answer = {"response": "ok"}
    try:
        emails = Emails.objects.all().filter(status=1)
    except Emails.DoesNotExist:
        return JsonResponse({"response": "no emails"})
    records = []
    for email in emails:
        tmp_rec = {"email": email.email,
                   "description": email.description,
                   "lsdt": email.last_scan_datetime,
                   "comment": email.comment}
        records.append(tmp_rec)
    answer["emails"] = records
    if get_config('grab_management') == '0':
        grab_manager = GrabManager()
        grab_manager.start()
    return JsonResponse(answer)


def add_email(request):
    if "token" not in request.POST or "email" not in request.POST or "password" not in request.POST or \
            "description" not in request.POST or "comment" not in request.POST:
        return JsonResponse({"response": "token error"})
    if request.POST["token"] != "111":
        return JsonResponse({"response": "access denied"})
    if Emails.objects.filter(email=request.POST['email']).exists():
        if Emails.objects.get(email=request.POST['email']).status == '0':
            eml = Emails.objects.get(email=request.POST['email'])
            eml.status = '1'
            eml.save()
            return JsonResponse({"response": 'ok'})
        else:
            return JsonResponse({"response": 'exists'})
    eml = Emails()
    eml.email = request.POST['email']
    eml.password = crypt(request.POST['password'])
    eml.description = request.POST['description']
    eml.last_scan_datetime = (datetime.datetime.now() - datetime.timedelta(days=30)).strftime('%d.%m.%Y %H:%M')
    eml.last_messages_datetime = eml.last_scan_datetime
    eml.comment = request.POST['comment']
    eml.status = '1'
    eml.save()
    return JsonResponse({"response": "ok"})


def delete_email(request):
    if "token" not in request.POST or "email" not in request.POST:
        return JsonResponse({"response": "token error"})
    if request.POST["token"] != "111":
        return JsonResponse({"response": "access denied"})
    try:
        eml = Emails.objects.get(email=request.POST['email'])
    except Emails.DoesNotExist:
        return JsonResponse({"response": "not exists"})
    eml.status = "0"
    eml.save()
    return JsonResponse({"response": "ok"})


def get_arch_info(request):
    if "token" not in request.GET:
        return JsonResponse({"response": "token error"})
    if request.GET["token"] != "111":
        return JsonResponse({"response": "access denied"})
    if get_config('grabbing') == '1':
        return JsonResponse({"response": "denied"})
    all_zips = Zips.objects.all()
    zips_dict = {}
    zips_record = []
    zips_dict['response'] = 'ok'
    zips_dict['count'] = Zips.objects.count()
    for a_zip in all_zips:
        zips_record.append(a_zip.name)
    zips_dict['zips'] = zips_record
    return JsonResponse(zips_dict)


def get_zips(request):
    if "token" not in request.GET and "zip_name" not in request.GET:
        return JsonResponse({"response": "filed_error"})
    if request.GET["token"] != "111":
        return JsonResponse({"response": "denied"})
    try:
        a_zip = Zips.objects.get(name=request.GET['zip_name'])
    except Zips.DoesNotExist:
        return JsonResponse({"response": "no_record"})
    the_file = a_zip.path
    file_name = os.path.basename(the_file)
    chunk_size = 8192
    response = StreamingHttpResponse(FileWrapper(open(the_file, 'rb'), chunk_size),
                                     content_type=mimetypes.guess_type(the_file)[0])
    response['Content-Length'] = os.path.getsize(the_file)
    response['Content-Disposition'] = "attachment; filename=%s" % file_name
    return response


def set_scan_time(request):
    if "token" not in request.POST and "time" not in request.POST:
        return JsonResponse({"response": "filed_error"})
    if request.POST["token"] != "111":
        return JsonResponse({"response": "denied"})
    set_config('scan_time', request.POST['time'])
    return JsonResponse({"response": "ok"})


def get_dirs(request):
    if "token" not in request.GET:
        return JsonResponse({"response": "filed_error"})
    if request.GET["token"] != "111":
        return JsonResponse({"response": "denied"})
    dirs = os.listdir('emails')
    response_dict = {}
    response_dict['response'] = 'ok'
    response_dict['count'] = len(dirs)
    response_dict['directories'] = dirs
    return JsonResponse(response_dict)


def clear_zips_table(request):
    if "token" not in request.POST:
        return JsonResponse({"response": "filed_error"})
    if request.POST["token"] != "111":
        return JsonResponse({"response": "denied"})
    clear_zips = ClearZips()
    clear_zips.start()
    return JsonResponse({"response": "ok"})
