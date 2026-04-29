from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .supabase_auth import decode_supabase_token
from core.config import settings

class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True, allowed_roles: list = None):
        super(JWTBearer, self).__init__(auto_error=auto_error)
        self.allowed_roles = allowed_roles or []

    async def __call__(self, request: Request):
        # Short-circuit auth when explicitly disabled (useful for local testing)
        if settings.DISABLE_AUTH:
            return self._mock_payload()

        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if not credentials:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")
        
        if not credentials.scheme == "Bearer":
            raise HTTPException(status_code=403, detail="Invalid authentication scheme.")
        
        payload = decode_supabase_token(credentials.credentials)
        
        if not payload:
            raise HTTPException(status_code=403, detail="Invalid or expired token.")

        if self.allowed_roles:
            user_roles = self.get_user_roles(payload)
            if not any(role in user_roles for role in self.allowed_roles):
                raise HTTPException(status_code=403, detail="You don't have permission to access this resource.")
        
        return payload

    def _mock_payload(self) -> dict:
        """Return a permissive payload when auth is disabled for testing."""
        roles = self.allowed_roles if self.allowed_roles else ["view-profile", "manage-account", "admin"]
        return {
            "sub": "test-user",
            "email": "test@example.com",
            "user_metadata": {
                "username": "test-user",
                "first_name": "Test",
                "last_name": "User"
            },
            "app_metadata": {
                "roles": roles
            }
        }

    def get_user_roles(self, payload: dict) -> list:
        """
        Extracts roles from the 'app_metadata' claim in Supabase.
        """
        try:
            return payload.get("app_metadata", {}).get("roles", [])
        except AttributeError:
            return []