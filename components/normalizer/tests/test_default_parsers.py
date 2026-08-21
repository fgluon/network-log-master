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


def test_default_registry_applies_nxos_ethport_parser():
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
        }
    )

    assert event.vendor == "cisco"
    assert event.os_family == "nxos"
    assert event.event_family == "ethport"
    assert event.signal_type == "state_transition"
    assert event.state == "down"
    assert event.entity_type == "interface"
    assert event.attributes["parser"] == "nxos-ethport-state"
    assert (
        event.entity_key
        == "INTERFACE|switch-example|Ethernet1/10"
    )


def test_default_registry_applies_nxos_fex_interface():
    event = normalize_record(
        {
            "hostname": "switch-example",
            "vendor_hint": "Cisco",
            "os_family_hint": "NX-OS",
            "message": (
                "%ETHPORT-5-IF_UP: "
                "Interface Ethernet101/1/10 is up"
            ),
        }
    )

    assert event.state == "up"
    assert event.signal_type == "recovery"
    assert event.attributes["interface"] == "Ethernet101/1/10"
    assert (
        event.entity_key
        == "INTERFACE|switch-example|Ethernet101/1/10"
    )


def test_default_registry_keeps_unknown_nxos_ethport_generic():
    event = normalize_record(
        {
            "hostname": "switch-example",
            "vendor_hint": "Cisco",
            "os_family_hint": "NX-OS",
            "message": (
                "%ETHPORT-5-NEW_FUTURE_EVENT: "
                "Interface Ethernet1/20 changed somehow"
            ),
        }
    )

    assert event.vendor == "cisco"
    assert event.os_family == "nxos"
    assert event.event_family == "ethport"
    assert event.state == ""
    assert event.attention_eligible is True
    assert event.attributes["normalization_path"] == "generic"
    assert "parser" not in event.attributes


def test_default_registry_applies_nxos_ospf_retransmissions():
    event = normalize_record(
        {
            "hostname": "switch-example",
            "vendor_hint": "Cisco",
            "os_family_hint": "NX-OS",
            "message": (
                "%OSPF-5-NBR_RETRANSMISSIONS: "
                "ospf-1 [1234] Nbr 192.0.2.60 "
                "re-transmits routing information"
            ),
        }
    )

    assert event.event_family == "ospf"
    assert event.protocol == "ospf"
    assert event.signal_type == "degradation"
    assert event.state == "retransmissions"
    assert event.attributes["parser"] == "nxos-ospf-retransmissions"
    assert (
        event.entity_key
        == "OSPF|switch-example|ospf-1|192.0.2.60"
    )


def test_default_registry_applies_nxos_ospfv3_retransmissions():
    event = normalize_record(
        {
            "hostname": "switch-example",
            "vendor_hint": "Cisco",
            "os_family_hint": "NX-OS",
            "message": (
                "%OSPFV3-5-NBR_RETRANSMISSIONS: "
                "ospfv3-2 [5678] Nbr 2001:db8::60 "
                "re-originates routing information"
            ),
        }
    )

    assert event.event_family == "ospfv3"
    assert event.protocol == "ospf"
    assert event.signal_type == "degradation"
    assert event.state == "retransmissions"
    assert event.attributes["parser"] == "nxos-ospf-retransmissions"
    assert (
        event.entity_key
        == "OSPF|switch-example|ospfv3-2|2001:db8::60"
    )
