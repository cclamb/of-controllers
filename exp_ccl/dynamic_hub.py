
import pdb

from pox.core import core


log = core.getLogger()


class DynamicHub:

    def __init__(self, connection):
        self.connection = connection
        connection.addListeners(self)

    def _handle_PacketIn (self, event):
        log.info('handling packet in event: ' + str(event))

    def _handle_PacketOut(self, event):
        log.info('handling packet out event: ' + str(event))


def launch():
    log.info('launching.')
    def start_hub(event):
        log.info('starting hub.')
        DynamicHub(event.connection)
    core.openflow.addListenerByName('ConnectionUp', start_hub)
      
