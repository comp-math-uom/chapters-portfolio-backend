# Chapters Portfolio Backend

FastAPI backend for the Chapters AI Portal portfolio domain. It provides API endpoints for projects, feedback, user/profile views, admin and user dashboard checks, and a utility endpoint.

## What This Service Does

- Serves portfolio project data from MongoDB through Beanie ODM.
- Protects selected endpoints with Keycloak-backed JWT validation.
- Exposes OpenAPI docs via FastAPI (`/docs`, `/redoc`).
- Supports local development auth bypass via `DISABLE_AUTH` (never enable in production).

## Tech Stack

- Python 3.10+ (recommended)
- FastAPI + Uvicorn
- MongoDB + Motor + Beanie
- Keycloak integration for auth and user-directory lookups
- Pydantic v2 + pydantic-settings

## Repository Structure

```text
.
├── app.py                 # FastAPI app wiring, middleware, router mount, lifecycle hooks
├── main.py                # Local dev runner (uvicorn, reload=True)
├── core/
│   ├── config.py          # Environment settings
│   └── database.py        # Mongo client + Beanie init/close
├── auth/
│   ├── jwt_bearer.py      # Route guard dependency and role checks
│   └── jwt_handler.py     # JWT decode + JWKS fetch/cache
├── routes/                # API route modules
├── database/              # Data-access helpers
├── models/                # Beanie documents
├── schemas/               # Request/response contracts
├── services/              # External service integrations
├── docs/                  # Extended technical docs
└── requirements.txt
```

## Quickstart

1. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create `.env` in the repository root:
   ```env
   MONGODB_URI=mongodb://localhost:27017
   MONGODB_DB=chapters_portfolio
   KEYCLOAK_URL=https://your-keycloak-host
   REALM=your-realm
   CLIENT_ID=your-client-id
   CLIENT_SECRET=your-client-secret
   DISABLE_AUTH=false
   ```
4. Run locally:
   ```bash
   python main.py
   ```

Service URL: `http://localhost:8080`  
OpenAPI docs: `http://localhost:8080/docs`  
ReDoc: `http://localhost:8080/redoc`

## Core Runtime Behavior

- Startup initializes MongoDB/Beanie via `core.database.init_db`.
- Shutdown closes the Motor client via `core.database.close_db_connection`.
- Routers are mounted under:
  - `/admin`
  - `/user`
  - `/projects`
  - `/utils`

## Important Configuration Notes

- `DISABLE_AUTH=true` returns a mock JWT payload from the auth dependency and bypasses token verification.
- `BACKEND_CORS_ORIGINS` defaults to localhost values and should be restricted per environment.
- `CLIENT_ID`, `REALM`, and `KEYCLOAK_URL` must match the token issuer/audience used by your Keycloak realm.

## Documentation Map

See [`docs/INDEX.md`](docs/INDEX.md) for complete architecture, API contract, data model, run/deploy, and issues/risk references.