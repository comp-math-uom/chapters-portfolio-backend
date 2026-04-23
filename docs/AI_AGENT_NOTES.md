# Chapters Portfolio Backend AI Agent Notes

## High-Risk Files
- `auth/jwt_bearer.py`
- `auth/jwt_handler.py`
- `routes/project.py`
- `routes/user.py`
- `core/config.py`

## Known Pitfalls
- `DISABLE_AUTH` allows mock payload and bypasses actual auth.
- Role requirements vary across routes and can be unintentionally permissive.
- Logging/observability is relatively basic, making silent regressions harder to detect.

## Safe Edit Strategy
1. Identify route auth intent before changing allowed roles.
2. Keep ObjectId validation and error responses consistent.
3. Preserve schema response compatibility for frontend consumers.
4. If changing auth logic, verify both enabled and disabled-auth local workflows.

## Verification Checklist
- Protected routes reject missing/invalid bearer token when auth enabled.
- Public routes continue to work without auth.
- CRUD and feedback routes maintain expected status codes.
- No accidental widening of role access after changes.
