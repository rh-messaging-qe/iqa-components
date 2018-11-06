from messaging_abstract.component.server.server import *
from messaging_abstract.component.server.router import *
from messaging_abstract.component.server.broker import *
from messaging_abstract.component.server.service import *
from .service_docker import *
from .service_system import *
import logging


class ServiceFactory(object):
    """
    This factory class can be used to help defining how Service implementation of the
    given Server Component will be used to manage startup/shutdown and ping of related
    component.

    When component is running in a docker container, startup/shutdown is done by
    starting / stopping the container.

    Otherwise a valid service name must be provided.
    """
    _logger = logging.getLogger(__name__)

    @staticmethod
    def create_service(executor: Executor, service_name: str=None, **kwargs) -> Service:

        if service_name:
            ServiceFactory._logger.debug("Creating ServiceSystem - name: %s - executor: %s"
                                         % (service_name, executor.__class__.__name__))
            return ServiceSystem(name=service_name, executor=executor)
        elif isinstance(executor, ExecutorContainer):
            ServiceFactory._logger.debug("Creating ServiceDocker - name: %s - executor: %s"
                                         % (executor.container_name, executor.__class__.__name__))
            return ServiceDocker(name=executor.container_name, executor=executor)

        ServiceFactory._logger.debug("Unable to determine Service")
        raise ValueError('Unable to determine service for server component')
