from fastapi import APIRouter, Depends

from auth.jwt_bearer import require_auth

router = APIRouter()


@router.get("/me")
async def get_current_user_info(user: dict = Depends(require_auth)):
    """Return the current authenticated user's normalized profile.

    The frontend uses this to (a) decide whether to show admin-only UI and
    (b) display the user's real first/last name across the app.
    """
    return {
        "user_id": user["user_id"],
        "email": user["email"],
        "first_name": user.get("first_name", ""),
        "last_name": user.get("last_name", ""),
        "username": user.get("username"),
        "role": user.get("role", "student"),
    }
