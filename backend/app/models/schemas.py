"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class JobStatusEnum(str, Enum):
    """Job status enumeration"""
    PENDING = "pending"
    UPLOADING = "uploading"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class VideoConfig(BaseModel):
    """Video processing configuration"""
    target_duration: int = Field(default=30, ge=10, le=300)
    quality: str = Field(default="high", pattern="^(low|medium|high)$")


class UploadResponse(BaseModel):
    """Upload endpoint response"""
    job_id: str
    message: str
    estimated_time: Optional[int] = None  # seconds


class JobStatusResponse(BaseModel):
    """Job status endpoint response"""
    job_id: str
    status: JobStatusEnum
    progress: int = Field(ge=0, le=100)
    message: Optional[str] = None
    result_url: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    processing_time: Optional[float] = None

    class Config:
        from_attributes = True


class JobDetailResponse(BaseModel):
    """Detailed job information"""
    job_id: str
    status: JobStatusEnum
    progress: int

    # File info
    original_filename: str
    file_size: Optional[int] = None
    duration: Optional[float] = None

    # Processing config
    target_duration: int
    config: Optional[Dict[str, Any]] = None

    # Results
    segments_selected: Optional[int] = None
    processing_time: Optional[float] = None
    result_metadata: Optional[Dict[str, Any]] = None

    # URLs
    download_url: Optional[str] = None

    # Timestamps
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    error_message: Optional[str] = None

    class Config:
        from_attributes = True


class ErrorResponse(BaseModel):
    """Error response schema"""
    error: str
    detail: Optional[str] = None
    job_id: Optional[str] = None
