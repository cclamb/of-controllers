
import pdb

from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.util import dpid_to_str
from pox.lib.util import str_to_bool
import time


log = core.getLogger()

def formedness_check(f):
    def new_f(obj, event):
        log.info("checking packet formedness for: " + f.__name__)
        packet = event.parsed
        if not packet.parsed:
            log.warning('packet is improperly formed for: ' + f.__name__)
            return
        f(obj, event)
    return new_f

def locality_check(f):
    def new_f(obj, event):
        log.info('checking for local traffic we do not pass on')
        packet = event.parsed
        if packet.type == packet.LLDP_TYPE or packet.dst.isBridgeFiltered():
            return
        f(obj, event)
    return new_f

def looping_check(f):
    def new_f(obj, event):
        packet = event.parsed
        port = obj.mac_to_port.get(packet.dst)
        if port == event.port:
             log.warning('same port for packet from %s -> %s on %s.%s.'
                        % (packet.src, packet.dst, dpid_to_str(event.dpid), port))
             return
        f(obj, event)
    return new_f
