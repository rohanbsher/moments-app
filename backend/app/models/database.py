"""
Database models and session management
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Enum as SQLEnum
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import enum

from ..core.config import settings

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True
)

# Create async session factory
async_session_maker = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()

class JobStatus(str, enum.Enum):
    """Job status enumeration"""
    PENDING = "pending"
    UPLOADING = "uploading"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ProcessingJob(Base):
    """Video processing job model"""
    __tablename__ = "processing_jobs"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=True)  # Optional for MVP

    # File info
    original_filename = Column(String, nullable=False)
    upload_path = Column(String, nullable=False)
    output_path = Column(String, nullable=True)

    # Video metadata
    duration = Column(Float, nullable=True)
    file_size = Column(Integer, nullable=True)

    # Processing config
    config = Column(JSON, nullable=True)
    target_duration = Column(Integer, default=30)

    # Status
    status = Column(SQLEnum(JobStatus), default=JobStatus.PENDING, index=True)
    progress = Column(Integer, default=0)  # 0-100
    error_message = Column(String, nullable=True)

    # Processing results
    segments_selected = Column(Integer, nullable=True)
    processing_time = Column(Float, nullable=True)
    result_metadata = Column(JSON, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Push notification
    device_token = Column(String, nullable=True)  # APNs device token


# Async database session dependency
async def get_db() -> AsyncSession:
    """Get database session"""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Initialize database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
