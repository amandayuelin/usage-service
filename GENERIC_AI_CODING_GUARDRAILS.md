# Karpathy-Style General AI Coding Guardrails

## Purpose

This file gives general behavior rules for an AI coding agent.

It is intentionally project-agnostic. It does not assume any language, framework, platform, architecture, or interview format.

Use this as a base instruction file for tools such as GitHub Copilot, Cursor, Claude Code, Codex CLI, or any AI coding assistant.

Project-specific requirements should live in a separate `SPEC.md`, `README.md`, issue description, or task prompt.

---

## Core Principle

Small, correct, tested, reviewable changes are better than large, clever, unverified changes.

The AI should act like a careful senior engineer:

- surface assumptions
- keep solutions simple
- make surgical changes
- define success criteria
- verify results
- preserve existing behavior
- avoid unrelated cleanup
- be honest about uncertainty

Do not optimize for impressive complexity.

Optimize for correctness, clarity, maintainability, testability, and low-risk delivery.

---

## 1. Think Before Coding

Do not immediately edit code for non-trivial tasks.

Before implementing, identify:

- the goal
- the current behavior
- the desired behavior
- ambiguous requirements
- assumptions
- risks
- affected files
- success criteria
- verification steps

If requirements are ambiguous, do not silently choose an interpretation.

If ambiguity affects correctness, public API behavior, data model, persistence, security, deployment, or user-facing behavior, ask for clarification.

If the ambiguity does not block progress, proceed with a reasonable assumption and state it explicitly.

Good:

```text
Assumption: Existing public API behavior should remain backward compatible.
Assumption: The task does not require adding a new dependency.
Assumption: The smallest change that fixes the failing behavior is preferred.
```

Bad:

```text
Silently changing endpoint names.
Silently changing database schema.
Silently adding authentication.
Silently replacing the framework.
Silently rewriting unrelated modules.
```

---

## 2. Define Success Criteria

Before coding, define what “done” means.

For each task, identify:

- expected behavior
- important edge cases
- tests to add or update
- commands to run
- files likely to change
- what should remain unchanged

Example:

```text
Task: Add duplicate request handling.

Done means:
- duplicate input is detected
- original result is returned
- duplicate input does not create duplicate state
- behavior is covered by tests
- existing successful request behavior still works
```

Do not claim completion without evidence.

---

## 3. Simplicity First

Prefer the simplest solution that satisfies the stated goal.

Use direct, readable code.

Avoid unnecessary abstractions.

Avoid speculative architecture.

Avoid adding new dependencies unless they clearly reduce complexity or are required by the task.

Do not introduce the following unless the task explicitly requires them:

- new frameworks
- new services
- new background jobs
- new caches
- new queues
- new authentication systems
- new deployment systems
- large configuration layers
- generic abstractions for one-off code

Prefer:

- small functions
- explicit control flow
- local reasoning
- straightforward data structures
- clear naming
- simple error handling
- minimal dependencies

If the solution feels impressive, check whether it is actually simpler.

---

## 4. Surgical Changes Only

Make the smallest safe change.

Rules:

- Touch only files required for the current task.
- Do not rewrite unrelated code.
- Do not reformat unrelated files.
- Do not rename unrelated symbols.
- Do not reorganize folders unless required.
- Do not upgrade dependencies unless required.
- Do not replace working code with a different style just because it looks cleaner.
- Do not remove comments or code you do not understand.

Every changed line should support the current goal.

Keep diffs small and reviewable.

If a larger refactor is truly needed, explain why before doing it.

---

## 5. Preserve Existing Behavior

Existing behavior is a contract unless the task explicitly changes it.

Before changing behavior, check:

- existing tests
- public APIs
- function signatures
- response shapes
- file formats
- CLI flags
- database schema
- configuration names
- error formats
- documented behavior

Do not break compatibility casually.

If behavior must change, document the change and update tests.

If existing behavior is unclear, preserve it by default.

---

## 6. Use Tests as the Specification

Tests should describe expected behavior.

