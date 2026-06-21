# GitHub Copilot Instructions

## Context

This is a timed backend engineering interview project.

The goal is to build a small, working, tested, deployable REST API service within a 3-hour window.

Prefer:
- simple working software over over-engineering
- explicit assumptions over silent guessing
- small incremental changes over large rewrites
- tests and verification over unverified code
- deployment readiness over extra features

Use Python FastAPI unless the project spec says otherwise.

## Core Behavioral Rules

### 1. Think Before Coding

Before implementing non-trivial changes:
- Restate the goal briefly.
- Identify ambiguous requirements.
- State assumptions explicitly.
- Ask for clarification if the ambiguity affects the API contract, data model, persistence, or deployment.
- Present trade-offs when there are multiple reasonable choices.

Do not silently invent requirements.

### 2. Simplicity First

Keep the implementation small enough to finish, test, Dockerize, and deploy within the interview timebox.

Avoid:
- unnecessary abstractions
- complex framework choices
- premature auth, queues, metrics dashboards, CI/CD, or distributed-system features
- large refactors unless required
- speculative configurability

Prefer:
- clear FastAPI endpoints
- Pydantic validation
- SQLite or simple PostgreSQL usage
- direct SQLAlchemy models
- pytest tests
- simple Dockerfile
- clear README

### 3. Surgical Changes

When editing code:
- Touch only files needed for the current task.
- Do not rewrite unrelated code.
- Do not change comments, formatting, or structure unrelated to the task.
- Remove only dead code introduced by the current change.
- Keep diffs small and reviewable.

Every changed line should map to the current goal.

### 4. Goal-Driven Execution

For each task:
- Define success criteria.
- Implement the smallest change that satisfies them.
- Add or update tests.
- Provide commands to verify locally.

Examples:
- "Add validation" means: add tests for invalid inputs, then make them pass.
- "Fix duplicate event handling" means: write a duplicate event test, then implement unique handling.
- "Make deployment-ready" means: verify Docker build, app startup, health check, and README instructions.

### 5. Interview Timebox Awareness

Optimize for the 3-hour full-cycle deliverable.

Suggested phases:
- 0-15 min: spec, assumptions, API contract
- 15-60 min: minimal working API
- 60-105 min: core persistence, duplicate handling, summary endpoint
- 105-135 min: tests and error handling
- 135-170 min: Dockerfile, README, DigitalOcean deployment
- 170-180 min: final verification and review notes

If adding features conflicts with deployment readiness, choose deployment readiness.

### 6. Testing Expectations

Prioritize tests for:
- health check
- successful ingestion
- validation errors
- duplicate event handling
- get by id success and not found
- listing/filtering if implemented
- summary aggregation

Keep tests deterministic and easy to run with:

```bash
pytest
```