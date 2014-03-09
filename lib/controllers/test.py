__author__ = 'cclamb'

from pox.core import core
from pox.lib.util import dpid_to_str
from pox.lib.util import str_to_bool
from util.network import NetworkManager
from controllers.interaction_manager import get_manager

import pdb
import time
import pox.openflow.libopenflow_01 as of
import pox.lib.packet as pkt
import thread as thread

from util.event.decorators import formedness_check


log = core.getLogger()


manager = get_manager()


class MyNetworkManager(NetworkManager):

    def __init__(self, nets = {}):
        super(MyNetworkManager, self).__init__()
        self._mutex = thread.allocate_lock()

    def data_listener(self, nets):
        log.info('setting new network: %s' % nets)
        self._mutex.acquire()
        self._networks = nets
        self._mutex.release()


local_manager = MyNetworkManager()
        

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


class Inspector(object):

    def _handle_PacketIn(self, event):
        packet = event.parsed
        log.info('inspecting packet %s received on %d' % (type(packet), event.port))
        if packet.type == pkt.ethernet.ARP_TYPE:
            if packet.payload.opcode == pkt.arp.REQUEST:
                log.info('arp request: \n\t %s' % str(packet))
                log.info('\t%s' % packet.dump())
            if packet.payload.opcode == pkt.arp.REPLY:
                log.info ('arp reply: \n\t %s' % str(packet))
                log.info('\t%s' % packet.dump())
        else:
            log.info('other packet: \n\t %s' % str(packet))
            log.info('\t%s' % packet.dump())


class Hub(object):        

    @formedness_check
    def _handle_PacketIn(self, event):
        pdb.set_trace()
        packet = event.parsed
        packet_in = event.ofp
        msg = of.ofp_packet_out()
        msg.data = packet_in
        action = of.ofp_action_output(port = of.OFPP_ALL)
        msg.actions.append(action)
        event.connection.send(msg)

class RestrictingHub(Hub):

    def __init(self, manager):
        self._manager = manager

    @formedness_check
    def _handle_PacketIn(self, event):
        if self._manager.match(src_ip, dest_ip):
            super(ResetrictingHub, self)._handle_PacketIn(self, event)

class Switch(object):

    @formedness_check
    def _handle_PacketIn(self, event):
        packet = event.parsed


def launch_on_event():
    log.info('launching.')

    def start_hub(event):
        global manager
        log.info('configuring manager with listeners.')
        manager.add_listener(local_manager.data_listener)
        log.info('starting hub.')
        event.connection.addListeners(Hub())
        event.connection.addListeners(Inspector())

    core.openflow.addListenerByName('ConnectionUp', start_hub)

def launch_on_mod():
    log.info('launching and starting hub.')
    core.openflow.addListeners(Hub())

def launch():
    launch_on_event()
    
