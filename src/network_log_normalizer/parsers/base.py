from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

from ..schema import NormalizedEvent


@dataclass(slots=True)
class ParserResult:
    """
    Enrichment returned by a vendor/event parser.

    Parsers may enrich an event, but they do not control capture
    or suppression policy.
    """

    vendor: str = "unknown"
    os_family: str = "unknown"
    event_family: str | None = None
    protocol: str = ""
    signal_type: str | None = None
    entity_type: str | None = None
    entity_key: str = ""
    state: str = ""
    attributes: dict[str, Any] = field(default_factory=dict)


class EventParser(Protocol):
    name: str

    def matches(self, event: NormalizedEvent) -> bool:
        ...

    def parse(self, event: NormalizedEvent) -> ParserResult:
        ...
