#!/usr/bin/env python

from time import sleep, time
from select import poll, POLLIN
from subprocess import Popen, PIPE
from signal import SIGINT

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.util import dumpNodeConnections, pmonitor
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

def testSimpleCmd(net):
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

def testLoopCmds(net):
    # Looping and waiting for good tymez...
    h1 = net.get('h1')
    print "\tLooping and waiting..."
    pids = []
    for i in range(10):
        h1.cmd('sleep %s &' % (i + 1))
        pids.append(int(h1.cmd('echo $!')))

    print "\tpids: %s" % (pids)

    # Wait for *all* the background processes to complete...
    h1.cmd('wait', *pids)

def testSendCmds(net):
    print "\tSending commands to the hosts..."
    for h in net.hosts:
        h.sendCmd('sleep 10; echo "Done on %s! Yay!"' % (h.name))

    print "\tWaiting for the output..."
    results = {}
    for h in net.hosts:
        results[h.name] = h.waitOutput()
    
    print "\tWhat do the host say?"
    print results

def monitorFiles(outfiles, seconds, timeoutms):
    """Monitor a set of files and return information from them."""
    devnull = open('/dev/null', 'w')
    tails, fdToFile, fdToHost = {}, {}, {}
    for h, outfile in outfiles.iteritems():
        tail = Popen(['tail', '-f', outfile], stdout = PIPE, stderr = devnull)
        fd = tail.stdout.fileno()
        tails[h] = tail
        fdToFile[fd] = tail.stdout
        fdToHost[fd] = h

    # Prepare to poll output files
    readable = poll()
    for t in tails.values():
        readable.register(t.stdout.fileno(), POLLIN)
        
    endTime = time() + seconds
    while time() < endTime:
        fdlist = readable.poll(timeoutms)
        if fdlist:
            for fd, _flags, in fdlist:
                f = fdToFile[fd]
                host = fdToHost[fd]
                line = f.readline().strip()
                yield host, line
        else:
            yield None, ''

    for t in tails.values():
        t.terminate()

    devnull.close()

def testMonitor(net, n = 3, seconds = 3):
    """This will fail with the terminating pingall, so comment out prior to running."""
    hosts = net.hosts
    server = hosts[0]
    outfiles, errfiles = {}, {}
    for h in hosts:
        outfiles[h] = '/tmp/%s.out' % (h.name)
        errfiles[h] = '/tmp/%s.err' % (h.name)
        h.cmd('echo > ', outfiles[h])
        h.cmd('echo > ', errfiles[h])

        # Start pinging.
        h.cmdPrint('ping', server.IP(),
                   '>', outfiles[h],
                   '2>', errfiles[h],
                   '&')

    print 'Monitoring output for', seconds, 'seconds'
    for h, line in monitorFiles(outfiles, seconds, timeoutms = 500):
        if h:
            print '%s, %s' % (h.name, line)

    for h in hosts:
        h.cmd('kill %ping')

    net.stop()

def testMonitorSimple(net, n = 3, seconds = 10):
    hosts = net.hosts
    server = hosts[0]
    popens = {}
    for h in hosts:
        popens[h] = h.popen('ping', server.IP())

    print 'Monitoring output for', seconds, 'seconds'
    endTime = time() + seconds
    for h, line in pmonitor(popens, timeoutms = 500):
        if h:
            print '%s: %s' % (h.name, line)
        if time() >= endTime:
            for proc in popens.values():
                proc.send_signal(SIGINT)
    net.stop()

def simpleTest():
    """Create and test a simple network"""
    topo = SingleSwitchTopo(n = 5)
    net = Mininet(topo)
    net.start()
    print "Dumping host connections..."
    dumpNodeConnections(net.hosts)

    testMonitorSimple(net)

    #print "Testing network connectivity..."
    #net.pingAll()
    #net.stop()

if __name__ == '__main__':
    setLogLevel('output')
    simpleTest()
    
