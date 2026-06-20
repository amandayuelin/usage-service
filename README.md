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

Deployment

See `deploy/README-do.md` and `app.yaml` for DigitalOcean App Platform instructions.
