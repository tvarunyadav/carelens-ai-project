from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_ENV: str = "development"
    APP_NAME: str = "CareLens AI"
    API_VERSION: str = "0.1.0"
    DEBUG: bool = True
    
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
