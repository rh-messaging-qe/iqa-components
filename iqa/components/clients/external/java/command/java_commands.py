
"""
Specialized implementation of external command for java clients (currently cli-qpid.jar only). 
"""
from messaging_components.clients.external.command.client_command import ConnectorClientCommand, ReceiverClientCommand, \
    SenderClientCommand
from messaging_components.clients.external.java.command.java_options import JavaControlOptionsCommon, \
    JavaControlOptionsReceiver, JavaControlOptionsSenderReceiver, JavaConnectionOptionsCommon


class JavaConnectorClientCommand(ConnectorClientCommand):
    """
    Java connector client command specialization.
    In Java client we must provide --broker and (optionally) --address.
    The control property instance used here is JavaControlOptionsCommon.
    """
    def __init__(self, stdout: bool=False, stderr: bool=False,
                   daemon: bool=False, timeout: int=0,
                   encoding: str="utf-8"):
        super(JavaConnectorClientCommand, self).__init__(stdout, stderr, daemon, timeout, encoding)
        self.control = JavaControlOptionsCommon()
        self.connection = JavaConnectionOptionsCommon()

    def main_command(self) -> list:
        return ['cli-qpid-connector']


class JavaReceiverClientCommand(ReceiverClientCommand):

    def __init__(self, stdout: bool=False, stderr: bool=False,
                   daemon: bool=False, timeout: int=0,
                   encoding: str="utf-8"):
        """
        Java receiver client command specialization.
        In Java client we must provide --broker and (optionally) --address.
        The control property instance used here is JavaControlOptionsCommon.
        """
        super(JavaReceiverClientCommand, self).__init__(stdout, stderr, daemon, timeout, encoding)
        self.control = JavaControlOptionsReceiver()
        self.connection = JavaConnectionOptionsCommon()

    def main_command(self) -> list:
        return ['cli-qpid-receiver']


class JavaSenderClientCommand(SenderClientCommand):
    def __init__(self, stdout: bool=False, stderr: bool=False,
                   daemon: bool=False, timeout: int=0,
                   encoding: str="utf-8"):
        """
        Java sender client command specialization.
        In Java client we must provide --broker and (optionally) --address.
        The control property instance used here is JavaControlOptionsCommon.
        """
        super(JavaSenderClientCommand, self).__init__(stdout, stderr, daemon, timeout, encoding)
        self.control = JavaControlOptionsSenderReceiver()
        self.connection = JavaConnectionOptionsCommon()

    def main_command(self) -> list:
        return ['cli-qpid-sender']
