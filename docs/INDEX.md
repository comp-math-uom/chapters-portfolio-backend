# Chapters Portfolio Backend Docs Index

This index is the primary navigation page for backend technical documentation.

## Start Here

- Project entrypoint: [`ReadMe.md`](../ReadMe.md)
- Architecture: [`ARCHITECTURE.md`](./ARCHITECTURE.md)
- API contract: [`API_AND_CONTRACTS.md`](./API_AND_CONTRACTS.md)
- Data model and storage: [`DATA_MODELS_AND_STORAGE.md`](./DATA_MODELS_AND_STORAGE.md)
- Run and deploy: [`RUN_AND_DEPLOY.md`](./RUN_AND_DEPLOY.md)
- Current issues and risks: [`CURRENT_ISSUES_AND_RISKS.md`](./CURRENT_ISSUES_AND_RISKS.md)

## Suggested Reading Paths

### New backend developer

1. [`ReadMe.md`](../ReadMe.md)
2. [`ARCHITECTURE.md`](./ARCHITECTURE.md)
3. [`API_AND_CONTRACTS.md`](./API_AND_CONTRACTS.md)
4. [`DATA_MODELS_AND_STORAGE.md`](./DATA_MODELS_AND_STORAGE.md)
5. [`RUN_AND_DEPLOY.md`](./RUN_AND_DEPLOY.md)

### API consumer / frontend developer

1. [`API_AND_CONTRACTS.md`](./API_AND_CONTRACTS.md)
2. [`DATA_MODELS_AND_STORAGE.md`](./DATA_MODELS_AND_STORAGE.md)
3. [`CURRENT_ISSUES_AND_RISKS.md`](./CURRENT_ISSUES_AND_RISKS.md)

### Operator / maintainer

1. [`RUN_AND_DEPLOY.md`](./RUN_AND_DEPLOY.md)
2. [`ARCHITECTURE.md`](./ARCHITECTURE.md)
3. [`CURRENT_ISSUES_AND_RISKS.md`](./CURRENT_ISSUES_AND_RISKS.md)
4. [`AI_AGENT_NOTES.md`](./AI_AGENT_NOTES.md)

## Maintenance Rules

- Keep docs aligned with source of truth in `app.py`, `core/`, `routes/`, `auth/`, `database/`, `models/`, and `services/`.
- Update API docs when any route signature, auth requirement, or response schema changes.
- Update run/deploy guidance when environment variables or startup assumptions change.
- Keep `CURRENT_ISSUES_AND_RISKS.md` updated as issues are fixed or newly discovered.
