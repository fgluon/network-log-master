from __future__ import annotations

import re
from dataclasses import dataclass


EVENT_CODE_RE = re.compile(
    r"%(?P<code>[A-Za-z0-9_.]+(?:-[A-Za-z0-9_.]+)+)"
)

SEVERITY_VALUES = {str(value) for value in range(8)}

SLOT_TOKEN_RE = re.compile(
    r"^(?:SLOT|LC|RP|RSP)\d*$",
    re.IGNORECASE,
)


@dataclass(slots=True, frozen=True)
class EventEnvelope:
    event_code: str = ""
    event_family: str = "unknown"
    code_severity: int | None = None


def _family_from_code(
    event_code: str,
    severity_index: int | None,
) -> str:
    """
    Derive a best-effort subsystem/family without requiring
    vendor-specific knowledge.

    For:

      ROUTING-BGP-5-ADJCHANGE

    the last meaningful token before the numeric severity is BGP.

    For:

      ETHPORT-5-IF_DOWN_LINK_FAILURE

    it is ETHPORT.

    Slot/chassis-position tokens are skipped because they describe
    location rather than the event subsystem.
    """

    if severity_index is None or severity_index <= 0:
        return "unknown"

    tokens = event_code.split("-")
    candidates = tokens[:severity_index]

    for candidate in reversed(candidates):
        candidate = candidate.strip()

        if not candidate:
            continue

        if SLOT_TOKEN_RE.fullmatch(candidate):
            continue

        return candidate.lower()

    return "unknown"


def extract_event_envelope(text: str) -> EventEnvelope:
    """
    Extract a generic percent-prefixed network syslog event envelope.

    Failure to recognize an envelope is not an error. The caller
    continues to emit the original event through the generic path.
    """

    if not text:
        return EventEnvelope()

    match = EVENT_CODE_RE.search(text)

    if match is None:
        return EventEnvelope()

    event_code = match.group("code").upper()
    tokens = event_code.split("-")

    severity_index: int | None = None
    code_severity: int | None = None

    for index, token in enumerate(tokens):
        if token in SEVERITY_VALUES:
            severity_index = index
            code_severity = int(token)
            break

    family = _family_from_code(
        event_code,
        severity_index,
    )

    return EventEnvelope(
        event_code=event_code,
        event_family=family,
        code_severity=code_severity,
    )
