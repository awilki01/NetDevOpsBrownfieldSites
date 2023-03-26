import logging

import nornir.core
import pytest
from nornir import InitNornir
from nornir.core.task import Task, Result
from nornir_utils.plugins.functions import print_result


@pytest.fixture(scope="session")
def init_nornir():
    nr = InitNornir()
    nr.config.logging.enabled = False
    yield nr
    nr.close_connections()






