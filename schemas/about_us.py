from datetime import datetime
from typing import List, Optional

from beanie import PydanticObjectId
from pydantic import BaseModel

from models.about_us import TeamMember


class AboutUsSchema(BaseModel):
    id: Optional[PydanticObjectId] = None
    hero_title: str
    hero_subtitle: str
    body_markdown: str
    cover_image: Optional[str] = None
    team: List[TeamMember] = []
    contact_email: Optional[str] = None
    contact_links: List[str] = []
    updated_at: datetime

    class Config:
        from_attributes = True


class AboutUsUpdateSchema(BaseModel):
    hero_title: Optional[str] = None
    hero_subtitle: Optional[str] = None
    body_markdown: Optional[str] = None
    cover_image: Optional[str] = None
    team: Optional[List[TeamMember]] = None
    contact_email: Optional[str] = None
    contact_links: Optional[List[str]] = None
