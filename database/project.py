from typing import List, Optional, Tuple
from bson import ObjectId

from models.project import Project, ProjectUpdate


def _visibility_filter(include_hidden: bool) -> dict:
    return {} if include_hidden else {"visibility": True}


async def get_project(id: ObjectId) -> Optional[Project]:
    return await Project.get(id)


async def create_project(project: Project) -> Project:
    return await project.insert()


async def update_project(id: ObjectId, project_update: ProjectUpdate) -> Optional[Project]:
    """Partial update. Reloads from DB so callers never see a stale snapshot."""
    project = await Project.get(id)
    if not project:
        return None
    update_data = project_update.dict(exclude_unset=True)
    if update_data:
        await project.update({"$set": update_data})
    return await Project.get(id)


async def delete_project(id: ObjectId) -> bool:
    project = await Project.get(id)
    if project:
        await project.delete()
        return True
    return False


async def list_projects_paginated(
    *,
    featured: bool = False,
    include_hidden: bool = False,
    page: int = 1,
    limit: int = 12,
) -> Tuple[List[Project], int]:
    """Paginated listing. ``include_hidden=True`` is for admin views only."""
    query: dict = _visibility_filter(include_hidden)
    if featured:
        query["featured"] = True

    skip = max(0, (page - 1) * limit)
    total = await Project.find(query).count()
    items = await Project.find(query).sort("-created_at").skip(skip).limit(limit).to_list()
    return items, total


async def search_projects(query: str, *, include_hidden: bool = False) -> List[Project]:
    """Case-insensitive substring search across topic, description, search_tags
    and contributors. Filters by visibility unless include_hidden is set.
    """
    base_filter = _visibility_filter(include_hidden)
    if not query:
        return await Project.find(base_filter).sort("-created_at").to_list()

    regex_clauses = [
        {"topic": {"$regex": query, "$options": "i"}},
        {"description": {"$regex": query, "$options": "i"}},
        {"search_tags": {"$regex": query, "$options": "i"}},
        {"contributors": {"$regex": query, "$options": "i"}},
    ]

    if base_filter:
        mongo_query = {"$and": [{"$or": regex_clauses}, base_filter]}
    else:
        mongo_query = {"$or": regex_clauses}

    return await Project.find(mongo_query).sort("-created_at").to_list()


async def set_featured_status(id: str, featured: bool) -> Optional[Project]:
    if not ObjectId.is_valid(id):
        return None
    project = await Project.get(ObjectId(id))
    if project:
        project.featured = featured
        await project.save()
        return project
    return None
