__author__ = 'cclamb'

import thread as thread
from copy import deepcopy


notify_mutex = thread.allocate_lock()


class InteractionManager(object):

    def __init__(self):
        self._listeners = []
        self._networks = {}

    @property
    def count(self):
        global notify_mutex
        notify_mutex.acquire()
        count = len(self._listeners)
        notify_mutex.release()
        return count

    def add_listener(self, listener):
        global notify_mutex
        notify_mutex.acquire()
        self._listeners.append(listener)
        notify_mutex.release()
    
    def _notify_listeners(self):
        global notify_mutex
        nets = deepcopy(self._networks)
        notify_mutex.acquire()
        for listener in self._listeners:
            listener(deepcopy(nets))
        notify_mutex.release()
    
    def set_networks(self, nets):
        global networks
        self._networks = deepcopy(nets)
        self._notify_listeners()

    def get_networks(self):
        global networks
        nets = {}
        nets = deepcopy(self._networks)
        return nets


_manager = InteractionManager()

def get_manager():
    return _manager
