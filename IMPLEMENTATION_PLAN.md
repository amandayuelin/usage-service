# Implementation Plan — Must-Have (3-hour timebox)

Purpose: a focused, timeboxed plan to implement, test, Dockerize, and deploy the Usage Events service to DigitalOcean within 3 hours. Follow `SPEC.md` and `.github/copilot-instructions.md` rules: spec first, small increments, tests, Docker, DO deployment.

High-level timeboxing (3 hours)
- 00:00–00:15 — Finalize spec & scaffold (confirm assumptions)
- 00:15–01:30 — Core implementation (API + persistence)
- 01:30–02:00 — Tests and fixes
- 02:00–02:05 — Freeze code and prepare Dockerfile
- 02:05–03:00 — Build image and deploy to DigitalOcean App Platform (or document attempt)

Task order (must-have minimal path)

1) Project setup (0–10m)
- Files to create/edit:
  - `requirements.txt`
  - `README.md` (scaffold)
  - `.gitignore`, `.env.example`
- Acceptance criteria: dependencies listed and developer can install them.
- Verify:
```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt
```
- Skip if short on time: polish README; keep a minimal README with commands.

2) App skeleton + health (5–15m)
- Files to create/edit:
  - `app/main.py` (FastAPI app and router mount)
  - `app/config.py` (env config)
  - `app/logging.py` (basic JSON / structured logging)
- Acceptance criteria: `GET /health` returns 200 `{ "status": "ok" }`.
- Verify:
```bash
.venv/bin/uvicorn app.main:app --port 8000
curl -sS http://localhost:8000/health
```
- Skip if short on time: no extras; ensure health is present.

3) Data model & persistence (20–35m)
- Files to create/edit:
  - `app/db.py` (SQLAlchemy engine/session and init)
  - `app/models.py` (Event model with unique `event_id`)
- Acceptance criteria: app can create a SQLite DB (default `./data.db`) and an `events` table with unique constraint on `event_id`.
- Verify:
```bash
# start app to run schema init
.venv/bin/uvicorn app.main:app --port 8000 &
ls -l data.db
sqlite3 data.db ".tables"
```
- Skip if short on time: use SQLite in-memory for tests; still ensure models compile.

4) API: ingest and query (30–60m)
- Files to create/edit:
  - `app/schemas.py` (Pydantic request/response models)
  - `app/routers/events.py` (POST /events, GET /events)
  - update `app/main.py` to include routers
- Acceptance criteria: `POST /events` validates payload and stores event; `GET /events` supports `customer_id`, `start`, `end`, `limit`, `offset` and returns expected JSON.
- Verify:
```bash
curl -sS -X POST http://localhost:8000/events -H "Content-Type: application/json" -d '{"event_id":"e1","customer_id":"c1","resource_id":"r1","resource_type":"vm","usage":1.5,"usage_unit":"vcpu-hour","timestamp":"2026-06-20T00:00:00Z"}'
curl -sS "http://localhost:8000/events?customer_id=c1"
```
- Skip if short on time: implement only POST and minimal GET by customer_id.

5) API: summaries (20–30m)
- Files to create/edit:
  - extend `app/routers/events.py` or create `app/routers/summaries.py`
- Acceptance criteria: `GET /summaries?customer_id=...&granularity=day` returns daily buckets with `usage_total`.
- Verify:
```bash
curl -sS "http://localhost:8000/summaries?customer_id=c1&granularity=day"
```
- Skip if short on time: return a simple total usage for the date range instead of bucketed results.

6) Duplicate handling (10–15m)
- Files to create/edit:
  - `app/models.py` (unique index)
  - `app/routers/events.py` (handle IntegrityError on insert)
