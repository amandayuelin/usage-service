# SPEC: Usage Events Ingestion & Summaries Service

**Restatement of requirements**

Build a small REST API service that ingests cloud resource usage events, prevents duplicate ingestion, stores events, and exposes query endpoints and usage summaries per customer. Deliverables: working REST API, automated tests, README, Dockerfile, and service deployed to DigitalOcean (or documented deployment attempt) within a 3-hour interview window.

**Assumptions (to confirm with interviewer)**
- Each event includes a globally-unique `event_id` supplied by producers and is the deduplication key.
- Summaries are computed by customer over configurable time windows (day/week/month). Minimal implement: daily summaries.
- No strict multi-tenant isolation beyond `customer_id` filter.
- Small scale: SQLite for dev/test; instructions to replace with Postgres for production.
- Authentication is out of scope unless interviewer asks for it.

**Clarifying questions to ask the interviewer**
1. Is `event_id` guaranteed unique across all producers, and should it be the dedupe key? If not, what dedupe strategy?  
2. Which summary windows are required (daily, weekly, monthly)? Default to daily.  
3. What fields must each event include; are there required resource types or a schema we must follow?  
4. Expected query patterns and cardinality (to choose indexes/storage): real-time queries, or offline batch queries?  
5. Any authentication, rate-limiting, or retention/archival policies required?  
6. Preferred DB for production (Postgres recommended) and whether migrations are expected.

**Minimal production-minded API contract (OpenAPI-esque)**

- Health
  - GET /health
    - 200: {"status":"ok"}

- Ingest event
  - POST /events
  - Description: Accept a single usage event (idempotent by `event_id`).
  - Request JSON:
    {
      "event_id": "string",            # unique id for dedupe
      "customer_id": "string",         # customer identifier
      "resource_id": "string",         # resource identifier
      "resource_type": "string",       # enum: e.g., vm, db, storage
      "usage": number,                   # usage amount (float)
      "usage_unit": "string",          # e.g., vcpu-hour, GB-month
      "timestamp": "ISO-8601 string",  # when usage occurred
      "metadata": { ... }                # optional
    }
  - Responses:
    - 201 Created: {"status":"created","event_id":"..."}
    - 200 OK: {"status":"duplicate","event_id":"..."} (if already ingested)
    - 400 Bad Request: validation errors

- Query events
  - GET /events
  - Query params: `customer_id` (required), `start`, `end` (ISO dates), `limit`, `offset`
  - 200: {"events": [...], "limit": n, "offset": m}

- Usage summaries
  - GET /summaries
  - Query params: `customer_id` (required), `start`, `end`, `granularity` (day|week|month) (default=day)
  - 200: {"customer_id":"...","granularity":"day","buckets":[{"start":"...","end":"...","usage_total":n}]}

Notes: All responses are JSON. Use proper HTTP codes. Include `X-Request-ID` optional header passthrough for tracing.

**Data model proposal**

- Event
  - id: integer (internal PK, auto)
  - event_id: string (unique, indexed)
  - customer_id: string (indexed)
  - resource_id: string
  - resource_type: string
  - usage: decimal/float
  - usage_unit: string
  - timestamp: timestamp (indexed)
  - metadata: JSON (nullable)
  - ingested_at: timestamp

- (Optional) CustomerSummary (computed on the fly or materialized)
  - customer_id, start_ts, end_ts, usage_total

Persistence: SQLite for dev/test with SQLAlchemy; for production swap to Postgres and add migrations.

**Deduplication strategy**
- Primary approach: require `event_id`; insert with unique constraint on `event_id`. On conflict, treat as duplicate and return 200+duplicate.
- If producers don't supply `event_id`, fallback: hash of (customer_id, resource_id, resource_type, usage, timestamp) with a small TTL window — confirm with interviewer.

**Validation rules**
- `event_id`: required, non-empty string, max length 255
- `customer_id`: required, non-empty string
- `resource_id`: required, non-empty string
- `resource_type`: required, non-empty string (allow free-form, but validate non-empty)
- `usage`: required, numeric >= 0
- `usage_unit`: required, non-empty string
- `timestamp`: required, valid ISO-8601 datetime (UTC recommended). Accept offsets.
- `metadata`: optional JSON object

**Error response format**
- All errors follow this JSON shape:
  {
    "error": {
      "code": "string_code",      # e.g., "validation_error", "duplicate_event"
      "message": "Human readable message",
      "details": { ... }           # optional map of field->error
    },
    "request_id": "..."           # echo or generated for tracing (optional)
  }

HTTP status codes map to `error.code` (400->validation_error, 409->conflict if needed, 500->internal_error).

