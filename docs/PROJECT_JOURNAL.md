# Project Journal

This file is append-only. It records important engineering checkpoints, architectural decisions, migration boundaries, and recovery context. Detailed implementation evidence belongs in commits, tests, component documentation, and rebuild status files.

## Journal operating rules

The journal is historical context, not the execution queue.

Authoritative roles:

- `docs/ARCHITECTURE.md` describes the intended system architecture and ownership boundaries.
- `docs/CURRENT_STATE.md` describes the present implementation state and is the authority for execution order and the single next action.
- `components/<component>/REBUILD_STATUS.md` contains detailed component-specific rebuild and validation state.
- `docs/PROJECT_JOURNAL.md` explains what happened, why decisions were made, what failed, and how the project reached the current state.

Each substantial work-session entry should record, when applicable:

- local timestamp including timezone
- goal of the session or checkpoint
- starting branch and commit
- affected components or files
- work completed
- validation evidence and important PASS/FAIL results
- architectural or operational decisions
- failed approaches or corrections worth remembering
- known risks, constraints, and intentionally deferred work
- resulting Git commit and whether the remote was verified
- worktree state at the checkpoint
- the explicit next action

Additional rules:

- Do not silently rewrite history when an earlier assumption is later found to be wrong. Append a new entry that supersedes or corrects the earlier entry.
- Do not use the journal as a substitute for `CURRENT_STATE.md`. Execution order must remain explicit in `CURRENT_STATE.md`.
- Do not record secrets, credentials, private keys, production addresses, customer-identifying logs, private operator identities, or restricted historical branding.
- Failed experiments should be recorded when repeating them would waste time, risk production, or obscure why the current implementation was chosen. Routine command noise should not be preserved.
- At milestone checkpoints, record the commit SHA and whether the remote branch was verified to match it.
- Before beginning work after a context reset, read `ARCHITECTURE.md`, `CURRENT_STATE.md`, the relevant component `REBUILD_STATUS.md`, the latest journal entries, then verify `git log` and `git status` before changing anything.

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

## 2026-08-21 01:58 PDT - Collector rebuild capture checkpoint published

### Goal

Create a durable public recovery point before continuing deeper clean-machine integration work so the collector does not need to be rediscovered if conversational context is lost.

### Starting point

- Branch: `main`
- Previous public milestone: normalizer replay/parity complete at `4220f50474d608fd8745b4465398af521d7625bd`
- Collector rebuild artifacts were present locally but had not yet been published.

### Work completed

Captured and published the current collector reconstruction artifacts for:

- package versions and package verification
- configuration rendering
- Vector syslog ingestion, ClickHouse sinks, AI-result ingestion, and durable GX10 spool output
- ClickHouse database objects, service accounts, grants, and settings profile
- Grafana ClickHouse datasources
- Grafana HTTPS configuration and TLS file contract
- Certbot renewal service, timer, and deploy hook
- restricted SFTP transport boundary, chroots, ACLs, and bind mounts
- AI-result validation gate
- spool-retention behavior
- independent collector runtime verification
- four Grafana 13 dashboard resources
- Grafana dashboard restore and verification scripts
- component recovery document at `components/collector/REBUILD_STATUS.md`

### Validation evidence

Important completed validation gates include:

- `COLLECTOR_PACKAGE_VERIFY=PASS`
- `TRANSPORT_VERIFY=PASS`
- `RETENTION_SCRIPT_CONTRACT=PASS`
- `RETENTION_RUNTIME_CONTRACT=PASS`
- `CLICKHOUSE_OBJECT_CONTRACT=PASS`
- `CLICKHOUSE_COLUMN_CONTRACT=PASS`
- `CLICKHOUSE_USER_POLICY=PASS`
- `CLICKHOUSE_GRANT_CONTRACT=PASS`
- `CLICKHOUSE_LOOPBACK_LISTENERS=PASS`
- `VECTOR_CRITICAL_CONFIG_PARITY=PASS`
- `VECTOR_SYSLOG_LISTENERS=PASS`
- `GRAFANA_HTTPS_OVERRIDE=PASS`
- `GRAFANA_HTTPS_HEALTH=PASS`
- `GRAFANA_DATASOURCE_CONTRACT=PASS`
- `CERTBOT_RUNTIME_CONTRACT=PASS`
- `COLLECTOR_RUNTIME_VERIFY=PASS`
- `GRAFANA_UNIFIED_RESOURCE_ROUND_TRIP=PASS`
- `GRAFANA_DRYRUN_RESTORE_PROOF=PASS`
- `GRAFANA_DASHBOARD_VERIFY=PASS`
- `GRAFANA_DASHBOARD_RESTORE_DRYRUN=PASS`
- `GRAFANA_DASHBOARD_LIVE_NONDESTRUCTIVE_TEST=PASS`

Grafana 13.1.1 was also verified to support secure administrator reset using `grafana cli admin reset-admin-password --password-from-stdin`.

### Decisions and constraints

- Do not execute `components/collector/install/install-runtime.sh` against the working collector. It is a clean-machine installer with an explicit clean-install guard.
- Preserve the current working Vector and Grafana behavior rather than changing configuration merely because it looks unusual.
- Public rebuild artifacts use neutral service names when live historical names contain private identity.
- Firewall/nftables reconstruction remains intentionally out of scope. Public documentation should state required network prerequisites without publishing deployment-specific firewall policy.
- Grafana dashboards are restored through the supported `dashboard.grafana.app/v2` API rather than by writing directly to Grafana SQLite state.
- Credentials, addresses, SSH keys, TLS private keys, and private environment identity remain operator-supplied and outside the public repository.

### Failed approaches worth remembering

- Early Grafana bootstrap audit commands incorrectly assumed `grafana` or `grafana-cli` was on `PATH`. The package service actually uses `/usr/share/grafana/bin/grafana`.
- One diagnostic contained a bare interactive-shell `exit 1` and could terminate the SSH session. Subsequent potentially failing command sequences must run inside a child shell.
- Grafana runtime wiring patch attempts were aborted because of an ambiguous text anchor and a heredoc delimiter collision. Those attempts failed before replacing `install-runtime.sh`; the published checkpoint intentionally records the Grafana runtime integration as unfinished.

### Git checkpoint

- Collector checkpoint commit: `e8df224`
- Commit message: `Checkpoint collector rebuild capture`
- 39 collector files were committed.
- `origin/main` was explicitly verified to match the local checkpoint commit.
- Worktree was clean after publication.

### Known incomplete work

Collector:

1. Wire `GRAFANA_ADMIN_PASSWORD_FILE` into `install-runtime.sh`.
2. Implement loopback-only first Grafana startup and secure administrator reset with `--password-from-stdin`.
3. Wire `restore-dashboards.py` and `verify-dashboards.py` into the clean-machine runtime installer.
4. Add package-install no-autostart protection before first configuration.
5. Re-run structural, runtime-contract, and public-safety checks.
6. Finish collector README/operator rebuild documentation.
7. Run final collector sanitation and milestone publication.
8. Perform a clean-machine end-to-end rebuild validation when practical.

GX10 remains the next major component milestone after the collector is closed.

### Next action

Refresh `docs/CURRENT_STATE.md` so it contains a strict numbered execution order with exactly one item marked `NEXT`. Then resume collector Grafana clean-machine integration from the published `e8df224` checkpoint. Do not begin GX10 capture until the collector milestone execution order is explicitly advanced or intentionally reprioritized in `CURRENT_STATE.md`.
