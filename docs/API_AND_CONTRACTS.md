# Chapters Portfolio Backend API and Contracts

## Base URLs and Docs

- Local service base URL: `http://localhost:8080`
- OpenAPI UI: `/docs`
- ReDoc: `/redoc`

## Auth Contract

- Protected routes use `Depends(JWTBearer(...))`.
- JWT roles are extracted from `resource_access[CLIENT_ID].roles` for authorization checks.
- `DISABLE_AUTH=true` bypasses auth and returns a mock payload from the dependency.
- Route-specific role requirements are currently mostly `["view-profile", "manage-account"]`.

## Common Error Behavior

- `400`: invalid ObjectId-like path values (for routes that validate IDs).
- `401`: Keycloak client/token related authorization failures inside Keycloak service functions.
- `403`: missing/invalid bearer token, wrong auth scheme, or role mismatch.
- `404`: resource not found (project/feedback/user).
- `500`: unhandled exceptions from route logic/DB operations.
- `502`: upstream Keycloak communication issues in service helpers.

## Endpoint Catalog

### Root

- `GET /`
  - Auth: public
  - Response: service metadata (`message`, `docs`, `version`)

### Admin (`/admin`)

- `GET /admin/dashboard`
  - Auth: protected, `allowed_roles=["view-profile", "manage-account"]`
  - Response: message payload
  - Notes: docstring states admin-only intent, but role list is broader.

### User (`/user`)

- `GET /user/keycloak-users`
  - Auth: protected, `allowed_roles=[]` (any authenticated token)
  - Response model: `List[KeycloakUser]`
  - Backend dependency: `services.keycloak.get_all_users()`

- `GET /user/keycloak-user/{user_id}`
  - Auth: protected, `allowed_roles=[]` (any authenticated token)
  - Response model: `KeycloakUser`
  - Backend dependency: `services.keycloak.get_user_by_id(user_id)`

- `GET /user/me`
  - Auth: protected, `allowed_roles=["view-profile", "manage-account"]`
  - Response model: `dict` (payload projection)
  - Response fields: `user_id`, `email`, `name`, `preferred_username`, `roles`

- `GET /user/dashboard`
  - Auth: protected, `allowed_roles=["view-profile", "manage-account"]`
  - Response: message payload

### Projects (`/projects`)

#### Public routes

- `GET /projects/all`
  - Query params: `featured` (bool, default `false`)
  - Auth: public
  - Response model: `ProjectListSchema`
  - Behavior:
    - `featured=false`: visible projects
    - `featured=true`: visible and featured projects

- `GET /projects/search/`
  - Query params: `query` (string, required)
  - Auth: public
  - Response model: `List[ProjectSchema]`
  - Behavior: case-insensitive regex match over `topic` and `description`, filtered by `visibility=true`

- `GET /projects/{projectId}`
  - Auth: public
  - Response model: `ProjectSchema`
  - Errors:
    - `400` for invalid `projectId`
    - `404` if project not found or not visible

#### Protected project routes

- `POST /projects/create`
  - Auth: protected, `allowed_roles=["view-profile", "manage-account"]`
  - Request model: `ProjectCreateSchema`
  - Response model: `ProjectSchema`
  - Status: `201`

- `PUT /projects/{projectId}`
  - Auth: protected, `allowed_roles=["view-profile", "manage-account"]`
  - Request model: `ProjectUpdateSchema`
  - Response model: `ProjectSchema`
  - Errors: `400` invalid ID, `404` not found

- `DELETE /projects/{projectId}`
  - Auth: protected, `allowed_roles=["view-profile", "manage-account"]`
  - Response: empty body
  - Status: `204`
  - Errors: `400` invalid ID, `404` not found

- `PUT /projects/{projectId}/featured`
  - Auth: protected, `allowed_roles=["view-profile", "manage-account"]`
  - Request body: `{ "featured": boolean }`
  - Response model: `ProjectSchema`
  - Errors: `404` not found
  - Note: route does not validate ObjectId before DB conversion.

#### Protected feedback routes

- `POST /projects/{projectId}/feedback`
  - Auth: protected, `allowed_roles=["view-profile", "manage-account"]`
  - Request model: `FeedbackCreate`
  - Response model: `FeedbackResponse`
  - Status: `201`

- `GET /projects/{projectId}/feedback`
  - Auth: protected, `allowed_roles=["view-profile", "manage-account"]`
  - Response model: `List[FeedbackResponse]`
  - Behavior: sorted by `created_at` descending

- `DELETE /projects/feedback/{feedbackId}`
  - Auth: protected, `allowed_roles=["view-profile", "manage-account"]`
  - Status: `204`
  - Errors: `400` invalid ID, `404` not found

- `PUT /projects/feedback/{feedbackId}/rank`
  - Auth: protected, `allowed_roles=["view-profile", "manage-account"]`
  - Request model: `FeedbackUpdate`
  - Response model: `FeedbackResponse`
  - Errors: `400` invalid ID, `404` not found

### Utils (`/utils`)

- `POST /utils/generate_thumbnail`
  - Auth: public
  - Request model: `thumbnail` (`title`, `weburl`)
  - Response: passthrough payload from `services.thumbnail_service.generate_thumbnail`
  - Error behavior: catches exceptions and returns `{"error": "..."}`

## Primary Data Contracts

- Project create/update/list/read schemas: `schemas/project.py`
- Feedback create/update/read schemas: `schemas/feedback.py`
- Keycloak user projection: `schemas/keycloak.py`

## Contract Caveats for Consumers

- Some protected routes are broad in authorization scope and may tighten in future revisions.
- `/user/me` returns roles from `resource_access.account.roles`, which differs from role source used for authorization checks.
- Search semantics are regex-based and may evolve to safer/indexed search behavior.
