from datetime import datetime
from typing import List, Optional

from beanie import Document
from pydantic import BaseModel, Field


class Project(Document):
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
    created_at: datetime = Field(default_factory=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Project {self.topic}>"

    class Settings:
        name = "projects"
        use_state_management = True

    async def save_with_timestamp(self) -> None:
        self.updated_at = datetime.utcnow()
        await self.save()

    @classmethod
    async def get_visible_projects(cls) -> List["Project"]:
        return await cls.find({"visibility": True}).to_list()

    @classmethod
    async def get_featured_projects(cls) -> List["Project"]:
        return await cls.find({"featured": True, "visibility": True}).to_list()


class ProjectUpdate(BaseModel):
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


class ProjectSearch(BaseModel):
    query: str
