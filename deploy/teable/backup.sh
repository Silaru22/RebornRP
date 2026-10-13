#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$script_dir"

if [[ ! -f .env ]]; then
  echo 'Missing deploy/teable/.env' >&2
  exit 1
fi

set -a
source .env
set +a

timestamp="$(date -u +'%Y%m%dT%H%M%SZ')"
backup_dir="$script_dir/backups/$timestamp"
mkdir -p "$backup_dir"

docker compose exec -T teable-db \
  pg_dump --format=custom --no-owner --username "$POSTGRES_USER" "$POSTGRES_DB" \
  > "$backup_dir/teable.pgdump"

tar -C "$script_dir/data" -czf "$backup_dir/teable-assets.tar.gz" teable-assets
sha256sum "$backup_dir/teable.pgdump" "$backup_dir/teable-assets.tar.gz" \
  > "$backup_dir/SHA256SUMS"

echo "Backup created: $backup_dir"
