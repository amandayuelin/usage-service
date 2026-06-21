Generic AI Coding Guardrails for Timed Backend Interview Projects

Use this file as a generic instruction set for GitHub Copilot, Cursor, Claude Code, ChatGPT, or any AI coding assistant during a timed backend backend engineering interview.

This file is intentionally **domain-agnostic**. It does not assume a specific problem such as payments, quotas, metrics, jobs, or inventory. Apply these rules to any REST API project involving data ingestion, processing, storage, querying, and deployment.

---

## 1. Context

This is a timed backend engineering interview project.

The goal is to build a small, working, tested, deployable, production-candidate REST API service within a limited time window.

The expected project type is usually a service that:

- accepts data through an API
- validates input
- stores durable records
- processes or transforms data
- exposes query/status/result endpoints
- includes tests
- can be run locally
- can be containerized and deployed

The goal is **not** to build a toy script.

The goal is also **not** to build a half-finished distributed system.

The correct target is:

> A production-candidate slice: small enough to finish, but structured enough to demonstrate production-ready thinking.

---

## 2. Evaluation Priorities

Optimize for the common interview rubric:

### Engineering Quality

- clean code organization
- sensible validation
- meaningful error handling
- clear API design
- maintainable project structure
- simple but intentional data model

### Testing

- structured automated tests
- validation tests
- API behavior tests
- business logic tests
- error-path tests

### Automation and Workflow

- repeatable local setup
- one-command run/test where possible
- Docker-based workflow
- clear README
- smoke test commands

### Operational Excellence

- health checks
- readiness checks
- request IDs
- structured logging
- environment-based configuration
- safe errors
- stateless API design
- scalability path

---

## 3. Golden Rule

Do not optimize for impressive complexity.

Optimize for a backend service that is:

- correct
- tested
- deployable
- explainable
- maintainable
- observable enough for a first production slice

Build:

```text
production-candidate slice
```

Do not build:

```text
toy script
```

Do not build:

```text
half-finished distributed system
```

---

## 4. Operating Mode for the AI Assistant

Act like a careful senior backend engineer.

For every non-trivial change:

1. Restate the goal.
2. Identify assumptions.
3. Identify risks or ambiguity.
4. Make the smallest useful change.
5. Add or update tests.
6. Provide verification commands.

Do not silently guess important requirements.

Do not overbuild.

Do not rewrite unrelated code.

Do not claim something works unless it has been verified or the verification command is provided.

---

## 5. Spec Before Code

Before implementation, create or update `SPEC.md`.

Keep it concise. It is a build guide, not a long essay.

`SPEC.md` should include:

1. Problem Statement
2. Goals
3. Non-Goals
4. Assumptions
5. API Contract
6. Data Model
7. Processing Rules
8. Idempotency or Duplicate Handling
9. Validation Rules
10. Error Handling
11. Operational Requirements
12. Testing Strategy
13. Automation and Workflow
14. Deployment Plan
15. Scalability Considerations
16. Trade-offs
17. Future Production Improvements

Do not start coding until the API contract and data model are clear enough to implement.

If the problem statement is vague, make reasonable assumptions and write them in `SPEC.md`.

---

## 6. Assumption Rules

Do not silently invent requirements.

When requirements are ambiguous:

- document the assumption
- proceed if the assumption does not materially change the user-facing contract
- ask for clarification only if the ambiguity blocks API design, data modeling, persistence, or deployment

Good assumptions:

```text
Assumption: processing can be synchronous for this time-boxed version.
Assumption: incoming records have a natural duplicate key if the payload includes an external ID.
Assumption: PostgreSQL is preferred, but SQLite may be used as a fallback if deployment risk is high.
Assumption: list endpoints should use pagination.
```

Bad behavior:

```text
Silently adding authentication.
Silently adding a queue and worker.
Silently changing endpoint names.
Silently inventing admin APIs.
Silently switching frameworks.
```

---

## 7. Scope Control

### Must Prioritize

- working REST API
- clean project structure
- validation
- persistence
- processing logic
- duplicate/idempotency handling when applicable
- consistent error responses
- health endpoint
- readiness endpoint
- request ID middleware
- structured request logging
- automated tests
- Dockerfile
- README
- smoke test commands

### Should Add If Time Allows

- Docker Compose
- Makefile
- basic pagination
- basic filtering
- simple deployment notes
- lightweight GitHub Actions skeleton

### Defer Unless Explicitly Required

- Redis
- message queue
- worker service
- dead-letter queue
- Kubernetes
- OAuth
- RBAC
- Prometheus
- Grafana
- OpenTelemetry
- complex CI/CD
- advanced admin UI
- multi-region deployment

Document deferred items as future production improvements instead of implementing them prematurely.

---

## 8. Simplicity Rules

Prefer the simplest design that satisfies the spec and interview rubric.

Prefer:

- Python
- FastAPI
- Pydantic
- SQLAlchemy
- pytest
- Docker
- Docker Compose
- Makefile
- PostgreSQL if feasible
- SQLite fallback if PostgreSQL threatens deployment success

Avoid:

