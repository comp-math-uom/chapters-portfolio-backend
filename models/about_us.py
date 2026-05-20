from datetime import datetime
from typing import List, Optional

from beanie import Document
from pydantic import BaseModel, Field


class TeamMember(BaseModel):
    name: str
    role: str
    image_url: Optional[str] = None


class AboutUs(Document):
    """Singleton document — only ever one row, keyed by ``key='main'``."""
    key: str = "main"
    hero_title: str = "About Chapters"
    hero_subtitle: str = "The AI Student Chapter"
    body_markdown: str = ""
    cover_image: Optional[str] = None
    team: List[TeamMember] = []
    contact_email: Optional[str] = None
    contact_links: List[str] = []  # social/contact URLs
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "about_us"
        use_state_management = True


class AboutUsUpdate(BaseModel):
    hero_title: Optional[str] = None
    hero_subtitle: Optional[str] = None
    body_markdown: Optional[str] = None
    cover_image: Optional[str] = None
    team: Optional[List[TeamMember]] = None
    contact_email: Optional[str] = None
    contact_links: Optional[List[str]] = None
