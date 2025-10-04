# Railway Deployment Guide

## Prerequisites

✅ GitHub repository created: https://github.com/rohanbsher/moments-app
✅ Code pushed to main branch
✅ Railway CLI installed

## Step 1: Login to Railway

```bash
railway login
```

This will open your browser. Login with GitHub and authorize Railway.

## Step 2: Create New Project

```bash
cd /Users/rohanbhandari/Desktop/Professional_Projects/ML_PROJECTS_AI/moments_app
railway init
```

- Choose: "Create a new project"
- Project name: `moments-app`

## Step 3: Link GitHub Repository

```bash
railway link
```

Or do it via Railway Dashboard:
1. Go to https://railway.app/dashboard
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose `rohanbsher/moments-app`
5. Select `backend` as the root directory

## Step 4: Configure Environment Variables

### Option A: Via CLI

```bash
railway variables set DATABASE_URL="sqlite+aiosqlite:///./moments.db"
```

### Option B: Via Dashboard (Recommended)

1. Go to your project in Railway dashboard
2. Click on "Variables" tab
3. Add these variables:

```bash
# Database (for now, SQLite - will migrate to PostgreSQL later)
DATABASE_URL=sqlite+aiosqlite:///./moments.db

# Storage (local for now - will migrate to R2 later)
STORAGE_TYPE=local
```

## Step 5: Configure Build Settings

Railway should auto-detect Python and use these settings:

**Build Command:**
```bash
pip install -r backend/requirements.txt
```

**Start Command:**
```bash
cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

**Root Directory:** `backend`

## Step 6: Deploy

```bash
railway up
```

Or trigger deployment via git push:
```bash
git push origin main
```

Railway will automatically deploy on every push to main.

## Step 7: Get Your Production URL

```bash
railway domain
```

This will generate a domain like: `https://moments-app-production.up.railway.app`

## Step 8: Test API

```bash
curl https://your-railway-url.up.railway.app/
```

Should return:
```json
{
  "message": "Moments API - Video Highlights Service",
  "version": "2.0.0",
  "status": "running"
}
```

## Step 9: Test API Documentation

Visit: `https://your-railway-url.up.railway.app/docs`

You should see the FastAPI Swagger documentation.

## Next Steps (After Basic Deployment Works)

### 1. Add PostgreSQL Database

```bash
railway add
```

Select PostgreSQL. Railway will automatically set `DATABASE_URL` environment variable.

Update your code to use PostgreSQL:
```python
# app/core/config.py
DATABASE_URL = os.getenv("DATABASE_URL").replace("postgres://", "postgresql+asyncpg://")
```

### 2. Setup Cloudflare R2 for Video Storage

1. Create Cloudflare account
2. Create R2 bucket: `moments-videos`
3. Generate API keys
4. Add to Railway variables:

```bash
STORAGE_TYPE=r2
R2_BUCKET=moments-videos
R2_ACCOUNT_ID=your-account-id
R2_ACCESS_KEY=your-access-key
R2_SECRET_KEY=your-secret-key
S3_ENDPOINT=https://your-account-id.r2.cloudflarestorage.com
```

## Troubleshooting

### Build fails

Check Railway logs:
```bash
railway logs
```

### Application crashes

Check runtime logs:
```bash
railway logs --follow
```

### Port binding error

Ensure your app uses `$PORT` environment variable:
```python
port = int(os.getenv("PORT", 8000))
uvicorn.run(app, host="0.0.0.0", port=port)
```

## Cost Estimate

- **Hobby Plan:** $5/month (512MB RAM, shared CPU)
- **Developer Plan:** $20/month (8GB RAM, shared CPU)

Start with Hobby plan. Upgrade when you exceed resource limits.

## Monitoring

View metrics in Railway dashboard:
- CPU usage
- Memory usage
- Request counts
- Response times

---

**Current Status:** Ready to deploy
**GitHub Repo:** https://github.com/rohanbsher/moments-app
**Next Action:** Run `railway login` and `railway init`
