from hier_config import Host


def main():
    host = Host(hostname="flg-rtr01.mylab.com", os="ios")
    host.load_tags_from_file("lineage.yaml")
    host.load_running_config_from_file("flg-rtr01-full_config.cfg")
    host.load_generated_config_from_file("flg-rtr01-configlet.cfg")

    print(host.remediation_config_filtered_text(include_tags={"ntp"}, exclude_tags={}))


if __name__ == "__main__":
    main()
