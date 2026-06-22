# Non-Functional Requirements Checklist for REST API Data Ingestion and Processing

Use this checklist at the beginning of a timed backend engineering interview when the prompt is:

> Build a functional REST API service that handles data ingestion and processing.

The goal is to quickly clarify scale, correctness, latency, processing semantics, storage, failure handling, and deployment expectations before choosing an architecture.

---

## 1. The 10 Most Important Questions

If time is limited, ask these first.

1. **What is the expected ingestion rate and peak throughput?**

   This determines whether a simple synchronous API is enough or whether the service needs buffering, batching, Kafka, and worker processing.

2. **What is the expected p95 latency for ingestion?**

   Clarifies whether the API must do all work before returning or whether it only needs to accept data quickly.

3. **Does processing need to complete before the API responds, or can I return `202 Accepted` and process asynchronously?**

   This is the key sync-vs-async decision.

4. **Is eventual consistency acceptable?**

   If yes, async processing is possible. If no, the write path probably needs a synchronous transaction.

5. **Can duplicate events arrive? What is the idempotency key?**

   External clients and retries often produce duplicates. The design should avoid double-counting or double-processing.

6. **Can events arrive out of order or late?**

   This affects Kafka partitioning, timestamp handling, state updates, and whether late events can correct previous results.

7. **What query patterns must be supported, especially large reads or time-range queries?**

   Query patterns determine indexes, pagination, aggregates, and whether raw data scans are acceptable.

8. **What retention period is required for raw data and processed or aggregate data?**

   Retention affects storage cost, cleanup jobs, partitioning, and downsampling.

9. **What should happen when processing fails? Retry? Dead-letter queue?**

   This determines whether we need retry metadata, worker retry logic, DLQ design, and replay strategy.

10. **Is Kafka or worker processing required for the MVP, or should I document it as production evolution?**

   This protects the timed build from over-engineering while still showing production thinking.

---

## 2. Design Decision Table

Use the answers to choose the simplest architecture that satisfies the requirements.

| Requirement / Signal | Recommended Design |
|---|---|
| Low throughput + immediate result required | `FastAPI -> PostgreSQL` |
| Moderate throughput + simple processing | `FastAPI -> PostgreSQL + aggregate/status table` |
| High throughput / burst traffic / async allowed | `FastAPI -> Kafka -> workers -> PostgreSQL` |
| Retry / background processing required | `Kafka or DB-backed queue + worker` |
| Large reads / time-range queries | Pagination + indexes + time range limits + aggregate table |
| Strict correctness required | PostgreSQL transaction + unique constraints + row locks / atomic update |
| Duplicate events possible | Idempotency key + unique constraint + idempotent worker |
| Ordering required | Kafka partition key by resource/customer/job ID |
| Long retention required | Partitioning + retention cleanup + aggregates/downsampling |
| Timed MVP with local dependencies | Use docker-compose PostgreSQL/Kafka only when justified |
| Production deployment | App Platform ingress/load balancing + Managed PostgreSQL/Kafka if required |
| Production IaC | Terraform for durable infra; App Spec for App Platform app shape |

---

## 3. When to Use Kafka

Use Kafka or a queue when one or more of these are true:

- High ingestion throughput.
- Burst traffic needs buffering.
- Processing does not need to finish before the API returns.
- Eventual consistency is acceptable.
- Background worker processing is required.
- Retry and DLQ behavior matter.
- Producers should not be blocked by slow downstream dependencies.
- The system needs to scale consumers independently from API servers.

A typical async architecture:

```text
Client
-> App Platform ingress/load balancing
-> FastAPI API replicas
-> Kafka
-> worker consumers
-> PostgreSQL
```

For a timed MVP, use local docker-compose Kafka only if these requirements justify it.

```text
Client
-> FastAPI API
-> local Kafka via docker-compose
-> local worker process/container
-> local PostgreSQL via docker-compose
```

---

## 4. When Not to Use Kafka

Do not add Kafka only because it is available.

Prefer a simpler synchronous design when:

- Throughput is low or moderate.
- Processing is simple and fast.
- The client needs the result immediately.
- Strong correctness is required in the request path.
- The MVP must be built and tested quickly.
- A database transaction is enough.

Example:

```text
Client
-> App Platform ingress/load balancing
-> FastAPI API
-> PostgreSQL
```

For quota enforcement, allocation, reservations, inventory limits, or other correctness-critical workflows, the core decision should usually happen synchronously in PostgreSQL with transactions and constraints.

---

## 5. Large Reads and Query Design

For large reads, avoid unbounded raw table scans.

Ask:

- Do users query by customer, resource, status, or time range?
- What is the maximum time range?
- Is raw data required, or is an aggregate acceptable?
- Do dashboards query many resources at once?
- What is the maximum page size?
- How long should raw and aggregate data be retained?

Use:

- Required time range filters.
- Pagination.
- Maximum page size.
- Indexes matching query patterns.
- Aggregate/status tables.
- Retention cleanup.
- Time partitioning in production if the raw data volume is large.

Example index patterns:

