"""
Video upload endpoint
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid
import os
import shutil
from pathlib import Path
import logging
from typing import Optional
import json

from ..core.config import settings
from ..models import ProcessingJob, JobStatus, get_db
from ..models.schemas import UploadResponse, VideoConfig, ErrorResponse
from ..tasks.processor import process_video_task

logger = logging.getLogger(__name__)

router = APIRouter()


def validate_video_file(filename: str) -> bool:
    """Validate video file extension"""
    ext = Path(filename).suffix.lower()
    return ext in settings.ALLOWED_VIDEO_FORMATS


@router.post("", response_model=UploadResponse, responses={400: {"model": ErrorResponse}})
async def upload_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="Video file to process"),
    target_duration: int = Form(default=30, description="Target highlight duration in seconds"),
    quality: str = Form(default="high", description="Output quality: low, medium, high"),
    device_token: Optional[str] = Form(default=None, description="APNs device token for push notifications"),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload a video for processing

    Args:
        file: Video file (mp4, mov, avi, mkv)
        target_duration: Desired highlight length (10-300 seconds)
        quality: Output quality setting
        device_token: Optional push notification token

    Returns:
        job_id and estimated processing time
    """

    # Validate file
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    if not validate_video_file(file.filename):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file format. Allowed formats: {', '.join(settings.ALLOWED_VIDEO_FORMATS)}"
        )

    # Generate job ID
    job_id = str(uuid.uuid4())

    # Save uploaded file
    upload_path = settings.UPLOAD_DIR / f"{job_id}_{file.filename}"

    try:
        # Stream file to disk
        with open(upload_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        file_size = upload_path.stat().st_size

        # Check file size
        if file_size > settings.MAX_UPLOAD_SIZE:
            upload_path.unlink()  # Delete file
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size: {settings.MAX_UPLOAD_SIZE / (1024**3):.1f}GB"
            )

        logger.info(f"File uploaded: {job_id} - {file.filename} ({file_size / (1024**2):.1f}MB)")

    except Exception as e:
        logger.error(f"Upload failed: {e}")
        if upload_path.exists():
            upload_path.unlink()
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

    # Create processing config
    config = VideoConfig(target_duration=target_duration, quality=quality)

    # Create job record
    job = ProcessingJob(
        id=job_id,
        original_filename=file.filename,
        upload_path=str(upload_path),
        file_size=file_size,
        status=JobStatus.PENDING,
        target_duration=target_duration,
        config=config.dict(),
        device_token=device_token
    )

    db.add(job)
    await db.commit()
    await db.refresh(job)

    logger.info(f"Job created: {job_id}")

    # Queue processing task (background)
    background_tasks.add_task(process_video_task, job_id)

    # Estimate processing time (rough: 0.5x - 1x video duration)
    estimated_time = int(file_size / (1024 * 1024) * 2)  # ~2 seconds per MB

    return UploadResponse(
        job_id=job_id,
        message="Video uploaded successfully. Processing started.",
        estimated_time=estimated_time
    )


@router.get("/formats")
async def get_supported_formats():
    """Get list of supported video formats"""
    return {
        "formats": settings.ALLOWED_VIDEO_FORMATS,
        "max_size_gb": settings.MAX_UPLOAD_SIZE / (1024**3),
        "max_duration_minutes": settings.MAX_VIDEO_DURATION / 60
    }
