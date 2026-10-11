# Backend, API, and data

Read this for endpoints, services, jobs, schemas, queries, and migrations. Load stack skills
from `skill-map.md` only when the repo uses that stack.

## 1. Trace the whole path

Request → validation → authorization → domain logic → persistence → side effects
(email, queue, webhook, cache) → response → what the user sees. Touch only the layers that
apply, but check the consequences in each one.

## 2. API

- Design around application behavior, not database tables. Never return internal models
  directly; return only the fields the caller needs.
- Validate input at the boundary on the server. Client validation is UX only.
- Authorization on every protected endpoint, per request, including object ownership.
- Consistent error shape with correct status codes; no stack traces or SQL in responses.
- Changing an existing public endpoint is tier 3: keep it backward compatible or version it.
- Operations that may be retried (payments, webhooks, jobs) are idempotent.

## 3. Data model

- Each fact has one owner. Derive instead of syncing copies.
- Constraints in the database (NOT NULL, FK, UNIQUE, CHECK), not only in app code.
- Index for the queries that actually run; check with `EXPLAIN` when performance matters.
- Watch for N+1 queries when adding relations to list endpoints.
- Transactions around multi-write operations that must succeed or fail together.

## 4. Migrations (always tier 3)

- Expand → migrate data → contract. Never rename or drop a column that running code still
  reads in the same deploy.
- Expand/contract is for databases with real data or running deploys. If nothing is deployed
  yet, a direct rename is fine. To rename only in code, map the field (Prisma `@map`,
  SQLAlchemy `Column("old_name")`) and leave the column alone. Ask which one the user means.
- Reversible where possible; write the down path or document why it cannot exist.
- Large tables: avoid long locks; batch backfills.
- Run on local or throwaway data first. Never run against a non-local database without
  explicit user approval (`AGENTS.md` §5).

## 5. Reliability

- No swallowed exceptions. Log with context, without secrets or PII.
- Timeouts and bounded retries on external calls.
- Background jobs: idempotent, with retry limits and a dead-letter or failure path.

## 6. Verify

Run the endpoint or job for real (curl, test client, integration test), including one
failure case and one unauthorized case. For migrations: up, down, and up again locally.