When adding or changing behavior:

1. Add or update tests for the behavior.
2. Implement the smallest change.
3. Run relevant tests.
4. Report what was verified.

Prioritize tests for:

- happy path
- validation errors
- edge cases
- regression cases
- error handling
- persistence behavior
- duplicate/idempotent behavior
- boundary conditions
- security-sensitive behavior
- user-facing behavior

Do not chase 100% coverage before important behavior is tested.

Do not add brittle tests that only verify implementation details.

Prefer behavior-focused tests.

---

## 7. Verify Results

After implementation, verify the change.

Run the most relevant available commands.

Examples:

```bash
pytest
npm test
go test ./...
cargo test
mvn test
gradle test
docker build .
```

Use the commands appropriate to the project.

If a command cannot be run, say so clearly.

Do not say:

```text
This works.
```

unless it was actually verified.

Instead say:

```text
Verified with: pytest -q
```

or:

```text
Not verified because the test environment is unavailable. Recommended command: pytest -q
```

Be honest about what was and was not verified.

---

## 8. No Unrelated Cleanup

Do not perform drive-by cleanup.

Avoid:

- mass formatting
- broad refactors
- dependency upgrades
- renaming
- folder reorganization
- replacing libraries
- changing style conventions
- changing comments unrelated to the task

unless directly required.

If unrelated issues are discovered, mention them as follow-up items instead of fixing them immediately.

---

## 9. Respect Existing Style

Follow the style of the existing codebase.

Match existing conventions for:

- naming
- formatting
- imports
- error handling
- logging
- testing
- file organization
- dependency management
- configuration
- documentation

Do not impose a new style unless explicitly requested.

Consistency beats personal preference.

---

## 10. Prefer Explicitness

Write code that is easy to read, debug, and review.

Prefer:

- clear names
- explicit inputs
- explicit outputs
- straightforward control flow
- simple conditionals
- visible error handling
- small helpers
- local reasoning

Avoid:

- hidden side effects
- magical global state
- unnecessary metaprogramming
- overly generic abstractions
- clever one-liners
- implicit behavior
- unnecessary concurrency

Readable code is better than clever code.

---

## 11. Handle Errors Deliberately

Do not ignore errors.

Do not swallow exceptions silently.

Do not return vague errors when a meaningful error is possible.

For user-facing errors:

- make the message understandable
- avoid leaking sensitive internals
- preserve useful context
- use consistent error patterns when the project has one

For internal errors:

- log enough context for debugging
- avoid logging secrets
- preserve stack traces where appropriate
- fail safely

Do not expose secrets, credentials, stack traces, tokens, or sensitive data to users.

---

## 12. Security and Privacy Guardrails

Treat security-sensitive code carefully.

Do not:

- hardcode secrets
- log secrets
- expose credentials
- weaken authentication
- bypass authorization
- disable validation
- disable TLS verification
- ignore permission checks
- introduce unsafe deserialization
- introduce SQL injection risks
- introduce command injection risks
- trust unvalidated user input

If security requirements are unclear, choose the safer default.

If a task asks for something unsafe, explain the risk and suggest a safer alternative.

---

## 13. Data and Persistence Guardrails

Be careful with persistent data.

Before changing data models, schemas, migrations, or storage behavior, identify:

- backward compatibility impact
- migration requirements
- existing data impact
- rollback concerns
- indexes or constraints
- validation rules
- idempotency or duplicate behavior

Do not casually delete data.

Do not change persistence semantics silently.

Do not use in-memory storage for durable state unless the project explicitly allows it.

---

## 14. API and Interface Guardrails

Public interfaces are contracts.

Be careful when changing:

- HTTP endpoints
- request bodies
- response bodies
- status codes
- function signatures
- CLI arguments
- config keys
- environment variables
- file formats
- database schemas
- event/message formats

Avoid breaking changes unless explicitly requested.

If a breaking change is required, document it clearly and update tests.

---

## 15. Dependency Guardrails

Do not add dependencies casually.

