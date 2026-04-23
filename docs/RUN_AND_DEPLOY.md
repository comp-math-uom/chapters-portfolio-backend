# Chapters Portfolio Backend Run and Deploy

## Local Development Runbook

### Prerequisites

- Python 3.10+ recommended
- Reachable MongoDB instance
- Reachable Keycloak instance (unless testing with `DISABLE_AUTH=true`)

### Environment Configuration

Create a `.env` file in the repository root:

```env
PROJECT_NAME=Chapters Portfolio API
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB=chapters_portfolio
KEYCLOAK_URL=https://your-keycloak-host
REALM=your-realm
CLIENT_ID=your-client-id
CLIENT_SECRET=your-client-secret
DISABLE_AUTH=false
```

Optional:

- `BACKEND_CORS_ORIGINS` (defaults to localhost-focused origins in `core/config.py`)

### Start Commands

- Quick dev run:
  - `python main.py`
- Equivalent explicit uvicorn:
  - `uvicorn app:app --host localhost --port 8080 --reload`

### Startup Validation Checklist

1. Service boots without import/settings errors.
2. `GET /` returns service metadata.
3. `GET /docs` loads OpenAPI UI.
4. DB-backed read endpoint responds (for example `GET /projects/all`).
5. Protected route behavior matches current auth mode:
   - with auth enabled: requires bearer token
   - with auth disabled: returns mock-auth access

## Runtime Behavior

- Startup event calls `init_db()`, which runs Beanie initialization.
- Shutdown event calls `close_db_connection()`.
- Auth dependency verifies JWTs using Keycloak JWKS and enforces route-level role checks.

## Deployment Guidance

This repository does not currently include a first-party Dockerfile or infrastructure manifests, so deployment is environment-orchestrator specific.

Recommended deployment controls:

- Run with explicit process manager or orchestrator health checks.
- Inject secrets via secure secret store (never hardcode in repo).
- Restrict CORS origins to trusted frontend domains.
- Enforce `DISABLE_AUTH=false` outside local/test contexts.
- Monitor DB connectivity and Keycloak availability.

## Production Safety Checklist

- [ ] `DISABLE_AUTH` is false in all production-like environments.
- [ ] Keycloak realm/client settings match token issuer and audience.
- [ ] Role mappings are validated for admin/user route access.
- [ ] Error logging is captured centrally.
- [ ] API smoke tests pass after deploy.

## Known Operational Gaps

- No built-in containerization/deployment artifacts.
- No explicit observability stack documented in-repo (metrics/tracing/alerts).
- No automated test suite currently present for release gating.
