
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

    def _is_local_traffic(self, packet):
        return packet.type == packet.LLDP_TYPE or packet.dst.isBridgeFiltered()

    @formedness_check
    def handle_packet(self, ctx, event):
        #pdb.set_trace()
        msg = of.ofp_packet_out()
        
        packet = event.parsed

        self.mac_to_port[packet.src] = event.port

        # This could also be done in a decorator
        if self._is_local_traffic(packet):
            # this is much more complex in example.
            return

        if packet.dst.is_multicast:
            HubTrait.handle_packet({'connection': ctx['connection']}, event)
            return

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
      
