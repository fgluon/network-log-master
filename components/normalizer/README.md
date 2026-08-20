# Normalizer Component

The normalizer converts capture-first records into deterministic structured network observations while preserving raw replayability.

Current live development coverage includes:

- generic capture-first normalization
- event-code/event-family envelope extraction
- explicit vendor/OS platform hints and trust boundaries
- ordered fail-open parser dispatch
- Arista EOS BGP adjacency parsing
- Cisco IOS XR BGP adjacency parsing
- Cisco NX-OS ETHPORT state parsing

Current verified live checkpoint:

```text
f95db38 Enable NX-OS ETHPORT parser in default registry
58 tests passing
clean working tree
```

Next parser: Cisco NX-OS OSPF/OSPFv3 retransmission degradation. The parser must preserve generic family identity (`ospf` versus `ospfv3`), source-IP fallback when hostname is absent, malformed-layout generic fallback, and cross-platform rejection.

The existing standalone normalizer repository remains the temporary published component source until the live development checkout is reconciled and migrated here.
