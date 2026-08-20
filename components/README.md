# Components

This directory is the long-term home for project components as they are consolidated into the master repository.

Current component boundaries:

- `collector/` - syslog ingress, Vector fan-out, ClickHouse, Grafana, normalizer integration, AI-result validation
- `normalizer/` - deterministic network-event normalization and parser framework
- `gx10/` - secure backlog ingest, deterministic incident engine, rolling context, local LLM orchestration, AI-result emission

Migration rule: do not copy a live component into this repository merely to make the directory look complete. First reconcile the live checkout, current public component repository, tests, and public-safety gates. Then migrate in a traceable commit with provenance documented in the component README.
