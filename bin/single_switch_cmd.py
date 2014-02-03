#!/usr/bin/env python

from time import sleep

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

    print "\tspawn two commands in the bg in h1..."
    h1.cmd('sleep 3 &')
    pid1 = int(h1.cmd('echo $!'))
    print "\tPID: %d" %  (pid1)
    h1.cmd('sleep 10 &')
    pid2 = int(h1.cmd('echo $!'))
    print "\tPID: %d" %  (pid2)
    # print "\t...and the process table?"
    # print "%s" % (h1.cmd('ps -f | grep sleep'))
    # print "\tCool, let's wait now..."
    # h1.cmd('wait', pid1, pid2)
    print "\tAdios processes..."
    h1.cmd('kill -9 ', pid1, pid2)

    # Wait to clear messages to console in shell; otherwise,
    # they'll be picked up in the below background commands
    # where we extract PIDs.
    sleep(1)

    # Looping and waiting for good tymez...
    print "\tLooping and waiting..."
    pids = []
    for i in range(10):
        h1.cmd('sleep %s &' % (i + 1))
        pids.append(int(h1.cmd('echo $!')))

    print "\tpids: %s" % (pids)

    # Wait for *all* the background processes to complete...
    h1.cmd('wait', *pids)

    print "Testing network connectivity..."
    net.pingAll()
    net.stop()

if __name__ == '__main__':
    setLogLevel('output')
    simpleTest()
    
