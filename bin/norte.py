#!/usr/bin/env python

__author__ = 'cclamb'

from code import InteractiveConsole
from pox.boot import boot
from copy import deepcopy
from util.network import *

import thread as thread
import time
import sys

NAME = 'norte'
ADDITIONAL_ARGS = ['log.level', '--DEBUG', 'log', '--no-default', '--file=norte.log']
CONTROLLER_NAME = 'controllers.test'
BANNER = '''Welcome to %s.
For this session, we are using the controller %s.
To exit, use either ctrl-D or exit().''' % (NAME, CONTROLLER_NAME)

mutex = thread.allocate_lock()
notify_mutex = thread.allocate_lock()


sys.argv.extend(ADDITIONAL_ARGS)
sys.argv.append(CONTROLLER_NAME)


class InteractionManager(object):

    def __init__(self):
        self._listeners = []
        self._networks = {}

    def add_listener(self, listener):
        global notify_mutex
        notify_mutex.acquire()
        self._listeners.append(listener)
        notify_mutex.release()
    
    def _notify_listeners(self):
        global mutex, notify_mutex
        mutex.acquire()
        nets = deepcopy(self._networks)
        mutex.release()
        notify_mutex.acquire()
        for listener in self._listeners:
            listener(deepcopy(nets))
        notify_mutex.release()
    
    def set_networks(self, nets):
        global mutex, networks
        mutex.acquire()
        self._networks = deepcopy(nets)
        mutex.release()

    def get_networks(self):
        global mutex, networks
        nets = {}
        mutex.acquire()
        nets = deepcopy(self._networks)
        mutex.release()
        return nets


def pox_main():
    boot()
        

def run_main():
    global NAME
    thread.start_new_thread(pox_main, ())
    sys.ps1 = '(%s) >>> ' % NAME
    sys.ps2 = '(%s) ... ' % NAME
    console = InteractiveConsole(globals())
    console.interact(BANNER)
    return 0


return_value = 0
manager = InteractionManager()


if __name__ == '__main__':
    return_value = run_main()

exit(return_value)
