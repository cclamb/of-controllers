#!/usr/bin/env python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Host
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.link import Link
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel

linkopts = {'bw': 10, 'delay': '5ms', 'loss': 10, 'max_queue_size': 1000, 'use_htb': True}


class SingleSwitchTopo(Topo):

    """A single switch linked to N nosts"""
    def __init__(self, n = 2, **opts):
        Topo.__init__(self, **opts)
        switch = self.addSwitch('s1')
        for h in range(n):
            # Each host get .5/n of system CPU
            host = self.addHost('h%s' % (h + 1), cpu = .5 / n)
            #host = self.addHost('h%s' % (h + 1))
            # 10 Mbps with 5 ms delay, 10% packet loss, 1000 packet queue
            self.addLink(host, switch, **linkopts)
            #self.addLink(host, switch)
            

def perfTest():
    """Create network and run simple perforance tests"""
    topo = SingleSwitchTopo(n = 5)
    net = Mininet(topo = topo, host = CPULimitedHost, link = TCLink)
    net.start()
    print "dumping host connections..."
    # dumpNodeConnections(net.hosts)
    net.pingAll()
    # h1, h4 = net.get('h1', 'h4')
    # net.iperf((h1, h4))
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    perfTest()
            
