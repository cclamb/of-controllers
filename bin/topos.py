#!/usr/bin/env python

from mininet.log import SetLogLevel
from mininet.net import Controller
from mininet.topolog import LinearTopo
from mininet.cli import CLI


class LinearTopology:

    def __init__(self, k=2, n=1, **opts):
        self.topology =  LinearTopo(k, n, **opts)

    def configure_mininet(self):
        self.net = Mininet(self.topo)

    def start(self):
        self.net.start()

    def test(self):
        self.net.pingAll()
        
    def stop(self):
        self.net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    
    
