# Beacon

**Beacon** is a static microsite by **Canopy Harbor LLC** — plain-language orientation to NIST SP 800-171 and CMMC for modern cloud and hybrid shops.

- Public URL (target): https://beacon.adavis.cloud
- Stack: static HTML/CSS + nginx (Docker Compose), loopback port **4843**
- Checklist PDF: [`downloads/beacon-cmmc-readiness-checklist.pdf`](downloads/beacon-cmmc-readiness-checklist.pdf)

This is educational orientation only — **not legal advice**, not an assessment, and not a substitute for official DoD / NIST publications.

## Local preview

```bash
docker compose up --build -d
curl -sS http://127.0.0.1:4843/healthz
```

Or any static server from the repo root (serve `index.html`, `css/`, `assets/`, `downloads/`).

## Production

See [HOSTING.md](HOSTING.md). Deploy via `scripts/deploy.sh` or the GitHub Actions **Deploy** workflow (`SSH_PRIVATE_KEY` secret).

## Theme

Navy / sage / cream — first readable skin for later bb5 polish.
