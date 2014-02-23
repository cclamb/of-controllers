
import pdb

from pox.core import core
from pox.lib.util import dpid_to_str
from pox.lib.util import str_to_bool

import time
import pox.openflow.libopenflow_01 as of

from l2_learning_switch_trait import L2LearningSwitchTrait
from decorators import formedness_check


log = core.getLogger()


class Hub(object):
    
    @formedness_check
    def handle_packet(self, ctx, event):
       packet = event.parsed
       packet_in = event.ofp

       msg = of.ofp_packet_out()
       msg.data = packet_in

       action = of.ofp_action_output(port = of.OFPP_ALL)
       msg.actions.append(action)

       connection= ctx['connection']
       connection.send(msg)

    def _handle_PacketIn(self, event):
        self.handle_packet({'connection': event.connection}, event)


def launch():
    log.info('launching.')

    def start_hub(event):
        log.info('starting hub.')
        event.connection.addListeners(Hub())

    core.openflow.addListenerByName('ConnectionUp', start_hub)
    
