from messaging_abstract.component import *
from messaging_components.clients.external.client_external import ClientExternal
from .nodejs import *
from .python import *
from .java import *
import logging


class ClientFactory(object):

    # Static element to store all available implementations
    _implementations: list = []

    @staticmethod
    def create_clients(implementation: str, node: Node, executor: Executor, **kwargs) -> list:

        for client in ClientExternal.__subclasses__():

            # Ignore clients with different implementation
            if client.implementation != implementation:
                continue

            # Now loop through concrete client types (sender, receiver, connector)
            clients = []
            for client_impl in client.__subclasses__():
                name = '%s-%s-%s' % (implementation, client_impl.__name__.lower(), node.hostname)
                clients.append(client_impl(name=name, node=node, executor=executor, **kwargs))

            return clients

        exception = ValueError('Invalid client implementation: %s' % implementation)
        logging.getLogger(ClientFactory.__module__).error(exception)
        raise exception

    @staticmethod
    def get_available_implementations() -> list:

        # If implementations list has already been loaded, use it
        if ClientFactory._implementations:
            return ClientFactory._implementations

        result = []

        for client in ClientExternal.__subclasses__():
            result.append(client.implementation)

        ClientFactory._implementations = result

        return result
