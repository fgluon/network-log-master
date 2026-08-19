from network_log_normalizer import normalize_record
from network_log_normalizer.parsers.eos_bgp import (
    EosBgpAdjchangeParser,
)


PARSER = EosBgpAdjchangeParser()


def test_eos_bgp_established_to_idle_is_down():
    event = normalize_record(
        {
            "hostname": "router-example",
            "message": (
                "%BGP-5-ADJCHANGE: "
                "peer 192.0.2.1 "
                "old state Established "
                "event AdminReset "
                "new state Idle"
            ),
        },
        parsers=[PARSER],
    )

    assert event.vendor == "arista"
    assert event.os_family == "eos"
    assert event.protocol == "bgp"
    assert event.signal_type == "state_transition"
    assert event.state == "down"
    assert event.entity_type == "bgp_peer"
    assert (
        event.entity_key
        == "BGP|router-example|default|192.0.2.1"
    )
    assert event.attributes["peer"] == "192.0.2.1"
    assert event.attributes["old_state"] == "Established"
    assert event.attributes["new_state"] == "Idle"
    assert event.attributes["trigger_event"] == "AdminReset"


def test_eos_bgp_openconfirm_to_established_is_recovery():
    event = normalize_record(
        {
            "hostname": "router-example",
            "message": (
                "%BGP-5-ADJCHANGE: "
                "peer 198.51.100.1 "
                "old state OpenConfirm "
                "event RecvKeepAlive "
                "new state Established"
            ),
        },
        parsers=[PARSER],
    )

    assert event.signal_type == "recovery"
    assert event.state == "up"
    assert (
        event.entity_key
        == "BGP|router-example|default|198.51.100.1"
    )


def test_eos_bgp_ipv6_peer_uses_same_identity_contract():
    event = normalize_record(
        {
            "hostname": "router-example",
            "message": (
                "%BGP-5-ADJCHANGE: "
                "peer 2001:db8::1 "
                "old state Established "
                "event AdminReset "
                "new state Idle"
            ),
        },
        parsers=[PARSER],
    )

    assert (
        event.entity_key
        == "BGP|router-example|default|2001:db8::1"
    )
    assert event.state == "down"


def test_eos_bgp_explicit_vrf_is_preserved():
    event = normalize_record(
        {
            "hostname": "router-example",
            "message": (
                "%BGP-5-ADJCHANGE: "
                "peer 192.0.2.20 "
                "VRF CUSTOMER_A "
                "old state Established "
                "event AdminReset "
                "new state Idle"
            ),
        },
        parsers=[PARSER],
    )

    assert event.attributes["vrf"] == "CUSTOMER_A"
    assert (
        event.entity_key
        == "BGP|router-example|CUSTOMER_A|192.0.2.20"
    )


def test_unrecognized_bgp_variant_stays_generic():
    event = normalize_record(
        {
            "hostname": "router-example",
            "message": (
                "%BGP-5-ADJCHANGE: "
                "brand new message format we do not understand"
            ),
        },
        parsers=[PARSER],
    )

    assert event.event_code == "BGP-5-ADJCHANGE"
    assert event.event_family == "bgp"
    assert event.vendor == "unknown"
    assert event.protocol == ""
    assert event.attention_eligible is True
    assert event.attributes["normalization_path"] == "generic"
