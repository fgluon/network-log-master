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

## Normalizer consolidation checkpoint

The standalone normalizer repository and live development checkout were reconciled at:

```text
f95db38 Enable NX-OS ETHPORT parser in default registry
58 tests passing
clean working tree
```

The verified normalizer history was then imported into this master repository under `components/normalizer/` using a history-preserving Git subtree merge.

Master import commit:

```text
8d55320 Import normalizer component history
```

The import commit retains `f95db38` as a parent and records the subtree split SHA in the commit metadata. The imported package was tested from its new master-repository path in an isolated virtual environment:

```text
58 passed
```

The master repository is now the active development source for the normalizer. The old standalone normalizer repository is retained only as historical/migration reference and should not receive new feature development.

Implemented deterministic parser coverage:

- Arista EOS BGP adjacency changes
- Cisco IOS XR BGP adjacency changes
- Cisco NX-OS ETHPORT interface state changes

Generic event envelope extraction, platform-hint trust boundaries, capture-first behavior, and fail-open parser dispatch are also implemented.

## Pinned OSPF checkpoint

Research is complete enough to begin the next parser. Implementation can now resume in `components/normalizer/` inside this master repository.

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

Important design finding: OSPF and OSPFv3 are already distinct generic event families. The future NX-OS parser must preserve that distinction.

Observed production message families also include Arista OSPF/OSPFv3 adjacency events and Cisco IOS XR OSPF/OSPFv3 adjacency events. Those must not be accidentally consumed by the NX-OS parser; they require separate platform-specific parsers.

## Immediate resume point

1. work only from `components/normalizer/` in the master repository
2. implement the isolated Cisco NX-OS OSPF/OSPFv3 retransmission parser
3. preserve the Cisco/NX-OS platform trust boundary
4. use synthetic documentation-range addresses in tests
5. require enough parsed identity to avoid ambiguous incident keys
6. prove malformed/future layouts stay capture-first generic
7. prove cross-platform events cannot enter the NX-OS parser
8. run the complete test suite before registering the parser in the default registry
9. replay and compare against the transitional GX10 classifier before any production cutover

Do not modify the production path until replay/parity testing proves the new normalizer behavior.
