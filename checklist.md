# Must-Have Implementation Checklist

Goal: finish, test, Dockerize, and deploy within a 3-hour interview.

1) Project setup
- Files to create/edit: `requirements.txt`, `README.md`, `.gitignore`, `.env.example`
- Acceptance criteria: `pip install -r requirements.txt` succeeds and README quickstart works.
- Verify:
```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt
```

2) App skeleton
- Files to create/edit: `app/main.py`, `app/config.py`, `app/routes.py`, `app/logging.py`
- Acceptance criteria: `GET /health` returns 200 JSON `{"status":"ok"}`.
- Verify:
```bash
.venv/bin/uvicorn app.main:app --port 8000
curl -sS http://localhost:8000/health
```

3) Data model and persistence
- Files to create/edit: `app/db.py`, `app/models.py`
- Acceptance criteria: app initializes SQLite `data.db` and creates `events` table with unique `event_id`.
- Verify:
```bash
# start app to allow schema init
.venv/bin/uvicorn app.main:app --port 8000 &
ls -l data.db
sqlite3 data.db ".tables"
```

4) API endpoints
- Files to create/edit: `app/schemas.py`, `app/routers/events.py`, update `app/main.py` to include routers
- Acceptance criteria: `POST /events`, `GET /events`, `GET /summaries` respond per SPEC with correct JSON.
- Verify:
```bash
curl -sS -X POST http://localhost:8000/events -H "Content-Type: application/json" -d '{"event_id":"e1","customer_id":"c1","resource_id":"r1","resource_type":"vm","usage":1.5,"usage_unit":"vcpu-hour","timestamp":"2026-06-20T00:00:00Z"}'
curl -sS "http://localhost:8000/events?customer_id=c1"
curl -sS "http://localhost:8000/summaries?customer_id=c1&granularity=day"
```

5) Duplicate event handling
- Files to create/edit: `app/models.py` (unique constraint), `app/routers/events.py` (conflict handling)
- Acceptance criteria: second POST with same `event_id` does not create a new row; API returns duplicate response per SPEC.
- Verify:
```bash
# POST first time
curl -X POST http://localhost:8000/events -H "Content-Type: application/json" -d '{"event_id":"dup1",...}'
# POST duplicate
curl -i -X POST http://localhost:8000/events -H "Content-Type: application/json" -d '{"event_id":"dup1",...}'
# Confirm DB row count = 1
sqlite3 data.db "SELECT COUNT(*) FROM events WHERE event_id='dup1';"
```

6) Tests
- Files to create/edit: `tests/test_events.py`, `tests/test_summaries.py`, `pytest.ini`
- Acceptance criteria: tests cover validation, dedupe, persistence, summary correctness; `pytest` passes using SQLite in-memory.
- Verify:
```bash
.venv/bin/pytest -q
```

7) Dockerfile
- Files to create/edit: `Dockerfile`, `.dockerignore`
- Acceptance criteria: image builds and container serves `/health` on port 8000.
- Verify:
```bash
docker build -t usage-service:local .
docker run --rm -p 8000:8000 usage-service:local &
curl -sS http://localhost:8000/health
```

8) README
- Files to create/edit: `README.md` (Quickstart, API examples, tests, Docker, DO deployment notes)
- Acceptance criteria: reviewer can follow README to run app locally and run tests.
- Verify: manually follow README steps to start app and run tests.

9) DigitalOcean deployment
- Files to create/edit: `app.yaml`, `deploy/README-do.md` (optional)
- Acceptance criteria: deployed app responds to `/health` OR a fully-documented deployment attempt with pushed image tag and `doctl` commands.
- Verify (deployed):
```bash
curl -sS https://<your-app-domain>/health
# or verify app exists via doctl
doctl apps list
```

---

Folder structure to create (scaffold only, no code files yet):

- `app/`
  - `app/routers/`
  - `app/models/`
  - `app/schemas/`
  - `app/db/`
- `tests/`
- `deploy/`

Create these directories before coding.

---

If this looks good I will create the folders now (no code).