- Acceptance criteria: re-sending same `event_id` does not create another row; API returns duplicate marker per SPEC (200 with `{"status":"duplicate"}` or 409 with standard error format). Prefer 200 duplicate to be idempotent.
- Verify:
```bash
curl -sS -X POST http://localhost:8000/events -H "Content-Type: application/json" -d '{"event_id":"dup1",...}'
curl -i -sS -X POST http://localhost:8000/events -H "Content-Type: application/json" -d '{"event_id":"dup1",...}'
sqlite3 data.db "SELECT COUNT(*) FROM events WHERE event_id='dup1';"
```
- Skip if short on time: return 409 conflict but still ensure DB unique constraint prevents duplication.

7) Tests (20–30m)
- Files to create/edit:
  - `tests/test_health.py`
  - `tests/test_events.py` (validation + dedupe)
  - `tests/test_summaries.py`
  - `pytest.ini`
- Acceptance criteria: tests cover health, ingest success, validation failure, duplicate handling, and summary correctness; `pytest` passes locally against SQLite in-memory DB.
- Verify:
```bash
.venv/bin/pytest -q
```
- Skip if short on time: reduce integration tests — keep unit tests for ingest + dedupe.

8) Dockerfile (15–25m)
- Files to create/edit:
  - `Dockerfile`
  - `.dockerignore`
- Acceptance criteria: image builds and container serves `/health` on port 8000.
- Verify:
```bash
docker build -t usage-service:local .
docker run --rm -p 8000:8000 usage-service:local &
curl -sS http://localhost:8000/health
```
- Skip if short on time: produce Dockerfile but postpone multi-stage optimization.

9) README polish (5–10m)
- Files to create/edit:
  - `README.md` (add examples for local run, tests, Docker, and DO deploy notes)
- Acceptance criteria: reviewer can follow to run app and tests.
- Verify: manually follow quickstart steps.
- Skip if short on time: keep README minimal but accurate.

10) DigitalOcean deployment (remaining ~55m)
- Files to create/edit:
  - `app.yaml` (DigitalOcean App Platform spec)
  - `deploy/README-do.md` (commands and notes)
- Deployment flow (App Platform, preferred):
  1. Build Docker image locally: `docker build -t registry.digitalocean.com/<registry>/usage-service:latest .`
  2. Push to DO registry (or Docker Hub) and create app using `doctl` or the web UI:
     - `doctl registry login`
     - `docker push registry.digitalocean.com/<registry>/usage-service:latest`
     - create `app.yaml` pointing to the image and env vars (`DATABASE_URL`, `PORT`)
     - `doctl apps create --spec app.yaml`
  3. Verify `/health` on deployed URL.
- Acceptance criteria: a live URL responding 200 on `/health`, or a documented deployment attempt with pushed image and `app.yaml` if credentials unavailable.
- Verify:
```bash
curl -sS https://<your-app-domain>/health
doctl apps list
```
- Skip if short on time: if unable to push to DO registry in time, push to Docker Hub and include full `app.yaml` + exact `doctl` commands in `deploy/README-do.md` as the documented deployment attempt.

What to skip if time is running out (priority order)
- Skip advanced features: Prometheus metrics, tracing, auth, pagination beyond basics, weekly/monthly aggregation (implement only daily), background workers or Celery.
- Keep SQLite; do not convert to Postgres unless trivial.
- Keep logging simple; avoid external sinks.

Stop-coding rule
- When core endpoints and tests for validation + dedupe + health pass locally and a Docker image builds, stop coding and begin deployment steps (target around 02:00 into timebox).

Notes & assumptions to lock before coding (confirm with interviewer)
- `event_id` is provided and globally unique (dedupe key). If not, agree on fallback dedupe logic.
- Required summary granularity: implement `day` by default.
- No authentication required unless requested.
- Use SQLite for interview; document switch to Postgres for production.

---

Files/folders touched by this plan (scaffolded):
- `app/`, `app/routers/`, `app/models/`, `app/schemas/`, `app/db/`, `tests/`, `deploy/`

Follow-up: If you confirm assumptions, I will scaffold minimal code files in small increments starting with the health endpoint.
