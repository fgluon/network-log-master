from network_log_normalizer.schema import NormalizedEvent, SCHEMA_VERSION


def test_unknown_event_is_capture_first_by_default():
    event = NormalizedEvent(
        timestamp="2026-08-19T17:00:00Z",
        hostname="unknown-switch",
        source_ip="192.0.2.10",
        message="completely new vendor event",
        raw_message="<raw> completely new vendor event",
    )

    data = event.to_dict()

    assert data["schema_version"] == SCHEMA_VERSION
    assert data["vendor"] == "unknown"
    assert data["event_family"] == "unknown"
    assert data["entity_type"] == "unknown"
    assert data["signal_type"] == "observation"
    assert data["attention_eligible"] is True
    assert data["suppression_rule_id"] is None
    assert data["raw_message"] == "<raw> completely new vendor event"


def test_explicit_suppression_must_be_visible():
    event = NormalizedEvent(
        message="known noisy event",
        raw_message="known noisy event",
        attention_eligible=False,
        suppression_rule_id="TEST-KNOWN-NOISE",
    )

    data = event.to_dict()

    assert data["attention_eligible"] is False
    assert data["suppression_rule_id"] == "TEST-KNOWN-NOISE"
