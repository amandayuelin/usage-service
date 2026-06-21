# Usage Events Service (MVP)

Minimal FastAPI service to ingest usage events, prevent duplicates, and provide summaries.

Quickstart

```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/uvicorn app.main:app --port 8000
```

Health

```bash
curl http://localhost:8000/health
```

Run tests

```bash
.venv/bin/pytest -q
```

Docker

```bash
docker build -t usage-service:local .
docker run --rm -p 8000:8000 usage-service:local
```

Demo (deployed)

The service is deployed on DigitalOcean App Platform for the interview demo.

1. Health check:

```bash
curl -i https://amanda-usage-api-hguu4.ondigitalocean.app/health
```

2. Smoke test (POST and GET):

```bash
curl -s -X POST https://amanda-usage-api-hguu4.ondigitalocean.app/events \
	-H "Content-Type: application/json" \
	-d '{"event_id":"smoke-1","customer_id":"demo","resource_id":"r1","resource_type":"vm","usage":1.5,"usage_unit":"vcpu-hour","timestamp":"2026-06-20T00:00:00Z"}' | jq

curl -s "https://amanda-usage-api-hguu4.ondigitalocean.app/events?customer_id=demo" | jq
```

3. Local demo script:

```bash
./scripts/demo.sh
```

CI

This repo includes a minimal GitHub Actions workflow to run tests on push and PR to `main` in `.github/workflows/ci.yml`.

Deployment

See `deploy/README-do.md` and `app.yaml` for DigitalOcean App Platform instructions.
