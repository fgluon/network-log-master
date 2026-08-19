from network_log_normalizer.parsers import (
    ParserResult,
    dispatch_event,
)
from network_log_normalizer.schema import NormalizedEvent


class NeverMatches:
    name = "never"

    def matches(self, event):
        return False

    def parse(self, event):
        raise AssertionError("parse should not be called")


class ExampleParser:
    name = "example"

    def matches(self, event):
        return event.event_family == "bgp"

    def parse(self, event):
        return ParserResult(
            vendor="example-vendor",
            os_family="example-os",
            protocol="bgp",
            entity_type="bgp_peer",
            entity_key="BGP|router-example|default|192.0.2.1",
            state="down",
            attributes={
                "peer": "192.0.2.1",
            },
        )


class BrokenParser:
    name = "broken"

    def matches(self, event):
        return True

    def parse(self, event):
        raise ValueError("simulated parser failure")


def test_no_matching_parser_keeps_generic_event():
    event = NormalizedEvent(
        message="unknown event",
        raw_message="unknown event",
    )

    result = dispatch_event(
        event,
        [NeverMatches()],
    )

    assert result is event
    assert result.vendor == "unknown"
    assert result.attention_eligible is True


def test_matching_parser_enriches_event():
    event = NormalizedEvent(
        hostname="router-example",
        event_family="bgp",
        message="peer down",
        raw_message="peer down",
    )

    result = dispatch_event(
        event,
        [ExampleParser()],
    )

    assert result.vendor == "example-vendor"
    assert result.os_family == "example-os"
    assert result.protocol == "bgp"
    assert result.entity_type == "bgp_peer"
    assert (
        result.entity_key
        == "BGP|router-example|default|192.0.2.1"
    )
    assert result.state == "down"
    assert result.attributes["peer"] == "192.0.2.1"
    assert result.attributes["parser"] == "example"
    assert result.attributes["normalization_path"] == "parser"


def test_parser_cannot_remove_raw_message():
    event = NormalizedEvent(
        event_family="bgp",
        message="parsed message",
        raw_message="<raw> parsed message",
    )

    result = dispatch_event(
        event,
        [ExampleParser()],
    )

    assert result.raw_message == "<raw> parsed message"


def test_broken_parser_does_not_drop_event():
    event = NormalizedEvent(
        message="important unknown event",
        raw_message="important unknown event",
    )

    result = dispatch_event(
        event,
        [BrokenParser()],
    )

    assert result is event
    assert result.message == "important unknown event"
    assert result.attention_eligible is True
    assert result.attributes["parser_errors"] == [
        {
            "parser": "broken",
            "error_type": "ValueError",
        }
    ]


def test_dispatch_continues_after_broken_parser():
    event = NormalizedEvent(
        event_family="bgp",
        message="peer down",
        raw_message="peer down",
    )

    result = dispatch_event(
        event,
        [
            BrokenParser(),
            ExampleParser(),
        ],
    )

    assert result.vendor == "example-vendor"
    assert result.attributes["parser"] == "example"
    assert result.attributes["parser_errors"][0][
        "parser"
    ] == "broken"
