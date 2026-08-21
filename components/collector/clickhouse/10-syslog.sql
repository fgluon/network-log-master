CREATE TABLE observability.syslog
(
    `timestamp` DateTime64(9, 'UTC'),
    `ingest_timestamp` DateTime64(9, 'UTC'),
    `device_timestamp` Nullable(DateTime64(9, 'UTC')),
    `collector_local_time` String,
    `source_ip` String,
    `source_port` UInt16 DEFAULT 0,
    `hostname` String DEFAULT '',
    `host` String DEFAULT '',
    `facility` LowCardinality(String) DEFAULT '',
    `severity` LowCardinality(String) DEFAULT '',
    `appname` String DEFAULT '',
    `message` String DEFAULT '',
    `raw_message` String DEFAULT '',
    `parse_status` LowCardinality(String),
    `source_type` LowCardinality(String) DEFAULT 'syslog',
    `version` UInt8 DEFAULT 0,
    `event_json` String DEFAULT ''
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(timestamp)
ORDER BY (timestamp, source_ip)
TTL timestamp + toIntervalMonth(12)
SETTINGS index_granularity = 8192
