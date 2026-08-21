from __future__ import annotations

import re

from ..schema import NormalizedEvent
from .base import ParserResult


DOWN_EVENT_CODE = "ETHPORT-5-IF_DOWN_LINK_FAILURE"
UP_EVENT_CODE = "ETHPORT-5-IF_UP"


DOWN_RE = re.compile(
    r"\bInterface\s+"
    r"(?P<interface>[A-Za-z0-9./:-]+)\s+"
    r"is\s+down\s*"
    r"\((?P<reason>[^)]*)\)",
    re.IGNORECASE,
)

UP_RE = re.compile(
    r"\bInterface\s+"
    r"(?P<interface>[A-Za-z0-9./:-]+)\s+"
    r"is\s+up"
    r"(?:\s+in\s+(?P<context>.+?))?"
    r"\s*$",
    re.IGNORECASE,
)


class NxosEthportStateParser:
    """
    Parse a narrow set of Cisco NX-OS ETHPORT interface
    state transitions.

    Matching is deliberately narrow. Other ETHPORT events remain
    capture-first generic observations until explicitly supported.
    """

    name = "nxos-ethport-state"

    def matches(self, event: NormalizedEvent) -> bool:
        if event.vendor != "cisco":
            return False

        if event.os_family != "nxos":
            return False

        if event.event_code == DOWN_EVENT_CODE:
            return DOWN_RE.search(event.message) is not None

        if event.event_code == UP_EVENT_CODE:
            return UP_RE.search(event.message) is not None

        return False

    def parse(self, event: NormalizedEvent) -> ParserResult:
        state: str
        signal_type: str
        interface: str
        attributes: dict[str, str]

        if event.event_code == DOWN_EVENT_CODE:
            match = DOWN_RE.search(event.message)

            if match is None:
                raise ValueError(
                    "NX-OS ETHPORT down fields not found"
                )

            interface = match.group("interface")
            reason = match.group("reason").strip()
            state = "down"
            signal_type = "state_transition"
            attributes = {
                "interface": interface,
                "reason": reason,
            }

        elif event.event_code == UP_EVENT_CODE:
            match = UP_RE.search(event.message)

            if match is None:
                raise ValueError(
                    "NX-OS ETHPORT up fields not found"
                )

            interface = match.group("interface")
            context = (match.group("context") or "").strip()
            state = "up"
            signal_type = "recovery"
            attributes = {
                "interface": interface,
            }

            if context:
                attributes["operational_context"] = context

        else:
            raise ValueError(
                "Unsupported NX-OS ETHPORT event code"
            )

        device = event.hostname or event.source_ip
        entity_key = f"INTERFACE|{device}|{interface}"

        return ParserResult(
            vendor="cisco",
            os_family="nxos",
            event_family="ethport",
            protocol="ethernet",
            signal_type=signal_type,
            entity_type="interface",
            entity_key=entity_key,
            state=state,
            attributes=attributes,
        )
