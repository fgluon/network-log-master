from __future__ import annotations

from .base import EventParser, ParserResult
from .dispatcher import dispatch_event
from .eos_bgp import EosBgpAdjchangeParser


DEFAULT_PARSERS: tuple[EventParser, ...] = (
    EosBgpAdjchangeParser(),
)


__all__ = [
    "DEFAULT_PARSERS",
    "EventParser",
    "ParserResult",
    "dispatch_event",
]
