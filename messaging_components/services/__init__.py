from messaging_abstract.component.server.server import *
from messaging_abstract.component.server.router import *
from messaging_abstract.component.server.broker import *
from messaging_abstract.component.server.service import *
from .service_docker import *
from .service_system_init import *
from .service_systemd import *
from .service_dummy_broker import *

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
            # Validate if systemd is available
            svc_cmd_exec: Execution = executor.execute(Command(['pidof', 'systemd'], stdout=True, timeout=30))
            if svc_cmd_exec.completed_successfully():
                # Create ServiceSystemD
                ServiceFactory._logger.debug("Creating ServiceSystemD - name: %s - executor: %s"
                                             % (service_name, executor.__class__.__name__))
                return ServiceSystemD(name=service_name, executor=executor)
            else:
                ServiceFactory._logger.debug("Creating ServiceSystemInit - name: %s - executor: %s"
                                             % (service_name, executor.__class__.__name__))
                return ServiceSystemInit(name=service_name, executor=executor)
        else:
            container_name = None
            if isinstance(executor, ExecutorContainer):
                container_name = executor.container_name
            elif isinstance(executor, ExecutorAnsible):
                ServiceFactory._logger.debug("Creating ServiceDummyBroker - name: %s - executor: %s"
                                             % (service_name, executor.__class__.__name__))
                return ServiceDummyBroker(name=service_name, executor=executor, **kwargs)
            elif isinstance(executor, ExecutorAnsible) and executor.ansible_connection == 'docker':
                container_name = executor.ansible_host

            if container_name:
                ServiceFactory._logger.debug("Creating ServiceDocker - name: %s - executor: %s"
                                             % (container_name, executor.__class__.__name__))
                return ServiceDocker(name=container_name, executor=executor)

        ServiceFactory._logger.debug("Unable to determine Service")
        raise ValueError('Unable to determine service for server component')
