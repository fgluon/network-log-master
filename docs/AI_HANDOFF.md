# AI Handoff

Use this file to resume the project safely in a fresh AI session.

## Read order

1. `README.md`
2. `docs/CURRENT_STATE.md`
3. `docs/ARCHITECTURE.md`
4. `docs/DATA_CONTRACTS.md`
5. `docs/ROADMAP.md`
6. `docs/PROJECT_JOURNAL.md`
7. component-specific documentation for the task at hand

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

## Security/publication rules

This is a public repository.

Never commit:

- credentials, API tokens, passwords, SSH private keys, or secret files
- production IP addresses or firewall allowlists
- customer-identifying raw logs
- private hostnames or environment-specific access paths unless explicitly sanitized for publication
- restricted historical branding or organization identifiers

Use RFC documentation address space and synthetic hostnames in examples.

## Current resume point

The next normalizer task is the isolated Cisco NX-OS OSPF/OSPFv3 retransmission parser. Before writing or registering it, verify the current live development checkout and full test baseline.

Known generic-family behavior must be preserved:

```text
OSPF  -> event_family ospf
OSPFv3 -> event_family ospfv3
```

Do not let Arista EOS or Cisco IOS XR OSPF events enter the NX-OS parser.

The production normalizer path has not yet been switched over; transitional GX10 enrichment remains available as a parity reference.
