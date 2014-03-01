#!/usr/bin/env python

__author__ = 'cclamb'

from code import InteractiveConsole

import thread as thread
import time
import sys

NAME = 'norte'
BANNER = 'Welcome to %s.\nTo exit, use either ctrl-D or exit().' % NAME

count = 0
mutex = thread.allocate_lock()


def get_count():
    global count, mutex
    mutex.acquire()
    cnt_buffer = count
    mutex.release()
    return cnt_buffer


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
    sys.ps1 = '(%s) >>> ' % NAME
    sys.ps2 = '(%s) ... ' % NAME
    console = InteractiveConsole(globals())
    console.interact(BANNER)
    return 0


return_value = 0

if __name__ == '__main__':
    return_value = run_main()

exit(return_value)