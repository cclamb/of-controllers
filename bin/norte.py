#!/usr/bin/env python

__author__ = 'cclamb'

from code import InteractiveConsole
from pox.boot import boot

import thread as thread
import time
import sys

NAME = 'norte'
ADDITIONAL_ARGS = ['log.level', '--DEBUG', 'log', '--no-default', '--file=norte.log']
CONTROLLER_NAME = 'controllers.test'
BANNER = '''Welcome to %s.
For this session, we are using the controller %s.
To exit, use either ctrl-D or exit().''' % (NAME, CONTROLLER_NAME)

count = 0
mutex = thread.allocate_lock()


sys.argv.extend(ADDITIONAL_ARGS)
sys.argv.append(CONTROLLER_NAME)


class Network(object):

    def __init__(self):
        self.hosts = []

    def add_host(self, host):
        self.hosts.append(host)

    def add_hosts(self, hosts):
        self.hosts.extend(hosts)


class NetworkManager(object):

    def __init__(self, networks):
        self.networks = []
        self.networks.extend(networks)
        return

    def match(self, host1, host2):
        for network in self.networks:
            cnt1 = network.count(host1)
            cnt2 = network.count(host2)
            if cnt1 > 0 and cnt2 > 0:
                return True
        return False


def get_count():
    global count, mutex
    mutex.acquire()
    cnt_buffer = count
    mutex.release()
    return cnt_buffer


def pox_main():
    boot()


def thread_main():
    global count, mutex
    while True:
        time.sleep(1)
        mutex.acquire()
        count += 1
        mutex.release()
        

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
