# Grafana

## Role

Grafana is the presentation layer for observability and AI results. It does not own incident truth, correlation state, or durable AI working memory.

## Data-source pattern

Grafana reads network logs through a semantic ClickHouse view rather than requiring the raw storage table to contain presentation-specific fields.

The log-oriented datasource maps semantic fields such as:

- time -> normalized event timestamp
- level -> normalized severity/level
- body -> log message body
- context -> device identity such as hostname/source address/device label

This keeps display concerns separate from raw storage and replay contracts.

## Drilldown behavior

The current dashboard design supports contextual drilldowns from summary panels into underlying device logs. Proven patterns include:

- BGP summary -> BGP logs for the selected device
- OSPF summary -> OSPF logs for the selected device
- Top Devices -> all logs for the selected device
- Severity summary -> logs for the clicked severity

Drilldowns preserve the dashboard time range.

For severity drilldowns, the clicked field value is used directly. A series-name variable is not used because it resolves to the query series identifier rather than the semantic severity value.

## NOC-view rule

The primary NOC dashboard should remain a high-signal operational view. It should not contain a permanent full raw-log panel.

Raw logs remain available through drilldowns when investigation requires them.

## AI presentation

AI panels should be added only after incident and AI-result contracts stabilize.

The intended pattern is:

1. deterministic incident/evidence state remains authoritative outside Grafana
2. validated AI result records are stored in ClickHouse
3. Grafana presents summaries, status, severity, and explanations
4. operators retain drilldown access to the underlying raw observations

Grafana must not become the incident state database or a substitute for deterministic correlation.

## Change discipline

When changing dashboard links or datasource mappings:

- verify the actual clicked field names in the returned dataset
- preserve time-range context
- test at least one positive drilldown end to end
- avoid modifying the raw storage schema solely for formatting convenience
