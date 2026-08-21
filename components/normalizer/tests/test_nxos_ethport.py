from network_log_normalizer import normalize_record
from network_log_normalizer.parsers.nxos_ethport import (
    NxosEthportStateParser,
)


PARSER = NxosEthportStateParser()


def test_nxos_ethport_link_failure_is_down_transition():
    event = normalize_record(
        {
            "hostname": "switch-example",
            "vendor_hint": "Cisco",
            "os_family_hint": "NX-OS",
            "message": (
                "%ETHPORT-5-IF_DOWN_LINK_FAILURE: "
                "Interface Ethernet1/10 is down "
                "(Link failure)"
            ),
        },
        parsers=[PARSER],
    )

    assert event.vendor == "cisco"
    assert event.os_family == "nxos"
    assert event.event_family == "ethport"
    assert event.protocol == "ethernet"
    assert event.signal_type == "state_transition"
    assert event.state == "down"
    assert event.entity_type == "interface"
    assert (
        event.entity_key
        == "INTERFACE|switch-example|Ethernet1/10"
    )
    assert event.attributes["interface"] == "Ethernet1/10"
    assert event.attributes["reason"] == "Link failure"
    assert event.attributes["parser"] == "nxos-ethport-state"


def test_nxos_ethport_up_is_recovery():
    event = normalize_record(
        {
            "hostname": "switch-example",
            "vendor_hint": "Cisco",
            "os_family_hint": "NX-OS",
            "message": (
                "%ETHPORT-5-IF_UP: "
                "Interface Ethernet1/10 is up"
            ),
        },
        parsers=[PARSER],
    )

    assert event.protocol == "ethernet"
    assert event.signal_type == "recovery"
    assert event.state == "up"
    assert (
        event.entity_key
        == "INTERFACE|switch-example|Ethernet1/10"
    )


def test_nxos_ethport_up_context_is_preserved():
    event = normalize_record(
        {
            "hostname": "switch-example",
            "vendor_hint": "Cisco",
            "os_family_hint": "NX-OS",
            "message": (
                "%ETHPORT-5-IF_UP: "
                "Interface Ethernet1/20 is up in mode trunk"
            ),
        },
        parsers=[PARSER],
    )

    assert event.state == "up"
    assert (
        event.attributes["operational_context"]
        == "mode trunk"
    )


def test_nxos_ethport_uses_source_ip_when_hostname_missing():
    event = normalize_record(
        {
            "source_ip": "192.0.2.80",
            "vendor_hint": "Cisco",
            "os_family_hint": "NX-OS",
            "message": (
                "%ETHPORT-5-IF_DOWN_LINK_FAILURE: "
                "Interface Ethernet1/30 is down "
                "(Link failure)"
            ),
        },
        parsers=[PARSER],
    )

    assert (
        event.entity_key
        == "INTERFACE|192.0.2.80|Ethernet1/30"
    )


def test_unknown_ethport_layout_stays_generic():
    event = normalize_record(
        {
            "hostname": "switch-example",
            "vendor_hint": "Cisco",
            "os_family_hint": "NX-OS",
            "message": (
                "%ETHPORT-5-IF_DOWN_LINK_FAILURE: "
                "future payload layout not understood"
            ),
        },
        parsers=[PARSER],
    )

    assert event.vendor == "cisco"
    assert event.os_family == "nxos"
    assert event.event_family == "ethport"
    assert event.state == ""
    assert event.attention_eligible is True
    assert event.attributes["normalization_path"] == "generic"
    assert "parser" not in event.attributes


def test_other_ethport_event_code_stays_generic():
    event = normalize_record(
        {
            "hostname": "switch-example",
            "vendor_hint": "Cisco",
            "os_family_hint": "NX-OS",
            "message": (
                "%ETHPORT-5-NEW_FUTURE_EVENT: "
                "Interface Ethernet1/40 changed somehow"
            ),
        },
        parsers=[PARSER],
    )

    assert event.event_code == "ETHPORT-5-NEW_FUTURE_EVENT"
    assert event.event_family == "ethport"
    assert event.vendor == "cisco"
    assert event.os_family == "nxos"
    assert event.state == ""
    assert event.attention_eligible is True
    assert event.attributes["normalization_path"] == "generic"


def test_iosxr_hint_cannot_enter_nxos_ethport_parser():
    event = normalize_record(
        {
            "hostname": "router-example",
            "vendor_hint": "Cisco",
            "os_family_hint": "IOS XR",
            "message": (
                "%ETHPORT-5-IF_DOWN_LINK_FAILURE: "
                "Interface Ethernet1/50 is down "
                "(Link failure)"
            ),
        },
        parsers=[PARSER],
    )

    assert event.vendor == "cisco"
    assert event.os_family == "iosxr"
    assert event.event_family == "ethport"
    assert event.state == ""
    assert event.attention_eligible is True
    assert event.attributes["normalization_path"] == "generic"
    assert "parser" not in event.attributes


def test_nxos_ethport_fex_interface_identity_is_preserved():
    event = normalize_record(
        {
            "hostname": "switch-example",
            "vendor_hint": "Cisco",
            "os_family_hint": "NX-OS",
            "message": (
                "%ETHPORT-5-IF_DOWN_LINK_FAILURE: "
                "Interface Ethernet101/1/10 is down "
                "(Link failure)"
            ),
        },
        parsers=[PARSER],
    )

    assert event.attributes["interface"] == "Ethernet101/1/10"
    assert (
        event.entity_key
        == "INTERFACE|switch-example|Ethernet101/1/10"
    )
    assert event.state == "down"
