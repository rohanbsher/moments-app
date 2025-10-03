"""
Main FastAPI application
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging

from .core.config import settings
from .models import init_db
from .api import upload, jobs

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting Moments API...")
    await init_db()
    logger.info("Database initialized")
    yield
    # Shutdown
    logger.info("Shutting down Moments API...")


# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AI-powered video highlight generation API",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for iOS app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify iOS app domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.DEBUG else "An error occurred"
        }
    )


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "service": settings.PROJECT_NAME
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API info"""
    return {
        "message": "Welcome to Moments API",
        "version": settings.VERSION,
        "docs": "/docs",
        "health": "/health"
    }


# Include routers
app.include_router(
    upload.router,
    prefix=f"{settings.API_V1_PREFIX}/upload",
    tags=["upload"]
)

app.include_router(
    jobs.router,
    prefix=f"{settings.API_V1_PREFIX}/jobs",
    tags=["jobs"]
)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
