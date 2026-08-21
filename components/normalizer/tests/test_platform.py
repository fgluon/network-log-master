from network_log_normalizer.platform import (
    extract_platform_hint,
)


def test_arista_eos_hint_is_recognized():
    hint = extract_platform_hint(
        "Arista Networks",
        "Arista EOS",
    )

    assert hint.vendor == "arista"
    assert hint.os_family == "eos"
    assert hint.raw_vendor == "Arista Networks"
    assert hint.raw_os_family == "Arista EOS"


def test_cisco_nxos_hint_is_recognized():
    hint = extract_platform_hint(
        "Cisco",
        "NX-OS",
    )

    assert hint.vendor == "cisco"
    assert hint.os_family == "nxos"


def test_cisco_iosxr_hint_is_recognized():
    hint = extract_platform_hint(
        "Cisco",
        "IOS XR",
    )

    assert hint.vendor == "cisco"
    assert hint.os_family == "iosxr"


def test_unknown_platform_hint_is_not_trusted():
    hint = extract_platform_hint(
        "FutureVendor",
        "FutureOS",
    )

    assert hint.vendor == "unknown"
    assert hint.os_family == "unknown"
    assert hint.raw_vendor == "FutureVendor"
    assert hint.raw_os_family == "FutureOS"
