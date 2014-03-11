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
        # log.info('inspecting packet %s received on %d' % (type(packet), event.port))
        if packet.type == pkt.ethernet.ARP_TYPE:
            if packet.payload.opcode == pkt.arp.REQUEST:
                log.info('arp request: %s' % str(packet))
                # log.info('\t%s' % packet.dump())
            if packet.payload.opcode == pkt.arp.REPLY:
                log.info ('arp reply: %s' % str(packet))
                # log.info('\t%s' % packet.dump())
        elif packet.type == pkt.ethernet.IP_TYPE:
            log.info('ip packet [%s -> %s]: %s' % \
                         (packet.next.srcip, packet.next.dstip, str(packet)))
        else:
            log.info('other packet: %s' % str(packet))
            # log.info('\t%s' % packet.dump())


class Hub(object):        

    @formedness_check
    def _handle_PacketIn(self, event):
        packet = event.parsed
        packet_in = event.ofp
        msg = of.ofp_packet_out()
        # pdb.set_trace()
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

    def __init__(self):
        self._port_map = {}
        
    @formedness_check
    def _handle_PacketIn(self, event):
        global local_manager
        packet = event.parsed

        if packet.type == pkt.ethernet.IPV6_TYPE:
            return

        self._map_address(event.port, packet.src)

        if packet.dst.is_multicast:
            log.info('Broadcasting multicast: %s' % packet)
            self._broadcast(event)
            return

        packet_in = event.ofp
        msg = of.ofp_packet_out()

        port = self._get_port_from_mac(packet.dst)

        if port == None:
            log.error('No mapping for mac address: %s', packet.dst)
            return

        if not local_manager.match(packet.src, packet.dst):
            log.info('%s and %s not in same network.' % (packet.src, packet.dst))
            return

        log.info('Sending to %s on %s' % (packet.dst, port))
        msg.data = packet_in
        action = of.ofp_action_output(port = port)
        msg.actions.append(action)
        event.connection.send(msg)

    def _broadcast(self, event):
        msg = of.ofp_packet_out()
        msg.data = event.ofp
        action = of.ofp_action_output(port = of.OFPP_ALL)
        msg.actions.append(action)
        event.connection.send(msg)

    def _map_address(self, port, src):
        if self._port_map.get(src) == None:
            self._port_map[src] = port

    def _get_port_from_mac(self, mac):
        return self._port_map.get(mac)


def launch_on_event():
    log.info('launching.')

    def start_hub(event):
        global manager
        log.info('configuring manager with listeners.')
        manager.add_listener(local_manager.data_listener)
        log.info('starting switch.')
        event.connection.addListeners(Switch())
        # event.connection.addListeners(Inspector())

    core.openflow.addListenerByName('ConnectionUp', start_hub)

def launch_on_mod():
    log.info('launching and starting hub.')
    core.openflow.addListeners(Hub())

def launch():
    launch_on_event()
    
