# Normalizer Migration

## Goal

Move deterministic vendor/event normalization from the transitional GX10 enrichment path to the collector-side Python normalizer without changing capture semantics or silently losing event coverage.

This is a controlled migration, not a rewrite-in-place.

## Source precedence during migration

1. live checked-out code and tests
2. live production/transitional behavior used as a parity reference
3. this repository's current-state and component documentation
4. older planning documents

If the live checkout and published component repository differ, stop and reconcile them before consolidation.

## Current verified checkpoint

```text
f95db38 Enable NX-OS ETHPORT parser in default registry
58 tests passing
clean working tree
```

Implemented collector-side parser coverage at this checkpoint:

- Arista EOS BGP adjacency changes
- Cisco IOS XR BGP adjacency changes
- Cisco NX-OS ETHPORT interface state changes

The framework also includes generic capture-first normalization, event-envelope extraction, explicit platform hints/trust boundaries, and fail-open parser dispatch.

## Parity reference

The transitional GX10 enrichment path remains operational and is useful for comparing:

- event family
- vendor/platform interpretation
- protocol
- entity type
- deterministic entity key
- state
- signal type
- structured attributes

It must not be removed until collector-side fixtures and replay establish equivalent or intentionally improved behavior.

## Known intentional improvement

For Cisco NX-OS OSPF retransmission evidence, the transitional process extraction recognizes normal `ospf-N` process names but does not fully preserve `ospfv3-N` process identity.

The collector-side implementation should preserve the generic distinction already proven by the current envelope layer:

```text
OSPF   -> event_family ospf
OSPFv3 -> event_family ospfv3
```

Correcting the OSPFv3 process identity is an intentional parity difference and should be covered by tests.

## Migration gates for each parser

1. inspect real message layouts privately
2. create sanitized synthetic fixtures/tests
3. implement parser behind an explicit platform trust boundary
4. prove normal layouts enrich correctly
5. prove malformed layouts remain generic observations
6. prove future/unknown event codes remain generic
7. prove other platforms cannot enter the parser
8. run the full test suite
9. register in the default parser registry only after isolated tests pass
10. replay representative stored observations
11. compare against transitional GX10 output
12. document intentional differences

## Production cutover gate

Do not wire the collector-side normalizer into the production ingest/handoff path until:

- parser coverage for the selected migration scope is complete
- fixture and negative-path suites pass
- replay is deterministic
- parity differences are understood
- unknown events remain visible and attention-eligible
- raw messages remain replayable
- rollback is straightforward

After cutover proves stable, retire duplicate vendor parsing on GX10 deliberately.
