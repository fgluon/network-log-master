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

Measured replay against the live transitional GX10 classifier established a stronger difference: transitional GX10 v3 leaves the reviewed OSPFv3 retransmission events on the generic observation path with no OSPF entity key. The collector-side parser intentionally classifies them as `ospfv3` neighbor degradation and preserves the `ospfv3-N` process identity.

## Platform-resolution and first replay checkpoint

Stored-observation replay exposed an important platform trust boundary before production integration.

Verified conclusions:

- platform-specific parsers must not infer platform identity from event syntax alone
- Vector fallback parser labels describe envelope parsing and are not authoritative vendor/platform identity
- trusted `vendor_hint` and `os_family_hint` values come from a private operator-maintained platform inventory keyed by the deployment's stable syslog `source_ip` identity
- message fingerprints may bootstrap and audit that private inventory, but are not runtime platform authority
- sources absent from the private inventory remain `unknown` and stay on the generic capture-first path
- production source identities and the private inventory remain outside this public repository

The private inventory bootstrap was exercised against stored backlog observations without introducing a reviewed cross-platform evidence conflict.

The resulting platform-resolution path was tested against six real stored Cisco NX-OS retransmission observations:

```text
3 OSPF retransmission observations
3 OSPFv3 retransmission observations
6 passed
0 failed
```

All six resolved through trusted platform hints and entered the NX-OS parser with:

```text
vendor        = cisco
os_family     = nxos
protocol      = ospf
signal_type   = degradation
entity_type   = ospf_neighbor
state         = retransmissions
entity_key    = present
```

OSPF records preserved `event_family = ospf` and `ospf-N` process identity.

OSPFv3 records preserved `event_family = ospfv3` and `ospfv3-N` process identity.

This establishes the first real-observation proof of:

```text
trusted source identity
-> private platform inventory
-> vendor/os hints
-> deterministic vendor parser
-> normalized semantic event
```

No production collector path has been switched to the new normalizer.

## Immediate resume point - broaden replay/parity

Do not add parser breadth merely to increase coverage.

The next engineering gate is to broaden stored-observation replay across the remaining selected migration scope:

1. Arista EOS BGP adjacency
2. Cisco IOS XR BGP adjacency
3. Cisco NX-OS ETHPORT state
4. compare collector-side semantics with transitional GX10 behavior where it provides a meaningful reference
5. record intentional differences rather than forcing incorrect parity
6. verify unknown and unmapped observations remain visible, attention-eligible, and replayable
7. verify repeated replay is deterministic
8. design production integration and rollback only after the selected replay scope passes

Do not modify the production path until the broader replay/parity gate is complete.
