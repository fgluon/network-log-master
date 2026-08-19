from __future__ import annotations

from .base import EventParser, ParserResult
from .dispatcher import dispatch_event


DEFAULT_PARSERS: tuple[EventParser, ...] = ()


__all__ = [
    "DEFAULT_PARSERS",
    "EventParser",
    "ParserResult",
    "dispatch_event",
]
