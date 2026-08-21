from __future__ import annotations

import re

from ..schema import NormalizedEvent
from .base import ParserResult


PEER_RE = re.compile(
    r"\bpeer\s+(?P<peer>[0-9A-Fa-f:.]+)",
    re.IGNORECASE,
)

STATE_RE = re.compile(
    r"\bold\s+state\s+(?P<old_state>[A-Za-z0-9_-]+)"
    r".*?"
    r"\bnew\s+state\s+(?P<new_state>[A-Za-z0-9_-]+)",
    re.IGNORECASE,
)

EVENT_RE = re.compile(
    r"\bevent\s+(?P<trigger>[A-Za-z0-9_-]+)",
    re.IGNORECASE,
)

VRF_RE = re.compile(
    r"\bVRF(?:\s*[:=]\s*|\s+)(?P<vrf>[A-Za-z0-9_.:-]+)",
    re.IGNORECASE,
)

VRF_AS_RE = re.compile(
    r"\bVRF\s+(?P<vrf>[A-Za-z0-9_.:-]+)"
    r"\s+AS\s+(?P<peer_as>\d+)\b",
    re.IGNORECASE,
)


class EosBgpAdjchangeParser:
    """
    Parse Arista EOS BGP adjacency state-change messages.

    Matching is intentionally narrow. Unknown or variant BGP messages
    remain on the generic capture-first path.
    """

    name = "eos-bgp-adjchange"

    def matches(self, event: NormalizedEvent) -> bool:
        if event.vendor != "arista":
            return False

        if event.os_family != "eos":
            return False

        if event.event_code != "BGP-5-ADJCHANGE":
            return False

        return (
            PEER_RE.search(event.message) is not None
            and STATE_RE.search(event.message) is not None
        )

    def parse(self, event: NormalizedEvent) -> ParserResult:
        peer_match = PEER_RE.search(event.message)
        state_match = STATE_RE.search(event.message)

        if peer_match is None or state_match is None:
            raise ValueError("EOS BGP ADJCHANGE fields not found")

        peer = peer_match.group("peer")
        old_state = state_match.group("old_state")
        new_state = state_match.group("new_state")

        vrf_as_match = VRF_AS_RE.search(event.message)

        if vrf_as_match is not None:
            vrf = vrf_as_match.group("vrf")
            peer_as = vrf_as_match.group("peer_as")
        else:
            vrf_match = VRF_RE.search(event.message)
            vrf = (
                vrf_match.group("vrf")
                if vrf_match is not None
                else "default"
            )
            peer_as = ""

        event_match = EVENT_RE.search(event.message)
        trigger = (
            event_match.group("trigger")
            if event_match is not None
            else ""
        )

        old_folded = old_state.casefold()
        new_folded = new_state.casefold()

        state = new_folded
        signal_type = "observation"

        if new_folded == "established":
            state = "up"
            signal_type = "recovery"
        elif (
            old_folded == "established"
            and new_folded != "established"
        ):
            state = "down"
            signal_type = "state_transition"

        device = event.hostname or event.source_ip
        entity_key = f"BGP|{device}|{vrf}|{peer}"

        return ParserResult(
            vendor="arista",
            os_family="eos",
            event_family="bgp",
            protocol="bgp",
            signal_type=signal_type,
            entity_type="bgp_peer",
            entity_key=entity_key,
            state=state,
            attributes={
                "peer": peer,
                "vrf": vrf,
                "old_state": old_state,
                "new_state": new_state,
                "trigger_event": trigger,
                **({"peer_as": peer_as} if peer_as else {}),
            },
        )
