from datetime import datetime
from typing import List, Optional

from beanie import PydanticObjectId
from pydantic import BaseModel


class AchievementSchema(BaseModel):
    id: PydanticObjectId
    title: str
    description: str
    category: str
    date: datetime
    image: str
    recipients: List[str]
    batch: Optional[str] = None
    search_tags: List[str] = []
    width: int
    height: int
    visibility: bool
    featured: bool
    created_at: datetime

    class Config:
        from_attributes = True


class AchievementCreateSchema(BaseModel):
    title: str
    description: str
    category: str
    date: datetime
    image: str
    recipients: List[str] = []
    batch: Optional[str] = None
    search_tags: List[str] = []
    width: int = 1200
    height: int = 800
    visibility: bool = True
    featured: bool = False

    class Config:
        json_schema_extra = {
            "example": {
                "title": "1st place — Inter-Uni AI Hackathon 2026",
                "description": "Team Alpha placed first out of 42 teams.",
                "category": "competition",
                "date": "2026-03-15T00:00:00Z",
                "image": "https://example.com/award.png",
                "recipients": ["Alice", "Bob", "Carol"],
                "batch": "2026",
                "search_tags": ["hackathon", "ml"],
                "width": 1200,
                "height": 800,
                "visibility": True,
                "featured": True,
            }
        }


class AchievementUpdateSchema(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    date: Optional[datetime] = None
    image: Optional[str] = None
    recipients: Optional[List[str]] = None
    batch: Optional[str] = None
    search_tags: Optional[List[str]] = None
    width: Optional[int] = None
    height: Optional[int] = None
    visibility: Optional[bool] = None
    featured: Optional[bool] = None


class AchievementListSchema(BaseModel):
    achievements: List[AchievementSchema]
    total: int = 0
    page: int = 1
    limit: int = 12
