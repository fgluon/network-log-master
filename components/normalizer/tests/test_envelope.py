from network_log_normalizer.envelope import (
    extract_event_envelope,
)


def test_simple_bgp_event_code():
    envelope = extract_event_envelope(
        "%BGP-5-ADJCHANGE: peer changed state"
    )

    assert envelope.event_code == "BGP-5-ADJCHANGE"
    assert envelope.event_family == "bgp"
    assert envelope.code_severity == 5


def test_multi_component_routing_bgp_code():
    envelope = extract_event_envelope(
        "%ROUTING-BGP-5-ADJCHANGE : neighbor Down"
    )

    assert (
        envelope.event_code
        == "ROUTING-BGP-5-ADJCHANGE"
    )
    assert envelope.event_family == "bgp"
    assert envelope.code_severity == 5


def test_ethport_event_code():
    envelope = extract_event_envelope(
        "%ETHPORT-5-IF_DOWN_LINK_FAILURE: interface down"
    )

    assert (
        envelope.event_code
        == "ETHPORT-5-IF_DOWN_LINK_FAILURE"
    )
    assert envelope.event_family == "ethport"
    assert envelope.code_severity == 5


def test_icmpv6_event_code():
    envelope = extract_event_envelope(
        "%ICMPV6-3-ND_LOG: neighbor discovery event"
    )

    assert envelope.event_code == "ICMPV6-3-ND_LOG"
    assert envelope.event_family == "icmpv6"
    assert envelope.code_severity == 3


def test_unknown_code_is_still_structured_generically():
    envelope = extract_event_envelope(
        "%FUTURETHING-2-SOMETHING_NEW: unknown event"
    )

    assert (
        envelope.event_code
        == "FUTURETHING-2-SOMETHING_NEW"
    )
    assert envelope.event_family == "futurething"
    assert envelope.code_severity == 2


def test_non_matching_message_is_not_an_error():
    envelope = extract_event_envelope(
        "plain message with no event envelope"
    )

    assert envelope.event_code == ""
    assert envelope.event_family == "unknown"
    assert envelope.code_severity is None
