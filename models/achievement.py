from datetime import datetime
from typing import List, Optional

from beanie import Document
from pydantic import BaseModel, Field


class Achievement(Document):
    """An award, competition placement, publication or similar recognition.

    Distinct from Project: an Achievement is something the chapter or its
    students earned, not built.
    """
    title: str
    description: str
    category: str  # e.g. "competition", "award", "publication", "recognition"
    date: datetime
    image: str
    recipients: List[str] = []          # free-text names, like Project.contributors
    batch: Optional[str] = None
    search_tags: List[str] = []
    width: int = 1200
    height: int = 800
    visibility: bool = True
    featured: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Achievement {self.title}>"

    class Settings:
        name = "achievements"
        use_state_management = True

    @classmethod
    async def get_visible(cls) -> List["Achievement"]:
        return await cls.find({"visibility": True}).sort("-date").to_list()

    @classmethod
    async def get_featured(cls) -> List["Achievement"]:
        return await cls.find({"featured": True, "visibility": True}).sort("-date").to_list()


class AchievementUpdate(BaseModel):
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
