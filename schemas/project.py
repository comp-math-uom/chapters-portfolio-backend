from datetime import datetime
from typing import List, Optional

from beanie import PydanticObjectId
from pydantic import BaseModel


class ProjectSchema(BaseModel):
    id: PydanticObjectId
    topic: str
    description: str
    batch: str
    contributors: List[str]
    search_tags: List[str]
    date: datetime
    image: str
    width: int
    height: int
    visibility: bool
    featured: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ProjectCreateSchema(BaseModel):
    topic: str
    description: str
    batch: str
    contributors: List[str]
    search_tags: List[str]
    date: datetime
    image: str
    width: int
    height: int
    visibility: bool = True
    featured: bool = True

    class Config:
        json_schema_extra = {
            "example": {
                "topic": "Chapters Portfolio API",
                "description": "Backend service for the portfolio",
                "batch": "2026",
                "contributors": ["Alice", "Bob"],
                "search_tags": ["fastapi", "mongodb"],
                "date": "2026-01-09T00:00:00Z",
                "image": "https://example.com/image.png",
                "width": 1200,
                "height": 630,
                "visibility": True,
                "featured": True,
            }
        }


class ProjectUpdateSchema(BaseModel):
    topic: Optional[str] = None
    description: Optional[str] = None
    image: Optional[str] = None
    batch: Optional[str] = None
    contributors: Optional[List[str]] = None
    search_tags: Optional[List[str]] = None
    date: Optional[datetime] = None
    width: Optional[int] = None
    height: Optional[int] = None
    visibility: Optional[bool] = None
    featured: Optional[bool] = None

    class Config:
        json_schema_extra = {
            "example": {
                "topic": "My Updated Topic",
                "description": "Updated description",
                "contributors": ["Alice", "Bob", "Carol"],
                "search_tags": ["ai", "ml"],
                "visibility": True,
                "featured": False,
            }
        }


class ProjectListSchema(BaseModel):
    """Paginated list response."""
    projects: List[ProjectSchema]
    total: int = 0
    page: int = 1
    limit: int = 12
