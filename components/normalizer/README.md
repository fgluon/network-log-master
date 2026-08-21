# Normalizer Component

The normalizer converts capture-first records into deterministic structured network observations while preserving raw replayability.

This directory is now the active development home for the normalizer inside the master repository. Its standalone repository history was imported here with a history-preserving Git subtree merge.

Consolidation checkpoint:

```text
source checkpoint: f95db38 Enable NX-OS ETHPORT parser in default registry
master import:      8d55320 Import normalizer component history
verification:       58 tests passing from components/normalizer/
```

Current coverage includes:

- generic capture-first normalization
- event-code/event-family envelope extraction
- explicit vendor/OS platform hints and trust boundaries
- ordered fail-open parser dispatch
- Arista EOS BGP adjacency parsing
- Cisco IOS XR BGP adjacency parsing
- Cisco NX-OS ETHPORT state parsing

Next parser task:

- Cisco NX-OS OSPF/OSPFv3 neighbor retransmission degradation

That parser must preserve generic family identity (`ospf` versus `ospfv3`), remain inside the Cisco/NX-OS platform trust boundary, use deterministic neighbor/process identity, and fall back to the generic capture-first path when a message cannot be identified safely.

The former standalone normalizer repository is retained for historical provenance only. New normalizer feature development should occur here.
