from fastapi import APIRouter, Depends

from auth.jwt_bearer import require_admin

router = APIRouter()


@router.get("/dashboard", dependencies=[Depends(require_admin)])
async def admin_dashboard():
    """Admin dashboard ping. Useful for verifying an admin JWT in dev."""
    return {"message": "Welcome to the admin dashboard!"}
