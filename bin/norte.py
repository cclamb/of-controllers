#!/usr/bin/env python

__author__ = 'cclamb'

from code import InteractiveConsole
from pox.boot import boot
from util.network import *
from controllers.interaction_manager import InteractionManager, get_manager

import thread as thread
import time
import sys


NAME = 'norte'
ADDITIONAL_ARGS = ['log.level', '--DEBUG', 'log', '--no-default', '--file=norte.log']
CONTROLLER_NAME = 'controllers.test'
BANNER = '''Welcome to %s.
For this session, we are using the controller %s.
To exit, use either ctrl-D or exit().''' % (NAME, CONTROLLER_NAME)


sys.argv.extend(ADDITIONAL_ARGS)
sys.argv.append(CONTROLLER_NAME)


manager = get_manager()


def pox_main():
    boot()


def test_main():
    global manager
    def listener(nets):
        print(nets)
    manager.add_listener(listener)
    while True:
        time.sleep(1)
         

def run_main():
    global manager
    thread.start_new_thread(pox_main, ())
    thread.start_new_thread(test_main, ())
    sys.ps1 = '(%s) >>> ' % NAME
    sys.ps2 = '(%s) ... ' % NAME
    console = InteractiveConsole(globals())
    console.interact(BANNER)
    return 0


return_value = 0


if __name__ == '__main__':
    return_value = run_main()

exit(return_value)
