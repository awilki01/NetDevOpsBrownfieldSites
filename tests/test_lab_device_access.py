import socket
import pytest
from netmiko import ConnectHandler

lab_device_dict = {
    "lab-rtr01.mylab.com": "10.1.1.10",
    "lab-sw01.mylab.com": "10.1.1.11",
}


class TestLabDeviceEnvironment:
    def test_ensure_bad_device_name_in_dns_throws_exception(self):
        with pytest.raises(socket.gaierror) as exc_info:
            socket.gethostbyname("bad_name.mylab.com")
        expected = "not known"
        assert expected in str(exc_info.value)

    def test_can_resolve_name_in_dns(self):
        for device, device_ip in lab_device_dict.items():
            dns_request = socket.gethostbyname(device)
            assert dns_request == device_ip

    def test_can_ssh_into_devices(self):
        for device in lab_device_dict:
            ssh_connection = ConnectHandler(
                device_type="cisco_ios",
                ip=device,
                username="labuser",
                password="password123",
            )
            result = ssh_connection.find_prompt()
            ssh_connection.disconnect()
            assert type(result) is str