```text
index(resource_id, timestamp)
index(customer_id, timestamp)
index(status, updated_at)
index(type, timestamp)
unique(event_id)
```

---

## 6. Idempotency and Duplicate Handling

For ingestion systems, assume clients may retry.

Ask:

- Can duplicate events arrive?
- What field uniquely identifies an event?
- Should duplicate submissions return `409 Conflict`, or return the previous result?
- Can Kafka deliver duplicate messages?
- How should worker processing avoid double-counting?

Recommended design:

- Require an idempotency key when possible.
- Add a PostgreSQL unique constraint on that key.
- Make the worker idempotent.
- Treat Kafka as at-least-once delivery.
- Let PostgreSQL constraints be the final correctness guard.

Example:

```text
event_id unique
sample_id unique
source + external_id unique
customer_id + request_id unique
resource_id + timestamp + metric_name unique
```

---

## 7. Ordering and Late Events

Ask:

- Does processing require ordering?
- Ordering per customer, resource, job, or event type?
- Can out-of-order events be corrected later?
- How should late events affect derived state or aggregates?

Kafka partition key examples:

```text
VM metrics: partition by vm_id
Quota usage: partition by customer_id
Resource state: partition by resource_id
Job events: partition by job_id
```

Ordering usually only needs to be preserved within a resource or customer, not globally.

---

## 8. Failure Handling

Ask:

- What should happen if processing fails?
- Should failed records be retried?
- How many retries?
- Should retries use backoff?
- What happens after max retries?
- Do we need a DLQ?
- Should failed records be manually replayable?

MVP fields for async processing:

```text
status: PENDING, PROCESSING, PROCESSED, FAILED
retry_count
last_error
processed_at
```

Production improvements:

- Retry topic.
- Dead-letter topic.
- Replay tooling.
- Alerts on worker failures and DLQ growth.
- Idempotent processing so retries are safe.

---

## 9. Retention and Storage

Ask:

- How long should raw ingested records be retained?
- How long should processed results or aggregates be retained?
- Do users need historical queries?
- Can old raw data be deleted or archived?
- Is downsampling acceptable?

Common pattern:

```text
Raw events/samples: short retention
Aggregates/summaries: longer retention
Old data: cleanup, archive, or downsample
```

For large time-series or event ingestion:

- Partition raw tables by time in production.
- Keep aggregate tables for dashboards and long-range queries.
- Add retention cleanup jobs.

---

## 10. Observability

Minimum MVP observability:

- `GET /healthz`.
- `GET /readyz`.
- `X-Request-ID` support.
- Request ID in response headers.
- Request ID in error responses.
- Structured logs for key operations.
- Consistent error codes.
- Deployment smoke tests.

Async processing observability:

- Kafka publish success/failure.
- Worker processing success/failure.
- Duplicate skipped count.
- Retry count.
- DLQ count.
- Consumer lag.
- Processing latency.

Production alerts:

- High 5xx rate.
- High p95/p99 latency.
- Database latency or connection failures.
- Kafka publish failures.
- Consumer lag above threshold.
- Worker error rate.
- DLQ growth.
- Business metric anomalies.

---

## 11. Deployment and IaC Strategy

For the timed MVP:

- Use only dependencies justified by the problem.
- Use local docker-compose PostgreSQL if durable persistence is required.
- Use local docker-compose Kafka only if async processing, buffering, retry, or high throughput is required.
- Do not block the timed build on provisioning DigitalOcean Managed PostgreSQL or Managed Kafka.
- Keep the app configurable through environment variables.

For the production story:

```text
Client
-> DigitalOcean App Platform ingress/load balancing
-> FastAPI web service replicas
-> DigitalOcean Managed Kafka, if required
-> App Platform worker replicas, if required
-> DigitalOcean Managed PostgreSQL
```

Production IaC:

- Terraform provisions durable infrastructure:
  - Managed PostgreSQL.
  - Managed Kafka.
  - Kafka topics.
  - network/trusted-source rules if needed.
  - alerts.
  - outputs.
  - Terraform state.
- App Platform spec defines app shape:
  - web service.
  - worker service.
  - health check.
  - instance size/count.
  - env var names and secret references.
  - build/run commands.

Do not hardcode secrets in source code, Terraform, App Spec, or README.

---

## 12. Quick Decision Script

Use this mental script during the interview:

```text
If the client needs the processed result immediately:
  prefer synchronous FastAPI + PostgreSQL.

If the client only needs acceptance and processing can happen later:
  return 202 Accepted and use Kafka/worker or a DB-backed queue.

If duplicate events are possible:
  require an idempotency key and enforce uniqueness in PostgreSQL.

If large reads are required:
  add pagination, time range limits, indexes, and aggregate tables.

If strict correctness is required:
  use PostgreSQL transactions, constraints, row locks, or atomic updates.

If throughput is high or bursty:
  use Kafka to buffer ingestion and scale workers independently.

If the MVP timebox is tight:
  implement the simplest design that works, use docker-compose for justified local dependencies, and document production evolution.
```

