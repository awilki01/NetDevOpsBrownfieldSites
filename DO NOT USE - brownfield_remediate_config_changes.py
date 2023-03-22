# import logging

from termcolor import colored
from nornir import InitNornir
from nornir.core.task import Task, Result
from netauto_helpers.helpers import save_running_configs, deploy_configs, remediate, del_directory


def nornir_workflow(task: Task) -> Result:
    lineage_filename = "hier_config_lineage/lineage.yaml"
    task.run(
        name="Save Running Config to Local File",
        # severity_level=logging.INFO,
        task=save_running_configs,
    )

    task.run(
        task=remediate,
        name="NTP Remediation",
        tag="ntp",
        lineage_filename=lineage_filename,
    )

    task.run(
        task=remediate,
        name="Syslog Remediation",
        tag="syslog",
        lineage_filename=lineage_filename,
    )

    task.run(
        name="Deploy Configs to Devices",
        task=deploy_configs,
        cfg_path=f"./remediation_config_changes/",
    )

    return Result(
        host=task.host,
    )


def main():
    # Delete contents of ./remediation_config_changes
    del_directory("./remediation_config_changes")

    nr = InitNornir()
    # nr = nr.filter(F(groups__contains="ios_lan_switches"))
    # nr = nr.filter(name="router2")

    workflow = nr.run(
        name="Brownfield Remediation Config Changes",
        task=nornir_workflow,
    )
    # print_result(workflow)
    print("\n\n")
    print("Failed Hosts:")
    # print(workflow.failed_hosts.keys())
    for k in workflow.failed_hosts:
        print(colored(f" - {k}", "red"))

    print("\n\n")
    # print_result(workflow, severity_level=logging.ERROR)


if __name__ == "__main__":
    main()