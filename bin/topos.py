#!/usr/bin/env python

from mininet.log import setLogLevel
from mininet.net import Mininet
from mininet.topo import Topo
from mininet.util import dumpNodeConnections
from mininet.cli import CLI
from mininet.node import RemoteController


class S1HNLinearTopo(Topo):

    def __init__(self, n=2, **opts):
        Topo.__init__(self, **opts)
        switch = self.addSwitch('s1')
        for h in range(n):
            host = self.addHost('h%d' % (h + 1))
            self.addLink(host, switch)

class S2HNTreeTopo(Topo):

    def __init__(self, m=2, n=2, **opts):
        Topo.__init__(self, **opts)
        s_idx, h_idx = 1, 1
        root_switch = self.addSwitch('s%d' % (s_idx))
        s_idx += 1
        for s in range(m):
            switch = self.addSwitch('s%d' % (s_idx))
            s_idx += 1
            self.addLink(switch, root_switch)
            for h in range(n):
                host = self.addHost('h%d' % (h_idx))
                h_idx += 1
                self.addLink(host, switch)
            

def run():
    setLogLevel('info')
    #topo = S1HNLinearTopo(n=4)
    topo = S2HNTreeTopo(n = 4)
    net = Mininet(topo=topo,
                  autoSetMacs=True,
                  controller = lambda name: RemoteController(name, ip='127.0.0.1'))
    dumpNodeConnections(net.hosts)
    net.start()
    CLI(net)
    net.stop()


if __name__ == '__main__':
    run()
    
    
