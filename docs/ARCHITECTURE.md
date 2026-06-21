# Architecture Notes — Usage Events Service

Purpose
- Ingest usage events, dedupe by `event_id`, store events, and provide query and daily summaries per customer.

Core design choices
- FastAPI + Pydantic for validation and OpenAPI docs.
- SQLAlchemy ORM with SQLite for the interview MVP; switch to Postgres for production.
- Deduplication via DB unique constraint on `event_id`. App returns idempotent response for duplicates.
- Summaries computed on-the-fly (daily buckets) for MVP; consider materialized aggregation for scale.

Trade-offs
- SQLite (simplicity) vs Postgres (durability): SQLite enables fast iteration and deterministic tests but is ephemeral in containerized deploys. Postgres recommended for production with migrations.
- Idempotency: rely on producer-supplied `event_id` for correctness. If unavailable, implement id-key hashing + TTL window.
- Aggregation: on-the-fly is simple but O(N) per query. For high volume, implement a scheduled aggregator (worker) that writes summary rows and indexes.

Operational considerations
- Deployment reproducibility: `app.yaml` contains App Platform spec; use `doctl apps update --spec app.yaml` to apply.
- Health checks: `/health` endpoint; App Platform health configured in the app spec.
- Observability: add structured logs and metrics (Prometheus/OpenTelemetry) in next iteration.

Immediate next steps
1. Make `DATABASE_URL` configurable and attach Managed Postgres. Add Alembic for migrations.
2. Add CI that runs tests and builds images. Protect `main` branch.
3. Add auth and rate limiting for multi-tenant protection.
4. Add a small worker to materialize daily summaries when throughput grows.

Longer-term
- Partitioning, retention policies, and streaming ingestion for very high throughput.
- Multi-region considerations and read-replicas for analytics.