- unnecessary abstractions
- complex framework choices
- speculative architecture
- premature authentication
- distributed systems before the core service works
- refactors that do not directly support the current goal

A simple complete system is better than an ambitious incomplete one.

---

## 9. Architecture Rules

Use a layered architecture.

Recommended structure:

```text
app/
  main.py
  api/
    routes/
      health.py
      resources.py
    dependencies.py
  core/
    config.py
    errors.py
    middleware.py
    logging.py
  db/
    database.py
    models.py
  domain/
    resources/
      schemas.py
      repository.py
      service.py
      processor.py
tests/
  unit/
  api/
Dockerfile
docker-compose.yml
Makefile
requirements.txt
README.md
SPEC.md
```

Responsibilities:

```text
api/routes:
- HTTP concerns only
- parse requests
- call service layer
- return responses

schemas:
- Pydantic request models
- Pydantic response models
- API-boundary validation

service:
- business workflow
- orchestration
- idempotency handling
- transaction coordination

processor:
- deterministic domain logic
- data transformation
- aggregation or calculation rules
- pure functions where possible

repository:
- database reads and writes
- duplicate lookups
- pagination queries

db:
- database engine/session
- SQLAlchemy models

core:
- configuration
- errors
- middleware
- logging
```

Forbidden:

- all logic in `main.py`
- business logic inside route handlers
- raw database queries inside route handlers
- durable state only in memory

---

## 10. API Design Rules

Use predictable REST APIs.

Include these endpoint categories when applicable:

```http
GET  /health
GET  /ready
POST /api/v1/{resources}
GET  /api/v1/{resources}/{id}
GET  /api/v1/{resources}
GET  /api/v1/{resources}/{id}/result
GET  /api/v1/{summary-or-status}
```

Use versioned API paths:

```text
/api/v1
```

List endpoints should support:

```text
limit
offset
```

Enforce a maximum page size from configuration.

Do not create unnecessary admin endpoints unless the problem requires them.

---

## 11. Validation Rules

Validate at the API boundary with Pydantic.

Also add domain-specific validation where required.

Validate:

- required fields
- non-empty strings
- supported enum values
- positive numeric values
- valid timestamps
- payload shape
- pagination limits
- problem-specific constraints

Never silently accept malformed input.

Return clear validation errors.

---

## 12. Idempotency and Duplicate Handling Rules

For ingestion APIs, implement idempotency when a natural duplicate key exists.

Common keys:

```text
source + external_id
account_id + external_id
client_id + request_id
```

Behavior:

```text
First request:
- create record
- process record
- return 201 Created

Duplicate request:
- do not create duplicate record
- do not process again
- return existing record/result
- return 200 OK
- include idempotent_replay = true
```

Back idempotency with a database uniqueness constraint.

Prefer idempotent replay over `409 Conflict` for ingestion APIs unless the problem explicitly expects conflict behavior.

---

## 13. Error Handling Rules

Use one JSON error shape everywhere:

```json
{
  "error": {
    "code": "string",
    "message": "string",
    "request_id": "string",
    "details": {}
  }
}
```

Use meaningful status codes:

```text
400 validation_error
404 not_found
409 conflict, only when duplicate behavior is not idempotent
500 internal_server_error
503 dependency_unavailable
```

Rules:

- never expose stack traces to clients
- always include `request_id` in error responses
- log unexpected exceptions server-side
- keep client-facing messages safe and predictable

---

## 14. Persistence Rules

Use durable persistence.

Prefer PostgreSQL if feasible.

Use SQLite only as a fallback if PostgreSQL setup becomes a deployment risk.

Do not store durable application state only in process memory.

Keep database access behind the repository layer.

Add uniqueness constraints for idempotency keys.

Add indexes for common query patterns:

```text
id
source/account_id/client_id when applicable
status
created_at
resource_type/category/type when applicable
```

For time-boxed builds, schema initialization can be simple.

Do not add Alembic unless it is already easy and does not threaten delivery.

Document migrations as a future production improvement if not implemented.

---

## 15. Processing Rules

Use synchronous processing for the time-boxed implementation unless the problem explicitly requires asynchronous processing.

Keep processing isolated behind a processor/service boundary.

Processing should be:

- deterministic
- testable
- separate from HTTP routing
- separate from persistence details where possible

Document the future migration path:

```text
Current:
API -> synchronous processor -> database

Future:
API -> database -> queue -> worker -> database
```

Do not implement queue/worker unless explicitly required or all core deliverables are already complete.

---

## 16. Operational Excellence Rules

Implement:

```http
GET /health
GET /ready
```

`/health` checks process liveness.

`/ready` checks dependency readiness, especially database connectivity.

Add request ID middleware:

- generate request ID if missing
- return request ID in response headers
- include request ID in error bodies
- include request ID in structured logs

Structured request logs should include:

```text
request_id
method
path
status_code
latency_ms
```

Use environment variables for runtime configuration:

```text
APP_ENV
PORT
DATABASE_URL
LOG_LEVEL
MAX_PAGE_SIZE
```

Keep the API stateless so it can scale horizontally.

---

## 17. Scalability Rules

The current implementation should scale through:

