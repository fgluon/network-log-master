from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from .envelope import extract_event_envelope
from .parsers import DEFAULT_PARSERS, EventParser, dispatch_event
from .schema import NormalizedEvent


def _text(value: Any) -> str:
    """
    Convert an arbitrary source value into text without raising.
    """
    if value is None:
        return ""

    if isinstance(value, str):
        return value

    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")

    try:
        return str(value)
    except Exception:
        return "<unprintable>"


def _nullable_text(value: Any) -> str | None:
    text = _text(value)
    return text if text else None


def _source_port(value: Any) -> int:
    """
    Normalize a source port without allowing malformed input
    to reject the event.
    """
    if value is None or isinstance(value, bool):
        return 0

    try:
        port = int(value)
    except (TypeError, ValueError, OverflowError):
        return 0

    if 0 <= port <= 65535:
        return port

    return 0


def normalize_record(
    record: Any,
    parsers: Iterable[EventParser] | None = None,
) -> NormalizedEvent:
    """
    Convert one source record into the stable NormalizedEvent schema.

    This is deliberately capture-first:

    - unknown records are emitted
    - malformed fields do not reject the event
    - vendor knowledge is not required
    - attention defaults to eligible
    - raw_message is retained whenever available

    Vendor parsers will enrich this generic event later.
    """

    if isinstance(record, Mapping):
        source = record
    else:
        # Even an unexpected non-mapping input becomes an observation.
        source = {
            "message": record,
            "raw_message": record,
        }

    hostname = _text(source.get("hostname"))
    if not hostname:
        hostname = _text(source.get("host"))

    message = _text(source.get("message"))
    raw_message = _text(source.get("raw_message"))

    # Preserve whichever representation exists.
    if not raw_message:
        raw_message = message

    if not message:
        message = raw_message

    envelope = extract_event_envelope(message)

    if not envelope.event_code and raw_message != message:
        envelope = extract_event_envelope(raw_message)

    attributes: dict[str, Any] = {
        "normalization_path": "generic",
    }

    if envelope.code_severity is not None:
        attributes["event_code_severity"] = (
            envelope.code_severity
        )

    event = NormalizedEvent(
        timestamp=_text(source.get("timestamp")),
        ingest_timestamp=_text(source.get("ingest_timestamp")),
        device_timestamp=_nullable_text(
            source.get("device_timestamp")
        ),
        hostname=hostname,
        source_ip=_text(source.get("source_ip")),
        source_port=_source_port(source.get("source_port")),
        facility=_text(source.get("facility")),
        severity=_text(source.get("severity")),
        appname=_text(source.get("appname")),
        message=message,
        raw_message=raw_message,
        parse_status=_text(source.get("parse_status")),
        event_code=envelope.event_code,
        event_family=envelope.event_family,
        attributes=attributes,
    )

    if parsers is None:
        parsers = DEFAULT_PARSERS

    return dispatch_event(event, parsers)
