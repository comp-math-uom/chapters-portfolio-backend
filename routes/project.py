from fastapi import APIRouter, HTTPException, Query, Body, Depends, Response, status
from typing import List
from bson import ObjectId

from auth.jwt_bearer import JWTBearer
from models.feedback import Feedback
from models.project import Project, ProjectUpdate
from schemas.feedback import FeedbackCreate, FeedbackResponse, FeedbackUpdate
from schemas.project import ProjectSchema, ProjectUpdateSchema, ProjectCreateSchema, ProjectListSchema
from database import project as project_db

router = APIRouter()

# --- Public Routes ---

@router.get("/all", response_model=ProjectListSchema)
async def list_projects(featured: bool = False):
    try:
        if featured:
            projects = await Project.get_featured_projects()
        else:
            projects = await Project.get_visible_projects()
        return ProjectListSchema(projects=projects)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search/", response_model=List[ProjectSchema])
async def search_projects_by_query(query: str):
    return await project_db.search_projects(query)

@router.get("/{projectId}", response_model=ProjectSchema)
async def get_project_by_id(projectId: str):
    if not ObjectId.is_valid(projectId):
        raise HTTPException(status_code=400, detail="Invalid project ID")
    project = await project_db.get_project(ObjectId(projectId))
    if not project or not project.visibility:
        raise HTTPException(status_code=404, detail="Project not found or not visible")
    return project

# --- Protected Routes ---

@router.post("/create", response_model=ProjectSchema, status_code=201, dependencies=[Depends(JWTBearer(allowed_roles=["view-profile", "manage-account", "authenticated"]))])
async def create_new_project(project: ProjectCreateSchema):
    new_project = Project(**project.dict())
    return await project_db.create_project(new_project)

@router.put("/{projectId}", response_model=ProjectSchema, dependencies=[Depends(JWTBearer(allowed_roles=["view-profile", "manage-account", "authenticated"]))])
async def update_existing_project(projectId: str, project_update: ProjectUpdateSchema):
    if not ObjectId.is_valid(projectId):
        raise HTTPException(status_code=400, detail="Invalid project ID")
    
    # Using ProjectUpdate model as it aligns with the database function
    update_data = ProjectUpdate(**project_update.dict(exclude_unset=True))
    updated_project = await project_db.update_project(ObjectId(projectId), update_data)
    
    if not updated_project:
        raise HTTPException(status_code=404, detail="Project not found")
    return updated_project

@router.delete("/{projectId}", status_code=204, dependencies=[Depends(JWTBearer(allowed_roles=["view-profile", "manage-account", "authenticated"]))])
async def delete_existing_project(projectId: str):
    if not ObjectId.is_valid(projectId):
        raise HTTPException(status_code=400, detail="Invalid project ID")
    deleted = await project_db.delete_project(ObjectId(projectId))
    if not deleted:
        raise HTTPException(status_code=404, detail="Project not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put("/{projectId}/featured", response_model=ProjectSchema, dependencies=[Depends(JWTBearer(allowed_roles=["view-profile", "manage-account", "authenticated"]))])
async def set_project_featured_status(projectId: str, featured: bool = Body(..., embed=True)):
    updated_project = await project_db.set_featured_status(projectId, featured)
    if not updated_project:
        raise HTTPException(status_code=404, detail="Project not found")
    return updated_project

# --- Feedback Routes (Protected) ---

@router.post("/{projectId}/feedback", response_model=FeedbackResponse, status_code=201, dependencies=[Depends(JWTBearer(allowed_roles=["view-profile", "manage-account", "authenticated"]))])
async def add_feedback(projectId: str, feedback: FeedbackCreate):
    if not ObjectId.is_valid(projectId):
        raise HTTPException(status_code=400, detail="Invalid project ID")
    project = await Project.get(ObjectId(projectId))
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    new_feedback = Feedback(
        project_id=projectId,
        username=feedback.username,
        content=feedback.content,
    )
    await new_feedback.insert()
    return new_feedback


@router.get("/{projectId}/feedback", response_model=List[FeedbackResponse], dependencies=[Depends(JWTBearer(allowed_roles=["view-profile", "manage-account", "authenticated"]))])
async def get_feedback_for_project(projectId: str):
    if not ObjectId.is_valid(projectId):
        raise HTTPException(status_code=400, detail="Invalid project ID")
    project = await Project.get(ObjectId(projectId))
    if not project or not project.visibility:
        raise HTTPException(status_code=404, detail="Project not found or not visible")
    return await Feedback.find({"project_id": projectId}).sort("-created_at").to_list()

@router.delete("/feedback/{feedbackId}", status_code=204, dependencies=[Depends(JWTBearer(allowed_roles=["view-profile", "manage-account", "authenticated"]))])
async def delete_feedback_by_id(feedbackId: str):
    if not ObjectId.is_valid(feedbackId):
        raise HTTPException(status_code=400, detail="Invalid feedback ID")
    feedback = await Feedback.get(ObjectId(feedbackId))
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    await feedback.delete()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put("/feedback/{feedbackId}/rank", response_model=FeedbackResponse, dependencies=[Depends(JWTBearer(allowed_roles=["view-profile", "manage-account", "authenticated"]))])
async def rank_feedback(feedbackId: str, rank_update: FeedbackUpdate):
    if not ObjectId.is_valid(feedbackId):
        raise HTTPException(status_code=400, detail="Invalid feedback ID")
    feedback = await Feedback.get(ObjectId(feedbackId))
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    feedback.rank = rank_update.rank
    await feedback.save()
    return feedback