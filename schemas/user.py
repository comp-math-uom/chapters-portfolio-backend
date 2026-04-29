from typing import Any

from pydantic import BaseModel, EmailStr


class UserProfile(BaseModel):
    id: str | None = None
    username: str
    email: EmailStr | None = None
    firstName: str | None = None
    lastName: str | None = None
    profile_pic_url: str = ""
    attributes: dict[str, Any] | None = None

    model_config = {
        "extra": "ignore",
    }
