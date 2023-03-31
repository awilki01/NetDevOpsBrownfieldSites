import os
import pytest
import nornir
from termcolor import colored
from nornir import InitNornir
from nornir.core.task import Task, Result
from nornir_utils.plugins.functions import print_result
from netauto_helpers.helpers import *
import netauto_helpers
from brownfield_config_changes import nornir_workflow

DIRECTORIES = ["./remediation_config_changes", "./rendered_configs", "./running_configs"]


class TestAutomationHelpers:
    def test_if_fails_when_directory_not_present(self) -> None:
        with pytest.raises(FileNotFoundError):
            del_directory_contents(["./bad_directory", "./bad_directory2", "./bad_directory3"])

    def test_directory_structure(self) -> None:
        """Ensure proper directory structure is in place"""
        result = os.path.isdir("./remediation_config_changes") and os.path.isdir("./rendered_configs") \
                 and os.path.isdir("./running_configs")
        assert result

    @staticmethod
    def create_new_file(paths: list[str]) -> None:
        """ Create test file called 'test.txt' in given directories list"""
        filename = "text.txt"
        for path in paths:
            with open(os.path.join(path, filename), 'w') as temp_file:
                temp_file.write("testing123")
                temp_file.close()

    def test_that_directory_contents_can_be_deleted(self) -> None:
        """ Test that directory contents can be deleted."""
        self.create_new_file(DIRECTORIES)
        del_directory_contents(DIRECTORIES)

    def test_nornir_initialization(self, init_nornir):
        """ Test to make sure Nornir can be initialized. This will show errors in inventory data files as well."""
        assert type(init_nornir) is nornir.core.Nornir

    def test_automate_brownfield(self, init_nornir):
        workflow = init_nornir.run(
            name="Brownfield Config Changes",
            task=nornir_workflow,
        )
        print_result(workflow)
        print()


