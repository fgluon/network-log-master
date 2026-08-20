# Collector Component

The collector/log-server component is the durable observability control point.

Responsibilities:

- receive network syslog
- preserve raw observations
- normalize deterministic event structure
- store observability data in ClickHouse
- present dashboards and drilldowns through Grafana
- maintain the compressed backlog consumed by GX10
- validate AI-result files before durable ingestion
- retain unknown-event inventory and replay material

Important implementation contracts:

- capture first; parser failure must not drop an event
- raw log storage remains independent of AI decisions
- Grafana presentation uses semantic views rather than mutating the raw schema for display concerns
- GX10 never receives direct authority to write ClickHouse records
- production normalizer cutover waits for fixture/replay/parity proof

Representative durable tables currently include raw syslog observations and validated AI updates. Exact production addresses, credentials, allowlists, and private host details are intentionally excluded from this public repository.
