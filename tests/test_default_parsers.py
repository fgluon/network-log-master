from network_log_normalizer import normalize_record


def test_default_registry_applies_eos_bgp_parser():
    event = normalize_record(
        {
            "hostname": "router-example",
            "vendor_hint": "Arista Networks",
            "os_family_hint": "Arista EOS",
            "message": (
                "%BGP-5-ADJCHANGE: "
                "peer 192.0.2.40 "
                "old state Established "
                "event AdminReset "
                "new state Idle"
            ),
        }
    )

    assert event.vendor == "arista"
    assert event.os_family == "eos"
    assert event.protocol == "bgp"
    assert event.signal_type == "state_transition"
    assert event.state == "down"
    assert event.attributes["parser"] == "eos-bgp-adjchange"
    assert (
        event.entity_key
        == "BGP|router-example|default|192.0.2.40"
    )


def test_default_registry_rejects_cisco_from_eos_parser():
    event = normalize_record(
        {
            "hostname": "router-example",
            "vendor_hint": "Cisco",
            "os_family_hint": "NX-OS",
            "message": (
                "%BGP-5-ADJCHANGE: "
                "peer 198.51.100.40 "
                "old state Established "
                "event AdminReset "
                "new state Idle"
            ),
        }
    )

    assert event.vendor == "cisco"
    assert event.os_family == "nxos"
    assert event.event_family == "bgp"
    assert event.protocol == ""
    assert event.state == ""
    assert event.attention_eligible is True
    assert event.attributes["normalization_path"] == "generic"
    assert "parser" not in event.attributes


def test_default_registry_keeps_unknown_eos_variant_generic():
    event = normalize_record(
        {
            "hostname": "router-example",
            "vendor_hint": "Arista Networks",
            "os_family_hint": "Arista EOS",
            "message": (
                "%BGP-5-ADJCHANGE: "
                "future message layout not understood"
            ),
        }
    )

    assert event.vendor == "arista"
    assert event.os_family == "eos"
    assert event.event_family == "bgp"
    assert event.protocol == ""
    assert event.attention_eligible is True
    assert event.attributes["normalization_path"] == "generic"
    assert "parser" not in event.attributes


def test_default_registry_applies_iosxr_bgp_parser():
    event = normalize_record(
        {
            "hostname": "router-example",
            "vendor_hint": "Cisco",
            "os_family_hint": "IOS XR",
            "message": (
                "%ROUTING-BGP-5-ADJCHANGE : "
                "neighbor 192.0.2.70 Down - "
                "User clear requested "
                "(VRF: default) "
                "(AS: 64520)"
            ),
        }
    )

    assert event.vendor == "cisco"
    assert event.os_family == "iosxr"
    assert event.protocol == "bgp"
    assert event.signal_type == "state_transition"
    assert event.state == "down"
    assert event.attributes["parser"] == "iosxr-bgp-adjchange"
    assert (
        event.entity_key
        == "BGP|router-example|default|192.0.2.70"
    )


def test_default_registry_keeps_unknown_iosxr_variant_generic():
    event = normalize_record(
        {
            "hostname": "router-example",
            "vendor_hint": "Cisco",
            "os_family_hint": "IOS XR",
            "message": (
                "%ROUTING-BGP-5-ADJCHANGE : "
                "future payload layout not understood"
            ),
        }
    )

    assert event.vendor == "cisco"
    assert event.os_family == "iosxr"
    assert event.event_family == "bgp"
    assert event.protocol == ""
    assert event.state == ""
    assert event.attention_eligible is True
    assert event.attributes["normalization_path"] == "generic"
    assert "parser" not in event.attributes


def test_default_registry_rejects_nxos_from_iosxr_parser():
    event = normalize_record(
        {
            "hostname": "router-example",
            "vendor_hint": "Cisco",
            "os_family_hint": "NX-OS",
            "message": (
                "%ROUTING-BGP-5-ADJCHANGE : "
                "neighbor 198.51.100.70 Down - "
                "User clear requested "
                "(VRF: default)"
            ),
        }
    )

    assert event.vendor == "cisco"
    assert event.os_family == "nxos"
    assert event.event_family == "bgp"
    assert event.protocol == ""
    assert event.state == ""
    assert event.attention_eligible is True
    assert event.attributes["normalization_path"] == "generic"
    assert "parser" not in event.attributes
