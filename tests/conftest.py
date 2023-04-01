import pytest
from nornir import InitNornir
from nornir.core.filter import F
from netauto_helpers.helpers import *


@pytest.fixture(scope="session")
def nr():
    """ Init nornir object for testing. """
    nr = InitNornir(logging={"enabled": False})
    nr = nr.filter(F(groups__contains="lab"))
    yield nr
    nr.close_connections()


@pytest.fixture(scope="function")
def del_running_dir_contents():
    """ Delete directory contents"""
    del_directory_contents(["./running_configs"])






