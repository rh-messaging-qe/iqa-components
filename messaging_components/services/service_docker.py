from enum import Enum
from iqa_common.executor import Command, Execution, ExecutorAnsible, CommandAnsible, ExecutorContainer, CommandContainer
from iqa_common.utils.docker_util import DockerUtil
from messaging_abstract.component import Service, ServiceStatus
import logging


class ServiceDocker(Service):
    """
    Implementation of a service represented by a docker container.
    So startup and shutdown are done by managing current state of related
    docker container name.
    """

    _logger = logging.getLogger(__name__)

    class ServiceDockerState(Enum):
        STARTED = ('start', 'started')
        STOPPED = ('stop', 'stopped')
        RESTARTED = ('restart', 'started')

        def __init__(self, system_state, ansible_state):
            self.system_state = system_state
            self.ansible_state = ansible_state

    def status(self) -> ServiceStatus:
        """
        Returns the status based on status of container name.
        :return: The status of this specific service
        :rtype: ServiceStatus
        """
        try:
            container = DockerUtil.get_container(self.name)
            if not container:
                ServiceDocker._logger.debug("Service: %s - Status: UNKNOWN" % self.name)
                return ServiceStatus.UNKNOWN

            if container.status == 'running':
                ServiceDocker._logger.debug("Service: %s - Status: RUNNING" % self.name)
                return ServiceStatus.RUNNING
            elif container.status == 'exited':
                ServiceDocker._logger.debug("Service: %s - Status: STOPPED" % self.name)
                return ServiceStatus.STOPPED
        except Exception:
            ServiceDocker._logger.exception('Error retrieving status of docker container')
            return ServiceStatus.FAILED

        return ServiceStatus.UNKNOWN

    def start(self) -> Execution:
        return self.executor.execute(self._create_command(self.ServiceDockerState.STARTED))

    def stop(self) -> Execution:
        return self.executor.execute(self._create_command(self.ServiceDockerState.STOPPED))

    def restart(self) -> Execution:
        return self.executor.execute(self._create_command(self.ServiceDockerState.RESTARTED))

    def enable(self) -> Execution:
        """
        Simply ignore it (not applicable to containers)
        :return:
        """
        return None

    def disable(self) -> Execution:
        """
        Simply ignore it (not applicable to containers)
        :return:
        """
        return None

    def _create_command(self, service_state: ServiceDockerState):
        """
        Creates a Command instance based on executor type and state
        that is specific to each type of command.
        :param service_state:
        :return:
        """
        if isinstance(self.executor, ExecutorAnsible):
            state = service_state.ansible_state
            restart = 'no'
            if service_state == self.ServiceDockerState.RESTARTED:
                restart = 'yes'

            print('name=%s state=%s restart=%s' % (self.name, state, restart))
            return CommandAnsible('name=%s state=%s restart=%s' % (self.name, state, restart),
                                  ansible_module='docker_container',
                                  stdout=True,
                                  timeout=self.TIMEOUT)
        elif isinstance(self.executor, ExecutorContainer):
            state = service_state.system_state
            return CommandContainer([], docker_command=state, stdout=True, timeout=self.TIMEOUT)
        else:
            state = service_state.system_state
            return Command(['docker', state, self.name], stdout=True, timeout=self.TIMEOUT)
