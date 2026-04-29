from typing import List, Optional
from schemas.user import UserProfile
from fastapi import HTTPException

# In-memory cache for profiles from JWT claims (similar to blogs backend)
_profile_cache = {}

def cache_profile(user_id: str, payload: dict):
    metadata = payload.get("user_metadata", {})
    profile = UserProfile(
        id=user_id,
        username=metadata.get("username") or payload.get("email", "").split("@")[0] or user_id,
        email=payload.get("email"),
        firstName=metadata.get("first_name"),
        lastName=metadata.get("last_name"),
        profile_pic_url=metadata.get("avatar_url") or metadata.get("picture") or ""
    )
    _profile_cache[user_id] = profile

def get_all_users() -> List[UserProfile]:
    return list(_profile_cache.values())

def get_user_by_id(user_id: str) -> Optional[UserProfile]:
    return _profile_cache.get(user_id)
