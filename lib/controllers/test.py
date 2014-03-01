from pox.core import core
from pox.lib.util import dpid_to_str
from pox.lib.util import str_to_bool

import pdb
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

        log.info(str(event))
        log.info('Packet type %s received on %d' % (type(packet), event.port))
        log.info('Packet Contents: \n\t %s' % packet.dump())

        msg = of.ofp_packet_out()
        msg.data = packet_in

        # pdb.set_trace()

        action = of.ofp_action_output(port = of.OFPP_ALL)
        msg.actions.append(action)
        event.connection.send(msg)

class Switch(object):

    @formedness_check
    def _handle_PacketIn(self, event):
        packet = event.parsed


def launch_on_event():
    log.info('launching.')

    def start_hub(event):
        log.info('starting hub.')
        event.connection.addListeners(Hub())

    core.openflow.addListenerByName('ConnectionUp', start_hub)

def launch_on_mod():
    log.info('launching and starting hub.')
    core.openflow.addListeners(Hub())

def launch():
    launch_on_event()
    
