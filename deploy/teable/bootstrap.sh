#!/usr/bin/env bash
set -euo pipefail

source_dir="${1:?Usage: bootstrap.sh SOURCE_DIR [TARGET_DIR]}"
target_dir="${2:-/opt/reborn/teable}"
service_user="${SERVICE_USER:-reborn}"

if [[ "$(id -u)" -ne 0 ]]; then
  echo 'Run this script as root.' >&2
  exit 1
fi

if ! id "$service_user" >/dev/null 2>&1; then
  echo "Missing service user: $service_user" >&2
  exit 1
fi

install -d -m 0750 -o "$service_user" -g "$service_user" "$target_dir"
install -m 0644 "$source_dir/compose.yaml" "$target_dir/compose.yaml"
install -m 0750 "$source_dir/backup.sh" "$target_dir/backup.sh"
sed -i 's/\r$//' "$target_dir/compose.yaml" "$target_dir/backup.sh"

if [[ ! -e "$target_dir/.env" ]]; then
  umask 077
  postgres_password="$(openssl rand -hex 32)"
  redis_password="$(openssl rand -hex 32)"
  secret_key="$(openssl rand -hex 48)"

  cat > "$target_dir/.env" <<EOF
TEABLE_IMAGE=ghcr.io/teableio/teable:release.2026-07-06T02-39-43Z.2116
TEABLE_BIND_ADDRESS=127.0.0.1
TEABLE_PORT=3000
PUBLIC_ORIGIN=http://localhost:3000

POSTGRES_HOST=teable-db
POSTGRES_PORT=5432
POSTGRES_BIND_ADDRESS=127.0.0.1
POSTGRES_PUBLISHED_PORT=5432
POSTGRES_DB=teable
POSTGRES_USER=teable
POSTGRES_PASSWORD=$postgres_password

REDIS_HOST=teable-cache
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=$redis_password

SECRET_KEY=$secret_key
PRISMA_DATABASE_URL=postgresql://teable:$postgres_password@teable-db:5432/teable
BACKEND_CACHE_PROVIDER=redis
BACKEND_CACHE_REDIS_URI=redis://default:$redis_password@teable-cache:6379/0
EOF

  chown "$service_user:$service_user" "$target_dir/.env"
  chmod 0600 "$target_dir/.env"
  echo "Created new secrets in $target_dir/.env"
else
  echo "Preserved existing secrets in $target_dir/.env"
fi

install -d -m 0750 -o "$service_user" -g "$service_user" \
  "$target_dir/data" "$target_dir/backups"
chown "$service_user:$service_user" \
  "$target_dir/compose.yaml" "$target_dir/backup.sh"

echo "Teable runtime prepared in $target_dir"
