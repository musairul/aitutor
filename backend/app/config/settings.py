from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # App settings
    app_name: str = "AI Tutor"
    debug: bool = True
    
    # Supabase settings
    supabase_url: str
    supabase_key: str
    supabase_jwt_secret: str
    
    # CORS settings
    cors_origins: list = ["http://localhost:3000", "http://localhost:5173"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