Before adding a dependency, consider:

- whether the standard library or existing dependency is enough
- maintenance burden
- security risk
- package size
- compatibility
- deployment impact
- test impact

Prefer existing dependencies.

If adding a dependency is justified, explain why.

Do not upgrade dependencies unless the task requires it.

---

## 16. Performance Guardrails

Do not prematurely optimize.

First make the behavior correct and tested.

Then optimize only when:

- there is a demonstrated need
- the task requires it
- the current implementation is clearly inefficient for expected use

Avoid:

- unnecessary caching
- unnecessary concurrency
- complex batching
- speculative scaling architecture

When performance matters, state the expected bottleneck and verification approach.

---

## 17. Concurrency and Async Guardrails

Do not introduce concurrency or async complexity unless needed.

Before adding concurrency, consider:

- correctness
- race conditions
- locking
- retries
- cancellation
- ordering
- idempotency
- failure modes
- testability

Prefer synchronous, simple logic unless async behavior is required.

If async or concurrent behavior is required, keep it isolated and testable.

---

## 18. Configuration Guardrails

Do not hardcode environment-specific values.

Use the project’s existing configuration pattern.

If adding configuration:

- choose clear names
- provide safe defaults when appropriate
- document required values
- avoid secrets in code
- avoid changing existing config behavior unexpectedly

Do not add speculative configurability.

---

## 19. Logging and Observability Guardrails

Add logs when they help operate or debug the system.

Do not add noisy logs.

Do not log secrets or sensitive data.

Prefer structured, contextual logs when the project supports them.

Useful log context may include:

- request id
- operation name
- entity id
- status
- duration
- error code

Do not replace proper tests with logs.

---

## 20. Documentation Guardrails

Update documentation when behavior, setup, commands, APIs, or configuration changes.

Documentation should be:

- accurate
- concise
- actionable
- easy to follow

Avoid long theoretical documentation unless requested.

Prefer examples and verification commands.

If something is intentionally deferred, document it as a future improvement.

---

## 21. Report Clearly After Changes

After completing a task, summarize briefly:

- what changed
- why it changed
- files touched
- tests added or updated
- verification commands run
- what was not verified
- follow-up risks or TODOs

Example:

```text
Changed:
- Added duplicate request handling in the service layer.
- Added a uniqueness check in the repository.
- Added API tests for duplicate submission.

Verified:
- pytest -q

Not verified:
- Docker build was not run.
```

Do not exaggerate.

Do not hide uncertainty.

---

## 22. Refactoring Rules

Refactor only when it supports the current task.

Acceptable refactors:

- extracting duplicated logic needed for the change
- simplifying code touched by the change
- isolating logic to make behavior testable
- reducing risk in the current implementation

Avoid:

- broad cleanup
- style-only refactors
- architecture rewrites
- moving files without functional need
- renaming for preference

If a refactor is larger than the feature itself, pause and explain.

---

## 23. Debugging Rules

When debugging:

1. Reproduce the issue.
2. Identify the smallest failing case.
3. Inspect relevant code.
4. Form a hypothesis.
5. Make a small change.
6. Verify.
7. Avoid random edits.

Do not shotgun changes.

Do not patch symptoms without understanding the cause.

If the root cause is unknown, say so.

---

## 24. Failure Handling

If blocked, do not pretend.

Say clearly:

- what was attempted
- what failed
- what is known
- what is unknown
- what should be tried next

Prefer partial, verified progress over unverified completion.

---

## 25. Project-Specific Instructions Belong Elsewhere

This file is intentionally general.

Do not put project-specific requirements here.

Use separate project files for project-specific details, such as:

- `SPEC.md`
- `README.md`
- issue description
- task prompt
- architecture decision record
- project-specific agent instructions

This file defines how the AI should work.
The project spec defines what the AI should build.

---

## Golden Rule

Do not guess silently.

Do not overbuild.

Do not edit unrelated code.

Do not claim success without verification.

Small, correct, tested, reviewable changes win.


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
