#!/usr/bin/env python

import sys
from mininet.node import Host
from mininet.util import ensureRoot

ensureRoot()

print 'creating nodes...'
h1, root = Host('h1'), Host('root', inNamespace = False)

print 'creating links...'
h1.linkTo(root)

print 'configuring...'
h1.setIP('10.0.0.7', 8)
root.setIP('10.0.0.9', 8)

print 'creating SSH banner...'

f = open('/tmp/%s.banner' % h1.name, 'w')
f.write('Dude! Thanks for dropping into %s at %s, yo!\n' % (h1.name, h1.IP()))
f.close()

print 'running sshd...'
cmd = '/usr/bin/sshd -o UseDNS=no, -u0, -o "Banner /tmp/%s.banner"' % h1.name
h1.cmd(cmd)

print 'ssh into ', h1.name, 'at', h1.IP()
