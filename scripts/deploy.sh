#!/usr/bin/env bash
# Deploy Beacon over SSH as a Docker Compose (static nginx) stack.
# Required env: HOST, REMOTE_USER, REMOTE_DIR
# Optional: SSH_KEY
set -euo pipefail

HOST="${HOST:?HOST is required}"
REMOTE_USER="${REMOTE_USER:?REMOTE_USER is required}"
REMOTE_DIR="${REMOTE_DIR:?REMOTE_DIR is required}"
SSH_KEY="${SSH_KEY:-}"

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

SSH_OPTS=(-o StrictHostKeyChecking=accept-new)
if [ -n "$SSH_KEY" ]; then
  SSH_OPTS=(-i "$SSH_KEY" -o IdentitiesOnly=yes -o StrictHostKeyChecking=yes)
elif [ -f "$HOME/.ssh/deploy_key" ]; then
  SSH_OPTS=(-i "$HOME/.ssh/deploy_key" -o IdentitiesOnly=yes -o StrictHostKeyChecking=yes)
elif [ -f "$HOME/.ssh/id_ed25519" ]; then
  SSH_OPTS=(-i "$HOME/.ssh/id_ed25519" -o IdentitiesOnly=yes -o StrictHostKeyChecking=accept-new)
fi

ssh_cmd() { ssh "${SSH_OPTS[@]}" "$@"; }
rsync_ssh() { printf 'ssh'; for o in "${SSH_OPTS[@]}"; do printf ' %q' "$o"; done; }

echo "==> Rsync to ${REMOTE_USER}@${HOST}:${REMOTE_DIR}"
ssh_cmd "${REMOTE_USER}@${HOST}" "mkdir -p $(printf '%q' "$REMOTE_DIR")"

rsync -avz \
  -e "$(rsync_ssh)" \
  --exclude .git \
  --exclude .github \
  --exclude .env \
  --exclude .DS_Store \
  Dockerfile \
  docker-compose.yml \
  .dockerignore \
  index.html \
  css \
  assets \
  downloads \
  nginx \
  deploy \
  scripts \
  HOSTING.md \
  README.md \
  "${REMOTE_USER}@${HOST}:${REMOTE_DIR}/"

echo "==> Install Docker stack on server"
ssh_cmd "${REMOTE_USER}@${HOST}" \
  REMOTE_DIR="$REMOTE_DIR" \
  bash -s <<'REMOTE'
set -euo pipefail
cd "${REMOTE_DIR}"

if ! command -v docker >/dev/null 2>&1; then
  echo "==> Installing docker.io + docker-compose-v2"
  export DEBIAN_FRONTEND=noninteractive
  apt-get update -qq
  apt-get install -y docker.io docker-compose-v2
fi
if ! docker compose version >/dev/null 2>&1; then
  echo "ERROR: docker compose plugin not found."
  exit 1
fi

upsert_env() {
  local key="$1" value="$2"
  [ -n "$value" ] || return 0
  touch .env
  if grep -qE "^[[:space:]]*${key}=" .env; then
    tmp="$(mktemp)"
    awk -v k="$key" -v v="$value" '
      BEGIN { done=0 }
      $0 ~ "^[[:space:]]*"k"=" { print k"="v; done=1; next }
      { print }
      END { if (!done) print k"="v }
    ' .env > "$tmp"
    mv "$tmp" .env
  else
    printf '%s=%s\n' "$key" "$value" >> .env
  fi
}

upsert_env HOST_BIND 127.0.0.1
upsert_env PORT 4843
chmod 600 .env 2>/dev/null || true

if command -v nginx >/dev/null 2>&1 && [ -f deploy/nginx-beacon.conf ]; then
  if [ -f /etc/nginx/sites-available/beacon ] && grep -q ssl_certificate /etc/nginx/sites-available/beacon; then
    echo "==> nginx site already has TLS; leaving sites-available/beacon in place"
    ln -sfn /etc/nginx/sites-available/beacon /etc/nginx/sites-enabled/beacon
  else
    echo "==> nginx reverse proxy (HTTP template; run certbot after DNS)"
    cp deploy/nginx-beacon.conf /etc/nginx/sites-available/beacon
    ln -sfn /etc/nginx/sites-available/beacon /etc/nginx/sites-enabled/beacon
  fi
  if nginx -t; then
    systemctl reload nginx
  else
    echo "WARNING: nginx -t failed; did not reload nginx"
  fi
fi

echo "==> docker compose up --build"
docker compose up --build -d --remove-orphans
docker compose ps

APP_PORT=4843
if [ -f .env ]; then
  ENV_PORT="$(grep -E '^[[:space:]]*PORT=' .env | tail -1 | cut -d= -f2- | tr -d '[:space:]' | tr -d \"\' || true)"
  if [ -n "${ENV_PORT:-}" ] && [[ "$ENV_PORT" =~ ^[0-9]+$ ]]; then
    APP_PORT="$ENV_PORT"
  fi
fi
HEALTH_URL="http://127.0.0.1:${APP_PORT}/healthz"
echo "==> Health check ${HEALTH_URL}"
ok=0
for i in $(seq 1 30); do
  sleep 2
  code="$(curl -s -o /dev/null -w '%{http_code}' --connect-timeout 2 --max-time 5 "$HEALTH_URL" || true)"
  echo "  attempt ${i}: HTTP ${code:-000}"
  if [ "$code" = "200" ]; then
    ok=1
    break
  fi
done
if [ "$ok" -ne 1 ]; then
  echo "Health check failed."
  docker compose logs --tail 80 || true
  exit 1
fi
echo "==> Home:"
curl -sS -o /dev/null -w 'home:%{http_code}\n' --max-time 5 "http://127.0.0.1:${APP_PORT}/"
echo "==> PDF:"
curl -sS -o /dev/null -w 'pdf:%{http_code}\n' --max-time 5 "http://127.0.0.1:${APP_PORT}/downloads/beacon-cmmc-readiness-checklist.pdf"
echo "Deploy complete."
REMOTE
