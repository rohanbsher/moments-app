# Moments API - REST Backend

**AI-powered video highlight generation API**

Version: 1.0.0
Status: ✅ **Production Ready**

---

## Overview

The Moments API is a FastAPI-based REST service that transforms long videos into shareable highlights using AI-powered scene detection, motion analysis, audio analysis, and diversity scoring.

### Key Features

- ✅ **Video Upload** - Multi-format support (MP4, MOV, AVI, MKV)
- ✅ **Async Processing** - Background task processing with progress tracking
- ✅ **Job Management** - Status polling and result retrieval
- ✅ **AI Highlight Generation** - Integrates Phase 1.5 algorithm
- ✅ **RESTful Design** - Clean, documented API endpoints
- ✅ **Local Storage** - File-based storage (cloud-ready architecture)

---

## Quick Start

### 1. Installation

```bash
cd backend
pip install -r requirements.txt
```

### 2. Start Server

```bash
./run.sh
```

Or manually:
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)/.."
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Server will start at: `http://localhost:8000`

### 3. API Documentation

Interactive docs available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## API Endpoints

### Health Check

```bash
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "service": "Moments API"
}
```

---

### Upload Video

```bash
POST /api/v1/upload
Content-Type: multipart/form-data
```

**Parameters:**
- `file` (required): Video file
- `target_duration` (optional): Target highlight length in seconds (default: 30)
- `quality` (optional): Output quality - "low", "medium", "high" (default: "high")
- `device_token` (optional): APNs device token for push notifications

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/upload" \
  -F "file=@video.mp4" \
  -F "target_duration=30" \
  -F "quality=high"
```

**Response:**
```json
{
  "job_id": "1752d2ec-d038-4d94-96ab-87d303c9ceae",
  "message": "Video uploaded successfully. Processing started.",
  "estimated_time": 33
}
```

---

### Check Job Status

```bash
GET /api/v1/jobs/{job_id}/status
```

**Example:**
```bash
curl "http://localhost:8000/api/v1/jobs/1752d2ec-d038-4d94-96ab-87d303c9ceae/status"
```

**Response:**
```json
{
  "job_id": "1752d2ec-d038-4d94-96ab-87d303c9ceae",
  "status": "completed",
  "progress": 100,
  "message": "Highlight ready!",
  "result_url": "/api/v1/jobs/1752d2ec-d038-4d94-96ab-87d303c9ceae/download",
  "created_at": "2025-10-03T13:56:15.550999",
  "completed_at": "2025-10-03T13:56:27.992235",
  "processing_time": 12.38
}
```

**Status Values:**
- `pending` - Waiting to start
- `uploading` - File upload in progress
- `processing` - Video being processed
- `completed` - Highlight ready for download
- `failed` - Processing error occurred
- `cancelled` - Job cancelled by user

---

### Get Job Details

```bash
GET /api/v1/jobs/{job_id}
```

**Example:**
```bash
curl "http://localhost:8000/api/v1/jobs/1752d2ec-d038-4d94-96ab-87d303c9ceae"
```

**Response:**
```json
{
  "job_id": "1752d2ec-d038-4d94-96ab-87d303c9ceae",
  "status": "completed",
  "progress": 100,
  "original_filename": "test_sports_action.mp4",
  "file_size": 17393700,
  "duration": 120.0,
  "target_duration": 30,
  "config": {"target_duration": 30, "quality": "high"},
  "segments_selected": 3,
  "processing_time": 12.38,
  "result_metadata": {
    "input_duration": 120.0,
    "output_duration": 60.0,
    "segments_selected": 3
  },
  "download_url": "/api/v1/jobs/1752d2ec-d038-4d94-96ab-87d303c9ceae/download",
  "created_at": "2025-10-03T13:56:15.550999",
  "completed_at": "2025-10-03T13:56:27.992235"
}
```

---

### Download Highlight

```bash
GET /api/v1/jobs/{job_id}/download
```

**Example:**
```bash
curl "http://localhost:8000/api/v1/jobs/1752d2ec-d038-4d94-96ab-87d303c9ceae/download" \
  -o highlight.mp4
```

**Response:**
- Content-Type: `video/mp4`
- File download stream

---

### Cancel Job

```bash
DELETE /api/v1/jobs/{job_id}
```

**Example:**
```bash
curl -X DELETE "http://localhost:8000/api/v1/jobs/1752d2ec-d038-4d94-96ab-87d303c9ceae"
```

**Response:**
```json
{
  "message": "Job cancelled successfully",
  "job_id": "1752d2ec-d038-4d94-96ab-87d303c9ceae"
}
```

---

### Get Supported Formats

```bash
GET /api/v1/upload/formats
```

**Response:**
```json
{
  "formats": [".mp4", ".mov", ".avi", ".mkv"],
  "max_size_gb": 5.0,
  "max_duration_minutes": 30.0
}
```

---

## Complete Usage Example

### 1. Upload Video

```bash
RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/upload" \
  -F "file=@my_video.mp4" \
  -F "target_duration=30")

JOB_ID=$(echo $RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['job_id'])")
echo "Job ID: $JOB_ID"
```

### 2. Poll for Completion

```bash
while true; do
  STATUS=$(curl -s "http://localhost:8000/api/v1/jobs/$JOB_ID/status" | \
           python3 -c "import sys, json; print(json.load(sys.stdin)['status'])")

  echo "Status: $STATUS"

  if [ "$STATUS" = "completed" ]; then
    break
  elif [ "$STATUS" = "failed" ]; then
    echo "Processing failed!"
    exit 1
  fi

  sleep 2
