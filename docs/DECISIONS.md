# Architecture Decision Log

This file records durable project decisions and the reasoning behind them. New entries are append-only unless a later decision explicitly supersedes an earlier one.

## ADR-001 - Capture first

**Status:** Accepted

All legitimate observations are retained even when no vendor parser recognizes them.

Why:

- unknown events are often the events most worth investigating
- parser coverage evolves over time
- replay requires preserved raw evidence
- admission allowlists create silent blind spots

Consequence: parser mismatch, malformed vendor payloads, and future event codes fall back to generic observations rather than being dropped.

## ADR-002 - Deterministic normalization belongs on the collector

**Status:** Accepted

Vendor decoding, event-envelope extraction, platform trust boundaries, suppression rules, and other deterministic observation normalization belong on the collector/log server.

Why:

- normalization should happen once near durable capture
- deterministic behavior is easier to test and replay centrally
- GX10 should receive prepared observations rather than repeatedly decode vendor syntax
- the reasoning host remains replaceable

Consequence: transitional vendor enrichment on GX10 is retained only as a migration/parity reference until collector-side replay parity is proven.

## ADR-003 - Incident correlation belongs on GX10

**Status:** Accepted

Compact incident identity, lifecycle, repeat/burst evidence, rolling context, and reasoning wake policy belong on GX10.

Why:

- those functions operate on prepared observations rather than raw vendor syntax
- incident working state is compact enough for the reasoning host
- it keeps large/long-lived raw stores on the collector while placing inference-adjacent state next to the local model runtime

Consequence: moving normalization to the collector does not imply moving the entire deterministic incident engine there.

## ADR-004 - The LLM is not the source of truth

**Status:** Accepted

The local model may explain, summarize, rank, and suggest, but it does not own canonical identity, deduplication, incident lifecycle, or deterministic state transitions.

Why:

- incident behavior must be replayable and testable
- model output is probabilistic
- outages or model changes must not corrupt canonical state

Consequence: the system remains operational and state-consistent even when inference is unavailable.

## ADR-005 - GX10 does not write directly to ClickHouse

**Status:** Accepted

AI results cross a write-only transport and collector-side validation gate before durable ingestion.

Why:

- least privilege
- malformed model output is isolated before storage
- the collector remains the durable data authority

Consequence: result files are validated, accepted atomically, or quarantined with a reason.

## ADR-006 - File backlog is the V1 transport

**Status:** Accepted

Prepared/backlog observations are transferred through durable files rather than introducing a message bus in the first production design.

Why:

- existing throughput and latency requirements do not justify additional infrastructure
- file replay and catch-up semantics are straightforward to inspect
- the transport already supports durable recovery

Consequence: streaming infrastructure is deferred until measured requirements demand it.

## ADR-007 - Public master repository

**Status:** Accepted

This repository is the durable public engineering record and eventual consolidated home for project components.

Why:

- one front door reduces documentation drift and recovery cost
- architecture, implementation state, and operational rules remain versioned together
- future AI-assisted sessions can resume from a compact verified record

Consequence: public-safety gates are mandatory, and live system state must still be verified before consequential production changes.
