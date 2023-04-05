from termcolor import colored
from netauto_helpers.helpers import (
    del_directory_contents,
    nornir_save_running_config_to_file,
    nornir_render_config,
    nornir_write_rendered_config_to_file,
    nornir_render_remediation_config,
    nornir_deploy_remediation_config,
)
from nornir import InitNornir
from nornir_utils.plugins.functions import print_result


def main():
    """
    This function performs a series of tasks using Nornir.

    Tasks performed:
    - Delete contents of directories
    - Save running config to file
    - Render config
    - Write rendered config to file
    - Render remediation config
    - Deploy remediation config

    Returns:
    None.
    """

    # Delete contents of directories
    del_directory_contents(
        ["./remediation_config_changes", "./rendered_configs", "./running_configs"]
    )

    nr = InitNornir()

    nornir_run = nr.run(
        task=nornir_save_running_config_to_file,
    )
    print_result(nornir_run)

    nornir_run = nr.run(
        task=nornir_render_config,
    )
    print_result(nornir_run)

    nornir_run = nr.run(
        task=nornir_write_rendered_config_to_file,
    )
    print_result(nornir_run)

    # nornir_run = nr.run(
    #     task=nornir_deploy_config,
    # )
    # print_result(nornir_run)

    nornir_run = nr.run(
        task=nornir_render_remediation_config,
    )
    print_result(nornir_run)

    nornir_run = nr.run(
        task=nornir_deploy_remediation_config,
    )
    print_result(nornir_run)
    print("\n\n")
    # print_result(workflow, severity_level=logging.ERROR)
    nr.close_connections()

    print("\n\n")
    print("Failed Hosts:")
    for k in nr.data.failed_hosts:
        print(colored(f" - {k}", "red"))


if __name__ == "__main__":
    main()
