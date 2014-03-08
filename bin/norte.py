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
networks = {}

sys.argv.extend(ADDITIONAL_ARGS)
sys.argv.append(CONTROLLER_NAME)


def set_networks(nets):
    global mutex, networks
    mutex.acquire()
    networks = deepcopy(nets)
    mutex.release()

def get_networks():
    global mutex, networks
    nets = {}
    mutex.acquire()
    nets = deepcopy(networks)
    mutex.release()
    return nets


def pox_main():
    boot()


def thread_main():
    global count, mutex
    while True:
        time.sleep(1)
        # This thread will execute the controller
        #mutex.acquire()
        #count += 1
        #mutex.release()
        

def run_main():
    global NAME
    thread.start_new_thread(thread_main, ())
    thread.start_new_thread(pox_main, ())
    sys.ps1 = '(%s) >>> ' % NAME
    sys.ps2 = '(%s) ... ' % NAME
    console = InteractiveConsole(globals())
    console.interact(BANNER)
    return 0


return_value = 0

if __name__ == '__main__':
    return_value = run_main()

exit(return_value)
