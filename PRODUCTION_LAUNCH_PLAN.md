# Moments - Production Launch Plan

**Target Launch Date:** 3 weeks from now
**Status:** In Progress
**Last Updated:** October 22, 2025

---

## 🎯 Launch Timeline

### Week 1: Backend Production Ready (Days 1-7)
**Goal:** Fully deployed, secure, monitored backend

- **Day 1-2:** Backend Infrastructure
  - [x] Deploy to Railway
  - [x] Configure PostgreSQL database
  - [x] Set up environment variables
  - [x] Configure file storage/volumes
  - [x] Add authentication system

- **Day 3-4:** Security & Performance
  - [ ] Configure CORS for production
  - [ ] Add rate limiting
  - [ ] Set up Sentry error tracking
  - [ ] Add request logging
  - [ ] Implement storage cleanup

- **Day 5-7:** Testing & Optimization
  - [ ] End-to-end API testing
  - [ ] Load testing (100 concurrent users)
  - [ ] Performance optimization
  - [ ] Documentation updates

### Week 2: iOS App Store Ready (Days 8-14)
**Goal:** App Store submission ready

- **Day 8-9:** iOS Configuration
  - [ ] Environment-based API URLs
  - [ ] Production build configuration
  - [ ] App icon (all sizes)
  - [ ] Launch screen

- **Day 10-11:** App Store Assets
  - [ ] Screenshots (all required sizes)
  - [ ] App preview video (30 seconds)
  - [ ] Privacy policy
  - [ ] Terms of service
  - [ ] App Store description

- **Day 12-13:** TestFlight Beta
  - [ ] Archive and upload to TestFlight
  - [ ] Invite 10-20 beta testers
  - [ ] Create testing instructions
  - [ ] Gather initial feedback

- **Day 14:** Beta Bug Fixes
  - [ ] Fix critical bugs from beta
  - [ ] Performance improvements
  - [ ] Upload updated build

### Week 3: Launch (Days 15-21)
**Goal:** Live on App Store

- **Day 15-16:** Final Preparation
  - [ ] App Store Connect listing complete
  - [ ] Final build uploaded
  - [ ] Submit for App Review
  - [ ] Marketing materials ready

- **Day 17-21:** App Review & Launch
  - [ ] Respond to App Review questions
  - [ ] Monitor review status
  - [ ] Release when approved
  - [ ] Monitor for crashes/issues
  - [ ] Respond to user reviews

---

## 📋 Detailed Implementation Checklist

## 1. Backend Production Deployment

### 1.1 Railway Setup
```bash
# Install Railway CLI
brew install railway

# Login
railway login

# Initialize project
cd backend
railway init

# Link to project
railway link
```

### 1.2 Environment Variables
```bash
# Set on Railway dashboard or CLI
railway variables set DATABASE_URL="postgresql://..."
railway variables set SECRET_KEY="your-secret-key-here"
railway variables set ENVIRONMENT="production"
railway variables set DEBUG="false"
railway variables set ALLOWED_ORIGINS="https://moments-app.com"
railway variables set SENTRY_DSN="your-sentry-dsn"
railway variables set MAX_UPLOAD_SIZE="524288000"  # 500MB
railway variables set STORAGE_PATH="/app/storage"
```

### 1.3 Database Migration
```bash
# Create PostgreSQL database on Railway
railway add

# Run migrations
railway run alembic upgrade head
```

### 1.4 Deploy
```bash
# Deploy
railway up

# Check status
railway status

# View logs
railway logs
```

---

## 2. Authentication System

### 2.1 API Key Authentication
- Simple API key in headers
- Generate unique keys per user/device
- Store hashed in database
- Rate limit per key

### 2.2 Implementation
Files to modify:
- `backend/app/core/config.py` - Add SECRET_KEY
- `backend/app/core/auth.py` - NEW: Auth middleware
- `backend/app/models/database.py` - Add APIKey model
- `backend/app/api/upload.py` - Add auth dependency
- `backend/app/api/jobs.py` - Add auth dependency

---

## 3. iOS Configuration

### 3.1 Environment-Based URLs
Files to modify:
- `ios/MomentsApp/Core/Config/Environment.swift` - NEW
- `ios/MomentsApp/Core/Services/APIClient.swift` - Use Environment
- `ios/MomentsApp.xcodeproj` - Add build schemes

