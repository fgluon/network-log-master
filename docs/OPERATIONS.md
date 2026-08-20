# Operations

## Purpose

This document records the current operational behavior of the observability pipeline without publishing environment-specific credentials, addresses, hostnames, or firewall policy.

## Collector ingest

Network devices send syslog to the collector. Vector is the collection and fan-out layer.

The important capture rule is that raw data is preserved before parsing decisions are made. The current ingest behavior is deliberately tolerant of vendor formatting differences:

1. preserve `raw_message`
2. attempt strict syslog parsing
3. attempt relaxed Cisco NX-OS parsing
4. attempt legacy NX-OS parsing
5. retain an explicit `raw_unparsed` observation when none of the structured paths match

UDP ingest uses a generic byte-oriented socket path rather than depending exclusively on a strict syslog source. TCP syslog remains supported through the structured syslog path.

Parser failure is metadata, not packet loss.

## ClickHouse delivery

Vector writes raw observations to ClickHouse. The production sink has a known operational exception: startup health checking is disabled because the health-check request path produced an authentication failure while runtime inserts were proven healthy.

Do not remove that exception merely because the configuration looks unusual. Re-enable startup health checking only after testing the exact authentication behavior with the deployed ClickHouse/Vector combination.

## Durable retention

Current retention policy:

- raw syslog observations: approximately 12 months
- validated AI updates: approximately 12 months
- compressed AI/backlog files: approximately 90 days

Retention policy is independent of AI decisions. Raw observations are not deleted because the reasoning layer ignored or suppressed them.

## Compressed backlog

The collector emits newline-delimited JSON compressed with Zstandard into hour-partitioned backlog files. This is the V1 handoff mechanism to GX10.

The backlog is intentionally file-based. A message bus is not introduced until throughput, latency, or operational requirements demonstrate a need for one.

## GX10 backlog fetch

The fetcher uses a read-only transport and must never mutate the collector backlog.

Operational behavior includes:

- short bootstrap window for first start
- overlap when scanning recent periods so late-arriving files are not skipped
- bounded catch-up window
- settle time before consuming a file that may still be written
- temporary local `.part` files
- Zstandard integrity testing before promotion
- SHA-256 verification/accounting
- atomic local move after validation
- durable checkpointing

The fetch path is designed so interruption can be retried without corrupting or deleting source data.

## GX10 local ingest

Fetched JSONL records are ingested into a local SQLite working database using WAL mode.

Important ingest contracts:

- timestamp and message fields are required strings
- timestamps must carry timezone information
- individual input lines are size-bounded
- the original JSON record is retained
- files move from incoming to processed only after successful ingest
- `(source_file, record_number)` is unique, making replay idempotent
- replaying an already ingested file must not create duplicate observations

This local database is working state, not the authoritative raw-log archive.

## AI result return path

GX10 emits thin JSONL result files through a separate write-only transport. The collector applies a validation gate before durable ingestion.

Current validation policy includes:

- settle interval before inspection
- maximum file size of 256 KiB
- maximum 100 JSONL records per file
- required timezone-aware timestamp
- required title and body
- accepted files move atomically to a ready area
- rejected files are quarantined with a reason

Validated records are then ingested into ClickHouse and become available to Grafana.

## Failure behavior

The system should fail in the direction of preserving evidence:

- parser failure -> keep generic observation
- model unavailable -> retain deterministic incident/evidence state
- malformed AI output -> reject/quarantine, do not write directly to ClickHouse
- transport interruption -> retry from durable file/checkpoint state
- replay -> no duplicate canonical records

## Operational change rule

Before promoting any new deterministic component into the production path:

1. test with synthetic fixtures
2. test malformed and future layouts
3. replay stored observations
4. compare against the current production/transitional behavior
5. document intentional parity differences
6. verify idempotency
7. only then automate the steady-state service path
