from typing import List
from fastapi import APIRouter, Depends
from auth.jwt_bearer import JWTBearer
from schemas.user import UserProfile
from services.auth_service import get_all_users, get_user_by_id, cache_profile

router = APIRouter()

@router.get(
    "/users",
    response_model=List[UserProfile],
    dependencies=[Depends(JWTBearer(allowed_roles=["admin", "authenticated"]))],
)
async def list_users():
    """List all users who have recently authenticated (cached)."""
    return get_all_users()

@router.get(
    "/user/{user_id}",
    response_model=UserProfile,
    dependencies=[Depends(JWTBearer(allowed_roles=["admin", "authenticated"]))],
)
async def get_user(user_id: str):
    user = get_user_by_id(user_id)
    if not user:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="User not found in cache")
    return user

@router.get("/me", response_model=dict)
async def get_current_user_info(payload: dict = Depends(JWTBearer(allowed_roles=["view-profile", "manage-account", "authenticated"]))):
    """
    Get current authenticated user's information directly from the Supabase JWT payload.
    """
    user_id = payload.get("sub")
    # Cache profile for other service calls
    cache_profile(user_id, payload)
    
    metadata = payload.get("user_metadata", {})
    return {
        "user_id": user_id,
        "email": payload.get("email"),
        "username": metadata.get("username"),
        "first_name": metadata.get("first_name"),
        "last_name": metadata.get("last_name"),
        "roles": payload.get("app_metadata", {}).get("roles", [])
    }

@router.get("/dashboard", dependencies=[Depends(JWTBearer(allowed_roles=["view-profile", "manage-account", "authenticated"]))])
async def user_dashboard():
    """
    User dashboard endpoint, accessible to users with required roles.
    """
    return {"message": "Welcome to the user dashboard!"}