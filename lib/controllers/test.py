
import pdb

from pox.core import core
from pox.lib.util import dpid_to_str
from pox.lib.util import str_to_bool

import time
import pox.openflow.libopenflow_01 as of

from l2_learning_switch_trait import L2LearningSwitchTrait
from util.event.decorators import formedness_check


log = core.getLogger()


class EventSink(object):

    def _handle_PacketIn(self, event):
        log.info('==> PacketIn from %s' % str(self.__class__))

    def _handle_ErrorIn(self, event):
        log.info('==> ErrorIn from %s' % str(self.__class__))

    def _handle_ConnectionDown(self, event):
        log.info('==> ConnectionDown from %s' % str(self.__class__))

    def _handle_PortStatus(self, event):
        log.info('==> PortStatus from %s' % str(self.__class__))

    def _handle_FlowRemoved(self, event):
        log.info('==> FlowRemoved from %s' % str(self.__class__))

    def _handle_BarrierIn(self, event):
        log.info('==> BarrierIn from %s' % str(self.__class__))

    def _handle_RawStatsReply(self, event):
        log.info('==> RawStats from %s' % str(self.__class__))

    def _handle_statsReply(self, event):
        log.info('==> Stats from %s' % str(self.__class__))

class Hub(object):

    @formedness_check
    def _handle_PacketIn(self, event):
        packet = event.parsed
        packet_in = event.ofp

        msg = of.ofp_packet_out()
        msg.data = packet_in

        action = of.ofp_action_output(port = of.OFPP_ALL)
        msg.actions.append(action)
        event.connection.send(msg)


def launch():
    log.info('launching.')

    def start_hub(event):
        log.info('starting hub.')
        event.connection.addListeners(Hub())

    core.openflow.addListeners(EventSink())
    core.openflow.addListenerByName('ConnectionUp', start_hub)
    
