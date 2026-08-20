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
