from autologging import logged, traced
from iqa_common.executor import Executor
from messaging_abstract.component.client import Node
from messaging_components.clients.external.client_external import ClientExternal

from messaging_components import protocols


@logged
@traced
class ClientJava(ClientExternal):
    """Java Qpid JMS client (base abstract class)."""

    supported_protocols = [protocols.Amqp10()]
    implementation = 'java'
    version = '1.0.1'

    def __init__(self, name: str, node: Node, executor: Executor, **kwargs):
        super(ClientJava, self).__init__(name, node, executor, **kwargs)
