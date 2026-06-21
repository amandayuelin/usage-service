# SPEC: Quota & Usage Service

This document captures the spec, API contract, data model, validation, transaction safety, tests, deployment plan, and trade-offs for a small REST API that manages per-customer quotas and enforces usage limits. The implementation will be a minimal, production-minded FastAPI service using PostgreSQL (configured via `DATABASE_URL`), with tests, Dockerfile, docker-compose, and a deployment path to DigitalOcean App Platform.

1. Concise restatement of requirements
-------------------------------------
- Provide a REST API to: define per-customer quotas for resource types, record usage events, check whether a requested usage increase is allowed, and query current quota and usage status.
- Prevent duplicate usage ingestion when producers retry events.
- Persist to PostgreSQL (use `DATABASE_URL`).
- Deliver: working API, automated tests, README, Dockerfile, docker-compose (Postgres), and deployment to DigitalOcean (or a documented attempt).

2. Clarifying questions to ask the interviewer
---------------------------------------------
- Are resource types a closed enum (e.g., `droplet`, `block_storage`, `bandwidth`, `managed_db`, `load_balancer`) or freeform strings?
- Are quotas simple integer limits (counts) or do some resources use units like bytes or vCPU-hours that need different semantics?
- Do usage events include releases (negative deltas)? If so, is `current` allowed to go down to 0 only (no negatives)?
- Should quotas support time windows (monthly limits) or only absolute counters?
- Must requests be authenticated? (Assume no auth for the interview unless requested.)
- Is strict consistency required for concurrent allocation bursts? (We will implement transactional safety.)

3. Explicit assumptions (if interviewer does not clarify)
-------------------------------------------------------
- Resource types will be a closed enum: `droplet`, `block_storage`, `bandwidth`, `managed_db`, `load_balancer`.
- Quotas are integer limits. Units for some resource types are implied (e.g., bandwidth in MB) and documented.
- Usage events are non-negative increments for the MVP; releases (decrements) are out of scope but noted as follow-up.
- If no quota exists for a customer/resource, the service denies new allocations (fail-closed).
- Clients provide a unique `event_id` for idempotency.
- No authentication in MVP.
- Use SQLAlchemy `create_all` for schema creation in the interview; production should use Alembic.

4. Scope (Must / Should / Nice-to-have)
---------------------------------------
- Must-have
  - FastAPI app with endpoints: create/update quota, record usage (idempotent), check, get status, health.
  - PostgreSQL persistence via `DATABASE_URL` and docker-compose for local development.
  - Tests: health, quota creation, usage ingestion, idempotency, quota enforcement, not-found.
  - Dockerfile and `docker-compose.yml` with Postgres service.
  - README with run/test/deploy instructions.
- Should-have
  - Prometheus metrics endpoint, structured JSON logging, request `trace_id` support.
- Nice-to-have
  - Time-windowed quotas (monthly), releases (decrement), Alembic migrations, RBAC/auth.

5. Minimal but production-minded API contract
--------------------------------------------
Common: JSON only, `Content-Type: application/json`. Use `trace_id`/`X-Request-ID` headers for correlation.

- GET /healthz
  - 200 OK -> {"status":"ok"}

- POST /quotas
  - Request body: { "customer_id": "string", "resource_type": "droplet", "limit": integer }
  - 201 Created -> created quota object
  - 400 validation errors

- GET /quotas/{customer_id}/{resource_type}
  - 200 -> { "customer_id","resource_type","limit","created_at","updated_at" }
  - 404 if not found

- POST /usage
  - Request body: { "event_id": "string", "customer_id": "string", "resource_type": "droplet", "delta": integer }
  - Behavior: idempotent ingestion. If `event_id` already processed, return 200 with prior result. If new, atomically check quota and record.
  - 201 Created -> { "event_id","customer_id","resource_type","delta","allowed": true, "new_total": int }
  - 409 Conflict -> when request would exceed quota (no record created)

- POST /check
  - Request body: { "customer_id","resource_type","delta" }
  - 200 -> { "allowed": true/false, "current": int, "limit": int, "would_be": int }

- GET /usage/{customer_id}/{resource_type}
  - 200 -> { "customer_id","resource_type","current": int, "limit": int|null }

6. PostgreSQL data model proposal
----------------------------------
- Table `quotas`
  - `id` UUID PK
  - `customer_id` TEXT NOT NULL
  - `resource_type` TEXT NOT NULL
  - `limit` BIGINT NOT NULL CHECK (limit >= 0)
  - `created_at`, `updated_at` timestamptz
  - UNIQUE(customer_id, resource_type)
  - Index on (customer_id, resource_type)

- Table `usage_counters`
  - `id` UUID PK
  - `customer_id` TEXT NOT NULL
  - `resource_type` TEXT NOT NULL
  - `current` BIGINT NOT NULL DEFAULT 0
  - `updated_at` timestamptz
  - UNIQUE(customer_id, resource_type)

- Table `usage_events`
  - `id` UUID PK
  - `event_id` TEXT NOT NULL UNIQUE
  - `customer_id` TEXT NOT NULL
  - `resource_type` TEXT NOT NULL
  - `delta` BIGINT NOT NULL
  - `recorded_at` timestamptz
  - Index on (customer_id, resource_type)

Rationale: `usage_events` provides durable deduplication and audit trail; `usage_counters` stores current totals for fast reads and safe transactional updates.

