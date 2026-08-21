# AI Handoff

Use this file to resume the project safely in a fresh AI session.

## Read order

1. `README.md`
2. `docs/CURRENT_STATE.md`
3. `docs/ARCHITECTURE.md`
4. `docs/DECISIONS.md`
5. `docs/DATA_CONTRACTS.md`
6. `docs/OPERATIONS.md`
7. `docs/CLICKHOUSE.md`
8. `docs/GRAFANA.md`
9. `docs/NORMALIZER_MIGRATION.md`
10. `docs/ROADMAP.md`
11. `docs/PROJECT_JOURNAL.md`
12. component-specific documentation for the task at hand

## Source precedence

When sources disagree, use this order:

1. live verified system/configuration and current checked-out code/tests
2. this repository's current-state and component documentation
3. current public component repositories
4. older runbooks or historical planning documents

Do not allow historical architecture to override a later verified design decision.

## Working method

- change one component at a time
- inspect the live or current implementation before replacing behavior
- prefer exact copy/paste commands for operator actions
- label every command block with the system/role where it must run
- build new deterministic logic beside production first
- use fixtures, negative paths, replay, and idempotency checks before service automation
- update `CURRENT_STATE.md` and append to `PROJECT_JOURNAL.md` at meaningful checkpoints
- update architecture/data contracts when a durable design decision changes
- append durable design choices and rationale to `DECISIONS.md`
- use `PUBLICATION_CHECKLIST.md` before publishing operational/code changes

## Security/publication rules

This is a public repository.

Never commit:

- credentials, API tokens, passwords, SSH private keys, or secret files
- production IP addresses or firewall allowlists
- customer-identifying raw logs
- private hostnames or environment-specific access paths unless explicitly sanitized for publication
- restricted historical branding or organization identifiers

Use RFC documentation address space and synthetic hostnames in examples.

## Historical normalizer checkpoint before broadened replay

The active normalizer source is `components/normalizer/` in this master repository.

```text
18ec113 Fix public repo gate for monorepo layout
7f7f592 Add Cisco NX-OS OSPF retransmission parser
81a3812 Enable NX-OS OSPF parser in default registry
70 tests passing
public repository gate passing
```

Implemented parser scope now includes:

- Arista EOS BGP adjacency
- Cisco IOS XR BGP adjacency
- Cisco NX-OS ETHPORT state
- Cisco NX-OS OSPF retransmission degradation
- Cisco NX-OS OSPFv3 retransmission degradation

The NX-OS OSPF parser preserves `ospf` versus `ospfv3`, uses protocol `ospf`, deterministic `OSPF|device|process|neighbor` identity, rejects mismatched process/event-code families, and fails open to the generic observation path on malformed or cross-platform input.

## Platform-resolution replay checkpoint

Stored-observation replay established the platform trust boundary required by the vendor parsers.

Current contract:

- runtime parser eligibility comes from trusted `vendor_hint` and `os_family_hint`
- a private operator-maintained inventory maps the deployment's stable syslog `source_ip` identity to platform
- Vector envelope-parser labels are not platform authority
- event-message fingerprints may bootstrap or audit the private inventory but do not become runtime identity
- unknown and unmapped sources fail closed to generic capture-first normalization
- the private platform inventory and real device identities are not stored in this public repository

The private inventory was used to replay three real NX-OS OSPF and three real NX-OS OSPFv3 retransmission observations.

All six passed the collector-side semantic gate.

Measured intentional difference: transitional GX10 v3 leaves the reviewed NX-OS OSPFv3 retransmission observations as generic observations with no OSPF entity key. Collector-side normalization intentionally recognizes them as `ospfv3` neighbor degradation events and preserves `ospfv3-N` process identity.

The production normalizer path has not yet been switched over.

## Completed gate - broaden replay/parity

Do not immediately add another parser.

Completed replay scope:

1. Arista EOS BGP adjacency
2. Cisco IOS XR BGP adjacency
3. Cisco NX-OS ETHPORT state
4. compare semantic output with transitional GX10 behavior where applicable
5. preserve and document intentional differences
6. prove unknown-source behavior remains capture-first
7. prove deterministic repeated replay
8. design production integration only after the selected replay scope passes

## Current resume point - replay/parity complete

The selected normalizer replay/parity milestone is complete.

Verified checkpoint:
- code checkpoint `99f623e` closes EOS peer-AS and NX-OS ETHPORT protocol gaps
- 24 representative stored observations compared with transitional GX10 v3
- 21 strict semantic matches
- 3 intentional NX-OS OSPFv3 differences
- 0 unexpected differences
- sanitized deterministic replay passed twice
- full normalizer suite: 73 passing tests
- unknown/unmapped input remains capture-first and generic

The IOS XR Down-event difference was representational only: GX10 captures a broader detail string, while the collector preserves the bounded reason.

The OSPFv3 difference remains intentional: collector-side normalization recognizes deterministic OSPFv3 neighbor degradation where transitional GX10 v3 remains generic.

No production path has been switched.

Next engineering gate: design collector-side production integration, validation, and rollback. Do not retire transitional GX10 classification until cutover is proven stable.
