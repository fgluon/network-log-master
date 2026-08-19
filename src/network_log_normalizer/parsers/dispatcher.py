from __future__ import annotations

from collections.abc import Iterable

from ..schema import NormalizedEvent
from .base import EventParser, ParserResult


def _apply_result(
    event: NormalizedEvent,
    parser_name: str,
    result: ParserResult,
) -> NormalizedEvent:
    event.vendor = result.vendor
    event.os_family = result.os_family

    if result.event_family is not None:
        event.event_family = result.event_family

    if result.protocol:
        event.protocol = result.protocol

    if result.signal_type is not None:
        event.signal_type = result.signal_type

    if result.entity_type is not None:
        event.entity_type = result.entity_type

    if result.entity_key:
        event.entity_key = result.entity_key

    if result.state:
        event.state = result.state

    event.attributes.update(result.attributes)
    event.attributes["parser"] = parser_name
    event.attributes["normalization_path"] = "parser"

    return event


def dispatch_event(
    event: NormalizedEvent,
    parsers: Iterable[EventParser],
) -> NormalizedEvent:
    """
    Run parsers in order.

    The first matching parser wins.

    Fail-open contract:
      - no match returns the generic event
      - parser exceptions do not drop the event
      - raw source fields are never replaced by ParserResult
    """

    for parser in parsers:
        try:
            if not parser.matches(event):
                continue

            result = parser.parse(event)

        except Exception as exc:
            errors = event.attributes.setdefault(
                "parser_errors",
                [],
            )
            errors.append(
                {
                    "parser": getattr(
                        parser,
                        "name",
                        parser.__class__.__name__,
                    ),
                    "error_type": exc.__class__.__name__,
                }
            )
            continue

        return _apply_result(
            event,
            parser.name,
            result,
        )

    return event
