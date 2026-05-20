from fastapi import APIRouter, HTTPException, Body, Depends, Query, Response, status
from typing import List, Optional
from bson import ObjectId

from auth.jwt_bearer import require_admin, get_optional_user
from models.achievement import Achievement, AchievementUpdate
from schemas.achievement import (
    AchievementSchema,
    AchievementCreateSchema,
    AchievementUpdateSchema,
    AchievementListSchema,
)
from database import achievement as achievement_db

router = APIRouter()


# --- Public routes ---

@router.get("/all", response_model=AchievementListSchema)
async def list_achievements(
    featured: bool = False,
    page: int = Query(1, ge=1),
    limit: int = Query(12, ge=1, le=100),
    user: Optional[dict] = Depends(get_optional_user),
):
    include_hidden = bool(user and user.get("role") == "admin")
    items, total = await achievement_db.list_paginated(
        featured=featured,
        include_hidden=include_hidden,
        page=page,
        limit=limit,
    )
    return AchievementListSchema(achievements=items, total=total, page=page, limit=limit)


@router.get("/search/", response_model=List[AchievementSchema])
async def search_achievements(
    query: str,
    user: Optional[dict] = Depends(get_optional_user),
):
    include_hidden = bool(user and user.get("role") == "admin")
    return await achievement_db.search(query, include_hidden=include_hidden)


@router.get("/{achievementId}", response_model=AchievementSchema)
async def get_achievement(
    achievementId: str,
    user: Optional[dict] = Depends(get_optional_user),
):
    if not ObjectId.is_valid(achievementId):
        raise HTTPException(status_code=400, detail="Invalid achievement ID")
    item = await achievement_db.get_one(ObjectId(achievementId))
    if not item:
        raise HTTPException(status_code=404, detail="Achievement not found")
    if not item.visibility and not (user and user.get("role") == "admin"):
        raise HTTPException(status_code=404, detail="Achievement not found")
    return item


# --- Admin-only routes ---

@router.post(
    "/create",
    response_model=AchievementSchema,
    status_code=201,
    dependencies=[Depends(require_admin)],
)
async def create_achievement(payload: AchievementCreateSchema):
    new_item = Achievement(**payload.dict())
    return await achievement_db.create(new_item)


@router.put(
    "/{achievementId}",
    response_model=AchievementSchema,
    dependencies=[Depends(require_admin)],
)
async def update_achievement(achievementId: str, payload: AchievementUpdateSchema):
    if not ObjectId.is_valid(achievementId):
        raise HTTPException(status_code=400, detail="Invalid achievement ID")
    update_data = AchievementUpdate(**payload.dict(exclude_unset=True))
    updated = await achievement_db.update(ObjectId(achievementId), update_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Achievement not found")
    return updated


@router.delete(
    "/{achievementId}",
    status_code=204,
    dependencies=[Depends(require_admin)],
)
async def delete_achievement(achievementId: str):
    if not ObjectId.is_valid(achievementId):
        raise HTTPException(status_code=400, detail="Invalid achievement ID")
    deleted = await achievement_db.delete(ObjectId(achievementId))
    if not deleted:
        raise HTTPException(status_code=404, detail="Achievement not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put(
    "/{achievementId}/featured",
    response_model=AchievementSchema,
    dependencies=[Depends(require_admin)],
)
async def set_featured(achievementId: str, featured: bool = Body(..., embed=True)):
    if not ObjectId.is_valid(achievementId):
        raise HTTPException(status_code=400, detail="Invalid achievement ID")
    updated = await achievement_db.set_featured(ObjectId(achievementId), featured)
    if not updated:
        raise HTTPException(status_code=404, detail="Achievement not found")
    return updated
