# Current Issues and Risks

This document tracks currently identified backend issues and risks for future remediation planning. It is based on static review of the current codebase and should be updated as fixes land.

## Executive Summary

- The highest-impact risks are in authorization scope, async performance behavior, and query/input safety.
- There are also meaningful reliability and scalability risks from unbounded queries and inconsistent validation.
- Testing and observability gaps increase the probability and detection latency of regressions.

## Critical

### 1) Over-broad access to Keycloak directory endpoints

- Severity: Critical
- Area: Authorization / Data exposure
- Evidence:
  - `routes/user.py`:
    - `GET /user/keycloak-users` uses `JWTBearer(allowed_roles=[])`
    - `GET /user/keycloak-user/{user_id}` uses `JWTBearer(allowed_roles=[])`
- Why it matters:
  - Any authenticated caller can query user-directory information, likely beyond intended least privilege.
- Recommended remediation:
  - Require explicit privileged roles for these endpoints.
  - Add authorization tests for deny/allow scenarios.
  - Minimize exposed user fields where possible.

### 2) Regex query safety risk in search endpoint

- Severity: Critical
- Area: Input validation / Query safety / Performance abuse
- Evidence:
  - `database/project.py` search uses raw user query in Mongo regex:
    - `{"topic": {"$regex": query, "$options": "i"}}`
    - `{"description": {"$regex": query, "$options": "i"}}`
- Why it matters:
  - User-controlled regex can trigger expensive query execution and denial-of-service behavior.
- Recommended remediation:
  - Escape user input before regex usage.
  - Add query length limits and request rate limits.
  - Consider indexed search alternatives for production scale.

## High

### 3) Blocking network calls in async request paths

- Severity: High
- Area: Performance / Reliability
- Evidence:
  - `auth/jwt_handler.py` uses synchronous `requests.get(...)` for JWKS.
  - `routes/user.py` async handlers call sync `services/keycloak.py` methods that use synchronous `httpx.get/post`.
- Why it matters:
  - Blocking I/O inside async handlers can reduce throughput and increase latency under load.
- Recommended remediation:
  - Migrate to async HTTP clients (`httpx.AsyncClient`) in request paths.
  - Reuse client sessions and define timeout/retry policies.

### 4) Route role intent mismatch for admin endpoint

- Severity: High
- Area: Authorization correctness
- Evidence:
  - `routes/admin.py` docstring says admin-only route.
  - Actual guard uses roles `["view-profile", "manage-account"]`.
- Why it matters:
  - Documentation and behavior diverge, and privileges may be broader than intended.
- Recommended remediation:
  - Define a central role matrix and align route guards to intended policy.
  - Add tests asserting role policy for privileged endpoints.

### 5) Auth bypass can disable all route protection

- Severity: High
- Area: Security configuration
- Evidence:
  - `core/config.py` exposes `DISABLE_AUTH`.
  - `auth/jwt_bearer.py` returns mock payload when enabled.
- Why it matters:
  - Misconfiguration in non-dev environments can fully bypass authorization.
- Recommended remediation:
  - Add startup guardrails to fail in production-like environments when `DISABLE_AUTH=true`.
  - Add deployment checks and environment validation.

## Medium

### 6) Unbounded list/search queries

- Severity: Medium
- Area: Scalability / Resource usage
- Evidence:
  - `models/project.py`: `to_list()` for visible/featured fetches without limit.
  - `database/project.py`: search uses `to_list()` with no bounds.
  - `routes/project.py`: feedback retrieval returns full result set.
- Why it matters:
  - Payload and memory growth can hurt latency and stability as data volume increases.
- Recommended remediation:
  - Introduce pagination and max page size limits across list endpoints.

### 7) Inconsistent ObjectId validation path

- Severity: Medium
- Area: API consistency / Error handling
- Evidence:
  - `routes/project.py` validates ObjectIds in most endpoints.
  - `PUT /projects/{projectId}/featured` passes raw ID to DB function.
  - `database/project.py` converts with `ObjectId(id)` directly.
- Why it matters:
  - Invalid input may produce inconsistent error behavior versus other endpoints.
- Recommended remediation:
  - Validate `projectId` consistently at route boundary for all relevant endpoints.

### 8) Potential stale object return after update

- Severity: Medium
- Area: Data correctness / API contract consistency
- Evidence:
  - `database/project.py::update_project` calls `await project.update(...)` then returns `project` without refresh.
- Why it matters:
  - Returned object may not reliably represent persisted post-update state.
- Recommended remediation:
  - Re-fetch updated document or use update flow that returns updated document atomically.

### 9) Role source inconsistency in `/user/me`

- Severity: Medium
- Area: Auth contract clarity
- Evidence:
  - Authorization guard uses `resource_access[CLIENT_ID].roles`.
  - `/user/me` response exposes `resource_access.account.roles`.
- Why it matters:
  - Consumers can receive role values that differ from enforcement source.
- Recommended remediation:
  - Standardize role source and document it explicitly.

## Low

### 10) Error handling and observability are minimal

- Severity: Low
- Area: Operations / Debuggability
- Evidence:
  - Broad exception handling and `print(...)` usage in DB/auth/service paths.
  - No structured logging, metrics, or tracing baseline documented.
- Why it matters:
  - Slower incident triage and weaker production insight.
- Recommended remediation:
  - Adopt structured logging and define baseline metrics/error instrumentation.

### 11) No automated test suite currently present

- Severity: Low (high strategic importance)
- Area: Quality assurance
- Evidence:
  - No backend test files found in repository.
- Why it matters:
  - Regression risk remains high, especially in auth and contract-sensitive routes.
- Recommended remediation:
  - Add baseline tests for auth guards, ObjectId validation, project CRUD, feedback flows, and search behavior.

## Cross-Cutting Gaps

- Testing: no enforced regression safety net.
- Observability: limited diagnostics and no documented SLO-oriented telemetry.
- Security policy documentation: endpoint role policy lacks central authoritative matrix.
- Performance hardening: query bounds and async I/O model need formalized standards.

## Recommended Remediation Order

1. Tighten authorization for Keycloak user-directory endpoints.
2. Harden search query handling to prevent regex abuse.
3. Replace blocking sync network calls in async request paths.
4. Enforce environment safeguards for `DISABLE_AUTH`.
5. Add pagination and limits for all list/search endpoints.
6. Standardize ID validation and error behavior.
7. Improve observability baseline (structured logs + essential metrics).
8. Add automated regression tests and integrate into CI.
