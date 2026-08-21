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

## Current verified normalizer checkpoint

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

## Current resume point - replay/parity

Do not immediately add another parser.

The next task is to inventory and exercise replay/parity against stored observations and the transitional GX10 enrichment path.

Required comparison fields:

- event family
- vendor/platform
- protocol
- signal type
- entity type
- entity key
- state
- structured attributes

Expected intentional difference: collector-side OSPFv3 parsing preserves the `ospfv3-N` process identity that the transitional GX10 classifier does not fully preserve.

The production normalizer path has not yet been switched over. Do not cut over until replay, parity, unknown-event visibility, and idempotency are proven.
