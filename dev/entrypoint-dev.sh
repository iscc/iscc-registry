#!/usr/bin/env bash
set -euo pipefail

until poetry run python -m dev.db_check; do
    echo "Still waiting for database…"
    sleep 1
done

if [ "${AUTO_MIGRATE_AND_INSTALL-false}" == "true" ]; then
    poetry run poe demo
fi

exec "$@"
