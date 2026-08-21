from __future__ import annotations

import re

from ..schema import NormalizedEvent
from .base import ParserResult


ADJ_RE = re.compile(
    r"\bneighbor\s+"
    r"(?P<peer>[0-9A-Fa-f:.]+)\s+"
    r"(?P<state>Up|Down)\b",
    re.IGNORECASE,
)

VRF_RE = re.compile(
    r"\(VRF:\s*(?P<vrf>[^)]+)\)",
    re.IGNORECASE,
)

AS_RE = re.compile(
    r"\(AS:\s*(?P<asn>[0-9]+)\)",
    re.IGNORECASE,
)

DOWN_REASON_RE = re.compile(
    r"\bDown\s*-\s*"
    r"(?P<reason>.*?)"
    r"(?=\s+\(VRF:|\s+\(AS:|$)",
    re.IGNORECASE,
)


class IosXrBgpAdjchangeParser:
    """
    Parse Cisco IOS XR BGP adjacency-change messages.

    Matching is deliberately narrow:
      - Cisco platform identity
      - IOS XR OS identity
      - ROUTING-BGP-5-ADJCHANGE event code
      - recognizable neighbor Up/Down payload

    Variants that do not match remain on the generic capture-first
    path.
    """

    name = "iosxr-bgp-adjchange"

    def matches(self, event: NormalizedEvent) -> bool:
        if event.vendor != "cisco":
            return False

        if event.os_family != "iosxr":
            return False

        if event.event_code != "ROUTING-BGP-5-ADJCHANGE":
            return False

        return ADJ_RE.search(event.message) is not None

    def parse(self, event: NormalizedEvent) -> ParserResult:
        adj_match = ADJ_RE.search(event.message)

        if adj_match is None:
            raise ValueError("IOS XR BGP adjacency fields not found")

        peer = adj_match.group("peer")
        xr_state = adj_match.group("state")

        vrf_match = VRF_RE.search(event.message)
        vrf = (
            vrf_match.group("vrf").strip()
            if vrf_match is not None
            else "default"
        )

        as_match = AS_RE.search(event.message)
        peer_as = (
            as_match.group("asn")
            if as_match is not None
            else ""
        )

        reason_match = DOWN_REASON_RE.search(event.message)
        reason = (
            reason_match.group("reason").strip()
            if reason_match is not None
            else ""
        )

        if xr_state.casefold() == "up":
            state = "up"
            signal_type = "recovery"
        else:
            state = "down"
            signal_type = "state_transition"

        device = event.hostname or event.source_ip
        entity_key = f"BGP|{device}|{vrf}|{peer}"

        attributes = {
            "peer": peer,
            "vrf": vrf,
            "xr_state": xr_state,
        }

        if peer_as:
            attributes["peer_as"] = peer_as

        if reason:
            attributes["reason"] = reason

        return ParserResult(
            vendor="cisco",
            os_family="iosxr",
            event_family="bgp",
            protocol="bgp",
            signal_type=signal_type,
            entity_type="bgp_peer",
            entity_key=entity_key,
            state=state,
            attributes=attributes,
        )
