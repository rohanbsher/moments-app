# Moments - Quick Start Guide

**Get up and running in 5 minutes!**

---

## 🚀 Start the API Server

```bash
cd /Users/rohanbhandari/Desktop/Professional_Projects/ML_PROJECTS_AI/moments_app/backend
./run.sh
```

Server starts at: **http://localhost:8000**

---

## ✅ Test the API

### 1. Health Check

```bash
curl http://localhost:8000/health
```

**Expected Response:**
```json
{"status": "healthy", "version": "1.0.0", "service": "Moments API"}
```

### 2. Upload a Video

```bash
cd /Users/rohanbhandari/Desktop/Professional_Projects/ML_PROJECTS_AI/moments_app

curl -X POST "http://localhost:8000/api/v1/upload" \
  -F "file=@test_sports_action.mp4" \
  -F "target_duration=30" \
  -F "quality=high"
```

**Expected Response:**
```json
{
  "job_id": "uuid-here",
  "message": "Video uploaded successfully. Processing started.",
  "estimated_time": 33
}
```

### 3. Check Status

```bash
# Replace with your job_id from step 2
JOB_ID="your-job-id-here"

curl "http://localhost:8000/api/v1/jobs/$JOB_ID/status"
```

**Expected Response:**
```json
{
  "job_id": "uuid",
  "status": "completed",
  "progress": 100,
  "result_url": "/api/v1/jobs/uuid/download"
}
```

### 4. Download Result

```bash
curl "http://localhost:8000/api/v1/jobs/$JOB_ID/download" -o highlight.mp4
```

---

## 📚 View API Documentation

Open in browser:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🎬 Complete Example Script

```bash
#!/bin/bash

# 1. Upload video
echo "Uploading video..."
RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/upload" \
  -F "file=@test_sports_action.mp4" \
  -F "target_duration=30")

JOB_ID=$(echo $RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['job_id'])")
echo "Job ID: $JOB_ID"

# 2. Poll for completion
echo "Waiting for processing..."
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

# 3. Download result
echo "Downloading highlight..."
curl -s "http://localhost:8000/api/v1/jobs/$JOB_ID/download" -o "highlight_$JOB_ID.mp4"
echo "Highlight saved to highlight_$JOB_ID.mp4"

# 4. Verify
ffprobe "highlight_$JOB_ID.mp4" 2>&1 | grep Duration
```

Save as `test_api.sh` and run:
```bash
chmod +x test_api.sh
./test_api.sh
```

---

## 📁 Project Files

**Documentation:**
- `PROJECT_STATUS.md` - Current progress
- `PHASE1_5_COMPLETE.md` - Audio analysis details
- `PHASE2_COMPLETE.md` - API backend details
- `IOS_APP_ROADMAP.md` - iOS implementation plan
- `backend/README.md` - Complete API documentation

**Code:**
- `core/` - Phase 1.5 algorithm
- `backend/` - Phase 2 REST API
- `tests/` - Test videos and scripts

---

## 🐛 Troubleshooting

**"Connection refused"**
→ Server not running. Run `./run.sh`

**"Module not found"**
→ Install dependencies: `pip install -r backend/requirements.txt`

**"Import error"**
→ Set PYTHONPATH: `export PYTHONPATH="${PYTHONPATH}:$(pwd)"`

**"Processing failed"**
→ Check logs: `tail -f /tmp/api.log`

---

## 📞 Help

**API Docs:** http://localhost:8000/docs

**Status:** All systems operational ✅

**Next Steps:** See `IOS_APP_ROADMAP.md` for iOS app development

---

**You're all set! 🎉**
