# GitHub Copilot Instructions

This is a backend engineering interview practice project.

The goal is to build a small, working, tested, deployable REST API service that demonstrates production-ready thinking.

Use Python FastAPI unless the project spec says otherwise.

## Interview Priorities

Optimize for the evaluation criteria:
- Engineering Quality: clean organization, sensible validation, meaningful error handling
- Testing: structured automated tests and validation
- Automation & Workflow: repeatable local/dev/deploy workflow
- Operational Excellence: live-environment thinking, observability, configurability, scalability

Prefer:
- simple working software over over-engineering
- explicit assumptions over silent guessing
- small reviewable changes over large rewrites
- tests and verification over unverified code
- deployment readiness over extra features

## Spec First

Before implementing non-trivial changes:
- Read `SPEC.md` and `IMPLEMENTATION_PLAN.md` if present.
- Restate the goal briefly.
- Identify ambiguous requirements.
- State assumptions explicitly.
- Do not silently invent requirements.
- Ask for clarification if ambiguity affects API contract, data model, persistence, or deployment.

## Technical Stack

Use:
- Python FastAPI
- PostgreSQL
- SQLAlchemy
- Pydantic
- pytest
- Docker
- docker-compose for local PostgreSQL

Do not use SQLite for this project.

Configure runtime behavior with environment variables:
- `PORT`
- `DATABASE_URL`
- `LOG_LEVEL`
- `ENVIRONMENT`

## Persistence

Design persistence with production in mind:
- Use `DATABASE_URL`-driven configuration.
- Use PostgreSQL as the primary persistence layer.
- Use database constraints where appropriate.
- Use unique constraints for idempotency keys such as usage event IDs.
- Add indexes for expected query patterns such as `customer_id`, `resource_type`, and `timestamp`.
- Keep database access isolated enough that the persistence layer remains testable.

For quota enforcement:
- Prefer transaction-safe check-and-record behavior.
- Avoid separate non-atomic check-then-write flows for hard enforcement.
- If full concurrency safety is not implemented, document the limitation clearly.

## API and Error Handling

Use clear REST endpoints.

Include:
- `GET /healthz`
- quota creation/listing/status endpoints
- usage ingestion endpoint
- usage check endpoint

Use Pydantic validation for request bodies.

Use consistent JSON error responses where practical, for example:

```json
{
  "error": "validation_error",
  "message": "Human-readable error message"
}
```