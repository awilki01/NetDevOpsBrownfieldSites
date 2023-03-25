import pytest
import socket


# def test_ensure_bad_device_name_in_dns_throws_exception():
#     match_regex = ".* not known"
#     with pytest.raises(socket.gaierror, match=match_regex):
#         dns_result = socket.gethostbyname("bad_name.mylab.com")


def test_ensure_bad_device_name_in_dns_throws_exception():
    with pytest.raises(socket.gaierror) as exc_info:
        socket.gethostbyname("bad_name.mylab.com")
    expected = "not known"
    assert expected in str(exc_info.value)


def test_can_resolve_router_name_in_dns():
    dns_request = socket.gethostbyname("lab-rtr01.mylab.com")
    assert dns_request == "10.1.1.10"


def test_can_resolve_switch_name_in_dns():
    dns_request = socket.gethostbyname("lab-sw01.mylab.com")
    assert dns_request == "10.1.1.11"



