from amom.client import Sender


def test_isinstance(sender: Sender):
    assert isinstance(sender, Sender)


def test_name(receiver: Sender):
    assert receiver.name == 'Internal core client'
