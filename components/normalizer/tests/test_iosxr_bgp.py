from network_log_normalizer import normalize_record
from network_log_normalizer.parsers.iosxr_bgp import (
    IosXrBgpAdjchangeParser,
)


PARSER = IosXrBgpAdjchangeParser()


def test_iosxr_bgp_down_is_state_transition():
    event = normalize_record(
        {
            "hostname": "router-example",
            "vendor_hint": "Cisco",
            "os_family_hint": "IOS XR",
            "message": (
                "%ROUTING-BGP-5-ADJCHANGE : "
                "neighbor 192.0.2.50 Down - "
                "User clear requested "
                "(VRF: default) "
                "(AS: 64512)"
            ),
        },
        parsers=[PARSER],
    )

    assert event.vendor == "cisco"
    assert event.os_family == "iosxr"
    assert event.protocol == "bgp"
    assert event.signal_type == "state_transition"
    assert event.state == "down"
    assert event.entity_type == "bgp_peer"
    assert (
        event.entity_key
        == "BGP|router-example|default|192.0.2.50"
    )
    assert event.attributes["peer"] == "192.0.2.50"
    assert event.attributes["peer_as"] == "64512"
    assert event.attributes["reason"] == "User clear requested"


def test_iosxr_bgp_up_is_recovery():
    event = normalize_record(
        {
            "hostname": "router-example",
            "vendor_hint": "Cisco",
            "os_family_hint": "IOS XR",
            "message": (
                "%ROUTING-BGP-5-ADJCHANGE : "
                "neighbor 198.51.100.50 Up "
                "(VRF: default) "
                "(AS: 64513)"
            ),
        },
        parsers=[PARSER],
    )

    assert event.signal_type == "recovery"
    assert event.state == "up"
    assert (
        event.entity_key
        == "BGP|router-example|default|198.51.100.50"
    )


def test_iosxr_bgp_vrf_uses_same_identity_contract():
    event = normalize_record(
        {
            "hostname": "router-example",
            "vendor_hint": "Cisco",
            "os_family_hint": "IOS XR",
            "message": (
                "%ROUTING-BGP-5-ADJCHANGE : "
                "neighbor 203.0.113.50 Down - "
                "Hold timer expired "
                "(VRF: CUSTOMER_A) "
                "(AS: 64514)"
            ),
        },
        parsers=[PARSER],
    )

    assert event.attributes["vrf"] == "CUSTOMER_A"
    assert (
        event.entity_key
        == "BGP|router-example|CUSTOMER_A|203.0.113.50"
    )


def test_iosxr_bgp_ipv6_uses_same_identity_contract():
    event = normalize_record(
        {
            "hostname": "router-example",
            "vendor_hint": "Cisco",
            "os_family_hint": "IOS XR",
            "message": (
                "%ROUTING-BGP-5-ADJCHANGE : "
                "neighbor 2001:db8::50 Down - "
                "Peer closed the session "
                "(VRF: default)"
            ),
        },
        parsers=[PARSER],
    )

    assert (
        event.entity_key
        == "BGP|router-example|default|2001:db8::50"
    )
    assert event.state == "down"


def test_iosxr_unknown_adjchange_layout_stays_generic():
    event = normalize_record(
        {
            "hostname": "router-example",
            "vendor_hint": "Cisco",
            "os_family_hint": "IOS XR",
            "message": (
                "%ROUTING-BGP-5-ADJCHANGE : "
                "future payload layout not understood"
            ),
        },
        parsers=[PARSER],
    )

    assert event.vendor == "cisco"
    assert event.os_family == "iosxr"
    assert event.event_family == "bgp"
    assert event.protocol == ""
    assert event.state == ""
    assert event.attention_eligible is True
    assert event.attributes["normalization_path"] == "generic"
    assert "parser" not in event.attributes


def test_nxos_hint_cannot_enter_iosxr_parser():
    event = normalize_record(
        {
            "hostname": "router-example",
            "vendor_hint": "Cisco",
            "os_family_hint": "NX-OS",
            "message": (
                "%ROUTING-BGP-5-ADJCHANGE : "
                "neighbor 192.0.2.60 Down - "
                "User clear requested "
                "(VRF: default)"
            ),
        },
        parsers=[PARSER],
    )

    assert event.vendor == "cisco"
    assert event.os_family == "nxos"
    assert event.protocol == ""
    assert event.state == ""
    assert event.attention_eligible is True
    assert event.attributes["normalization_path"] == "generic"
