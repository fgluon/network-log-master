#!/usr/bin/env bash
set -euo pipefail

die()
{
    echo "FAIL: $*" >&2
    exit 1
}

SCRIPT_DIR="$(
    cd "$(
        dirname "${BASH_SOURCE[0]}"
    )" \
        && pwd
)"

set -a
. "$SCRIPT_DIR/versions.env"
set +a

require_version()
{
    local package="$1"
    local expected="$2"
    local actual

    actual="$(
        dpkg-query \
            -W \
            -f='${Version}' \
            "$package" \
            2>/dev/null
    )" \
        || die "$package is not installed"

    [ "$actual" = "$expected" ] \
        || die "$package expected=$expected actual=$actual"

    echo \
        "package=$package" \
        "version=$actual"
}

require_version \
    vector \
    "$VECTOR_VERSION"

require_version \
    clickhouse-server \
    "$CLICKHOUSE_VERSION"

require_version \
    clickhouse-client \
    "$CLICKHOUSE_VERSION"

require_version \
    grafana \
    "$GRAFANA_VERSION"

actual_certbot="$(
    /usr/local/bin/certbot --version \
        | awk '{print $2}'
)"

[ "$actual_certbot" = "$CERTBOT_VERSION" ] \
    || die \
        "certbot expected=$CERTBOT_VERSION actual=$actual_certbot"

echo "certbot_version=$actual_certbot"

PLUGIN_JSON="/var/lib/grafana/plugins/grafana-clickhouse-datasource/plugin.json"

[ -f "$PLUGIN_JSON" ] \
    || die "Grafana ClickHouse plugin is missing"

python3 - "$PLUGIN_JSON" "$GRAFANA_CLICKHOUSE_PLUGIN_VERSION" <<'PY'
from pathlib import Path
import json
import sys

path = Path(sys.argv[1])
expected = sys.argv[2]

data = json.loads(
    path.read_text(
        encoding="utf-8",
        errors="strict",
    )
)

plugin_id = str(
    data.get(
        "id",
        "",
    )
)

actual = str(
    (data.get("info") or {}).get(
        "version",
        "",
    )
)

if plugin_id != "grafana-clickhouse-datasource":
    raise SystemExit(
        "FAIL: unexpected Grafana plugin ID"
    )

if actual != expected:
    raise SystemExit(
        f"FAIL: Grafana plugin expected={expected} "
        f"actual={actual}"
    )

print(
    f"grafana_plugin={plugin_id} "
    f"version={actual}"
)
PY

for file in \
    /etc/apt/sources.list.d/vector.list \
    /etc/apt/sources.list.d/clickhouse.list \
    /etc/apt/sources.list.d/grafana.list
do
    [ -s "$file" ] \
        || die "repository definition missing: $file"
done

echo "COLLECTOR_PACKAGE_VERIFY=PASS"
