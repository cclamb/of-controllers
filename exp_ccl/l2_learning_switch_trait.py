
import pdb

from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.util import dpid_to_str
from pox.lib.util import str_to_bool
import time

from hub_trait import HubTrait
from decorators import formedness_check, locality_check, looping_check


log = core.getLogger()


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
            super(L2LearningSwitchTrait, self).handle_packet({'connection': ctx['connection']}, event)
            return

        port = self.mac_to_port.get(packet.dst, None)
        
        if port == None:
            log.info('we do not have the port; revert to hub')
            super(L2LearningSwitchTrait, self).handle_packet({'connection': ctx['connection']}, event)
            return

        log.info('installing flow for %s.%i -> %s.%i'
                 % (str(packet.src), event.port, str(packet.dst), port))
        msg = of.ofp_flow_mod()
        msg.match = of.ofp_match.from_packet(packet, event.port)
        msg.idle_timeout = 10
        msg.hard_timeout = 30
        msg.actions.append(of.ofp_action_output(port = port))
        msg.data = event.ofp
        ctx['connection'].send(msg)