### 3.2 Build Configurations
- Debug: Local development (http://192.168.0.5:8000)
- Staging: Railway staging (https://moments-staging.up.railway.app)
- Release: Railway production (https://moments-api.up.railway.app)

---

## 4. Security Improvements

### 4.1 CORS Configuration
```python
# Production CORS
allow_origins=[
    "https://moments-app.com",
    "https://www.moments-app.com",
    "capacitor://localhost",  # If using Capacitor
    "ionic://localhost",
]
```

### 4.2 Rate Limiting
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

# Apply to endpoints
@limiter.limit("5/minute")
async def upload_video():
    ...
```

### 4.3 Input Validation
- File type validation (ffprobe)
- File size limits
- Duration limits
- Sanitize filenames

---

## 5. Monitoring & Logging

### 5.1 Sentry Setup
```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    integrations=[FastApiIntegration()],
    traces_sample_rate=1.0,
    environment=settings.ENVIRONMENT,
)
```

### 5.2 Structured Logging
```python
import structlog

logger = structlog.get_logger()
logger.info("video_uploaded", job_id=job_id, file_size=file_size)
```

### 5.3 Health Checks
```python
@app.get("/health")
async def health_check():
    # Check database connection
    # Check disk space
    # Check processing queue
    return {
        "status": "healthy",
        "database": "connected",
        "disk_space": "ok",
        "queue_size": 0
    }
```

---

## 6. App Store Submission

### 6.1 App Store Connect Setup
1. Create Apple Developer account ($99/year)
2. Create App ID: `com.yourdomain.moments`
3. Create App Store Connect app
4. Fill in metadata:
   - Name: "Moments - AI Video Highlights"
   - Subtitle: "Transform videos into highlights"
   - Category: Photo & Video
   - Age Rating: 4+

### 6.2 Required Assets

**App Icon (all sizes):**
- 1024x1024 (App Store)
- 180x180 (iPhone)
- 167x167 (iPad Pro)
- 152x152 (iPad)
- 120x120 (iPhone)
- 87x87 (iPhone)
- 80x80 (iPad)
- 76x76 (iPad)
- 60x60 (iPhone)
- 58x58 (iPhone)
- 40x40 (iPhone/iPad)
- 29x29 (iPhone/iPad)
- 20x20 (iPhone/iPad)

**Screenshots (required):**
- 6.7" Display (iPhone 16 Pro Max): 1320x2868px (2-10 images)
- 6.5" Display (iPhone 14 Pro Max): 1284x2778px
- 5.5" Display (iPhone 8 Plus): 1242x2208px

**App Preview Video (optional but recommended):**
- Up to 30 seconds
- Show key features: select video → processing → result
- Portrait orientation
- Same sizes as screenshots

### 6.3 Privacy Policy
Required sections:
- Data collected: Videos (processed and deleted)
- Photo library access: Why we need it
- Network usage: Where videos are sent
- Data retention: How long we keep videos
- Data sharing: We don't share/sell data
- Contact: support email

### 6.4 App Description
```
Transform long videos into shareable highlights in seconds using AI.

Moments uses advanced computer vision and audio analysis to automatically find the most interesting parts of your videos. Perfect for:

• Sports events - Capture the winning goal
• Parties & celebrations - Relive the best moments
• Conferences & presentations - Get the key takeaways
• Family gatherings - Remember the laughter

HOW IT WORKS
1. Select any video from your library
2. Our AI analyzes motion, audio, and scene changes
3. Get a perfect highlight reel in seconds

FEATURES
• AI-powered scene detection
• Motion and audio analysis
• Fast processing (10-15x real-time)
• Beautiful, modern interface
• Share directly to social media
• Save to your photo library

No subscriptions. No ads. Just great highlights.
```

### 6.5 Keywords (100 characters max)
```
video,highlights,clips,editing,AI,moments,sports,party,events,short
```

---

## 7. Testing Plan

### 7.1 Backend Testing
```bash
# API endpoint tests
curl https://moments-api.up.railway.app/health
curl -X POST https://moments-api.up.railway.app/api/v1/upload \
  -F "file=@test.mp4" \
  -H "Authorization: Bearer YOUR_API_KEY"

# Load testing with Apache Bench
ab -n 100 -c 10 https://moments-api.up.railway.app/health
```

### 7.2 iOS Testing
- [ ] Test on iPhone 16 Pro Max (latest)
- [ ] Test on iPhone SE (oldest supported)
- [ ] Test on iPad
- [ ] Test with iOS 17.0 (minimum)
- [ ] Test with iOS 18 (latest)
- [ ] Test in Airplane mode (error handling)
- [ ] Test with large videos (500MB+)
- [ ] Test with corrupted videos (error handling)

### 7.3 End-to-End Scenarios
1. **Happy Path**
   - Select video → Upload → Process → Download → Play → Share

2. **Error Scenarios**
   - Network disconnects during upload
   - Processing fails
   - Server error
   - Invalid video format
   - File too large

3. **Edge Cases**
   - Very short video (< 5 seconds)
   - Very long video (> 30 minutes)
   - Video with no audio
   - Video with no motion
   - Black screen video

---

## 8. Post-Launch Monitoring

### 8.1 Key Metrics to Track
- **Performance:**
  - API response times
  - Processing times
  - Success rate

- **Usage:**
  - Videos uploaded per day
  - Active users
  - Retention rate

- **Errors:**
  - Upload failures
  - Processing failures
  - App crashes

- **Infrastructure:**
  - CPU usage
  - Memory usage
  - Disk space
  - Database connections

### 8.2 Alerts to Set Up
- Processing failure rate > 5%
- API error rate > 1%
- Disk space < 10GB
- Average processing time > 2 minutes
- Database connection errors

### 8.3 Success Criteria (Week 1)
- [ ] 100 downloads
- [ ] 50 videos processed
- [ ] < 1% crash rate
- [ ] < 5% error rate
- [ ] Average processing time < 60s
- [ ] 4+ star rating

---

## 9. Rollback Plan

If critical issues arise:

### 9.1 Backend Rollback
```bash
# Revert to previous deployment
railway rollback

# Or specific version
railway rollback --version v1.0.0
```

### 9.2 iOS Rollback
- Cannot rollback App Store version
- But can:
  - Submit hotfix update (expedited review)
  - Remove from sale temporarily
  - Add warning in description

### 9.3 Communication Plan
- Email to beta testers
- App Store update notes
- Social media announcement
- Support page update

---

## 10. Cost Estimates

### Month 1 (1,000 users, ~500 videos)
- Railway Starter: $5/month (backend)
- PostgreSQL: $5/month
- Storage (20GB): $2/month
- Sentry: $0 (free tier)
- **Total: $12/month**

### Month 3 (10,000 users, ~5,000 videos)
- Railway Pro: $20/month
- PostgreSQL: $10/month
- Storage (100GB): $10/month
- Sentry: $26/month (Team plan)
- **Total: $66/month**

### Month 6 (50,000 users, ~25,000 videos)
- Railway Scale: $100/month
- PostgreSQL: $25/month
- Storage (500GB): $50/month
- Sentry: $26/month
- **Total: $201/month**

### Revenue Projections (assuming 3% conversion to $4.99/month)
- Month 1: $150 (50 subs × $4.99) - Cost: $12 = **$138 profit**
- Month 3: $1,500 (300 subs × $4.99) - Cost: $66 = **$1,434 profit**
- Month 6: $7,500 (1,500 subs × $4.99) - Cost: $201 = **$7,299 profit**

---

## 11. Marketing & Launch Strategy

### Pre-Launch (Week before)
- [ ] Create Product Hunt listing (draft)
- [ ] Create Twitter/X account
- [ ] Create landing page
- [ ] Prepare launch announcement
- [ ] Email beta testers

### Launch Day
- [ ] Submit to Product Hunt
- [ ] Post on Twitter/X, LinkedIn
- [ ] Post in relevant Reddit communities
- [ ] Share in iOS dev communities
- [ ] Email friends and family

### Post-Launch (First week)
- [ ] Respond to all reviews
- [ ] Monitor analytics
- [ ] Fix critical bugs
- [ ] Gather user feedback
- [ ] Plan next features

---

## 12. Next Steps (Immediate Actions)

### Today (Day 1)
1. [x] Create this launch plan
2. [ ] Set up Railway account
3. [ ] Deploy backend to Railway
4. [ ] Add authentication system
5. [ ] Fix iOS hardcoded URLs

### Tomorrow (Day 2)
1. [ ] Set up PostgreSQL
2. [ ] Configure environment variables
3. [ ] Test end-to-end with production backend
4. [ ] Set up Sentry
5. [ ] Add rate limiting

### This Week (Days 3-7)
1. [ ] Storage cleanup implementation
2. [ ] Complete security hardening
3. [ ] Load testing
4. [ ] Create app icon
5. [ ] Start privacy policy

---

## 13. Success Metrics

### Technical Metrics
- [x] Backend deploys successfully
- [ ] 99.9% uptime
- [ ] API response time < 100ms
- [ ] Processing time < 2 minutes for 5-minute video
- [ ] Error rate < 1%

### Business Metrics
- [ ] 1,000 downloads in first month
- [ ] 100 active users (process ≥1 video)
- [ ] 3% free-to-paid conversion
- [ ] 4.5+ App Store rating
- [ ] < 5% churn rate

---

## 14. Risk Assessment

### High Risk
- **App rejection:** Mitigate with thorough review guidelines check
- **Server overload:** Mitigate with rate limiting and auto-scaling
- **Processing failures:** Mitigate with robust error handling and monitoring

### Medium Risk
- **High costs:** Mitigate with usage limits and pricing tiers
- **Poor reviews:** Mitigate with beta testing and quick bug fixes
- **Competition:** Mitigate with unique AI features and polish

### Low Risk
- **Legal issues:** Privacy policy and terms cover us
- **Data loss:** Backups and short retention period
- **Security breach:** Authentication and rate limiting in place

---

## 15. Contact & Support

### Support Channels
- Email: support@moments-app.com
- Twitter: @MomentsApp
- Website: https://moments-app.com

### On-Call Rotation
Week 1-2: Daily monitoring (you)
Week 3+: Monitor 2x per day

---

**Status:** Ready to execute
**Confidence:** High - All technical pieces are in place
**Timeline:** 3 weeks to App Store launch

Let's ship this! 🚀
