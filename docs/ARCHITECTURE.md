# Architecture

## Purpose

The platform turns raw network telemetry into durable observations, deterministic normalized events, long-lived incident state, and concise local-AI explanations without allowing the LLM to become the source of truth for identity or lifecycle.

## Component ownership

### Collector / log server

Owns:

- syslog ingress
- durable raw capture
- parsing and normalization
- ClickHouse storage
- Grafana presentation
- unknown-event inventory
- validation and storage of AI results
- large and long-lived data stores

### GX10

Owns:

- receiving prepared observations
- compact active incident state
- repeat/burst accounting
- deterministic correlation
- rolling incident context
- deciding when the local LLM should run
- local inference
- returning thin AI result records

GX10 is intentionally not a raw-log archive, dashboard server, or general infrastructure host.

## Data path

```text
Devices
  -> syslog ingress
  -> Vector
     -> ClickHouse raw store
     -> compressed AI backlog

Prepared observations
  -> GX10 deterministic incident engine
  -> local LLM when warranted
  -> validated AI result files
  -> collector validation gate
  -> ClickHouse AI results
  -> Grafana
```

## Capture-first contract

The system captures legitimate observations before deciding whether they are understood. Unknown events are valid observations and remain attention-eligible by default.

Vendor/event decoders are enrichment modules. A parser mismatch or exception must not drop the raw event.

Suppression is narrowly defined: an explicit rule may prevent an event from waking the reasoning layer, but suppression never means deletion.

## Time contract

Collector arrival time is authoritative for event ordering. A device-supplied timestamp is retained separately when available.

## Incident model

Syslog records are observations. Incidents are persistent objects created and updated by deterministic logic.

Target lifecycle:

```text
CANDIDATE -> OPEN -> RECOVERING -> RESOLVED
```

The LLM may summarize or explain an incident but does not decide canonical identity, deduplication, or lifecycle state.

## Context model

The incident engine should build deterministic compact summaries over approximately:

- 60 minutes
- 180 minutes
- 24 hours

Open incidents persist until resolved. Compact resolved history may remain available for substantially longer periods to improve operator context.

## LLM wake policy

Normal reasoning runs should be event-driven and rate-limited rather than invoked for every record. Approximate target behavior:

- periodic analysis when meaningful new evidence exists
- immediate wake for major/critical conditions
- interface flaps are valid wake reasons
- OSPF retransmission degradation is a valid wake reason

The exact policy remains deterministic and testable outside the LLM.

## Trust boundaries

Input and output transport credentials are independent and least-privilege.

- backlog reader: read-only
- AI result writer: write-only
- AI results: validated before durable ingestion
- GX10: no direct ClickHouse write path

## Production migration rule

New deterministic parsing logic is built beside the current production path first. It is promoted only after fixture, replay, parity, and idempotency checks. Transitional logic is retired deliberately rather than rewritten in-place without comparison.
