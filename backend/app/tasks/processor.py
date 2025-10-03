"""
Video processing task - integrates with existing Moments algorithm
"""
import sys
import os
from pathlib import Path
import logging
from datetime import datetime
import asyncio
import json
import numpy as np
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Add parent directory to path to import core modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from core.simple_processor import SimpleVideoProcessor, SimpleConfig
from backend.app.models.database import ProcessingJob, JobStatus, Base
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

# Create async engine for background tasks
engine = create_async_engine(settings.DATABASE_URL, echo=False)
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


def convert_numpy_types(obj):
    """Convert NumPy types to Python native types for JSON serialization"""
    if isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, np.bool_):
        return bool(obj)
    else:
        return obj


async def update_job_status(
    job_id: str,
    status: JobStatus = None,
    progress: int = None,
    error_message: str = None,
    **kwargs
):
    """Update job status in database"""
    async with async_session_maker() as session:
        result = await session.execute(
            select(ProcessingJob).where(ProcessingJob.id == job_id)
        )
        job = result.scalar_one_or_none()

        if job:
            if status:
                job.status = status
            if progress is not None:
                job.progress = progress
            if error_message:
                job.error_message = error_message

            # Update other fields
            for key, value in kwargs.items():
                if hasattr(job, key):
                    setattr(job, key, value)

            await session.commit()
            logger.info(f"Job {job_id} updated: status={status}, progress={progress}")


def process_video_task(job_id: str):
    """
    Process video task - runs in background

    This is a synchronous wrapper for the async processing task
    to be compatible with BackgroundTasks
    """
    asyncio.run(_process_video_async(job_id))


async def _process_video_async(job_id: str):
    """
    Async video processing task

    Integrates with the existing SimpleVideoProcessor
    """
    logger.info(f"Starting video processing for job: {job_id}")

    try:
        # Get job details
        async with async_session_maker() as session:
            result = await session.execute(
                select(ProcessingJob).where(ProcessingJob.id == job_id)
            )
            job = result.scalar_one_or_none()

            if not job:
                logger.error(f"Job not found: {job_id}")
                return

            upload_path = job.upload_path
            target_duration = job.target_duration
            original_filename = job.original_filename

        # Update status to processing
        await update_job_status(
            job_id,
            status=JobStatus.PROCESSING,
            progress=10,
            started_at=datetime.utcnow()
        )

        # Generate output path
        output_filename = f"highlight_{job_id}_{Path(original_filename).stem}.mp4"
        output_path = settings.OUTPUT_DIR / output_filename

        # Configure processor
        config = SimpleConfig(target_duration=target_duration)
        processor = SimpleVideoProcessor(config)

        # Progress callback
        async def progress_callback(stage: str, progress: int):
            """Update progress during processing"""
            await update_job_status(job_id, progress=progress)
            logger.info(f"Job {job_id} - {stage}: {progress}%")

        # Process video
        logger.info(f"Processing video: {upload_path} -> {output_path}")

        # Scene detection (0-30%)
        await update_job_status(job_id, progress=20)

        # Run processing (synchronous call to existing processor)
        result = await asyncio.to_thread(
            processor.process_video,
            str(upload_path),
            str(output_path)
        )

        # Update to 80% after processing
        await update_job_status(job_id, progress=80)

        # Video composition (80-100%)
        await update_job_status(job_id, progress=90)

        # Get video duration
        import cv2
        cap = cv2.VideoCapture(str(upload_path))
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        duration = frame_count / fps if fps > 0 else 0
        cap.release()

        # Convert NumPy types in result metadata
        result_clean = convert_numpy_types(result)

        # Mark as completed
        await update_job_status(
            job_id,
            status=JobStatus.COMPLETED,
            progress=100,
            output_path=str(output_path),
            duration=duration,
            segments_selected=result_clean.get('segments_selected', 0),
            processing_time=result_clean.get('processing_time', 0),
            result_metadata=result_clean,
            completed_at=datetime.utcnow()
        )

        logger.info(f"Job completed successfully: {job_id}")
        logger.info(f"  Input: {duration:.1f}s")
        logger.info(f"  Output: {result.get('output_duration', 0):.1f}s")
        logger.info(f"  Segments: {result.get('segments_selected', 0)}")
        logger.info(f"  Processing time: {result.get('processing_time', 0):.1f}s")

    except Exception as e:
        logger.error(f"Processing failed for job {job_id}: {e}", exc_info=True)
        await update_job_status(
            job_id,
            status=JobStatus.FAILED,
            error_message=str(e),
            completed_at=datetime.utcnow()
        )
