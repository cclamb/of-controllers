
import pdb

from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.util import dpid_to_str
from pox.lib.util import str_to_bool
import time

from decorators import formedness_check

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
