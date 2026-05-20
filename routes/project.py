from fastapi import APIRouter, HTTPException, Body, Depends, Query, Response, status
from typing import List, Optional
from bson import ObjectId

from auth.jwt_bearer import require_admin, get_optional_user
from models.project import Project, ProjectUpdate
from schemas.project import ProjectSchema, ProjectUpdateSchema, ProjectCreateSchema, ProjectListSchema
from database import project as project_db

router = APIRouter()


# --- Public routes ---

@router.get("/all", response_model=ProjectListSchema)
async def list_projects(
    featured: bool = False,
    page: int = Query(1, ge=1),
    limit: int = Query(12, ge=1, le=100),
    user: Optional[dict] = Depends(get_optional_user),
):
    """Paginated project list. Admins automatically see hidden items too."""
    include_hidden = bool(user and user.get("role") == "admin")
    try:
        items, total = await project_db.list_projects_paginated(
            featured=featured,
            include_hidden=include_hidden,
            page=page,
            limit=limit,
        )
        return ProjectListSchema(projects=items, total=total, page=page, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search/", response_model=List[ProjectSchema])
async def search_projects_by_query(
    query: str,
    user: Optional[dict] = Depends(get_optional_user),
):
    include_hidden = bool(user and user.get("role") == "admin")
    return await project_db.search_projects(query, include_hidden=include_hidden)


@router.get("/{projectId}", response_model=ProjectSchema)
async def get_project_by_id(
    projectId: str,
    user: Optional[dict] = Depends(get_optional_user),
):
    if not ObjectId.is_valid(projectId):
        raise HTTPException(status_code=400, detail="Invalid project ID")
    project = await project_db.get_project(ObjectId(projectId))
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    # Hidden projects: only admins can see them.
    if not project.visibility and not (user and user.get("role") == "admin"):
        raise HTTPException(status_code=404, detail="Project not found")
    return project


# --- Admin-only routes ---

@router.post(
    "/create",
    response_model=ProjectSchema,
    status_code=201,
    dependencies=[Depends(require_admin)],
)
async def create_new_project(project: ProjectCreateSchema):
    new_project = Project(**project.dict())
    return await project_db.create_project(new_project)


@router.put(
    "/{projectId}",
    response_model=ProjectSchema,
    dependencies=[Depends(require_admin)],
)
async def update_existing_project(projectId: str, project_update: ProjectUpdateSchema):
    if not ObjectId.is_valid(projectId):
        raise HTTPException(status_code=400, detail="Invalid project ID")

    update_data = ProjectUpdate(**project_update.dict(exclude_unset=True))
    updated_project = await project_db.update_project(ObjectId(projectId), update_data)

    if not updated_project:
        raise HTTPException(status_code=404, detail="Project not found")
    return updated_project


@router.delete(
    "/{projectId}",
    status_code=204,
    dependencies=[Depends(require_admin)],
)
async def delete_existing_project(projectId: str):
    if not ObjectId.is_valid(projectId):
        raise HTTPException(status_code=400, detail="Invalid project ID")
    deleted = await project_db.delete_project(ObjectId(projectId))
    if not deleted:
        raise HTTPException(status_code=404, detail="Project not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put(
    "/{projectId}/featured",
    response_model=ProjectSchema,
    dependencies=[Depends(require_admin)],
)
async def set_project_featured_status(projectId: str, featured: bool = Body(..., embed=True)):
    if not ObjectId.is_valid(projectId):
        raise HTTPException(status_code=400, detail="Invalid project ID")
    updated_project = await project_db.set_featured_status(projectId, featured)
    if not updated_project:
        raise HTTPException(status_code=404, detail="Project not found")
    return updated_project
