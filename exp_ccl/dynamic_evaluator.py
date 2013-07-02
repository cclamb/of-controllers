
import pdb

from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.util import dpid_to_str
from pox.lib.util import str_to_bool
import time


log = core.getLogger()


def formedness_check(f):
    def new_f(obj, ctx, event):
        log.info("checking packet formedness for: " + f.__name__)
        packet = event.parsed
        if not packet.parsed:
            log.warning('packet is improperly formed for: ' + f.__name__)
            return
        f(obj, ctx, event)
    return new_f

def locality_check(f):
    def new_f(obj, ctx, event):
        log.info('checking for local traffic we do not pass on')
        packet = event.parsed
        if packet.type == packet.LLDP_TYPE or packet.dst.isBridgeFiltered():
            return
        f(obj, ctx, event)
    return new_f

def looping_check(f):
    def new_f(obj, ctx, event):
        packet = event.parsed
        port = obj.mac_to_port.get(packet.dst)
        if port == event.port:
             log.warning('same port for packet from %s -> %s on %s.%s.'
                        % (packet.src, packet.dst, dpid_to_str(event.dpid), port))
             return
        f(obj, ctx, event)
    return new_f


class HubTrait(object):

    @formedness_check
    def handle_packet(self, ctx, event):
        packet = event.parsed
        packet_in = event.ofp

        msg = of.ofp_packet_out()
        msg.data = packet_in

        action = of.ofp_action_output(port = of.OFPP_ALL)
        msg.actions.append(action)

        connection = ctx['connection']
        connection.send(msg)
        log.info('processing event')


class L2LearningSwitchTrait(HubTrait):

    def __init__(self):
        self.mac_to_port = {}
        super(L2LearningSwitchTrait, self).__init__()

    @formedness_check
    @locality_check
    @looping_check
    def handle_packet(self, ctx, event):
        #pdb.set_trace()
        msg = of.ofp_packet_out()
        
        packet = event.parsed

        self.mac_to_port[packet.src] = event.port

        if packet.dst.is_multicast:
            HubTrait().handle_packet({'connection': ctx['connection']}, event)
            return

        port = self.mac_to_port[packet.dst]
        #if port == event.port:
        #    log.warning('same port for packet from %s -> %s on %s.%s.'
        #                % (packet.src, packet.dst, dpid_to_str(event.dpid), port))
        #    return

        log.info('installing flow for %s.%i -> %s.%i'
                 % (str(packet.src), event.port, str(packet.dst), port))
        msg = of.ofp_flow_mod()
        msg.match = of.ofp_match.from_packet(packet, event.port)
        msg.idle_timeout = 10
        msg.hard_timeout = 30
        msg.actions.append(of.ofp_action_output(port = port))
        msg.data = event.ofp
        ctx['connection'].send(msg)
        return
        

class DynamicEvaluator:

    def __init__(self, connection, trait):
        self.connection = connection
        self.trait = trait
        connection.addListeners(self)

    def _handle_PacketIn (self, event):
        log.info('handling packet in event: ' + str(event))
        self.trait.handle_packet({'connection': self.connection}, event)

    def _handle_PacketOut(self, event):
        log.info('handling packet out event: ' + str(event))


def launch():
    log.info('launching.')
    def start_hub(event):
        log.info('starting hub.')
        DynamicEvaluator(event.connection, L2LearningSwitchTrait())
    core.openflow.addListenerByName('ConnectionUp', start_hub)
      
