import pytest

from netauto_helpers.helpers import del_directory


def test_if_fails_when_directory_not_present():
    with pytest.raises(FileNotFoundError):
        del_directory(["./bad_directory", "./bad_directory2", "./bad_directory3"])


def test_that_directory_contents_can_be_deleted():
    del_directory(["./remediation_config_changes", "./rendered_configs", "./running_configs"])
