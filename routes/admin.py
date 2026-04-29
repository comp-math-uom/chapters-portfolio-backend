from fastapi import APIRouter, Depends
from auth.jwt_bearer import JWTBearer

router = APIRouter()

@router.get("/dashboard", dependencies=[Depends(JWTBearer(allowed_roles=["view-profile", "manage-account"]))])
async def admin_dashboard():
    """
    Admin dashboard endpoint, accessible only to users with the required roles in Supabase.
    """
    return {"message": "Welcome to the admin dashboard!"}