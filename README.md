# Moments - AI-Powered Video Highlights

Transform long videos into shareable highlights in seconds using AI-powered scene detection, motion analysis, and audio analysis.

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)](https://fastapi.tiangolo.com/)
[![iOS](https://img.shields.io/badge/iOS-17.0+-black.svg)](https://developer.apple.com/ios/)

---

## 🎯 Overview

Moments is a video highlighting application consisting of:
- **Backend API** (FastAPI/Python) - AI-powered video processing
- **iOS App** (SwiftUI/Swift) - Native mobile experience (coming soon)

**Processing Speed:** 10-15x real-time
**Algorithm:** Scene detection + Motion analysis + Audio analysis + Diversity scoring

---

## 🚀 Quick Start

### Backend API

```bash
cd backend
pip install -r requirements.txt
./run.sh
```

Server starts at `http://localhost:8000`

**API Documentation:** http://localhost:8000/docs

---

## 📱 Features

- **Intelligent Scene Detection**: Automatically identifies distinct scenes and segments
- **Motion Analysis**: Detects action moments and camera movements using optical flow
- **Audio Intelligence**: Speech detection, music recognition, excitement level analysis
- **Smart Ranking**: ML-based ranking system to identify the most important moments
- **Automatic Composition**: Creates smooth, watchable highlight reels
- **Background Processing**: Async job queue for handling large videos
- **RESTful API**: Clean API for integration with mobile apps

---

## 🏗️ Architecture

### Backend (FastAPI)

```
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── endpoints/
│   │           └── jobs.py          # Upload, status, download endpoints
│   ├── models/
│   │   └── job.py                   # Job model (SQLAlchemy)
│   ├── services/
│   │   └── video_processor.py      # Core AI processing logic
│   └── main.py                      # FastAPI application
├── storage/
│   ├── uploads/                     # Uploaded videos
│   └── outputs/                     # Processed highlights
└── requirements.txt
```

### iOS App (SwiftUI) - Coming Soon

```
MomentsApp/
├── Core/
│   ├── Models/                      # Job, VideoConfig
│   ├── Services/                    # APIClient, SubscriptionManager
│   └── Utilities/
├── Features/
│   ├── Home/
│   ├── Upload/                      # Video picker, upload flow
│   ├── Result/                      # Playback, share
│   └── Subscription/                # Paywall, StoreKit 2
└── Resources/
```

**Architecture Pattern:** MVVM with @Observable (iOS 17+)

---

## 🎬 API Endpoints

### Upload Video
```http
POST /api/v1/jobs/upload
Content-Type: multipart/form-data

Parameters:
- file: Video file (mp4, mov, avi)
- duration: Target duration in seconds (default: 180)
- min_segment: Minimum segment length (default: 3)
- max_segment: Maximum segment length (default: 10)

Response:
{
  "job_id": "uuid",
  "status": "queued"
}
```

### Check Status
```http
GET /api/v1/jobs/{job_id}/status

Response:
{
  "job_id": "uuid",
  "status": "processing",
  "progress": 45,
  "message": "Analyzing scene 23 of 50"
}
```

### Download Highlight
```http
GET /api/v1/jobs/{job_id}/download

Response: Video file (mp4)
```

---

## 🚀 Deployment

### Production (Railway)

1. **Push to GitHub:**
```bash
git add .
git commit -m "Deploy to production"
git push origin main
```

2. **Connect Railway:**
   - Connect GitHub repository
   - Select `backend` directory
   - Railway auto-detects FastAPI

3. **Environment Variables:**
```bash
DATABASE_URL=postgresql://...
STORAGE_TYPE=r2
R2_BUCKET=moments-videos
R2_ACCESS_KEY=...
R2_SECRET_KEY=...
```

**Production URL:** `https://moments-api.up.railway.app`

---

## 🔧 Development

### Local Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
./run.sh
```

### Run Tests

```bash
pytest tests/
```

### API Documentation

Interactive docs: http://localhost:8000/docs

---

## 💡 How It Works

1. **Scene Detection**: Analyzes video to find natural scene boundaries using PySceneDetect
2. **Multi-Modal Analysis**:
   - Motion intensity (OpenCV optical flow)
   - Audio characteristics (Whisper speech detection, librosa music analysis)
   - Quality metrics (brightness, contrast, sharpness)
3. **Intelligent Ranking**: ML-based scoring combining motion, audio, and diversity
4. **Smart Selection**: Top-ranked segments selected to fit target duration
5. **Professional Composition**: Segments combined with smooth transitions via FFmpeg

**Processing Speed:** 10-15x real-time (60-minute video → 4-6 minutes processing)

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit pull requests.

## Acknowledgments

- OpenAI Whisper for speech recognition
- PySceneDetect for scene detection
- MoviePy for video processing
- OpenCV for computer vision