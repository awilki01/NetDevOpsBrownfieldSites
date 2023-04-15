from termcolor import colored
import netauto_helpers as nh
from nornir import InitNornir
from nornir_utils.plugins.functions import print_result
from nornir.core.filter import F


def main():
    """
    This function performs a series of tasks using Nornir.

    Tasks performed:
    - Delete contents of directories
    - Save running config to file
    - Render config from Jinja templates
    - Write rendered config to file
    - Render remediation config from hier_config
    - Deploy remediation config

    Returns:
    None.
    """

    # Delete contents of directories
    nh.del_directory_contents(
        ["./remediation_config_changes", "./rendered_configs", "./running_configs"]
    )

    nr = InitNornir()
    # nr = nr.filter(name="lab-rtr01")

    nornir_run = nr.run(
        task=nh.nornir_save_running_config_to_file,
    )
    print_result(nornir_run)

    nornir_run = nr.run(
        task=nh.nornir_render_config,
    )
    print_result(nornir_run)

    nornir_run = nr.run(
        task=nh.nornir_write_rendered_config_to_file,
    )
    print_result(nornir_run)

    nornir_run = nr.run(
        task=nh.nornir_render_remediation_config,
    )
    print_result(nornir_run)

    nornir_run = nr.run(
        task=nh.nornir_deploy_remediation_config,
    )
    print_result(nornir_run)
    print("\n\n")
    nr.close_connections()

    print("\n\n")
    print("Failed Hosts:")
    for k in nr.data.failed_hosts:
        print(colored(f" - {k}", "red"))


if __name__ == "__main__":
    main()
