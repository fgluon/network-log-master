from network_log_normalizer import normalize_record


def test_unknown_event_is_emitted_capture_first():
    event = normalize_record(
        {
            "timestamp": "2026-08-19T12:00:00Z",
            "hostname": "router-example",
            "source_ip": "192.0.2.10",
            "source_port": 514,
            "severity": "warning",
            "message": "%MYSTERYTHING-3-EVENT: something happened",
            "raw_message": (
                "<132>%MYSTERYTHING-3-EVENT: something happened"
            ),
            "parse_status": "parsed",
        }
    )

    assert event.hostname == "router-example"
    assert event.source_ip == "192.0.2.10"
    assert event.source_port == 514
    assert event.vendor == "unknown"
    assert event.event_code == "MYSTERYTHING-3-EVENT"
    assert event.event_family == "mysterything"
    assert event.attributes["event_code_severity"] == 3
    assert event.entity_type == "unknown"
    assert event.signal_type == "observation"
    assert event.attention_eligible is True
    assert event.suppression_rule_id is None
    assert event.attributes["normalization_path"] == "generic"
    assert (
        event.raw_message
        == "<132>%MYSTERYTHING-3-EVENT: something happened"
    )


def test_host_is_used_when_hostname_is_missing():
    event = normalize_record(
        {
            "host": "switch-example",
            "message": "test message",
        }
    )

    assert event.hostname == "switch-example"
    assert event.message == "test message"
    assert event.raw_message == "test message"


def test_malformed_field_types_do_not_drop_event():
    event = normalize_record(
        {
            "hostname": 12345,
            "source_ip": None,
            "source_port": "not-a-port",
            "message": {"unexpected": "object"},
            "raw_message": b"binary-ish input",
        }
    )

    assert event.hostname == "12345"
    assert event.source_ip == ""
    assert event.source_port == 0
    assert "unexpected" in event.message
    assert event.raw_message == "binary-ish input"
    assert event.attention_eligible is True


def test_non_mapping_input_is_still_emitted():
    event = normalize_record(
        "%UNKNOWN-1-ODDTHING: unexpected standalone input"
    )

    assert (
        event.message
        == "%UNKNOWN-1-ODDTHING: unexpected standalone input"
    )
    assert event.raw_message == event.message
    assert event.vendor == "unknown"
    assert event.attention_eligible is True


def test_empty_record_is_still_a_valid_observation():
    event = normalize_record({})

    assert event.message == ""
    assert event.raw_message == ""
    assert event.vendor == "unknown"
    assert event.event_family == "unknown"
    assert event.attention_eligible is True


def test_generic_normalizer_extracts_event_envelope():
    event = normalize_record(
        {
            "message": (
                "%ROUTING-BGP-5-ADJCHANGE: "
                "neighbor changed state"
            ),
        }
    )

    assert event.event_code == "ROUTING-BGP-5-ADJCHANGE"
    assert event.event_family == "bgp"
    assert event.attributes["event_code_severity"] == 5
    assert event.vendor == "unknown"
    assert event.attention_eligible is True


def test_unknown_future_family_remains_attention_eligible():
    event = normalize_record(
        {
            "message": (
                "%FUTURETHING-2-SOMETHING_NEW: "
                "new event type"
            ),
        }
    )

    assert (
        event.event_code
        == "FUTURETHING-2-SOMETHING_NEW"
    )
    assert event.event_family == "futurething"
    assert event.vendor == "unknown"
    assert event.attention_eligible is True


def test_normalizer_can_apply_injected_parser():
    from network_log_normalizer.parsers import ParserResult

    class TestParser:
        name = "test-parser"

        def matches(self, event):
            return event.event_family == "bgp"

        def parse(self, event):
            return ParserResult(
                vendor="test-vendor",
                os_family="test-os",
                protocol="bgp",
            )

    event = normalize_record(
        {
            "message": "%BGP-5-ADJCHANGE: peer down",
        },
        parsers=[TestParser()],
    )

    assert event.vendor == "test-vendor"
    assert event.os_family == "test-os"
    assert event.protocol == "bgp"
    assert event.attributes["parser"] == "test-parser"


def test_normalizer_survives_injected_broken_parser():
    class BrokenParser:
        name = "broken-test-parser"

        def matches(self, event):
            return True

        def parse(self, event):
            raise RuntimeError("simulated failure")

    event = normalize_record(
        {
            "message": "%MYSTERYTHING-3-EVENT: important event",
        },
        parsers=[BrokenParser()],
    )

    assert event.event_code == "MYSTERYTHING-3-EVENT"
    assert event.attention_eligible is True
    assert event.attributes["parser_errors"][0]["parser"] == (
        "broken-test-parser"
    )


def test_explicit_platform_hint_is_preserved():
    event = normalize_record(
        {
            "vendor_hint": "Arista Networks",
            "os_family_hint": "Arista EOS",
            "message": "%BGP-5-ADJCHANGE: unknown variant",
        }
    )

    assert event.vendor == "arista"
    assert event.os_family == "eos"
    assert event.attributes["vendor_hint"] == "Arista Networks"
    assert event.attributes["os_family_hint"] == "Arista EOS"
    assert event.attention_eligible is True


def test_untrusted_platform_hint_remains_unknown():
    event = normalize_record(
        {
            "vendor_hint": "FutureVendor",
            "os_family_hint": "FutureOS",
            "message": "%FUTURETHING-3-EVENT: important event",
        }
    )

    assert event.vendor == "unknown"
    assert event.os_family == "unknown"
    assert event.attributes["vendor_hint"] == "FutureVendor"
    assert event.attributes["os_family_hint"] == "FutureOS"
    assert event.event_code == "FUTURETHING-3-EVENT"
    assert event.attention_eligible is True
