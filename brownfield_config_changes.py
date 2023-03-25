# import logging

from termcolor import colored
from nornir import InitNornir
from nornir.core.task import Task, Result
from nornir_utils.plugins.functions import print_result
from netauto_helpers.helpers import *


def nornir_workflow(task: Task) -> Result:
    task.run(
        name="Save Running Config to Local File",
        # severity_level=logging.INFO,
        task=save_running_configs,
    )

    task.run(
        name="Render Device Configurations",
        task=render_configs,
    )

    task.run(
        name="Write Configs to File",
        task=write_configs,
    )

    task.run(
        name="Deploy Configs to Devices",
        task=deploy_configs,
        cfg_path=f"rendered_configs/",
    )

    # Config remediation steps
    task.run(
        name="Save Running Config to Local File",
        # severity_level=logging.INFO,
        task=save_running_configs,
    )

    lineage_filename = "hier_config_lineage/lineage.yaml"

    task.run(
        task=remediate,
        name="Config Remediation Generation for Safe Services",
        tag="safe_services",
        lineage_filename=lineage_filename,
    )

    task.run(
        name="Deploy Remediation Configs to Devices",
        task=deploy_configs,
        cfg_path=f"./remediation_config_changes/",
    )

    return Result(
        host=task.host,
    )


def main():
    # Delete contents of directories
    del_directory_contents(["./remediation_config_changes", "./rendered_configs", "./running_configs"])

    nr = InitNornir()
    # Apply inventory filters, if needed. Examples:
    # nr = nr.filter(F(groups__contains="ios_lan_switches"))
    # nr = nr.filter(name="flg-rtr01")

    workflow = nr.run(
        name="Brownfield Config Changes",
        task=nornir_workflow,
    )
    print_result(workflow)
    print("\n\n")
    print("Failed Hosts:")
    # print(workflow.failed_hosts.keys())
    for k in workflow.failed_hosts:
        print(colored(f" - {k}", "red"))

    print("\n\n")
    # print_result(workflow, severity_level=logging.ERROR)


if __name__ == "__main__":
    main()

