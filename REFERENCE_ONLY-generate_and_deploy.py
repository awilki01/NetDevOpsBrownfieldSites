from nornir import InitNornir
from nornir.core.filter import F
from nornir.core.task import Task, Result
from nornir_utils.plugins.functions import print_result
from nornir_jinja2.plugins.tasks import template_string, template_file
from nornir_utils.plugins.tasks.files import write_file
from nornir_napalm.plugins.tasks import napalm_configure, napalm_get
from nornir_netmiko import netmiko_send_config
from hier_config import Host



def remediate(task: Task, tag: str, lineage_filename: str) -> Result:

    host = Host(hostname=f"{task.host.name}", os="ios")
    host.load_tags_from_file(lineage_filename)
    host.load_running_config_from_file(f"running_configs/{task.host.name}.cfg")
    host.load_generated_config_from_file(f"generated_configs/{task.host.name}.cfg")

    print(f"{task.host.name}")
    print(host.remediation_config_filtered_text(include_tags={tag}, exclude_tags={}))
    changes = host.remediation_config_filtered_text(include_tags={tag}, exclude_tags={})
    cfg_change_path = f"remediation_config_changes/"
    filename = f"{cfg_change_path}{task.host.name}_change.cfg"

    task.run(
        task=write_file,
        filename=filename,
        content=changes,
        dry_run=False,
        append=True,
    )


def save_running_configs(task: Task) -> Result:
    cfg_path = f"running_configs/"
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
    template_path = f"templates"
    if "ios_lan_switches" in task.host.groups:
        template = f"/switches/base_config.j2"
    else:
        template = f"/routers/base_config.j2"

    result = task.run(
        task=template_file,
        template=template,
        path=template_path,
        **task.host,
        # **task.host unpacks the host name so you don't have to do "host.interfaces.items()"
        # in jinja template. It allows you to just do "interfaces.items()".
        # Its just a personal preference.
    )

    rendered_config = result[0].result

    # This adds information to the host data field. We are storing rendered config in
    # data field of host object
    task.host['rendered_config'] = rendered_config

    return Result(
        host=task.host,
    )


def write_configs(task: Task) -> Result:
    cfg_path = f"rendered_configs/"
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


def deploy_configs(task: Task) -> Result:
    # filename = f"rendered_configs/{task.host.name}.cfg"
    # with open(filename, "r") as f:
    #     commands = f.readlines()
    #
    # print(commands)
    #
    # # Replace newline char in commands
    # commands = [c.replace("\n", "") for c in commands]
    #
    # print(commands)

    cfg_path = f"rendered_configs/"
    config = f"{cfg_path}{task.host.name}.cfg"

    task.run(
        task=napalm_configure,
        filename=config,
    )

    return Result(
        host=task.host,
    )

# def deploy_configs(task: Task) -> Result:
#     filename = f"configlets/{task.host.name}.txt"
#     with open(filename, "r") as f:
#         cfg = f.read()
#
#     task.run(
#         task=napalm_configure,
#         configuration=cfg,
#         replace=True,
#     )
#
#     return Result(
#         host=task.host,
#     )


def main():
    nr = InitNornir()
    # nr = nr.filter(F(groups__contains="ios_lan_switches"))
    # nr = nr.filter(name="router2")

    nr.run(
        task=save_running_configs,
    )
    # print_result(get_running_configs)

    render_result = nr.run(
        task=render_configs,
    )
    print_result(render_result)

    write_result = nr.run(
        task=write_configs,
    )
    print_result(write_result)

    # NTP remediation
    nr.run(
        task=remediate,
        tag="ntp",
        lineage_filename="hier_config_lineage/lineage.yaml",
    )

    # Syslog server remediation
    # nr.run(
    #     task=remediate,
    #     tag="syslog",
    #     lineage_filename="lineage-syslog.yaml",
    # )

    deploy_result = nr.run(
        task=deploy_configs,
    )
    print_result(deploy_result)
    print()


if __name__ == "__main__":
    main()
