# Moments - Deployment Guide

Complete step-by-step guide to deploy Moments to production.

---

## Prerequisites

Before you begin, make sure you have:

- [x] GitHub account
- [x] Railway account (https://railway.app)
- [x] Apple Developer account ($99/year) - for App Store
- [x] Sentry account (https://sentry.io) - for error tracking (free tier)
- [x] Code pushed to GitHub repository

---

## Part 1: Backend Deployment to Railway

### Step 1: Create Railway Account

1. Go to https://railway.app
2. Sign up with GitHub
3. Connect your GitHub account

### Step 2: Create New Project

```bash
# Option A: Using Railway CLI (recommended)
brew install railway  # Install Railway CLI
railway login         # Login to Railway
cd backend/
railway init          # Create new project
railway link          # Link to project

# Option B: Using Railway Dashboard
# 1. Click "New Project" in Railway dashboard
# 2. Select "Deploy from GitHub repo"
# 3. Choose your repository
# 4. Select "backend" directory as root
```

### Step 3: Add PostgreSQL Database

```bash
# Using CLI
railway add --database postgresql

# Or in Dashboard:
# 1. Click "New Service"
# 2. Select "Database"
# 3. Choose "PostgreSQL"
```

Railway will automatically set the `DATABASE_URL` environment variable.

### Step 4: Configure Environment Variables

```bash
# Using CLI
railway variables set ENVIRONMENT=production
railway variables set DEBUG=false
railway variables set SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
railway variables set ALLOWED_ORIGINS="*"  # Or your specific domain
railway variables set SENTRY_DSN="your-sentry-dsn-here"
railway variables set RATE_LIMIT_ENABLED=true

# Or in Dashboard:
# 1. Go to your service
# 2. Click "Variables"
# 3. Add each variable manually
```

**Required Variables:**
```
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=<generate-random-string>
DATABASE_URL=<auto-set-by-railway>
ALLOWED_ORIGINS=*
SENTRY_DSN=<your-sentry-dsn>
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=10
RATE_LIMIT_PER_HOUR=100
```

### Step 5: Add Storage Volume (for videos)

```bash
# Using CLI
railway volume create storage /app/storage

# Or in Dashboard:
# 1. Go to service settings
# 2. Click "Volumes"
# 3. Add new volume
#    - Name: storage
#    - Mount path: /app/storage
```

### Step 6: Deploy

```bash
# Using CLI
railway up

# Or push to GitHub (auto-deploys)
git add .
git commit -m "Deploy to production"
git push origin main
```

### Step 7: Verify Deployment

```bash
# Check deployment status
railway status

# View logs
railway logs

# Get deployment URL
railway domain

# Test health endpoint
curl https://your-app.up.railway.app/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "service": "Moments API"
}
```

### Step 8: Set Custom Domain (Optional)

```bash
# Add custom domain
railway domain add moments-api.yourdomain.com

# Or in Dashboard:
# 1. Go to service settings
# 2. Click "Domains"
# 3. Add custom domain
# 4. Update DNS: CNAME moments-api.yourdomain.com -> your-app.up.railway.app
```

---

## Part 2: Sentry Setup (Error Tracking)

### Step 1: Create Sentry Project

1. Go to https://sentry.io
2. Sign up / Log in
3. Create new project
   - Platform: Python
   - Project name: moments-api
4. Copy the DSN (looks like: `https://xxx@o123.ingest.sentry.io/456`)

### Step 2: Add to Railway

```bash
railway variables set SENTRY_DSN="https://xxx@o123.ingest.sentry.io/456"
```

### Step 3: Verify

1. Go to Sentry dashboard
2. Navigate to Issues
3. Should see events appear when backend starts
4. Test by triggering an error: `curl https://your-app.up.railway.app/api/v1/nonexistent`

---

## Part 3: iOS App Configuration

### Step 1: Update Production URL

The app is now configured to automatically use the production URL when built in Release mode.

No code changes needed! The `Environment.swift` file handles this:
- DEBUG builds: Use local IP (development)
- RELEASE builds: Use Railway URL (production)

### Step 2: Configure Xcode Build Settings

1. Open `MomentsApp.xcodeproj` in Xcode
2. Select the project (top of file navigator)
3. Select "MomentsApp" target
4. Go to "Build Settings"
5. Search for "Swift Compiler - Custom Flags"
6. Expand "Other Swift Flags"
7. For **Release** configuration:
   - Leave as is (no custom flags)
8. For **Debug** configuration:
   - Should have `-D DEBUG`

### Step 3: Update Production API URL

Edit `ios/MomentsApp/Core/Config/Environment.swift`:

```swift
case .production:
    // Update this to your Railway URL
    return "https://your-app.up.railway.app"
```

Or set via environment variable:
```bash
# In Xcode scheme settings
API_BASE_URL=https://your-app.up.railway.app
```

---

## Part 4: App Store Submission

### Step 1: Create App Store Connect Listing

1. Go to https://appstoreconnect.apple.com
2. Click "My Apps"
3. Click "+" to create new app
4. Fill in:
   - Platform: iOS
   - Name: Moments - AI Video Highlights
   - Primary Language: English
   - Bundle ID: com.yourdomain.moments (create in Developer Portal first)
   - SKU: moments-001
   - User Access: Full Access

### Step 2: Prepare App Metadata

**Required Information:**

- **App Name:** Moments - AI Video Highlights
- **Subtitle:** Transform videos into highlights
- **Privacy Policy URL:** https://yourdomain.com/privacy
- **Category:** Photo & Video
- **Age Rating:** 4+ (no objectionable content)

**App Description:**
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

**Keywords (100 characters max):**
```
video,highlights,clips,editing,AI,moments,sports,party,events,short
```

**Promotional Text (170 characters max):**
```
Create amazing video highlights in seconds with AI. Perfect for sports, parties, and events. Fast, easy, and free!
```

### Step 3: Create App Icon

You need app icons in all required sizes. Use a tool like https://appicon.co

Required sizes:
- 1024x1024 (App Store)
- 180x180, 120x120, 87x87, 80x80, 76x76, 60x60, 58x58, 40x40, 29x29, 20x20

Place in: `ios/MomentsApp/Assets.xcassets/AppIcon.appiconset/`

### Step 4: Take Screenshots

Required for all device sizes:

**6.7" Display (iPhone 16 Pro Max) - 1320x2868px:**
- Upload screen
- Processing screen
- Success screen
- Result playback

**6.5" Display (iPhone 14 Pro Max) - 1284x2778px:**
- Same 4 screenshots

**5.5" Display (iPhone 8 Plus) - 1242x2208px:**
- Same 4 screenshots

**How to take screenshots:**
1. Run app in simulator
2. Navigate to each screen
3. Cmd+S to save screenshot
4. Scale to required dimensions

### Step 5: Create Privacy Policy

Create a simple privacy policy at `https://yourdomain.com/privacy`

**Required sections:**
```markdown
# Privacy Policy for Moments

Last updated: [Date]

## Data Collection
- We collect videos you choose to upload
- Videos are processed on our servers
- Videos are automatically deleted after 7 days
- We do NOT sell or share your data

## Photo Library Access
We request photo library access to allow you to select videos for processing.

## Data Processing
Videos are sent to our servers for AI processing. Processing typically takes 30-120 seconds. Videos are stored temporarily and deleted within 7 days.

## Contact
For privacy questions: support@yourdomain.com
```

### Step 6: Archive and Upload to App Store

**In Xcode:**

1. Select "Any iOS Device" as destination
2. Product → Archive (⌘+B first to ensure it builds)
3. Wait for archive to complete
4. Window → Organizer → Archives
5. Select your archive
6. Click "Distribute App"
7. Choose "App Store Connect"
8. Select "Upload"
9. Choose automatic signing
10. Click "Upload"

**Wait for Processing:**
- Apple will process your build (10-30 minutes)
- You'll receive an email when ready
- Check in App Store Connect → TestFlight

### Step 7: TestFlight Beta Testing

1. Go to App Store Connect
2. Select your app
3. Go to TestFlight tab
4. Select your build
5. Add "What to Test" notes:
   ```
   Thank you for testing Moments!

   Please test:
   - Upload a video from your library
   - Wait for processing to complete
   - Play the result
   - Share or save the highlight

   Known issues:
   - First upload may take longer

   Report bugs to: support@yourdomain.com
   ```
6. Enable testing
7. Add testers (max 10,000):
   - Click "Add Testers"
   - Enter email addresses
   - They'll receive invite email

### Step 8: Submit for App Review

1. Go to App Store Connect
2. Select your app
3. Click "Prepare for Submission"
4. Fill in all required fields:
   - Screenshots (all sizes)
   - Description
   - Keywords
   - Support URL
   - Privacy Policy URL
   - App icon
5. Select build from TestFlight
6. Answer review questions:
   - Does your app use encryption? → No (or Yes if using HTTPS)
   - Does it use location? → No
   - Does it use IDFA? → No
7. Click "Submit for Review"

**Review Timeline:**
- Typically 1-7 days
- You'll get status updates via email
- May receive questions from reviewer

### Step 9: Launch!

Once approved:

1. Set release preference:
   - Manual release (you control when)
   - Automatic release (goes live immediately)
2. Click "Release this Version"
3. Monitor for:
   - Crash reports
   - User reviews
   - Server load

---

## Part 5: Post-Launch Monitoring

### Check Backend Health

```bash
# Health check
curl https://your-app.up.railway.app/health

# Check logs
railway logs

# Monitor metrics in Railway dashboard
# - CPU usage
# - Memory usage
# - Request count
```

### Monitor Sentry

1. Go to Sentry dashboard
2. Check for errors
3. Set up alerts:
   - Error rate > 5%
   - New issue detected
   - Performance degradation

### App Store Connect Analytics

1. Go to App Store Connect
2. Select your app
3. Go to "Analytics"
4. Monitor:
   - Downloads
   - Crashes
   - User retention
   - Ratings & reviews

### Railway Usage

Monitor costs:
```
Free Tier: $5/month credit
Starter: $5/month + usage
```

Check usage in Railway dashboard:
- Compute hours
- Data transfer
- Storage

---

## Part 6: Rollback Plan

### If Backend Has Issues

```bash
# Rollback to previous deployment
railway rollback

# Or specific version
railway deployment list
railway rollback <deployment-id>
```

### If iOS App Has Issues

**Cannot rollback App Store version**, but you can:

1. **Submit Hotfix:**
   - Fix the bug
   - Increment build number
   - Submit for expedited review (mention critical bug)

2. **Temporarily Remove:**
   - App Store Connect → Remove from Sale
   - Fix issues
   - Re-submit

3. **Add Warning:**
   - Update app description
   - Respond to reviews

---

## Part 7: Cost Management

### Estimated Monthly Costs

**Month 1 (1,000 users):**
- Railway: $5-10/month
- PostgreSQL: $5/month
- Storage: $2/month
- Sentry: Free
- **Total: ~$12/month**

**Month 3 (10,000 users):**
- Railway: $20/month
- PostgreSQL: $10/month
- Storage: $10/month
- Sentry: $26/month
- **Total: ~$66/month**

### Auto-Scaling

Railway auto-scales based on:
- CPU usage
- Memory usage
- Request count

Configure limits:
```bash
railway variables set MAX_REPLICAS=3
railway variables set MIN_REPLICAS=1
```

---

## Part 8: Troubleshooting

### Backend Won't Start

**Check logs:**
```bash
railway logs
```

**Common issues:**
- Missing environment variables → Check `railway variables`
- Database connection → Verify DATABASE_URL
- Port binding → Railway auto-sets PORT variable

### iOS Can't Connect

**Check:**
1. Backend is running: `curl https://your-app.up.railway.app/health`
2. CORS is configured: `ALLOWED_ORIGINS=*`
3. Network connectivity
4. API URL is correct in Environment.swift

**Debug:**
- Check Xcode console for APIClient logs
- Verify endpoint URLs
- Test with curl/Postman

### Videos Not Processing

**Check:**
1. Storage volume mounted: `/app/storage`
2. FFmpeg installed: `railway run which ffmpeg`
3. Logs for processing errors: `railway logs | grep ERROR`

---

## Part 9: Next Steps

After successful launch:

### Week 1: Monitor & Fix
- [ ] Monitor crash reports
- [ ] Respond to user reviews
- [ ] Fix critical bugs
- [ ] Watch server metrics

### Week 2: Optimize
- [ ] Improve processing speed
- [ ] Reduce costs
- [ ] Enhance features based on feedback

### Month 2: Grow
- [ ] Marketing push
- [ ] Add requested features
- [ ] Consider monetization

---

## Support

### Documentation
- Backend API: https://your-app.up.railway.app/docs
- Project README: README.md
- Launch Plan: PRODUCTION_LAUNCH_PLAN.md

### Help
- Railway Docs: https://docs.railway.app
- FastAPI Docs: https://fastapi.tiangolo.com
- Sentry Docs: https://docs.sentry.io

### Contact
- Email: support@yourdomain.com
- GitHub Issues: https://github.com/yourusername/moments-app/issues

---

**Ready to deploy! Follow these steps carefully and you'll be live in a few hours.** 🚀

Good luck with your launch!
