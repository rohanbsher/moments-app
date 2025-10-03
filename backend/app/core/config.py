"""
Application configuration using Pydantic settings
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
import os
from pathlib import Path

class Settings(BaseSettings):
    """Application settings"""

    # API Settings
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Moments API"
    VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Security
    SECRET_KEY: str = Field(default="dev-secret-key-change-in-production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # Database
    DATABASE_URL: str = Field(default="sqlite+aiosqlite:///./moments.db")

    # Redis (for Celery)
    REDIS_URL: str = Field(default="redis://localhost:6379/0")

    # Storage
    STORAGE_TYPE: str = "local"  # local, s3, r2
    UPLOAD_DIR: Path = Path("storage/uploads")
    OUTPUT_DIR: Path = Path("storage/outputs")
    MAX_UPLOAD_SIZE: int = 5 * 1024 * 1024 * 1024  # 5GB

    # S3/R2 (optional, for cloud deployment)
    S3_BUCKET: Optional[str] = None
    S3_REGION: Optional[str] = None
    S3_ACCESS_KEY: Optional[str] = None
    S3_SECRET_KEY: Optional[str] = None
    S3_ENDPOINT: Optional[str] = None  # For Cloudflare R2

    # Video Processing
    DEFAULT_TARGET_DURATION: int = 30  # seconds
    MAX_VIDEO_DURATION: int = 1800  # 30 minutes
    ALLOWED_VIDEO_FORMATS: list = [".mp4", ".mov", ".avi", ".mkv"]

    # Celery
    CELERY_BROKER_URL: str = Field(default="redis://localhost:6379/0")
    CELERY_RESULT_BACKEND: str = Field(default="redis://localhost:6379/0")

    # Push Notifications (APNs)
    APNS_ENABLED: bool = False
    APNS_KEY_PATH: Optional[str] = None
    APNS_KEY_ID: Optional[str] = None
    APNS_TEAM_ID: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create directories if they don't exist
        self.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        self.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
