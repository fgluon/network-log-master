from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


SCHEMA_VERSION = 1


@dataclass(slots=True)
class NormalizedEvent:
    """
    Stable handoff contract between the network log normalizer and downstream
    correlation/AI systems.

    Capture-first contract:
      - unknown events are valid events
      - raw_message is preserved
      - enrichment fields may be empty
      - attention_eligible defaults to True
      - suppression requires an explicit rule
    """

    # Contract metadata
    schema_version: int = SCHEMA_VERSION

    # Source identity / timing
    timestamp: str = ""
    ingest_timestamp: str = ""
    device_timestamp: str | None = None
    hostname: str = ""
    source_ip: str = ""
    source_port: int = 0

    # Original syslog information
    facility: str = ""
    severity: str = ""
    appname: str = ""
    message: str = ""
    raw_message: str = ""
    parse_status: str = ""

    # Best-effort normalization / enrichment
    vendor: str = "unknown"
    os_family: str = "unknown"
    event_code: str = ""
    event_family: str = "unknown"
    protocol: str = ""
    signal_type: str = "observation"

    # Correlation identity
    entity_type: str = "unknown"
    entity_key: str = ""
    state: str = ""

    # Repeat/burst evidence
    repeat_count: int = 1

    # Attention policy
    attention_eligible: bool = True
    suppression_rule_id: str | None = None

    # Extension point for vendor/event-specific facts
    attributes: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
