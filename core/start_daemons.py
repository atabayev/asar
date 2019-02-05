from time import sleep
from threading import Thread
from core.daemon import get_config
from core.vpn_manager import VpnManager
from core.grab_manager import GrabManager
from core.checker import CheckFtp
from core.attack import Attacking


class StartDaemons(Thread):

    def __init__(self):
        Thread.__init__(self)

    def run(self):
        if get_config('vpn_manager') == '0':
            vpn = VpnManager()
            vpn.start()
            sleep(10)
        if get_config('grab_management') == '0':
            grab_manager = GrabManager()
            grab_manager.start()
            sleep(5)
        if get_config('attacking') == '0':
            atk = Attacking()
            atk.start()
            sleep(5)
        if get_config('checking_ftp') == '0':
            check = CheckFtp()
            check.start()
