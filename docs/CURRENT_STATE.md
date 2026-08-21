# Current State

Last verified checkpoint: 2026-08-20.

## Platform

The production observability path is operational for raw syslog collection, ClickHouse storage, Grafana visualization, compressed backlog creation, secure backlog retrieval by GX10, GX10 ingest, and validated AI-result return to the collector.

The deterministic incident correlator and local-LLM orchestration are not yet production-complete.

## Collector / log server

Verified capabilities:

- Vector receives network syslog and fans out to durable storage and a compressed AI backlog.
- ClickHouse retains raw syslog observations.
- Grafana reads from a semantic log view rather than forcing display-specific fields into the raw table.
- A validated AI result ingestion path writes accepted result records into ClickHouse.
- The Python network log normalizer is developed in this master repository but is not yet wired into the production path.

## GX10

Verified capabilities:

- read-only secure fetch of compressed backlog files
- local durable ingest with replay/idempotency protection
- transitional deterministic enrichment used as a parity reference
- write-only secure return path for AI result files
- local Ollama runtime available for later reasoning work

Not yet complete:

- long-lived deterministic incident objects
- repeat/burst incident evidence model
- deterministic rolling context summaries
- production LLM wake/orchestration logic

## Normalizer repository checkpoint

The normalizer is now developed from `components/normalizer/` in this master repository. Its standalone history was preserved during consolidation.

History-preserving import checkpoint:

```text
8d55320 Import normalizer component history
```

The public-repository gate was repaired for the monorepo layout without weakening the private deny list:

```text
18ec113 Fix public repo gate for monorepo layout
```

Current verified normalizer feature checkpoint:

```text
7f7f592 Add Cisco NX-OS OSPF retransmission parser
81a3812 Enable NX-OS OSPF parser in default registry
70 tests passing
public repository gate passing
5 local forbidden terms loaded
clean working tree before publication
```

Implemented deterministic parser coverage now includes:

- Arista EOS BGP adjacency changes
- Cisco IOS XR BGP adjacency changes
- Cisco NX-OS ETHPORT interface state changes
- Cisco NX-OS OSPF neighbor retransmission degradation
- Cisco NX-OS OSPFv3 neighbor retransmission degradation

Generic event envelope extraction, platform-hint trust boundaries, capture-first behavior, and fail-open parser dispatch are also implemented.

## NX-OS OSPF/OSPFv3 checkpoint

The previously pinned parser task is complete and registered in the default parser registry.

Supported event codes:

```text
OSPF-5-NBR_RETRANSMISSIONS
OSPFV3-5-NBR_RETRANSMISSIONS
```

Deterministic enrichment contract:

```text
protocol      = ospf
signal_type   = degradation
entity_type   = ospf_neighbor
state         = retransmissions
entity_key    = OSPF|device|process|neighbor
```

The parser preserves `event_family = ospf` versus `event_family = ospfv3` and requires the process identity to agree with the event code (`ospf-N` for OSPF and `ospfv3-N` for OSPFv3).

Malformed layouts, missing identity, unsupported event codes, and non-NX-OS platform hints stay on the generic capture-first path. Synthetic tests cover IPv4, IPv6, hostname/source fallback, future layouts, event-code/process mismatch, Cisco IOS XR rejection, and Arista EOS rejection.

The collector implementation intentionally improves on the transitional GX10 classifier by preserving OSPFv3 process identity rather than collapsing it to an unknown process.

## Immediate resume point - replay and parity

Do not add another parser merely to increase coverage. The next engineering gate is to prove the current collector-side normalizer against stored observations and the transitional GX10 enrichment path.

Next sequence:

1. inventory the existing replay/sample tooling and stored observation sources without modifying production
2. build or adapt a deterministic replay harness for the selected migration scope
3. replay representative EOS BGP, IOS XR BGP, NX-OS ETHPORT, NX-OS OSPF, and NX-OS OSPFv3 observations
4. compare event family, vendor/platform, protocol, signal type, entity type/key, state, and structured attributes against transitional GX10 enrichment
5. record intentional differences, especially corrected OSPFv3 process identity
6. verify malformed/unknown observations remain visible and replayable
7. verify repeated replay is deterministic and idempotent
8. only after parity is understood, design the production collector integration/cutover

Do not modify the production path until this replay/parity gate is complete.
