# Project Journal

This file is append-only. It records important engineering checkpoints, architectural decisions, and migration boundaries. Detailed implementation evidence belongs in commits, tests, and component documentation.

## 2026-08-19 - Master repository established

- Established this repository as the public master project record.
- Confirmed the preferred long-term structure is a single master repository with component subdirectories rather than multiple independently drifting copies.
- Kept the existing normalizer repository temporarily separate while its live development checkout remains ahead of the published remote.
- Established the rule that live verified code and system state take precedence over historical documentation.
- Established a strict public-repository posture: no credentials, production addresses, customer-identifying logs, or restricted historical branding.

## 2026-08-19 - Architecture boundary confirmed

- Collector/log server owns collection, durable storage, deterministic normalization, presentation, unknown-event inventory, AI-result validation, and long-lived stores.
- GX10 owns compact incident state, deterministic correlation, local reasoning, and explanation.
- Transitional vendor parsing that exists on GX10 is a migration reference, not the desired permanent boundary.
- GX10 remains replaceable and receives prepared observations instead of becoming the raw-log authority.

## 2026-08-19 - Normalizer checkpoint

Verified live development state:

```text
f95db38 Enable NX-OS ETHPORT parser in default registry
58 tests passing
clean working tree
```

Implemented parser families at this checkpoint:

- Arista EOS BGP adjacency
- Cisco IOS XR BGP adjacency
- Cisco NX-OS ETHPORT state

## 2026-08-19 - OSPF research checkpoint

Production examples were inspected before parser implementation.

Verified that the generic normalizer distinguishes:

```text
OSPF-5-NBR_RETRANSMISSIONS   -> event_family ospf
OSPFV3-5-NBR_RETRANSMISSIONS -> event_family ospfv3
```

Both remain generic observations until the NX-OS parser is added.

A transitional GX10 classifier already treats retransmission evidence as a degradation and keys known neighbors using a deterministic OSPF device/process/neighbor identity. A limitation was identified in the transitional process extraction: it recognizes `ospf-N` but does not fully preserve `ospfv3-N`. The new collector-side parser should correct this while preserving OSPF versus OSPFv3 family identity.

Implementation was deliberately paused at this point for design discussion.

## 2026-08-19 - Documentation hardening pass

- Added operational pipeline documentation covering collector ingest, durable backlog, GX10 replay-safe ingest, AI-result validation, and failure behavior.
- Added ClickHouse schema and sink-contract documentation.
- Added Grafana datasource, drilldown, and NOC-view behavior documentation.
- Added an architecture decision log covering capture-first behavior, collector/GX10 ownership, LLM authority limits, transport boundaries, and master-repository policy.
- Added a controlled normalizer migration document with parser-by-parser parity gates.
- Added a public publication checklist for secrets, restricted terms, fixtures, tests, diffs, and migration provenance.
- Expanded the master README so these documents are discoverable from the repository front page.
- No production path was changed as part of this documentation pass.

## 2026-08-20 - Normalizer source consolidated into master repository

- Reconciled the live normalizer checkout with its standalone public repository at `f95db38`.
- Re-ran the public-repository sanitation gate successfully.
- Re-ran the full normalizer suite with 58 tests passing.
- Published the 14 previously local reviewed commits to the standalone repository to preserve provenance.
- Imported the standalone normalizer history into `components/normalizer/` using a Git subtree merge.
- Master import commit `8d55320` retains `f95db38` as a parent and records the subtree split SHA.
- Verified the imported package resolves from the master-repository path rather than the old checkout.
- Re-ran all 58 tests from the imported master-repository component successfully.
- Published the history-preserving import to the master repository.
- Declared `components/normalizer/` in the master repository the active development source for future normalizer work.
- The standalone normalizer repository is now historical/migration reference only.
- No production collector or GX10 service behavior changed during this consolidation.

## 2026-08-20 - NX-OS OSPF/OSPFv3 parser completed

- Repaired the public-repository gate for the monorepo layout in `18ec113` without weakening the local forbidden-term policy.
- Added the isolated Cisco NX-OS OSPF/OSPFv3 retransmission parser in `7f7f592`.
- Registered the parser in the default parser registry in `81a3812`.
- Parser coverage includes both `%OSPF-5-NBR_RETRANSMISSIONS` and `%OSPFV3-5-NBR_RETRANSMISSIONS`.
- Preserved generic family identity (`ospf` versus `ospfv3`) while grouping both under protocol `ospf`.
- Added deterministic `OSPF|device|process|neighbor` identity and required the process prefix to agree with the event code.
- Added negative-path tests for malformed identity, future codes, OSPF/OSPFv3 process mismatches, Cisco IOS XR, and Arista EOS.
- Verified source-IP fallback when hostname is absent.
- Verified malformed and unsupported observations stay capture-first generic and attention-eligible.
- Full suite reached 70 passing tests.
- Public-repository gate passed with all five local forbidden terms loaded.
- Published the parser and registry commits to the master repository.
- No production collector or GX10 path was changed.
- Next gate is replay/parity against stored observations and transitional GX10 enrichment, not additional parser breadth by default.

## 2026-08-20 - Platform resolution and first real replay proof

- Inspected live collector Vector parsing behavior and established that fallback parser labels describe syslog envelope parsing rather than trustworthy device platform identity.
- Established a private platform-resolution contract based on the deployment's stable syslog `source_ip` identity.
- Used deliberately narrow production-observed message fingerprints only to bootstrap and audit the private inventory.
- Kept the runtime trust path independent of message fingerprints.
- Preserved fail-closed behavior: sources absent from the private inventory remain generic capture-first observations.
- Kept production source identities, hostnames, and the private inventory outside the public repository.
- Replay exposed an initial inventory-evidence gap for NX-OS OSPF retransmission events.
- Added the already-supported narrow OSPF/OSPFv3 retransmission grammar to the private bootstrap evidence rather than creating a one-off source exception.
- The revised private evidence set introduced no reviewed cross-platform conflicts.
- Replayed three real stored NX-OS OSPF and three real stored NX-OS OSPFv3 retransmission observations through trusted platform resolution and the collector-side normalizer.
- All six passed the semantic gate for vendor, OS family, event family, protocol, signal type, entity type, state, entity-key presence, process identity, and neighbor presence.
- Verified that transitional GX10 v3 leaves the reviewed OSPFv3 retransmission observations generic, while the collector-side parser intentionally recognizes them as OSPFv3 neighbor degradation.
- No production collector path was changed.
- Next gate is broader replay/parity for EOS BGP, IOS XR BGP, and NX-OS ETHPORT before production integration design.

## 2026-08-20 - Selected normalizer replay/parity milestone completed

- Replayed the selected EOS BGP, IOS XR BGP, NX-OS ETHPORT, NX-OS OSPF, and NX-OS OSPFv3 migration scope.
- Compared 24 representative stored observations against transitional GX10 v3.
- Corrected two genuine collector gaps: EOS peer-AS preservation and NX-OS ETHPORT protocol identity.
- Confirmed the IOS XR reason/detail discrepancy was representational rather than semantic.
- Final parity result: 21 strict matches, 3 intentional OSPFv3 differences, 0 unexpected differences, PASS.
- Added sanitized deterministic replay coverage including an unmapped-source generic case.
- Repeated replay passed twice with identical output.
- Full normalizer suite reached 73 passing tests.
- No production collector or GX10 service path was changed.
- Next gate is production integration and rollback design.
