from __future__ import annotations

from .base import EventParser, ParserResult
from .dispatcher import dispatch_event
from .eos_bgp import EosBgpAdjchangeParser
from .iosxr_bgp import IosXrBgpAdjchangeParser
from .nxos_ethport import NxosEthportStateParser
from .nxos_ospf import NxosOspfRetransmissionsParser


DEFAULT_PARSERS: tuple[EventParser, ...] = (
    EosBgpAdjchangeParser(),
    IosXrBgpAdjchangeParser(),
    NxosEthportStateParser(),
    NxosOspfRetransmissionsParser(),
)


__all__ = [
    "DEFAULT_PARSERS",
    "EventParser",
    "ParserResult",
    "dispatch_event",
]
