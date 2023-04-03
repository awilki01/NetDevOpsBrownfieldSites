import os, shutil, hashlib, uuid
from pathlib import Path
from nornir import InitNornir
from nornir.core.filter import F
from nornir.core.task import Task, Result
from nornir_utils.plugins.functions import print_result
from nornir_jinja2.plugins.tasks import template_string, template_file
from nornir_utils.plugins.tasks.files import write_file
from nornir_napalm.plugins.tasks import napalm_configure, napalm_get
from nornir_netmiko import netmiko_send_config
from hier_config import Host


# class NetworkConfigUtils:
#     def __init__(self, task: Task):
#         self.task = task


def del_directory_contents(directory_names: list[str]):
    for name in directory_names:
        for filename in os.listdir(name):
            file_path = os.path.join(name, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))


def remediate(task: Task, tag: str, lineage_filename: str) -> Result:
    host = Host(hostname=f"{task.host.name}", os="ios")
    host.load_tags_from_file(lineage_filename)
    host.load_running_config_from_file(f"./running_configs/{task.host.name}.cfg")
    host.load_generated_config_from_file(f"./rendered_configs/{task.host.name}.cfg")

    # print(f"{task.host.name}")
    # print(host.remediation_config_filtered_text(include_tags={tag}, exclude_tags={}))
    changes = host.remediation_config_filtered_text(include_tags={tag}, exclude_tags={})
    # print(task.host.name)

    if changes == "":
        print("No changes")

    # print("---------------------------")
    # print(changes)
    # print("---------------------------")
    cfg_change_path = f"./remediation_config_changes/"
    filename = f"{cfg_change_path}{task.host.name}.cfg"

    # Check if file exists. If it does, then append a newline to it so appended results
    # are added correctly. If the file does not exist, create it.
    if os.path.isfile(filename):
        # print("FILE EXISTS")
        with open(filename, "a") as file:
            file.write("\n")
    else:
        # print("NO FILE EXISTS")
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


def save_running_config(task: Task) -> Result:
    cfg_path = f"./running_configs/"
    filename = f"{cfg_path}{task.host.name}.cfg"

    running_config = task.run(
        task=napalm_get,
        getters=["get_config"],
    )

    content = running_config[0].result['get_config']['running']

    task.run(
        task=write_file,
        filename=filename,
        content=content,
        dry_run=False,
    )

    # print(running_config[0].result['get_config']['running'])
    # task.host['running_config'] = running_config

    return Result(
        host=task.host,
    )


def render_configs(task: Task) -> Result:
    """ This function places rendered config in host's data within the Nornir inventory. It does not save it to file."""
    template_path = f"./templates"
    if "ios_lan_switches" in task.host.groups:
        template = f"/switches/base_config.j2"
    else:
        template = f"/routers/base_config.j2"

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
    task.host['rendered_config'] = rendered_config
    # The uuid value is compared in tests to ensure proper config was pushed. This is done later by comparing
    # the Loopback1000 description text on the device running-config and the uuid value stored in the nornir
    # inventory object.
    task.host['uuid_str'] = uuid_str

    return Result(
        host=task.host,
    )


def write_rendered_config(task: Task) -> Result:
    cfg_path = f"./rendered_configs/"
    filename = f"{cfg_path}{task.host.name}.cfg"
    content = task.host['rendered_config']

    task.run(
        task=write_file,
        filename=filename,
        content=content,
        dry_run=False,
    )

    return Result(
        host=task.host
    )


def deploy_config(task: Task, cfg_path: str) -> Result:
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
    print(f"{task.host.name}---------------------------------")
    task.run(
        name="Save Running Config to Local File",
        task=save_running_config,
    )
    return Result(
        host=task.host,
    )


def nornir_render_config(task: Task) -> Result:
    print(f"{task.host.name}---------------------------------")
    task.run(
        name="Render Device Configuration to Local File",
        task=render_configs,
    )
    return Result(
        host=task.host,
    )


def nornir_write_rendered_config_to_file(task: Task) -> Result:
    print(f"{task.host.name}---------------------------------")
    task.run(
        name="Write Rendered Config to File",
        task=write_rendered_config,
    )
    return Result(
        host=task.host,
    )


def nornir_deploy_config(task: Task) -> Result:
    print(f"{task.host.name}---------------------------------")
    task.run(
        name="Deploy Config to Devices",
        task=deploy_config,
        cfg_path=f"rendered_configs/",
    )
    return Result(
        host=task.host,
    )


def nornir_render_remediation_config(task: Task) -> Result:
    print(f"{task.host.name}---------------------------------")
    lineage_filename = "hier_config_lineage/lineage.yaml"
    task.run(
        task=remediate,
        name="Config Remediation Generation for Safe Services",
        tag="safe_services",
        lineage_filename=lineage_filename,
    )
    return Result(
        host=task.host,
    )


def nornir_deploy_remediation_config(task: Task) -> Result:
    print(f"{task.host.name}---------------------------------")
    task.run(
        name="Deploy Remediation Configs to Devices",
        task=deploy_config,
        cfg_path=f"./remediation_config_changes/",
    )
    return Result(
        host=task.host,
    )



