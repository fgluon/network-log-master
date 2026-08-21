from network_log_normalizer import normalize_record
from network_log_normalizer.parsers.nxos_ospf import (
    NxosOspfRetransmissionsParser,
)


PARSER = NxosOspfRetransmissionsParser()


def test_nxos_ospf_retransmissions_is_degradation():
    event = normalize_record(
        {
            "hostname": "switch-example",
            "vendor_hint": "Cisco",
            "os_family_hint": "NX-OS",
            "message": (
                "%OSPF-5-NBR_RETRANSMISSIONS: "
                "ospf-1 [1234] Nbr 192.0.2.10 "
                "re-transmits routing information"
            ),
        },
        parsers=[PARSER],
    )

    assert event.vendor == "cisco"
    assert event.os_family == "nxos"
    assert event.event_family == "ospf"
    assert event.protocol == "ospf"
    assert event.signal_type == "degradation"
    assert event.entity_type == "ospf_neighbor"
    assert event.state == "retransmissions"
    assert event.attributes["process"] == "ospf-1"
    assert event.attributes["neighbor"] == "192.0.2.10"
    assert event.attributes["parser"] == "nxos-ospf-retransmissions"
    assert (
        event.entity_key
        == "OSPF|switch-example|ospf-1|192.0.2.10"
    )


def test_nxos_ospfv3_retransmissions_preserves_family_and_process():
    event = normalize_record(
        {
            "hostname": "switch-example",
            "vendor_hint": "Cisco",
            "os_family_hint": "NX-OS",
            "message": (
                "%OSPFV3-5-NBR_RETRANSMISSIONS: "
                "ospfv3-2 [5678] Nbr 2001:db8::10 "
                "re-originates routing information"
            ),
        },
        parsers=[PARSER],
    )

    assert event.event_family == "ospfv3"
    assert event.protocol == "ospf"
    assert event.signal_type == "degradation"
    assert event.state == "retransmissions"
    assert event.attributes["process"] == "ospfv3-2"
    assert event.attributes["neighbor"] == "2001:db8::10"
    assert (
        event.entity_key
        == "OSPF|switch-example|ospfv3-2|2001:db8::10"
    )


def test_nxos_ospf_uses_source_ip_when_hostname_missing():
    event = normalize_record(
        {
            "source_ip": "192.0.2.80",
            "vendor_hint": "Cisco",
            "os_family_hint": "NX-OS",
            "message": (
                "%OSPF-5-NBR_RETRANSMISSIONS: "
                "ospf-3 [9012] Nbr 198.51.100.20 "
                "re-transmits routing information"
            ),
        },
        parsers=[PARSER],
    )

    assert (
        event.entity_key
        == "OSPF|192.0.2.80|ospf-3|198.51.100.20"
    )


def test_nxos_ospf_missing_neighbor_stays_generic():
    event = normalize_record(
        {
            "hostname": "switch-example",
            "vendor_hint": "Cisco",
            "os_family_hint": "NX-OS",
            "message": (
                "%OSPF-5-NBR_RETRANSMISSIONS: "
                "ospf-1 [1234] future payload layout"
            ),
        },
        parsers=[PARSER],
    )

    assert event.event_family == "ospf"
    assert event.protocol == ""
    assert event.state == ""
    assert event.attention_eligible is True
    assert event.attributes["normalization_path"] == "generic"
    assert "parser" not in event.attributes


def test_nxos_ospfv3_missing_process_stays_generic():
    event = normalize_record(
        {
            "hostname": "switch-example",
            "vendor_hint": "Cisco",
            "os_family_hint": "NX-OS",
            "message": (
                "%OSPFV3-5-NBR_RETRANSMISSIONS: "
                "Nbr 2001:db8::20 future payload layout"
            ),
        },
        parsers=[PARSER],
    )

    assert event.event_family == "ospfv3"
    assert event.protocol == ""
    assert event.state == ""
    assert event.attention_eligible is True
    assert event.attributes["normalization_path"] == "generic"
    assert "parser" not in event.attributes


def test_future_nxos_ospf_event_code_stays_generic():
    event = normalize_record(
        {
            "hostname": "switch-example",
            "vendor_hint": "Cisco",
            "os_family_hint": "NX-OS",
            "message": (
                "%OSPF-5-NEW_FUTURE_EVENT: "
                "ospf-1 [1234] Nbr 192.0.2.30 changed"
            ),
        },
        parsers=[PARSER],
    )

    assert event.event_code == "OSPF-5-NEW_FUTURE_EVENT"
    assert event.event_family == "ospf"
    assert event.protocol == ""
    assert event.state == ""
    assert event.attention_eligible is True
    assert "parser" not in event.attributes


def test_iosxr_cannot_enter_nxos_ospf_parser():
    event = normalize_record(
        {
            "hostname": "router-example",
            "vendor_hint": "Cisco",
            "os_family_hint": "IOS XR",
            "message": (
                "%OSPF-5-NBR_RETRANSMISSIONS: "
                "ospf-1 [1234] Nbr 192.0.2.40 "
                "re-transmits routing information"
            ),
        },
        parsers=[PARSER],
    )

    assert event.vendor == "cisco"
    assert event.os_family == "iosxr"
    assert event.event_family == "ospf"
    assert event.protocol == ""
    assert event.state == ""
    assert event.attention_eligible is True
    assert "parser" not in event.attributes


def test_eos_cannot_enter_nxos_ospf_parser():
    event = normalize_record(
        {
            "hostname": "router-example",
            "vendor_hint": "Arista Networks",
            "os_family_hint": "Arista EOS",
            "message": (
                "%OSPF-5-NBR_RETRANSMISSIONS: "
                "ospf-1 [1234] Nbr 198.51.100.40 "
                "re-transmits routing information"
            ),
        },
        parsers=[PARSER],
    )

    assert event.vendor == "arista"
    assert event.os_family == "eos"
    assert event.event_family == "ospf"
    assert event.protocol == ""
    assert event.state == ""
    assert event.attention_eligible is True
    assert "parser" not in event.attributes


def test_ospf_code_rejects_ospfv3_process_identity():
    event = normalize_record(
        {
            "hostname": "switch-example",
            "vendor_hint": "Cisco",
            "os_family_hint": "NX-OS",
            "message": (
                "%OSPF-5-NBR_RETRANSMISSIONS: "
                "ospfv3-1 [1234] Nbr 192.0.2.50 "
                "re-transmits routing information"
            ),
        },
        parsers=[PARSER],
    )

    assert event.event_family == "ospf"
    assert event.protocol == ""
    assert event.state == ""
    assert "parser" not in event.attributes


def test_ospfv3_code_rejects_ospf_process_identity():
    event = normalize_record(
        {
            "hostname": "switch-example",
            "vendor_hint": "Cisco",
            "os_family_hint": "NX-OS",
            "message": (
                "%OSPFV3-5-NBR_RETRANSMISSIONS: "
                "ospf-1 [1234] Nbr 2001:db8::50 "
                "re-transmits routing information"
            ),
        },
        parsers=[PARSER],
    )

    assert event.event_family == "ospfv3"
    assert event.protocol == ""
    assert event.state == ""
    assert "parser" not in event.attributes
