# Network Log Intelligence Platform

A capture-first network observability and local-AI incident reasoning platform.

This repository is the master engineering record for the project. It documents architecture, data contracts, operational boundaries, current state, roadmap, and component ownership. Component code will be consolidated here in a controlled manner as live implementations are synchronized and verified.

## Core design

```text
Network devices
    |
    | syslog
    v
Collector / log server
    |-- Vector ingest and fan-out
    |-- ClickHouse durable storage
    |-- Python deterministic normalizer
    |-- Grafana presentation
    |-- validated AI-result ingestion
    |
    | prepared observations
    v
GX10
    |-- compact incident/state engine
    |-- deterministic correlation
    |-- rolling context summaries
    |-- local LLM reasoning via Ollama
    |
    | validated AI updates
    v
Collector / ClickHouse / Grafana
```

## Architectural invariants

- Capture first. Legitimate observations are retained even when no parser recognizes them.
- Unknown and rare events remain attention-eligible by default.
- Vendor-specific parsing enriches events; it never acts as an admission allowlist.
- Suppression means "do not wake the reasoning layer", not deletion.
- Raw messages remain replayable.
- Collector arrival time is authoritative; device-provided time is secondary metadata.
- The collector owns collection, durable storage, normalization, presentation, and large/long-lived datasets.
- GX10 owns compact incident state, correlation, reasoning, and explanation.
- GX10 is replaceable and does not become the authoritative raw-log store.
- The LLM does not own identity, deduplication, incident lifecycle, or deterministic state transitions.
- GX10 does not write directly to ClickHouse; AI results cross a validation boundary first.
- File-based backlog remains the V1 transport. A streaming bus is deferred until a real requirement justifies it.

## Repository map

- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) - end-to-end design and ownership boundaries.
- [`docs/CURRENT_STATE.md`](docs/CURRENT_STATE.md) - verified project checkpoint and immediate resume point.
- [`docs/DATA_CONTRACTS.md`](docs/DATA_CONTRACTS.md) - raw, normalized, incident, and AI-result contracts.
- [`docs/ROADMAP.md`](docs/ROADMAP.md) - ordered build sequence and gates.
- [`docs/PROJECT_JOURNAL.md`](docs/PROJECT_JOURNAL.md) - append-only engineering history.
- [`docs/AI_HANDOFF.md`](docs/AI_HANDOFF.md) - concise instructions for resuming work in a new AI session.
- [`SECURITY.md`](SECURITY.md) - public-repository publication rules.
- [`components/`](components/) - component-specific ownership and migration notes.

## Source-of-truth policy

This repository is the durable project control plane, but production changes must still be verified against the live system and the current checked-out code before modification. If documentation and a live implementation disagree, stop and reconcile the difference instead of guessing.

Historical documents are reference material only. Current verified state and current code take precedence.

## Public-repository posture

This repository intentionally excludes credentials, keys, tokens, production addresses, firewall allowlists, customer/device-identifying raw logs, and other sensitive operational data. Public examples use documentation-only addresses and synthetic device names.
