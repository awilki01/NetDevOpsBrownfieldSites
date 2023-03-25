import os
import pytest
from termcolor import colored
from nornir import InitNornir
from nornir.core.task import Task, Result
from nornir_utils.plugins.functions import print_result
from netauto_helpers.helpers import *
import netauto_helpers

DIRECTORIES = ["./remediation_config_changes", "./rendered_configs", "./running_configs"]


def test_if_fails_when_directory_not_present():
    with pytest.raises(FileNotFoundError):
        del_directory_contents(["./bad_directory", "./bad_directory2", "./bad_directory3"])


def test_directory_structure():
    """Ensure proper directory structure is in place"""
    result = os.path.isdir("./remediation_config_changes") and os.path.isdir("./rendered_configs") \
             and os.path.isdir("./running_configs")
    assert result


def create_new_file(paths: list[str]):
    """ Create test file called 'test.txt' in given directories list"""
    filename = "text.txt"
    for path in paths:
        with open(os.path.join(path, filename), 'w') as temp_file:
            temp_file.write("testing123")
            temp_file.close()


def test_that_directory_contents_can_be_deleted():
    create_new_file(DIRECTORIES)
    del_directory_contents(DIRECTORIES)