- stateless API design
- external durable database
- pagination
- indexed queries
- bounded request size
- environment-based configuration
- horizontal scaling on a managed platform

Document future scalability improvements:

- queue + worker
- retry policy
- dead-letter handling
- Redis or Valkey for cache/rate limiting
- metrics and tracing
- API authentication
- database migrations
- CI/CD pipeline

Do not implement future improvements unless explicitly required.

---

## 18. Testing Rules

Prioritize tests for high-risk behavior.

Minimum tests:

- health endpoint
- readiness endpoint
- successful ingestion
- validation failure
- duplicate/idempotent replay behavior if applicable
- get by id success
- get by id not found
- get result/status/summary
- list endpoint with pagination
- processor/business rules

Use pytest.

Use FastAPI `TestClient` for API tests.

Tests must be deterministic and runnable with:

```bash
pytest -v
```

Do not chase 100% coverage before core behavior is tested.

For every feature change, update tests.

---

## 19. Automation and Workflow Rules

Include:

```text
Dockerfile
docker-compose.yml
Makefile
README.md
```

Makefile should include:

```makefile
run:
	uvicorn app.main:app --host 0.0.0.0 --port $${PORT:-8000}

test:
	pytest -v

docker-build:
	docker build -t interview-api .

docker-run:
	docker run -p 8000:8000 --env-file .env interview-api

compose-up:
	docker compose up --build

smoke-local:
	curl http://localhost:8000/health
	curl http://localhost:8000/ready
```

README should include:

- overview
- architecture
- endpoints
- example requests
- environment variables
- local setup
- tests
- Docker usage
- deployment notes
- smoke tests
- trade-offs
- future improvements

---

## 20. Deployment Readiness Rules

Prefer Dockerized deployment.

Runtime configuration must come from environment variables.

Deployment is not done until smoke tests are documented and can be run:

```bash
curl https://YOUR_APP_URL/health
curl https://YOUR_APP_URL/ready
curl -X POST https://YOUR_APP_URL/api/v1/... \
  -H "Content-Type: application/json" \
  -d '{...}'
```

If extra features conflict with deployment readiness, choose deployment readiness.

---

## 21. Surgical Change Rules

When editing code:

- touch only files needed for the current task
- do not rewrite unrelated code
- do not reformat unrelated files
- do not rename unrelated functions
- do not change unrelated comments
- keep diffs small and reviewable
- remove only dead code introduced by the current change

Every changed line should map to the current goal.

---

## 22. Goal-Driven Execution Rules

For each task:

1. Define success criteria.
2. Implement the smallest change that satisfies them.
3. Add or update tests.
4. Provide commands to verify locally.

Examples:

```text
"Add validation" means:
- add tests for invalid inputs
- implement validation
- verify tests pass

"Fix duplicate event handling" means:
- add duplicate submission test
- implement idempotency
- verify no duplicate processing

"Make deployment-ready" means:
- Docker build works
- app starts
- /health works
- /ready works
- README has deployment and smoke test instructions
```

---

## 23. Timebox Rules

Optimize for the full deliverable, not isolated feature depth.

Suggested flow:

```text
0-15 min:
- SPEC.md
- assumptions
- API contract
- data model

15-60 min:
- minimal FastAPI app
- health/ready
- ingestion endpoint
- validation

60-105 min:
- persistence
- idempotency
- processing
- query endpoints

105-135 min:
- tests
- error handling
- request_id/logging

135-170 min:
- Dockerfile
- docker-compose
- Makefile
- README
- deployment prep

170-180 min:
- smoke tests
- final verification
- review notes
```

When behind schedule:

1. preserve working API
2. preserve tests
3. preserve Docker/deployment readiness
4. cut optional features

---

## 24. Review Notes Rule

Maintain a short review section in README explaining:

- what was built
- API design
- code organization
- validation
- error handling
- idempotency
- testing
- deployment workflow
- operational features
- trade-offs
- future production evolution

Preferred review framing:

```text
This service is a production-candidate slice, not a one-off script.

It prioritizes clean architecture, validation, persistence, idempotency, meaningful errors, automated tests, Docker workflow, health/readiness checks, structured logs, configuration, and deployability.

Processing is synchronous in this version to reduce deployment risk within the timebox. The processing logic is isolated behind a service boundary, so it can move to a queue-backed worker later without changing the public API contract.
```

---

## 25. Final Verification Checklist

Before declaring done, verify:

```text
[ ] SPEC.md exists
[ ] README.md exists
[ ] app starts locally
[ ] /health works
[ ] /ready works
[ ] ingestion endpoint works
[ ] invalid input returns structured error
[ ] duplicate input is handled safely if applicable
[ ] get by id works
[ ] list endpoint works if implemented
[ ] tests pass
[ ] Docker image builds
[ ] Docker container starts
[ ] smoke test commands are documented
```

---

## 26. Final Instruction to the AI Assistant

When implementing this project:

- think first
- write the spec first
- make small changes
- test important behavior
- avoid unrelated edits
- avoid unnecessary complexity
- prioritize deployability
- document trade-offs

The desired outcome is a reliable, tested, deployable, explainable backend service.
