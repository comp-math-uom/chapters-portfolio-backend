"""
Authentication & role resolution for the portfolio backend.

The portal has 3 effective roles, derived from the Supabase JWT:
    - admin      : email in settings.ADMIN_EMAILS
    - student    : any other authenticated user
    - anonymous  : unauthenticated (no Bearer token)

Public endpoints have no dependency.
Authenticated-only endpoints use ``Depends(require_auth)``.
Admin-only endpoints use ``Depends(require_admin)``.

The legacy ``JWTBearer(allowed_roles=[...])`` is kept as a thin wrapper so
existing call sites keep working until they are migrated, but the role check
now goes through ``resolve_role`` instead of looking at unused
``app_metadata.roles`` claims.
"""
from typing import Optional, List

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from core.config import settings
from .supabase_auth import decode_supabase_token


# ---------- role resolution ----------

def resolve_role(email: Optional[str]) -> str:
    """Return 'admin' if email is in ADMIN_EMAILS, else 'student'."""
    if not email:
        return "student"
    return "admin" if email.lower() in settings.ADMIN_EMAILS else "student"


def _payload_to_user(payload: dict) -> dict:
    metadata = payload.get("user_metadata", {}) or {}
    email = payload.get("email")
    return {
        "user_id": payload.get("sub"),
        "email": email,
        "first_name": metadata.get("first_name") or metadata.get("firstName") or "",
        "last_name": metadata.get("last_name") or metadata.get("lastName") or "",
        "username": metadata.get("username"),
        "role": resolve_role(email),
        "raw": payload,
    }


# ---------- dependencies ----------

_bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer_scheme),
) -> dict:
    """Decode the Bearer token and return a normalized user dict.

    Raises 401 if no/invalid token. For optional auth, use ``get_optional_user``.
    """
    if settings.DISABLE_AUTH:
        return {
            "user_id": "test-user",
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
            "username": "test-user",
            "role": "admin",
            "raw": {},
        }

    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")

    payload = decode_supabase_token(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    return _payload_to_user(payload)


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer_scheme),
) -> Optional[dict]:
    """Best-effort user resolution. Returns None for anonymous callers."""
    if credentials is None or credentials.scheme.lower() != "bearer":
        return None
    try:
        payload = decode_supabase_token(credentials.credentials)
    except HTTPException:
        return None
    if not payload:
        return None
    return _payload_to_user(payload)


async def require_auth(user: dict = Depends(get_current_user)) -> dict:
    """Require any authenticated user (student or admin)."""
    return user


async def require_admin(user: dict = Depends(get_current_user)) -> dict:
    """Require an admin user (email in ADMIN_EMAILS)."""
    if user.get("role") != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return user


# ---------- legacy shim ----------

class JWTBearer(HTTPBearer):
    """Legacy class kept for backwards compatibility.

    New code should use ``Depends(require_auth)`` or ``Depends(require_admin)``.
    Any ``allowed_roles`` containing the literal ``"admin"`` enforces admin;
    otherwise, only authentication is required.
    """

    def __init__(self, auto_error: bool = True, allowed_roles: Optional[List[str]] = None):
        super().__init__(auto_error=auto_error)
        self.allowed_roles = allowed_roles or []
        self._admin_only = "admin" in (r.lower() for r in self.allowed_roles)

    async def __call__(self, request: Request):
        if settings.DISABLE_AUTH:
            return {
                "sub": "test-user",
                "email": "test@example.com",
                "user_metadata": {"first_name": "Test", "last_name": "User"},
                "role": "admin",
            }

        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        if not credentials or credentials.scheme.lower() != "bearer":
            raise HTTPException(status_code=403, detail="Invalid authentication scheme.")

        payload = decode_supabase_token(credentials.credentials)
        if not payload:
            raise HTTPException(status_code=403, detail="Invalid or expired token.")

        if self._admin_only:
            email = payload.get("email")
            if not email or email.lower() not in settings.ADMIN_EMAILS:
                raise HTTPException(status_code=403, detail="Admin access required")

        return payload
