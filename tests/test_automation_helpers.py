import os


def test_directory_structure():
    result = os.path.isdir("../remediation_config_changes") and os.path.isdir("../rendered_configs") \
             and os.path.isdir("../running_configs")
    assert result


