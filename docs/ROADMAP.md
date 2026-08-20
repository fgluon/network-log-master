# Roadmap

The project advances through deterministic gates. Each stage should be proven manually and with replay before service automation is expanded.

## Phase 1 - Deterministic normalization on the collector

1. maintain the normalized event schema and fixture harness
2. complete platform-specific enrichment migration from transitional GX10 logic
3. add Cisco NX-OS OSPF/OSPFv3 retransmission parsing
4. add remaining high-value Arista and Cisco IOS XR event families
5. add stable generic fingerprint/entity fallback for unknown events
6. maintain an unknown-event inventory so parser coverage can improve without losing data

Exit gate: synthetic fixtures, negative-path tests, public-repository sanitation, and replay parity are clean.

## Phase 2 - Prepared observation handoff

1. define the normalized collector-to-GX10 file/stream contract
2. prove deterministic serialization and replay
3. prove no raw observation is lost when parsers fail
4. compare new collector-side normalization against the transitional GX10 enrichment path

Exit gate: parity differences are understood and intentional.

## Phase 3 - Deterministic incident engine on GX10

1. implement incident identity and lifecycle
2. implement append-only transitions/evidence
3. implement repeat and burst accounting
4. implement 60-minute, 180-minute, and 24-hour compact context summaries
5. implement replay/idempotency tests
6. exercise manually against stored observations

Exit gate: replaying the same input cannot create duplicate canonical incidents or contradictory state.

## Phase 4 - Steady-state correlation service

1. package the correlator as a managed service
2. add health and backlog telemetry
3. add deterministic LLM wake policy
4. preserve safe failure modes when the model runtime is unavailable

## Phase 5 - Local LLM reasoning

1. assemble compact incident packets only
2. establish model/prompt version tracking
3. require structured output suitable for validation
4. keep deterministic facts separate from model interpretation
5. benchmark latency and usefulness before increasing invocation frequency

## Phase 6 - AI result publication

1. emit validated JSON result files
2. use the existing write-only return transport
3. pass results through the collector validation gate
4. store accepted results in ClickHouse
5. quarantine rejected results with a reason

## Phase 7 - Grafana AI presentation

1. add incident and AI-analysis panels only after contracts stabilize
2. retain drilldowns into the underlying raw logs
3. keep Grafana stateless with respect to incident truth
4. avoid turning the primary NOC view into a permanent raw-log wall

## Phase 8 - Consolidation and operations

1. move verified component code into this master repository in controlled commits
2. keep public documentation synchronized with deployed behavior
3. add recovery and rebuild runbooks
4. add CI/publication gates for tests, secrets, banned terms, and unsafe fixtures
5. periodically verify documentation against live systems
