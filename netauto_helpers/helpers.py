"""
    This module has many functions to assist with network automation tasks
    and the framework it applies to. The framework assumes there is three
    directories relative to where the python code is being executed:
        - remediation_config_changes
        - rendered_configs
        - running_configs

    Author: Adam Wilkins
    Email: awilki01@gmail.com
"""

import os
import shutil
import uuid
from pathlib import Path
from nornir.core.task import Task, Result
from nornir_jinja2.plugins.tasks import template_file
from nornir_utils.plugins.tasks.files import write_file
from nornir_napalm.plugins.tasks import napalm_configure, napalm_get
from hier_config import Host


def del_directory_contents(directory_names: list[str]):
    """
    This function deletes all files and directories in the specified directories.

    Args:
        directory_names (list[str]): A list of directory names to delete.

    Returns:
        None
    """
    for name in directory_names:
        for filename in os.listdir(name):
            file_path = os.path.join(name, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f"Failed to delete {file_path}. Reason: {e}]")


def _remediate(task: Task, tag: str, lineage_filename: str) -> Result:
    """
    This function remediates a device based on the specified tag.

    Args:
        task (Task): A Nornir task object.
        tag (str): The tag to remediate.
        lineage_filename (str): The filename of the lineage file to be used with
        hier_config library. See hier_config documentation for details.

    Returns:
        Result
    """
    host = Host(hostname=f"{task.host.name}", os="ios")
    host.load_tags_from_file(lineage_filename)
    host.load_running_config_from_file(f"./running_configs/{task.host.name}.cfg")
    host.load_generated_config_from_file(f"./rendered_configs/{task.host.name}.cfg")
    changes = host.remediation_config_filtered_text(include_tags={tag}, exclude_tags={})

    if changes == "":
        print("No changes")

    cfg_change_path = "./remediation_config_changes/"
    filename = f"{cfg_change_path}{task.host.name}.cfg"

    # Check if file exists. If it does, then append a newline to it so appended results
    # are added correctly. If the file does not exist, create it.
    if os.path.isfile(filename):
        # print("FILE EXISTS")
        with open(filename, "a", encoding="utf-8") as file:
            file.write("\n")
    else:
        Path(filename).touch()

    if changes != "":
        task.run(
            task=write_file,
            filename=filename,
            content=changes,
            dry_run=False,
            append=True,
        )

    return Result(
        host=task.host,
    )


def _save_running_config(task: Task) -> Result:
    """
    This function saves the running configuration of a device.

    Args:
        task (Task): A Nornir task object.

    Returns:
        Result
    """
    cfg_path = "./running_configs/"
    filename = f"{cfg_path}{task.host.name}.cfg"

    running_config = task.run(
        task=napalm_get,
        getters=["get_config"],
    )

    content = running_config[0].result["get_config"]["running"]

    task.run(
        task=write_file,
        filename=filename,
        content=content,
        dry_run=False,
    )

    return Result(
        host=task.host,
    )


def _render_configs(task: Task) -> Result:
    """This function places rendered config in host's data within the Nornir inventory.
    It does not save it to a file.

    Args:
        task (Task): A Nornir task object.

    Returns:
        Result

    """
    template_path = "./templates"
    if "ios_lan_switches" in task.host.groups:
        template = "/switches/base_config.j2"
    else:
        template = "/routers/base_config.j2"

    uuid_str = str(uuid.uuid4())

    result = task.run(
        task=template_file,
        template=template,
        path=template_path,
        uuid=uuid_str,
        **task.host,
        # **task.host unpacks the host name so you don't have to do "host.interfaces.items()"
        # in jinja template. It allows you to just do "interfaces.items()".
        # Its just a personal preference.
    )

    rendered_config = result[0].result

    # This adds information to the host data field. We are storing rendered config in
    # data field of host object
    task.host["rendered_config"] = rendered_config
    # The uuid value is compared in tests to ensure proper config was pushed. This is done
    # later by comparing the Loopback1000 description text on the device running-config and
    # the uuid value stored in the nornir inventory object.
    task.host["uuid_str"] = uuid_str

    return Result(
        host=task.host,
    )


def _write_rendered_config(task: Task) -> Result:
    """
    This function writes the rendered configuration of a device to file.

    Args:
        task (Task): A Nornir task object.

    Returns:
        Result.
    """
    cfg_path = "./rendered_configs/"
    filename = f"{cfg_path}{task.host.name}.cfg"
    content = task.host["rendered_config"]

    task.run(
        task=write_file,
        filename=filename,
        content=content,
        dry_run=False,
    )

    return Result(host=task.host)


def _deploy_config(task: Task, cfg_path: str) -> Result:
    """
    This function deploys the configuration in defined cfg_path
    to a network device.

    Args:
        task (Task): A Nornir task object.
        cfg_path (str): The path to the configuration file.

    Returns:
        Result
    """
    config_file = f"{cfg_path}{task.host.name}.cfg"

    # If file is empty do not apply. NAPALM errors out on blank files.
    if os.stat(config_file).st_size != 0:
        task.run(
            task=napalm_configure,
            filename=config_file,
        )

    return Result(
        host=task.host,
    )


def nornir_save_running_config_to_file(task: Task) -> Result:
    """
    This function saves the running configuration of a device to a local file.

    Args:
        task (Task): A Nornir task object.

    Returns:
        Result
    """
    task.run(
        name="Save Running Config to Local File",
        task=_save_running_config,
    )
    return Result(
        host=task.host,
    )


def nornir_render_config(task: Task) -> Result:
    """
    This function renders the configuration of a device and saves it
    to the Nornir inventory object for that device.

    Args:
        task (Task): A Nornir task object.

    Returns:
        Result
    """
    task.run(
        name="Render Device Configuration to Local File",
        task=_render_configs,
    )
    return Result(
        host=task.host,
    )


def nornir_write_rendered_config_to_file(task: Task) -> Result:
    """
    This function writes the rendered configuration of a device to file.

    Args:
        task (Task): A Nornir task object.

    Returns:
        Result
    """
    task.run(
        name="Write Rendered Config to File",
        task=_write_rendered_config,
    )
    return Result(
        host=task.host,
    )


def nornir_deploy_config(task: Task) -> Result:
    """
    This function deploys the configuration saved to file to a device.

    Args:
        task (Task): A Nornir task object.

    Returns:
        Result
    """
    task.run(
        name="Deploy Config to Devices",
        task=_deploy_config,
        cfg_path="rendered_configs/",
    )
    return Result(
        host=task.host,
    )


def nornir_render_remediation_config(task: Task) -> Result:
    """
    This function generates remediation configurations.

    Args:
        task (Task): A Nornir task object.

    Returns:
        Result
    """
    lineage_filename = "hier_config_lineage/lineage.yaml"
    task.run(
        task=_remediate,
        name="Config Remediation Generation for Safe Services",
        tag="safe_services",
        lineage_filename=lineage_filename,
    )
    return Result(
        host=task.host,
    )


def nornir_deploy_remediation_config(task: Task) -> Result:
    """
    This function deploys remediation configurations to devices.

    Args:
        task (Task): A Nornir task object.

    Returns:
        Result
    """
    task.run(
        name="Deploy Remediation Configs to Devices",
        task=_deploy_config,
        cfg_path="./remediation_config_changes/",
    )
    return Result(
        host=task.host,
    )
