import os
import pytest
import nornir
from termcolor import colored
from nornir import InitNornir
from nornir.core.task import Task, Result
from nornir_utils.plugins.functions import print_result
from nornir_napalm.plugins.tasks import napalm_get
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
    def check_file_name(path: str, name: str) -> bool:
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

    def test_ensure_running_config_file_exists_and_is_valid(self, nr):
        """ Test to see if running config file exists and is indeed an actual config by checking for a few config lines.
            It tests a common config line at top and bottom of configs for both routers and switches. """
        device_list = []
        for key in nr.inventory.hosts.keys():
            device_list.append(key)
        for device in device_list:
            with open(f"./running_configs/{device}.cfg", 'r') as file:
                output = file.read()
                assert ('boot-start-marker' in output and 'line con 0' in output)

    def test_ensure_configs_are_properly_rendered(self, nr):
        """ Test to ensure configs are properly rendered. """
        nr.run(
            task=nornir_render_config,
        )
        for key in nr.inventory.hosts.keys():
            rendered_config = nr.inventory.hosts[key].data['rendered_config']
            print(rendered_config)
            assert ('-BEGIN RENDER-' in rendered_config and '-END RENDER-' in rendered_config)

    def test_render_configs_to_file(self, nr):
        """ Test that rendered configs are saved to file. """
        result = nr.run(
            task=nornir_write_rendered_config_to_file,
        )
        path = "./rendered_configs"
        # TODO: iterate over nr.inventory.hosts.keys()?
        for key in result.keys():
            assert self.check_file_name(path, key)
            # Print output with pytest -s option for debugging
            if self.check_file_name(path, key):
                print(f"File in directory for device: {key}")
            else:
                print(f"File NOT in directory for device: {key}")

    def test_ensure_rendered_config_file_exists_and_is_valid(self, nr):
        """ Test to see if rendered config file exists and is indeed an actual config by checking for a few config
            lines. It tests a common config line at top and bottom of rendered configs for both routers and switches.
        """
        device_list = []
        for key in nr.inventory.hosts.keys():
            device_list.append(key)
        for device in device_list:
            with open(f"./rendered_configs/{device}.cfg", 'r') as file:
                output = file.read()
                assert ('-BEGIN RENDER-' in output and '-END RENDER-' in output)

    # def test_deploy_rendered_config(self, nr):
    #     """ Test deploy rendered configs to device. """
    #     result = nr.run(
    #         task=nornir_deploy_config,
    #     )
    #     # pytest.set_trace()
    #     assert not result.failed

    def test_render_remediation_config(self, nr):
        """ Test remediation functionality for device. """
        # TODO: Think of ways to best test this further
        result = nr.run(
            task=nornir_render_remediation_config,
        )
        assert not result.failed

    def test_deploy_remediation_config(self, nr):
        """ Test deployment of remediation config to device. """
        # TODO: Think of ways to best test this further
        result = nr.run(
            task=nornir_deploy_remediation_config,
        )
        assert not result.failed

    def test_proper_configs_were_pushed_to_device(self, nr):
        """ Test to ensure configs pushed to device were the same configs rendered in the nornir
        inventory object under task.host['rendered_config'] in the helpers.render_configs function. """

        result = nr.run(
            task=napalm_get,
            getters='get_interfaces',
        )
        print_result(result)

        for key in nr.inventory.hosts.keys():
            nr_inventory_uuid = nr.inventory.hosts[key].data['uuid_str']
            device_uuid = result[key][0].result['get_interfaces']['Loopback1000']['description']
            assert nr_inventory_uuid == device_uuid