7. Validation rules
-------------------
- `customer_id`: non-empty string, max 255.
- `resource_type`: must be one of allowed enum values.
- `limit`: integer >= 0.
- `delta`: integer > 0 (MVP). If supporting releases, allow negative but ensure `current + delta >= 0`.
- `event_id`: required, non-empty, max 255.

Validation performed with Pydantic schemas; reject invalid requests with 400/422.

8. Duplicate / idempotency behavior
----------------------------------
- Clients MUST supply `event_id` for usage ingestion.
- `usage_events.event_id` has a UNIQUE constraint.
- On POST /usage:
  - Begin DB transaction.
  - Try to insert into `usage_events` with provided `event_id`.
    - If conflict on `event_id` (duplicate), fetch and return previous result (200 OK) — do not reapply delta.
    - If insert succeeds, perform transactional quota check and update `usage_counters`, then commit.
  - Response includes `already_processed: true` for duplicates (or returns prior result payload).

9. Transaction & concurrency considerations for quota enforcement
---------------------------------------------------------------
- One DB transaction per record-and-check operation:
  1. Begin transaction.
 2. SELECT quota row for (customer_id, resource_type).
 3. Upsert or SELECT FOR UPDATE the `usage_counters` row.
 4. Compute `new_total = current + delta`.
 5. If `new_total > quota.limit`, rollback and return 409.
 6. Insert `usage_events` (if not already inserted) and UPDATE `usage_counters` SET current = new_total.
 7. Commit.

- Use `SELECT ... FOR UPDATE` on `usage_counters` to serialize concurrent writers for the same customer/resource. Alternatively use `UPDATE ... RETURNING` with checks.
- Keep transactions short. Default isolation (READ COMMITTED) is acceptable with row-level locking.

10. Error response format
-------------------------
JSON error envelope used for all failures. Example:

{
  "error": {
    "code": "quota_exceeded",
    "message": "Quota exceeded for resource_type",
    "details": { "customer_id": "...", "resource_type": "...", "limit": 10, "current": 9, "attempted_delta": 2 }
  },
  "trace_id": "uuid"
}

HTTP mapping: 400 validation, 404 not found, 409 quota_exceeded/conflict, 422 unprocessable, 500 internal.

11. Test plan
-------------
- Unit tests (pytest): validate schemas and calculation helpers.
- Integration tests (against docker-compose Postgres):
  - `test_health.py` — GET /healthz returns 200.
  - `test_quota_create_and_get` — create quota, GET returns expected values.
  - `test_usage_ingest_success` — POST /usage with enough quota creates event and updates counter.
  - `test_idempotency` — POST same `event_id` twice: second returns prior result and not double-count.
  - `test_quota_enforcement` — POST exceeding delta fails and does not create event.
  - Concurrency test: parallel clients attempting to consume remaining quota — verify only allowed subset succeed.

- Test harness: pytest fixtures to spin up/tear down schema; use docker-compose Postgres for integration tests.

12. Observability & configuration
---------------------------------
- Environment variables (Pydantic Settings): `DATABASE_URL`, `PORT`, `LOG_LEVEL`, `METRICS_ENABLED`.
- Logging: structured JSON; include `trace_id` and request context.
- Metrics: expose Prometheus `/metrics` (counters for requests, quota_denials, ingestion_success, idempotent_hits).
- Health: `/healthz` will check DB connectivity.

13. Implementation plan (when to stop coding and start deployment)
------------------------------------------------------------------
- Phase A (design) — this doc.
- Phase B (implementation) — scaffold FastAPI, config, DB wiring, models, endpoints, tests. Stop coding when all tests pass locally and Docker image builds.
- Phase C (deployment) — prepare Dockerfile, docker-compose, deploy to DigitalOcean App Platform and validate.

Stop-coding criteria: all core tests pass locally, app builds in Docker, and local smoke tests succeed.

14. DigitalOcean App Platform deployment plan
--------------------------------------------
- Pre-req: Git repo and DO account. Create a managed PostgreSQL cluster and capture `DATABASE_URL`.
- App Platform steps:
  1. Build Docker image and push to DO Container Registry or use App Platform build from repo.
  2. Configure App with `DATABASE_URL`, `PORT`, health check `/healthz`.
  3. Ensure DB tables created at startup (use `create_all` for interview or run a migration step).
  4. Deploy and run smoke tests (create quota, ingest usage, check `/healthz`).

- If DO access is unavailable, provide an `app.yaml` and `doctl` commands plus a Docker image that the interviewer could deploy.

15. Trade-offs and follow-up improvements
---------------------------------------
- Chosen for speed: `create_all` vs Alembic. Follow-up: add migrations.
- Strong consistency via row locks limits per-customer write throughput; follow-up: optimistic concurrency or sharded counters for scale.
- Idempotency via `event_id` is simple; follow-up: time-windowed dedupe or dedupe service for producers that can't provide stable ids.
- Add auth, RBAC, retention policies, and monitoring integrations for production readiness.

Deliverables to create when coding:
- README with run/test/deploy steps
- `Dockerfile` and `docker-compose.yml` with a Postgres service
- FastAPI app under `app/` with `main.py`, `models.py`, `schemas.py`, `db.py`, `config.py`
- Tests under `tests/` and a `pytest.ini`

Next step: confirm the assumptions above (resource enum, units, releases allowed). Once you confirm, I'll scaffold the project and implement the minimal feature set.