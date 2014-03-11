__author__ = 'cclamb'

import json

def create_network_file(file_name):
    fh, nets = open(file_name), None
    try:
        nets = json.load(fh)
    finally:
        fh.close()
    return nets


def create_network_json(json):
    return json.loads(json)


class NetworkManager(object):

    def __init__(self, networks = {}):
        self._networks = networks
        return

    def set_networks(self,nets):
        self._networks = nets

    def add_network(self, network):
        self._networks.update(network)

    def match(self, host1, host2):
        for network in self._networks:
            cnt1 = network.count(host1)
            cnt2 = network.count(host2)
            if cnt1 > 0 and cnt2 > 0:
                return True
        return False

