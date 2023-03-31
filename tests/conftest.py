import logging

import nornir.core
import pytest
from nornir import InitNornir
from nornir.core.task import Task, Result
from nornir_utils.plugins.functions import print_result
from nornir.core.filter import F


@pytest.fixture(scope="session")
def init_nornir():
    """ Init nornir object for testing. """
    nr = InitNornir()
    nr = nr.filter(F(groups__contains="lab"))
    nr.config.logging.enabled = False
    yield nr
    nr.close_connections()






