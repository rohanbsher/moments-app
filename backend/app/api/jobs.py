"""
Job status and management endpoints
"""
from fastapi import APIRouter, HTTPException, Depends, Response
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging
from pathlib import Path
from typing import Optional

from ..core.config import settings
from ..models import ProcessingJob, JobStatus, get_db
from ..models.schemas import JobStatusResponse, JobDetailResponse, ErrorResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/{job_id}/status", response_model=JobStatusResponse)
async def get_job_status(
    job_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get processing job status

    Returns current status, progress, and result URL if completed
    """
    result = await db.execute(select(ProcessingJob).where(ProcessingJob.id == job_id))
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Build response
    response = JobStatusResponse(
        job_id=job.id,
        status=job.status,
        progress=job.progress,
        message=_get_status_message(job),
        created_at=job.created_at,
        completed_at=job.completed_at,
        processing_time=job.processing_time
    )

    # Add result URL if completed
    if job.status == JobStatus.COMPLETED and job.output_path:
        response.result_url = f"{settings.API_V1_PREFIX}/jobs/{job_id}/download"

    return response


@router.get("/{job_id}", response_model=JobDetailResponse)
async def get_job_details(
    job_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed job information including metadata and results
    """
    result = await db.execute(select(ProcessingJob).where(ProcessingJob.id == job_id))
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    response = JobDetailResponse(
        job_id=job.id,
        status=job.status,
        progress=job.progress,
        original_filename=job.original_filename,
        file_size=job.file_size,
        duration=job.duration,
        target_duration=job.target_duration,
        config=job.config,
        segments_selected=job.segments_selected,
        processing_time=job.processing_time,
        result_metadata=job.result_metadata,
        created_at=job.created_at,
        started_at=job.started_at,
        completed_at=job.completed_at,
        error_message=job.error_message
    )

    # Add download URL if completed
    if job.status == JobStatus.COMPLETED and job.output_path:
        response.download_url = f"{settings.API_V1_PREFIX}/jobs/{job_id}/download"

    return response


@router.get("/{job_id}/download")
async def download_result(
    job_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Download processed highlight video

    Returns the video file or a redirect to cloud storage URL
    """
    result = await db.execute(select(ProcessingJob).where(ProcessingJob.id == job_id))
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status != JobStatus.COMPLETED:
        raise HTTPException(
            status_code=400,
            detail=f"Job not completed. Current status: {job.status}"
        )

    if not job.output_path:
        raise HTTPException(status_code=404, detail="Output file not found")

    output_path = Path(job.output_path)

    if not output_path.exists():
        logger.error(f"Output file missing: {output_path}")
        raise HTTPException(status_code=404, detail="Output file not found on server")

    # Return file
    return FileResponse(
        path=output_path,
        media_type="video/mp4",
        filename=f"highlight_{job.original_filename}"
    )


@router.delete("/{job_id}")
async def cancel_job(
    job_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Cancel a pending or processing job
    """
    result = await db.execute(select(ProcessingJob).where(ProcessingJob.id == job_id))
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot cancel job with status: {job.status}"
        )

    # Update status
    job.status = JobStatus.CANCELLED
    await db.commit()

    logger.info(f"Job cancelled: {job_id}")

    return {"message": "Job cancelled successfully", "job_id": job_id}


def _get_status_message(job: ProcessingJob) -> Optional[str]:
    """Generate user-friendly status message"""
    if job.status == JobStatus.PENDING:
        return "Waiting to start..."
    elif job.status == JobStatus.UPLOADING:
        return "Uploading video..."
    elif job.status == JobStatus.PROCESSING:
        if job.progress < 20:
            return "Analyzing scenes..."
        elif job.progress < 50:
            return "Detecting motion..."
        elif job.progress < 80:
            return "Analyzing audio..."
        else:
            return "Creating highlight..."
    elif job.status == JobStatus.COMPLETED:
        return "Highlight ready!"
    elif job.status == JobStatus.FAILED:
        return job.error_message or "Processing failed"
    elif job.status == JobStatus.CANCELLED:
        return "Job cancelled"
    return None
