from typing import List, Optional, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import json

import os

class Settings(BaseSettings):
    APP_ENV: str = "development"
    APP_NAME: str = "CareLens AI"
    API_VERSION: str = "0.1.0"
    DEBUG: bool = True
    
    HOST: str = "0.0.0.0"
    PORT: int = 8010
    
    CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            v = v.strip()
            if v.startswith("[") and v.endswith("]"):
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [i.strip() for i in v.split(",") if i.strip()]
        return v

    # Supabase Configuration (Milestone 2)
    SUPABASE_URL: str = "https://your-supabase-project.supabase.co"
    SUPABASE_ANON_KEY: str = "your-supabase-anon-key"
    SUPABASE_SERVICE_ROLE_KEY: Optional[str] = None
    SUPABASE_JWT_SECRET: Optional[str] = None

    # AI LLM Provider Configuration (Milestone 4)
    GEMINI_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None
    PRIMARY_LLM_MODEL: str = "gemini-2.5-flash"
    FALLBACK_LLM_MODEL: str = "llama-3.3-70b-versatile"

    model_config = SettingsConfigDict(
        env_file=[
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"),
            ".env"
        ],
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
