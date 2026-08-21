from copy import deepcopy

from network_log_normalizer import normalize_record


FIXTURES = [
    {
        "name": "eos_bgp_down",
        "record": {
            "timestamp": "2026-01-01T00:00:00Z",
            "ingest_timestamp": "2026-01-01T00:00:01Z",
            "hostname": "eos-example",
            "source_ip": "192.0.2.10",
            "vendor_hint": "Arista Networks",
            "os_family_hint": "Arista EOS",
            "message": (
                "%BGP-5-ADJCHANGE: "
                "peer 198.51.100.10 "
                "(VRF default AS 64512) "
                "old state Established "
                "event AdminReset "
                "new state Idle"
            ),
        },
        "expected": {
            "event_family": "bgp",
            "vendor": "arista",
            "os_family": "eos",
            "protocol": "bgp",
            "signal_type": "state_transition",
            "entity_type": "bgp_peer",
            "state": "down",
        },
    },
    {
        "name": "eos_bgp_up",
        "record": {
            "timestamp": "2026-01-01T00:01:00Z",
            "ingest_timestamp": "2026-01-01T00:01:01Z",
            "hostname": "eos-example",
            "source_ip": "192.0.2.10",
            "vendor_hint": "Arista Networks",
            "os_family_hint": "Arista EOS",
            "message": (
                "%BGP-5-ADJCHANGE: "
                "peer 198.51.100.10 "
                "(VRF default AS 64512) "
                "old state OpenConfirm "
                "event RecvKeepAlive "
                "new state Established"
            ),
        },
        "expected": {
            "event_family": "bgp",
            "vendor": "arista",
            "os_family": "eos",
            "protocol": "bgp",
            "signal_type": "recovery",
            "entity_type": "bgp_peer",
            "state": "up",
        },
    },
    {
        "name": "iosxr_bgp_down",
        "record": {
            "timestamp": "2026-01-01T00:02:00Z",
            "ingest_timestamp": "2026-01-01T00:02:01Z",
            "hostname": "iosxr-example",
            "source_ip": "192.0.2.20",
            "vendor_hint": "Cisco",
            "os_family_hint": "IOS XR",
            "message": (
                "%ROUTING-BGP-5-ADJCHANGE : "
                "neighbor 198.51.100.20 Down - "
                "Hold timer expired "
                "(VRF: default) "
                "(AS: 64513)"
            ),
        },
        "expected": {
            "event_family": "bgp",
            "vendor": "cisco",
            "os_family": "iosxr",
            "protocol": "bgp",
            "signal_type": "state_transition",
            "entity_type": "bgp_peer",
            "state": "down",
        },
    },
    {
        "name": "iosxr_bgp_up",
        "record": {
            "timestamp": "2026-01-01T00:03:00Z",
            "ingest_timestamp": "2026-01-01T00:03:01Z",
            "hostname": "iosxr-example",
            "source_ip": "192.0.2.20",
            "vendor_hint": "Cisco",
            "os_family_hint": "IOS XR",
            "message": (
                "%ROUTING-BGP-5-ADJCHANGE : "
                "neighbor 198.51.100.20 Up "
                "(VRF: default) "
                "(AS: 64513)"
            ),
        },
        "expected": {
            "event_family": "bgp",
            "vendor": "cisco",
            "os_family": "iosxr",
            "protocol": "bgp",
            "signal_type": "recovery",
            "entity_type": "bgp_peer",
            "state": "up",
        },
    },
    {
        "name": "nxos_ethport_down",
        "record": {
            "timestamp": "2026-01-01T00:04:00Z",
            "ingest_timestamp": "2026-01-01T00:04:01Z",
            "hostname": "nxos-example",
            "source_ip": "192.0.2.30",
            "vendor_hint": "Cisco",
            "os_family_hint": "NX-OS",
            "message": (
                "%ETHPORT-5-IF_DOWN_LINK_FAILURE: "
                "Interface Ethernet1/10 is down "
                "(Link failure)"
            ),
        },
        "expected": {
            "event_family": "ethport",
            "vendor": "cisco",
            "os_family": "nxos",
            "protocol": "ethernet",
            "signal_type": "state_transition",
            "entity_type": "interface",
            "state": "down",
        },
    },
    {
        "name": "nxos_ethport_up",
        "record": {
            "timestamp": "2026-01-01T00:05:00Z",
            "ingest_timestamp": "2026-01-01T00:05:01Z",
            "hostname": "nxos-example",
            "source_ip": "192.0.2.30",
            "vendor_hint": "Cisco",
            "os_family_hint": "NX-OS",
            "message": (
                "%ETHPORT-5-IF_UP: "
                "Interface Ethernet1/10 is up in mode trunk"
            ),
        },
        "expected": {
            "event_family": "ethport",
            "vendor": "cisco",
            "os_family": "nxos",
            "protocol": "ethernet",
            "signal_type": "recovery",
            "entity_type": "interface",
            "state": "up",
        },
    },
    {
        "name": "nxos_ospf",
        "record": {
            "timestamp": "2026-01-01T00:06:00Z",
            "ingest_timestamp": "2026-01-01T00:06:01Z",
            "hostname": "nxos-example",
            "source_ip": "192.0.2.30",
            "vendor_hint": "Cisco",
            "os_family_hint": "NX-OS",
            "message": (
                "%OSPF-5-NBR_RETRANSMISSIONS: "
                "ospf-1 [1234] Nbr 198.51.100.30 "
                "re-transmits routing information"
            ),
        },
        "expected": {
            "event_family": "ospf",
            "vendor": "cisco",
            "os_family": "nxos",
            "protocol": "ospf",
            "signal_type": "degradation",
            "entity_type": "ospf_neighbor",
            "state": "retransmissions",
        },
    },
    {
        "name": "nxos_ospfv3",
        "record": {
            "timestamp": "2026-01-01T00:07:00Z",
            "ingest_timestamp": "2026-01-01T00:07:01Z",
            "hostname": "nxos-example",
            "source_ip": "192.0.2.30",
            "vendor_hint": "Cisco",
            "os_family_hint": "NX-OS",
            "message": (
                "%OSPFV3-5-NBR_RETRANSMISSIONS: "
                "ospfv3-1 [5678] Nbr 2001:db8::30 "
                "re-originates routing information"
            ),
        },
        "expected": {
            "event_family": "ospfv3",
            "vendor": "cisco",
            "os_family": "nxos",
            "protocol": "ospf",
            "signal_type": "degradation",
            "entity_type": "ospf_neighbor",
            "state": "retransmissions",
        },
    },
    {
        "name": "unknown_source_stays_generic",
        "record": {
            "timestamp": "2026-01-01T00:08:00Z",
            "ingest_timestamp": "2026-01-01T00:08:01Z",
            "hostname": "unknown-example",
            "source_ip": "192.0.2.40",
            "message": (
                "%BGP-5-ADJCHANGE: "
                "peer 198.51.100.40 "
                "old state Established "
                "event AdminReset "
                "new state Idle"
            ),
        },
        "expected": {
            "event_family": "bgp",
            "vendor": "unknown",
            "os_family": "unknown",
            "protocol": "",
            "signal_type": "observation",
            "entity_type": "unknown",
            "state": "",
        },
    },
]


def replay():
    return [
        normalize_record(
            deepcopy(fixture["record"])
        ).to_dict()
        for fixture in FIXTURES
    ]


def test_sanitized_replay_semantics():
    output = replay()

    assert len(output) == len(FIXTURES)

    for fixture, event in zip(
        FIXTURES,
        output,
        strict=True,
    ):
        for field, expected in fixture["expected"].items():
            assert event[field] == expected, (
                fixture["name"],
                field,
                event[field],
                expected,
            )


def test_repeated_replay_is_deterministic():
    first = replay()
    second = replay()

    assert first == second
