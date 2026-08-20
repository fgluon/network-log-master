# Current State

Last verified checkpoint: 2026-08-19.

## Platform

The production observability path is operational for raw syslog collection, ClickHouse storage, Grafana visualization, compressed backlog creation, secure backlog retrieval by GX10, GX10 ingest, and validated AI-result return to the collector.

The deterministic incident correlator and local-LLM orchestration are not yet production-complete.

## Collector / log server

Verified capabilities:

- Vector receives network syslog and fans out to durable storage and a compressed AI backlog.
- ClickHouse retains raw syslog observations.
- Grafana reads from a semantic log view rather than forcing display-specific fields into the raw table.
- A validated AI result ingestion path writes accepted result records into ClickHouse.
- The Python network log normalizer is under active development beside production and is not yet wired into the production path.

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

## Normalizer checkpoint

Current verified live development tree:

```text
f95db38 Enable NX-OS ETHPORT parser in default registry
58 tests passing
clean working tree
```

Implemented deterministic parser coverage:

- Arista EOS BGP adjacency changes
- Cisco IOS XR BGP adjacency changes
- Cisco NX-OS ETHPORT interface state changes

Generic event envelope extraction and platform-hint trust boundaries are also implemented.

The live development checkout is authoritative when it is ahead of the previously published normalizer repository. Synchronize deliberately before consolidating the code into this master repository.

## Pinned OSPF checkpoint

Research is complete enough to begin the next parser, but implementation is intentionally paused.

Verified generic normalization behavior:

```text
OSPF-5-NBR_RETRANSMISSIONS
  event_family = ospf
  vendor       = cisco
  os_family    = nxos
  protocol     = ""
  signal_type  = observation

OSPFV3-5-NBR_RETRANSMISSIONS
  event_family = ospfv3
  vendor       = cisco
  os_family    = nxos
  protocol     = ""
  signal_type  = observation
```

Important design finding: OSPF and OSPFv3 are already distinct generic event families. The future NX-OS parser should preserve that distinction.

Observed production message families also include Arista OSPF/OSPFv3 adjacency events and Cisco IOS XR OSPF/OSPFv3 adjacency events. Those must not be accidentally consumed by the NX-OS parser; they require separate platform-specific parsers.

## Immediate resume point

When normalizer work resumes:

1. implement the isolated Cisco NX-OS OSPF/OSPFv3 retransmission parser
2. preserve the platform trust boundary
3. use synthetic documentation-range addresses in tests
4. prove malformed/future layouts stay capture-first generic
5. prove cross-platform events cannot enter the NX-OS parser
6. run the complete test suite before registering the parser in the default registry

Do not modify the production path until replay/parity testing proves the new normalizer behavior.
