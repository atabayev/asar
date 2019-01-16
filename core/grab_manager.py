import shutil, os
from threading import Thread
from core.daemon import get_config, set_config
from datetime import datetime
from core.grabber import Grabbing
from time import sleep
from grabber.models.Emails import Zips


class GrabManager(Thread):

    def __init__(self):
        Thread.__init__(self)

    def run(self):
        grab_managing()


def grab_managing():
    if get_config('grab_management') == '1':
        return
    set_config('grab_management', '1')
    scan_time = get_config('scan_time')
    try:
        while True:
            if datetime.now().time().strftime('%H:%M') == scan_time and get_config('grabbing') == '0':
                grabber = Grabbing()
                grabber.start()
            sleep(58)
    finally:
        set_config('grab_management', '0')


class ClearZips(Thread):

    def __init__(self):
        Thread.__init__(self)

    def run(self):
        clear_zips()


def clear_zips():
    dirs = os.listdir('emails')
    for the_dir in dirs:
        shutil.rmtree(os.path.join('emails', the_dir), ignore_errors=True)
    try:
        Zips.objects.all().delete()
    except:
        return 'error'
    return 'ok'
