
import pdb

from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.util import dpid_to_str
from pox.lib.util import str_to_bool
import time

from l2_learning_switch_trait import L2LearningSwitchTrait


log = core.getLogger()
        

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
        log.info('starting L2 learning switch.')
        DynamicEvaluator(event.connection, L2LearningSwitchTrait())
    core.openflow.addListenerByName('ConnectionUp', start_hub)
      
