#!/usr/bin/env bash
set -euo pipefail

runtime_dir="${TEABLE_RUNTIME_DIR:-/opt/reborn/teable}"

systemctl start docker
cd "$runtime_dir"
docker compose up -d

# A persistent Windows-side WSL process keeps the lightweight VM alive. Docker
# restart policies handle the individual containers if one of them exits.
exec sleep infinity
