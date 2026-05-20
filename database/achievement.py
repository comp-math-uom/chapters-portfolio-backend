from typing import List, Optional, Tuple
from bson import ObjectId

from models.achievement import Achievement, AchievementUpdate


def _visibility_filter(include_hidden: bool) -> dict:
    return {} if include_hidden else {"visibility": True}


async def get_one(id: ObjectId) -> Optional[Achievement]:
    return await Achievement.get(id)


async def create(achievement: Achievement) -> Achievement:
    return await achievement.insert()


async def update(id: ObjectId, payload: AchievementUpdate) -> Optional[Achievement]:
    achievement = await Achievement.get(id)
    if not achievement:
        return None
    update_data = payload.dict(exclude_unset=True)
    if update_data:
        await achievement.update({"$set": update_data})
    return await Achievement.get(id)


async def delete(id: ObjectId) -> bool:
    achievement = await Achievement.get(id)
    if achievement:
        await achievement.delete()
        return True
    return False


async def list_paginated(
    *,
    featured: bool = False,
    include_hidden: bool = False,
    page: int = 1,
    limit: int = 12,
) -> Tuple[List[Achievement], int]:
    query: dict = _visibility_filter(include_hidden)
    if featured:
        query["featured"] = True

    skip = max(0, (page - 1) * limit)
    total = await Achievement.find(query).count()
    items = await Achievement.find(query).sort("-date").skip(skip).limit(limit).to_list()
    return items, total


async def search(query: str, *, include_hidden: bool = False) -> List[Achievement]:
    base_filter = _visibility_filter(include_hidden)
    if not query:
        return await Achievement.find(base_filter).sort("-date").to_list()

    regex_clauses = [
        {"title": {"$regex": query, "$options": "i"}},
        {"description": {"$regex": query, "$options": "i"}},
        {"search_tags": {"$regex": query, "$options": "i"}},
        {"recipients": {"$regex": query, "$options": "i"}},
        {"category": {"$regex": query, "$options": "i"}},
    ]
    if base_filter:
        mongo_query = {"$and": [{"$or": regex_clauses}, base_filter]}
    else:
        mongo_query = {"$or": regex_clauses}
    return await Achievement.find(mongo_query).sort("-date").to_list()


async def set_featured(id: ObjectId, featured: bool) -> Optional[Achievement]:
    achievement = await Achievement.get(id)
    if achievement:
        achievement.featured = featured
        await achievement.save()
        return achievement
    return None
