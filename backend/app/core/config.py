from pydantic import Field, field_validator
from pydantic_settings import BaseSettings as PydanticSettings
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()

ENV = os.getenv("ENVIRONMENT", "local")  # 'local'|'development'|'production'


class Settings(PydanticSettings):
    """ Default Config """
    # Application Configuration
    API_V1_STR: str = Field("/api/v1", env="API_V1_STR")
    APP_NAME: str = Field("FastAPI API", env="APP_NAME")
    APP_VERSION: str = Field("0.0.1", env="APP_VERSION")

    # CORS 설정
    BACKEND_CORS_ORIGINS: List[str] = []

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v):
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # External API Keys
    GROQ_API_KEY: str = Field("...", env="GROQ_API_KEY")
    GROQ_MODEL: str = Field("openai/gpt-oss-20b", env="GROQ_MODEL")

    # Security
    SECRET_KEY: str = Field("your-secret-key-here", env="SECRET_KEY")


settings = Settings()
