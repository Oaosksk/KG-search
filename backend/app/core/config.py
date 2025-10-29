from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str
    OPENROUTER_API_KEY: Optional[str] = "sk-dummy-key"
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    LLM_MODEL: str = "deepseek/deepseek-r1"
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    FRONTEND_URL: str
    BACKEND_URL: str
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    
    class Config:
        env_file = ".env"

settings = Settings()