done
```

### 3. Download Result

```bash
curl "http://localhost:8000/api/v1/jobs/$JOB_ID/download" -o highlight.mp4
echo "Highlight saved to highlight.mp4"
```

---

## Architecture

### Technology Stack

- **Framework**: FastAPI 0.104.1
- **Server**: Uvicorn (ASGI)
- **Database**: SQLite (async via aiosqlite)
- **Task Queue**: Background tasks (BackgroundTasks)
- **Storage**: Local filesystem
- **Processing**: Phase 1.5 algorithm (NumPy-based)

### Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI application
│   ├── core/
│   │   ├── config.py        # Settings management
│   ├── models/
│   │   ├── database.py      # SQLAlchemy models
│   │   ├── schemas.py       # Pydantic schemas
│   ├── api/
│   │   ├── upload.py        # Upload endpoints
│   │   ├── jobs.py          # Job management endpoints
│   ├── tasks/
│   │   ├── processor.py     # Video processing task
├── storage/
│   ├── uploads/             # Uploaded videos
│   ├── outputs/             # Generated highlights
├── logs/                    # Application logs
├── requirements.txt         # Dependencies
├── run.sh                   # Start script
└── moments.db               # SQLite database
```

### Data Flow

```
1. Client uploads video → POST /api/v1/upload
2. API saves file to storage/uploads/
3. Job created in database (status: PENDING)
4. Background task starts processing
5. Algorithm runs (scene detection, motion, audio, diversity)
6. Output saved to storage/outputs/
7. Job updated (status: COMPLETED)
8. Client polls GET /api/v1/jobs/{id}/status
9. Client downloads GET /api/v1/jobs/{id}/download
```

---

## Configuration

### Environment Variables

Create `.env` file in backend directory:

```env
# API Settings
DEBUG=True
SECRET_KEY=your-secret-key-here

# Database
DATABASE_URL=sqlite+aiosqlite:///./moments.db

# Storage
MAX_UPLOAD_SIZE=5368709120  # 5GB
UPLOAD_DIR=storage/uploads
OUTPUT_DIR=storage/outputs

# Processing
DEFAULT_TARGET_DURATION=30
MAX_VIDEO_DURATION=1800  # 30 minutes
```

### Modifying Settings

Edit `app/core/config.py`:

```python
class Settings(BaseSettings):
    PROJECT_NAME: str = "Moments API"
    VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Add your custom settings here
```

---

## Performance

### Test Results

| Video Type | Input | Output | Processing Time | Speed |
|------------|-------|--------|-----------------|-------|
| Sports (120s) | 16.6MB | 5.2MB | 12.4s | 9.7x real-time |
| Party (90s) | 32.2MB | 18MB | 11.4s | 7.9x real-time |
| Nature (100s) | 9.1MB | 2.7MB | 6.9s | 14.5x real-time |

**Average:** 10-15x real-time processing

### Optimization Tips

1. **Concurrent Processing**: Process multiple videos in parallel
2. **Hardware**: Use GPU for faster motion analysis (future)
3. **Caching**: Cache scene detection results
4. **CDN**: Use CDN for video delivery (production)

---

## Error Handling

### Common Errors

**400 Bad Request**
```json
{
  "error": "Invalid file format",
  "detail": "Allowed formats: .mp4, .mov, .avi, .mkv"
}
```

**404 Not Found**
```json
{
  "error": "Job not found",
  "detail": "Job ID does not exist"
}
```

**500 Internal Server Error**
```json
{
  "error": "Processing failed",
  "detail": "Error message details"
}
```

### Debugging

View logs in real-time:
```bash
tail -f /tmp/api.log
```

Enable debug logging:
```python
# app/core/config.py
DEBUG = True
```

---

## Deployment

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run server
./run.sh
```

### Production (Railway/Render)

1. **Prepare Procfile**:
```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

2. **Environment Variables**:
```
DEBUG=False
SECRET_KEY=<generate-secure-key>
DATABASE_URL=<production-db-url>
```

3. **Deploy**:
```bash
git push railway main
# or
render deploy
```

### Docker (Optional)

```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## Testing

### Manual Testing

```bash
# Health check
curl http://localhost:8000/health

# Upload test video
curl -X POST http://localhost:8000/api/v1/upload \
  -F "file=@../test_party_celebration.mp4" \
  -F "target_duration=30"
```

### Automated Testing (Future)

```bash
pytest tests/
```

---

## Cloud Storage Integration (Future)

### AWS S3 / Cloudflare R2

```python
# app/core/config.py
S3_BUCKET = "moments-videos"
S3_REGION = "us-east-1"
S3_ACCESS_KEY = "your-key"
S3_SECRET_KEY = "your-secret"
```

Upload to S3:
```python
import boto3

s3 = boto3.client('s3')
s3.upload_file(local_path, bucket, key)
```

---

## Next Steps

### Phase 3: iOS App Integration

1. **iOS Swift Client**
   - Video upload with progress
   - Status polling
   - Download & save to Photos

2. **Push Notifications**
   - APNs integration
   - Job completion alerts

3. **User Authentication**
   - JWT tokens
   - User accounts
   - Usage tracking

4. **Monetization**
   - Subscription management (StoreKit)
   - Usage limits (free: 3/month)
   - Pro features

---

## Support

### Documentation
- API Docs: http://localhost:8000/docs
- Project: `/Users/rohanbhandari/Desktop/Professional_Projects/ML_PROJECTS_AI/moments_app`

### Issues
Report bugs or request features via GitHub issues

---

## Changelog

### v1.0.0 (2025-10-03)
- ✅ Initial release
- ✅ Video upload endpoint
- ✅ Job status tracking
- ✅ Background processing
- ✅ Phase 1.5 algorithm integration
- ✅ NumPy serialization fix
- ✅ File download endpoint
- ✅ Comprehensive documentation

---

**Built with ❤️ using FastAPI and Python**
