import os
import pytest
import nornir
from termcolor import colored
from nornir import InitNornir
from nornir.core.task import Task, Result
from nornir_utils.plugins.functions import print_result
from netauto_helpers.helpers import *
import netauto_helpers


DIRECTORIES = ["./remediation_config_changes", "./rendered_configs", "./running_configs"]


class TestAutomationHelpers:

    @staticmethod
    def create_new_file(paths: list[str]) -> None:
        """ Create test file called 'test.txt' in given directories list"""
        filename = "text.txt"
        for path in paths:
            with open(os.path.join(path, filename), 'w') as temp_file:
                temp_file.write("testing123")
                temp_file.close()

    @staticmethod
    def check_file_name(path, name):
        for file in os.listdir(path):
            if os.path.isfile(os.path.join(path, file)):
                if name in file:
                    return True
        return False

    def test_if_fails_when_directory_not_present(self) -> None:
        with pytest.raises(FileNotFoundError):
            del_directory_contents(["./bad_directory", "./bad_directory2", "./bad_directory3"])

    def test_directory_structure(self) -> None:
        """Ensure proper directory structure is in place"""
        result = os.path.isdir("./remediation_config_changes") and os.path.isdir("./rendered_configs") \
                 and os.path.isdir("./running_configs")
        assert result

    def test_that_directory_contents_can_be_deleted(self) -> None:
        """ Test that directory contents can be deleted."""
        self.create_new_file(DIRECTORIES)
        del_directory_contents(DIRECTORIES)

    def test_nornir_initialization(self, nr):
        """ Test to make sure Nornir can be initialized. This will show errors in inventory data files as well."""
        assert type(nr) is nornir.core.Nornir

    def test_save_running_config_to_file(self, nr, del_running_dir_contents):
        """ Test the ability to save device running configs to ./running_configs folder."""
        nornir_run = nr.run(
            task=nornir_save_running_config_to_file,
        )
        path = "./running_configs"
        # pytest.set_trace()
        for key in nornir_run.keys():
            assert self.check_file_name(path, key)
            # Print output with pytest -s option for debugging
            if self.check_file_name(path, key):
                print(f"File in directory for device: {key}")
            else:
                print(f"File NOT in directory for device: {key}")

    def test_ensure_running_config_file_exists_and_is_proper(self, nr):
        """ Test to see if running config file exists and is indeed an actual config by checking for a few config lines.
            It tests a common config line at top and bottom of configs for both routers and switches. """
        device_list = []
        for key in nr.inventory.hosts.keys():
            device_list.append(key)
        for device in device_list:
            with open(f"./running_configs/{device}.cfg", 'r') as file:
                output = file.read()
                if 'boot-start-marker' in output and 'line con 0' in output:
                    assert True
                else:
                    assert False







