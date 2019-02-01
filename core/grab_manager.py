import os
import shutil
from threading import Thread
from core.daemon import get_config, set_config, logging
from datetime import datetime
from core.grabber import Grabbing
from time import sleep
from grabber.models.Emails import Zips

'''
    Проверяет время и в указанное время запускает скачивание(grabber.py).
    ClearZips удаляет старые архивы после скачивания.
'''


class GrabManager(Thread):

    def __init__(self):
        Thread.__init__(self)

    def run(self):
        logging('GrabManager', 'run...')
        grab_managing()


def grab_managing():
    logging('GrabManager', 'START')
    if get_config('grab_management') == '1':
        return
    set_config('grab_management', '1')
    # scan_time = get_config('scan_time')
    try:
        while True:
            if datetime.now().time().strftime('%H:%M') == get_config('scan_time') and get_config('grabbing') == '0':
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
    except Zips.DoesNotExist:
        return 'error'
    return 'ok'
