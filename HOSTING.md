# Hosting Beacon (production)

Static site packaged as a **Docker Compose** stack (nginx:alpine). GitHub Actions rsyncs the tree and runs `docker compose up --build -d` on the VPS.

Production target:

- VPS `root@74.208.35.191` (`zen88` / `ws`) → `/var/www/beacon`
- Container published as `127.0.0.1:4843` (`HOST_BIND=127.0.0.1`, host `PORT=4843` → container `:80`)
- Host nginx (`beacon`) reverse-proxies `/` to that loopback port
- Public URL: **https://beacon.adavis.cloud** (Let's Encrypt via certbot after DNS)
- Same port family as ocean-market (`:4840`), chllc (`:4841`), canopy-goods (`:4842`)

## DNS

Create an **A record**: `beacon.adavis.cloud` → `74.208.35.191`

Until DNS exists you can still verify on the VPS:

```bash
curl -sS -H 'Host: beacon.adavis.cloud' http://127.0.0.1/
curl -sS http://127.0.0.1:4843/healthz
curl -sS -o /dev/null -w '%{http_code}\n' http://127.0.0.1:4843/downloads/beacon-cmmc-readiness-checklist.pdf
```

## Server requirements

- Linux VPS (Ubuntu on zen88)
- Docker Engine + Compose v2
- nginx as reverse proxy
- You do **not** need Node.js on the host

## 1. Upload

```bash
HOST=74.208.35.191 REMOTE_USER=root REMOTE_DIR=/var/www/beacon bash scripts/deploy.sh
```

Prefer running this from **tetraschool** (neon key authorized on zen88). From this box, set `SSH_KEY` to a key that can reach `root@74.208.35.191`.

## 2. Environment

`scripts/deploy.sh` writes `/var/www/beacon/.env`:

```env
HOST_BIND=127.0.0.1
PORT=4843
```

No application secrets are required for this static site. Do not commit secrets.

## 3. Start the stack

```bash
cd /var/www/beacon
docker compose up --build -d
docker compose ps
curl -sS http://127.0.0.1:4843/healthz
```

## 4. Reverse proxy + HTTPS

First-install HTTP template: `deploy/nginx-beacon.conf` → `/etc/nginx/sites-available/beacon`.

`scripts/deploy.sh` will **not** overwrite the live site once `ssl_certificate` is present (certbot-managed).

```bash
# first install only (also done by deploy.sh)
sudo cp deploy/nginx-beacon.conf /etc/nginx/sites-available/beacon
sudo ln -sfn /etc/nginx/sites-available/beacon /etc/nginx/sites-enabled/beacon
sudo nginx -t && sudo systemctl reload nginx

# after DNS A record exists:
sudo certbot --nginx -d beacon.adavis.cloud --redirect
```

## Updating later

Push to `main` (GitHub Actions Deploy workflow) or run `scripts/deploy.sh`.

| Command | Purpose |
|---------|---------|
| `docker compose ps` | Container status |
| `docker compose logs -f web` | Tail logs |
| `docker compose up --build -d` | Rebuild and restart after a deploy |
| `docker compose down` | Stop without deleting images |

## Checklist PDF

Served at: `/downloads/beacon-cmmc-readiness-checklist.pdf`
