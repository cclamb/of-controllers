
import pdb

from pox.core import core


log = core.getLogger()


def formedness_check(f):
    def new_f(obj, event):
        log.info("entering: " + f.__name__)
        f(obj, event)
        log.info("exited: " + f.__name__)
    return new_f


class HubTrait:

    @formedness_check
    def handle_packet(self, event):
        log.info('processing event')
        

class DynamicHub:

    def __init__(self, connection, trait):
        self.connection = connection
        self.trait = trait
        connection.addListeners(self)

    def _handle_PacketIn (self, event):
        log.info('handling packet in event: ' + str(event))
        self.trait.handle_packet(event)

    def _handle_PacketOut(self, event):
        log.info('handling packet out event: ' + str(event))


def launch():
    log.info('launching.')
    def start_hub(event):
        log.info('starting hub.')
        DynamicHub(event.connection, HubTrait())
    core.openflow.addListenerByName('ConnectionUp', start_hub)
      
