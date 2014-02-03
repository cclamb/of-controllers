#!/usr/bin/env python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel


class SingleSwitchTopo(Topo):
    
    """Single switch connected to n hosts"""
    def __init__(self, n = 2, **opts):
        # Initialize the topology.
        Topo.__init__(self, **opts)
        switch = self.addSwitch('s1')
        
        # Generate hosts from 0..(n-1)
        for h in range(n):
            host = self.addHost('h%s' % (h+1))
            self.addLink(host, switch)

def simpleTest():
    """Create and test a simple network"""
    topo = SingleSwitchTopo(n = 5)
    net = Mininet(topo)
    net.start()
    print "Dumping host connections..."
    dumpNodeConnections(net.hosts)

    print "Testing some commands..."
    h1 = net.get('h1')

    print "\tspawn a command in the bg in h1..."
    h1.cmd('sleep 10 &')
    pid = int(h1.cmd('echo $!'))

    print "\tgrab the pid and kill"
    h1.cmd('kill %while')
    print "\tPID: %d\n" % (pid)

    print "Testing network connectivity..."
    net.pingAll()
    net.stop()

if __name__ == '__main__':
    setLogLevel('output')
    simpleTest()
    
