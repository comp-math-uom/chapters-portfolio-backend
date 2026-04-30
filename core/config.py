import os
import json
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

def _parse_cors_origins(origins: str) -> List[str]:
    if not origins:
        return [
            "http://localhost",
            "http://localhost:3000",
            "http://localhost:8000",
            "https://chapters-frontend-three.vercel.app",
        ]
    try:
        # Try to parse as JSON array
        return json.loads(origins)
    except json.JSONDecodeError:
        # Fallback to comma-separated string
        return [origin.strip() for origin in origins.split(",") if origin.strip()]

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
    
    # CORS Settings
    BACKEND_CORS_ORIGINS: List[str] = _parse_cors_origins(os.getenv("BACKEND_CORS_ORIGINS", ""))
    
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)


settings = Settings()
