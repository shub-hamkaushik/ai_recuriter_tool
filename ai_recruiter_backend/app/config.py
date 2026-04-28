from pydantic import Field
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    database_url: str = Field(default="postgresql://postgres:shubham45@localhost:5432/ai_recruiter")
    secret_key: str = Field(default="your-secret-key")
    jwt_secret_key: str = Field(default="change-me-dev-jwt-secret-key-at-least-32-bytes")
    llm_api_url: Optional[str] = Field(default=None)
    llm_api_key: Optional[str] = Field(default=None)
    openai_api_key: Optional[str] = Field(default=None)
    openai_model: str = Field(default="gpt-5.2")
    openai_base_url: str = Field(default="https://api.openai.com/v1")
    openai_project: Optional[str] = Field(default=None)
    upload_dir: str = Field(default="uploads")
    max_upload_mb: int = Field(default=5)

    class Config:
        env_file = ".env"

settings = Settings()
