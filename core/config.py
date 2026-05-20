"""
Application settings.

Defaults declared inline are evaluated when the Settings *class body* runs,
which happens before pydantic-settings reads ``.env``. That timing meant a
plain ``os.getenv("ADMIN_EMAILS", "")`` would always return ``""`` locally,
silently dropping the admin allowlist. We now declare ADMIN_EMAILS /
BACKEND_CORS_ORIGINS as real pydantic fields so the env_file loader fills
them, and a single ``mode="before"`` validator handles both JSON arrays and
comma-separated forms.
"""
import json
from typing import List, Union

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _coerce_string_list(value: Union[str, list, None], *, lowercase: bool = False) -> List[str]:
    """Parse a value that may arrive as a JSON array, comma-separated string,
    or already-decoded list. Empty values produce an empty list.
    """
    if value is None or value == "":
        return []
    if isinstance(value, list):
        items = [str(v).strip() for v in value if str(v).strip()]
        return [i.lower() for i in items] if lowercase else items

    text = str(value).strip()
    if not text:
        return []
    try:
        parsed = json.loads(text)
        if isinstance(parsed, list):
            items = [str(v).strip() for v in parsed if str(v).strip()]
            return [i.lower() for i in items] if lowercase else items
    except json.JSONDecodeError:
        pass

    items = [item.strip() for item in text.split(",") if item.strip()]
    return [i.lower() for i in items] if lowercase else items


_DEFAULT_CORS_ORIGINS = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8000",
    "https://chapters-frontend-three.vercel.app",
    "https://www.aistudentchapter.lk",
    "https://aistudentchapter.lk",
]


class Settings(BaseSettings):
    PROJECT_NAME: str = "Chapters Portfolio API"

    # MongoDB settings
    MONGODB_URI: str
    MONGODB_DB: str

    # Supabase settings
    SUPABASE_URL: str
    SUPABASE_JWT_AUDIENCE: str = "authenticated"

    # Auth toggles
    DISABLE_AUTH: bool = False

    # CORS Settings — parsed from env, with a safe fallback that always
    # includes localhost so frontend dev never breaks.
    BACKEND_CORS_ORIGINS: List[str] = list(_DEFAULT_CORS_ORIGINS)

    # Admin allowlist (case-insensitive emails)
    ADMIN_EMAILS: List[str] = []

    # Contact-form delivery — Resend is preferred; SMTP is the fallback.
    RESEND_API_KEY: str = ""
    CONTACT_TO_EMAIL: str = ""
    CONTACT_FROM_EMAIL: str = "onboarding@resend.dev"
    CONTACT_SMTP_HOST: str = ""
    CONTACT_SMTP_PORT: int = 587
    CONTACT_SMTP_USER: str = ""
    CONTACT_SMTP_PASSWORD: str = ""

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def _parse_cors(cls, v):
        parsed = _coerce_string_list(v)
        if not parsed:
            return list(_DEFAULT_CORS_ORIGINS)
        # Always keep localhost reachable for local frontend dev.
        merged = parsed + [o for o in _DEFAULT_CORS_ORIGINS if o not in parsed and "localhost" in o]
        return merged

    @field_validator("ADMIN_EMAILS", mode="before")
    @classmethod
    def _parse_admin_emails(cls, v):
        return _coerce_string_list(v, lowercase=True)


settings = Settings()