**Observability**
- Emit `X-Request-ID` if provided, otherwise generate and include in responses.
- Logs structure: JSON logs with at least `ts`, `level`, `msg`, `request_id`, `customer_id` when present.
- Basic metrics to expose via `/metrics` (Prometheus) if time permits; otherwise provide guidance in README.

**Test plan**
- Unit tests (pytest):
  - Validation: missing/invalid fields produce 400 with details
  - Deduplication: POST duplicate `event_id` returns duplicate response and does not create second row
  - Persistence: POST creates event; GET /events returns it
  - Summaries: ingest sample events and assert `GET /summaries` totals per bucket
- Integration tests:
  - Start app with test DB (SQLite in-memory or temp file) and exercise end-to-end flow
- CI: run `pytest` in container; tests must be fast (< 1-2 min)

**Implementation plan & 3-hour timebox (stop coding and start deployment approx at ~2hr mark)**

Time allocation (total 3 hours):
- 00:00–00:15 (15m): Finalize spec & repo scaffolding (we're here). Confirm assumptions/questions.
- 00:15–01:30 (75m): Implement core service (FastAPI): models, `POST /events`, dedupe, `GET /events`, `GET /summaries` (daily), health endpoint. Minimal logging and env config.
- 01:30–02:00 (30m): Write tests covering validation, dedupe, summary logic. Run and fix failures.
- 02:00 (stop coding)–02:05 (5m): Prepare Dockerfile and build instructions; freeze code.
- 02:05–03:00 (55m): Deployment to DigitalOcean (or document attempt). If deployment blocked, document step-by-step and include artifacts (Dockerfile, app spec).

Stop-coding trigger: when core endpoints are passing tests locally (unit/integration), and Docker image builds successfully — stop coding and begin deployment.

**DigitalOcean deployment plan (complete within 55 minutes after coding)**
Prerequisites (ask interviewer):
- DigitalOcean account and API token with App Platform or registry permissions, or provide credentials.
- `doctl` installed locally (or use web UI). Otherwise use Docker Hub or GitHub Container Registry.

Simple App Platform flow (recommended):
1. Create Docker image locally: `docker build -t registry.digitalocean.com/<registry>/usage-service:latest .`
2. Push to DO Container Registry (or Docker Hub) after `doctl registry create` and `docker login` to DO registry.
3. Create `app.yaml` minimal spec for DigitalOcean App Platform that uses image from registry, exposes port 8000, sets environment variables (e.g., `DATABASE_URL`, `ENV=production`).
4. Use `doctl apps create --spec app.yaml` to deploy, or create App via DigitalOcean web UI pointing to container image.
5. Run migrations (for SQLite this is a no-op; for Postgres run migration container command or include startup script to run migrations.)
6. Verify `/health` and sample endpoints.

Alternative (Droplet + Docker):
- Provision a small Droplet, SSH, install Docker, run the image with env vars and optional `docker-compose`.

Common blockers & mitigations
- No DO account or no token: push image to Docker Hub and show `docker run` commands and App Platform `app.yaml` — counts as documented deployment attempt.
- Registry permission issues: provide full `Dockerfile`, `app.yaml`, and step-by-step commands to run manually.

**Config via environment variables**
- `DATABASE_URL` (default sqlite:///./data.db)
- `PORT` (default 8000)
- `LOG_LEVEL` (default info)
- `DOCKER_ENV` or `ENV` (development/production)

**README minimal contents (to include)**
- Project description & API summary
- Quickstart (local): python venv, install deps, run uvicorn, example curl commands
- Tests: `pytest` instructions
- Docker build and run example
- Deployment notes for DigitalOcean (app.yaml example and `doctl` commands)

**Trade-offs and follow-up improvements**
- Use SQLite for speed and simplicity in interview; production should use Postgres with migrations and connection pooling.
- Dedup by `event_id` assumes producers supply stable IDs; if not possible, need idempotency keys or a time-windowed dedupe layer (more complex).
- Summaries are computed on-the-fly which is simple but may be slow at scale — consider periodic batch aggregation (worker + materialized tables) for high-volume workloads.
- Add authentication, authorization, rate-limiting, and quotas for multi-tenant safety.
- Add observability: Prometheus metrics, distributed tracing (Jaeger), structured logs to a central sink.
- Add schema migrations and CI/CD pipeline to automate tests and deployments.

**Files to create next (if you confirm)**
- `SPEC.md` (this file)
- `README.md` (scaffold)
- `app/` FastAPI app scaffold: `main.py`, `models.py`, `schemas.py`, `db.py`, `config.py`
- `tests/` pytest cases
- `Dockerfile`, `.dockerignore`
- `app.yaml` (DigitalOcean App spec)

---

Please review and confirm assumptions or answer the clarifying questions you want to lock in. After you confirm, I will scaffold the project files (keeping scope minimal) and implement the core endpoints until the 2-hour mark, then start deployment steps as planned.