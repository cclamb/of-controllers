
import pdb

from pox.core import core
import pox.openflow.libopenflow_01 as of


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


class HubTrait:

    @formedness_check
    def handle_packet(self,ctx, event):
        packet = event.parsed
        packet_in = event.ofp

        msg = of.ofp_packet_out()
        msg.data = packet_in

        action = of.ofp_action_output(port = of.OFPP_ALL)
        msg.actions.append(action)

        connection = ctx['connection']
        connection.send(msg)
        log.info('processing event')
        

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
        DynamicEvaluator(event.connection, HubTrait())
    core.openflow.addListenerByName('ConnectionUp', start_hub)
      
