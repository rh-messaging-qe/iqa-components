import posixpath
import re
import logging
import time
from enum import Enum
from iqa_common.executor import Command, Execution, ExecutorAnsible, CommandAnsible, Executor
from iqa_common.utils.tcp_util import TcpUtil
from messaging_abstract.component import Service, ServiceStatus


class ServiceDummyBroker(Service):
    """
    Implementation of a Artemis pseudo-service to manage a Server component.
    """

    MAX_ATTEMPTS = 10
    DELAY = 3

    _logger = logging.getLogger(__name__)

    def __init__(self, name: str, executor: Executor, **kwargs):
        super().__init__(name, executor)
        self.name = "artemis-service"

        self.ansible_host = kwargs.get("ansible_host", "localhost")
        self.service_default_port = kwargs.get("artemis_port", "61616")
        self.service_web_port = kwargs.get("broker_web_port", "8161")
        self.service_path = posixpath.join(kwargs.get("broker_path"), "bin", "artemis-service")
        self.service_username = kwargs.get("broker_service_user", "jamq")

    class ServiceSystemState(Enum):
        STARTED = ('start', 'started')
        STOPPED = ('stop', 'stopped')
        RESTARTED = ('restart', 'restarted')

        def __init__(self, system_state, ansible_state):
            self.system_state = system_state
            self.ansible_state = ansible_state

    def status(self) -> ServiceStatus:
        """
        Returns the service status based on linux service.
        :return: The status of this specific service
        :rtype: ServiceStatus
        """
        # service output :
        # is running
        # is stopped

        # systemctl output:
        # (running)
        # (dead)

        # On RHEL7> service is automatically redirected to systemctl
        cmd_status = Command(['runuser', '-l', self.service_username, '%s status' % self.service_path], stdout=True, timeout=self.TIMEOUT)
        execution = self.executor.execute(cmd_status)

        if not execution.read_stdout():
            ServiceDummyBroker._logger.debug("Service: %s - Status: FAILED" % self.name)
            return ServiceStatus.FAILED

        service_output = execution.read_stdout()

        if re.search('(is running|\(running\)|Running)', service_output):
            ServiceDummyBroker._logger.debug("Service: %s - Status: RUNNING" % self.name)
            return ServiceStatus.RUNNING
        elif re.search('(is stopped|\(dead\)|Stopped)', service_output):
            ServiceDummyBroker._logger.debug("Service: %s - Status: STOPPED" % self.name)
            return ServiceStatus.STOPPED

        ServiceDummyBroker._logger.debug("Service: %s - Status: UNKNOWN" % self.name)
        return ServiceStatus.UNKNOWN

    def start(self) -> Execution:
        return self.executor.execute(self._create_command(self.ServiceSystemState.STARTED))

    def start_and_wait(self, wait_for_messaging):
        execution = self.executor.execute(self._create_command(self.ServiceSystemState.STARTED))
        self._wait_for_messaging(wait_for_messaging)

    def stop(self) -> Execution:
        return self.executor.execute(self._create_command(self.ServiceSystemState.STOPPED))

    def restart(self) -> Execution:
        return self.executor.execute(self._create_command(self.ServiceSystemState.RESTARTED))

    def _wait_for_messaging(self, messaging_wait=False):
        # Wait until broker web port is available
        self.__tcp_wait_for_accessible_port(self.service_web_port, self.ansible_host)

        # Or also messaging subsystem goes up
        if messaging_wait:
            self.__tcp_wait_for_accessible_port(self.service_default_port, self.ansible_host)

    @staticmethod
    def __tcp_wait_for_accessible_port(port, host):
        for attempt in range(ServiceDummyBroker.MAX_ATTEMPTS):
            if attempt == ServiceDummyBroker.MAX_ATTEMPTS - 1:
                print("     broker is not reachable after %d attempts" % ServiceDummyBroker.MAX_ATTEMPTS)

            if TcpUtil.is_tcp_port_available(port, host):
                return True

            time.sleep(ServiceDummyBroker.DELAY)
        ServiceDummyBroker._logger.info("Unable to connect to hostname:port: %s:%s" % (host, port))
        return False

    def _create_command(self, service_state: ServiceSystemState):
        """
        Creates a Command instance based on executor type and state
        that is specific to each type of command.
        :param service_state:
        :return:
        :return:
        """
        command = 'runuser -l %s %s %s' % (self.service_username, self.service_path, service_state.system_state)
        if isinstance(self.executor, ExecutorAnsible):
            state = service_state.ansible_state
            return CommandAnsible(command,
                                  ansible_module='command',
                                  stdout=True,
                                  timeout=self.TIMEOUT)
        else:
            state = service_state.system_state
            return Command(command.split(), stdout=True, timeout=self.TIMEOUT)
