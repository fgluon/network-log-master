from __future__ import annotations

import re

from ..schema import NormalizedEvent
from .base import ParserResult


OSPF_EVENT_CODE = "OSPF-5-NBR_RETRANSMISSIONS"
OSPFV3_EVENT_CODE = "OSPFV3-5-NBR_RETRANSMISSIONS"

SUPPORTED_EVENT_CODES = {
    OSPF_EVENT_CODE,
    OSPFV3_EVENT_CODE,
}


OSPF_PROCESS_RE = re.compile(
    r"\b(?P<process>ospf-\d+)\s+\[\d+\]",
    re.IGNORECASE,
)

OSPFV3_PROCESS_RE = re.compile(
    r"\b(?P<process>ospfv3-\d+)\s+\[\d+\]",
    re.IGNORECASE,
)

NEIGHBOR_RE = re.compile(
    r"\bNbr\s+(?P<neighbor>[0-9A-Fa-f:.]+)",
    re.IGNORECASE,
)


class NxosOspfRetransmissionsParser:
    """
    Parse Cisco NX-OS OSPF/OSPFv3 neighbor retransmission
    degradation events.

    Matching is deliberately narrow. Unsupported codes or
    layouts remain capture-first generic observations.
    """

    name = "nxos-ospf-retransmissions"

    def matches(self, event: NormalizedEvent) -> bool:
        if event.vendor != "cisco":
            return False

        if event.os_family != "nxos":
            return False

        if event.event_code not in SUPPORTED_EVENT_CODES:
            return False

        process_re = self._process_re(event)

        if process_re is None:
            return False

        if process_re.search(event.message) is None:
            return False

        if NEIGHBOR_RE.search(event.message) is None:
            return False

        return True

    @staticmethod
    def _process_re(
        event: NormalizedEvent,
    ) -> re.Pattern[str] | None:
        if event.event_code == OSPF_EVENT_CODE:
            return OSPF_PROCESS_RE

        if event.event_code == OSPFV3_EVENT_CODE:
            return OSPFV3_PROCESS_RE

        return None

    def parse(self, event: NormalizedEvent) -> ParserResult:
        process_re = self._process_re(event)

        if process_re is None:
            raise ValueError(
                "Unsupported NX-OS OSPF retransmission event code"
            )

        process_match = process_re.search(event.message)
        neighbor_match = NEIGHBOR_RE.search(event.message)

        if process_match is None or neighbor_match is None:
            raise ValueError(
                "NX-OS OSPF retransmission identity fields not found"
            )

        process = process_match.group("process").lower()
        neighbor = neighbor_match.group("neighbor")
        device = event.hostname or event.source_ip

        if event.event_code == OSPF_EVENT_CODE:
            event_family = "ospf"
        elif event.event_code == OSPFV3_EVENT_CODE:
            event_family = "ospfv3"
        else:
            raise ValueError(
                "Unsupported NX-OS OSPF retransmission event code"
            )

        return ParserResult(
            vendor="cisco",
            os_family="nxos",
            event_family=event_family,
            protocol="ospf",
            signal_type="degradation",
            entity_type="ospf_neighbor",
            entity_key=(
                f"OSPF|{device}|{process}|{neighbor}"
            ),
            state="retransmissions",
            attributes={
                "process": process,
                "neighbor": neighbor,
            },
        )
