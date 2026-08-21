CREATE VIEW observability.grafana_logs
(
    `timestamp` DateTime64(9, 'UTC'),
    `body` String,
    `level` LowCardinality(String),
    `device` String,
    `hostname` String,
    `source_ip` String,
    `source_port` UInt16,
    `facility` LowCardinality(String),
    `appname` String,
    `message` String,
    `raw_message` String,
    `parse_status` LowCardinality(String),
    `device_timestamp` Nullable(DateTime64(9, 'UTC')),
    `ingest_timestamp` DateTime64(9, 'UTC'),
    `source_type` LowCardinality(String)
)
SQL SECURITY INVOKER
AS SELECT
    timestamp,
    concat('[', if(hostname != '', hostname, source_ip), '] [', source_ip, '] ', message) AS body,
    severity AS level,
    if(hostname != '', hostname, source_ip) AS device,
    hostname,
    source_ip,
    source_port,
    facility,
    appname,
    message,
    raw_message,
    parse_status,
    device_timestamp,
    ingest_timestamp,
    source_type
FROM observability.syslog
