# 🚀 STREAMLIT CLOUD DEPLOYMENT GUIDE

## Overview

Streamlit Cloud is **perfect for deploying your dashboard** - it's free, easy, and designed for Streamlit apps!

### Architecture
```
┌─────────────────────────────────────────────────┐
│  Streamlit Cloud                                │
│  • Dashboard UI (FREE)                          │
│  • Hosted at: yourapp.streamlit.app            │
└─────────────────────────────────────────────────┘
                    ↓ API calls
┌─────────────────────────────────────────────────┐
│  Backend (Deploy separately)                    │
│  • FastAPI + ML + Database                      │
│  • Deploy to: Heroku, AWS, or Render           │
└─────────────────────────────────────────────────┘
```

---

## ✅ Files Created

- `dashboard/requirements.txt` - Lightweight dependencies for dashboard
- `dashboard/.streamlit/config.toml` - Streamlit configuration
- `dashboard/.streamlit/secrets.toml` - API URL configuration

---

## Deployment Steps

### Step 1: Push to GitHub

#### A. Create GitHub Repository
1. Go to https://github.com/new
2. Create a new repository: `fake-review-detector`
3. Don't initialize with README (you already have files)

#### B. Push Your Code
```powershell
# In PowerShell (after restarting for Git)
cd d:\fake-review-detector

# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - Fake Review Detection System"

# Add remote
git remote add origin https://github.com/YOUR_USERNAME/fake-review-detector.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### Step 2: Deploy Dashboard to Streamlit Cloud

#### A. Sign Up for Streamlit Cloud
1. Go to https://streamlit.io/cloud
2. Click "Sign up" 
3. Sign in with your GitHub account
4. Authorize Streamlit to access your repositories

#### B. Deploy Your App
1. Click "New app" button
2. Select your repository: `YOUR_USERNAME/fake-review-detector`
3. Set main file path: `dashboard/app.py`
4. Click "Deploy!"

Your dashboard will be live at:
```
https://YOUR_USERNAME-fake-review-detector.streamlit.app
```

### Step 3: Deploy Backend API Separately

**Option 1: Heroku (Easiest)**
```powershell
# See HEROKU_DEPLOYMENT.md
heroku create fake-review-api
heroku addons:create heroku-postgresql:mini
git push heroku main
```

**Option 2: Render (Free Tier)**
1. Go to https://render.com
2. Connect GitHub repo
3. Create "Web Service"
4. Build command: `pip install -r requirements.txt`
5. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

**Option 3: Railway (Simple)**
1. Go to https://railway.app
2. "New Project" → "Deploy from GitHub"
3. Select your repo
4. Auto-deploys!

### Step 4: Connect Dashboard to Backend

#### Update Streamlit Secrets
1. In Streamlit Cloud dashboard, go to your app
2. Click "⋮" menu → "Settings" → "Secrets"
3. Add your API URL:
```toml
API_URL = "https://your-backend-api.herokuapp.com"
```

#### Update Dashboard Code to Use Secrets
The dashboard app will automatically use `st.secrets["API_URL"]`

---

## 🆓 Cost Breakdown

### Streamlit Cloud
- **FREE** for public apps
- Unlimited viewers
- Auto-updates from GitHub
- Custom subdomain

### Backend Options
| Platform | Free Tier | Paid |
|----------|-----------|------|
| **Render** | Free (sleeps after inactivity) | $7/month |
| **Railway** | $5 free credit | $5/month |
| **Heroku** | No free tier | $5-25/month |
| **Fly.io** | Free allowance | $1.94/month+ |

**Recommended**: Render.com (free tier) for backend + Streamlit Cloud (free) = **$0/month**

---

## Quick Deployment Commands

### Complete Setup (After Git/GitHub Setup)
```powershell
# 1. Push to GitHub
git init
git add .
git commit -m "Initial deployment"
git remote add origin https://github.com/YOUR_USERNAME/fake-review-detector.git
git push -u origin main

# 2. Deploy backend to Render
# Visit: https://render.com
# Create Web Service from GitHub repo
# Set start command: uvicorn app.main:app --host 0.0.0.0 --port $PORT

# 3. Deploy dashboard to Streamlit
# Visit: https://streamlit.io/cloud
# Click "New app" → Select repo → Set path: dashboard/app.py

# 4. Configure secrets in Streamlit
# Add API_URL in Streamlit settings
```

---

## Configuration Files Explained

### `dashboard/requirements.txt`
Minimal dependencies for dashboard only:
- streamlit
- plotly (for charts)
- pandas (for data handling)
- requests (for API calls)

### `dashboard/.streamlit/config.toml`
Streamlit configuration:
- Theme colors
- Server settings
- Browser settings

### `dashboard/.streamlit/secrets.toml` (Local only)
Store API URL locally. In production, use Streamlit Cloud secrets manager.

---

## Update Dashboard App to Use API

Modify `dashboard/app.py` to connect to your backend:

```python
import streamlit as st
import requests

# Get API URL from secrets
API_URL = st.secrets.get("API_URL", "http://localhost:8000")

# Example: Fetch dashboard stats
@st.cache_data(ttl=60)
def get_dashboard_stats():
    try:
        response = requests.get(f"{API_URL}/api/admin/dashboard/stats")
        return response.json()
    except Exception as e:
        st.error(f"Cannot connect to API: {e}")
        return None

# Use throughout the app
stats = get_dashboard_stats()
if stats:
    st.metric("Total Reviews", stats["total_reviews"])
    st.metric("Fake Reviews", stats["fake_count"])
```

---

## Troubleshooting

### Issue: "Module not found"
**Solution**: Update `dashboard/requirements.txt` and redeploy

### Issue: "Cannot connect to API"
**Solution**: 
1. Verify backend is running
2. Check API_URL in Streamlit secrets
3. Ensure CORS is enabled in FastAPI:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://*.streamlit.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue: "App is sleeping"
**Solution**: Upgrade Render to paid tier ($7/month) for always-on

### Issue: "Secrets not found"
**Solution**: Add secrets in Streamlit Cloud → Settings → Secrets

---

## Advantages of Streamlit Cloud

✅ **Free forever** for public apps
✅ **Auto-deploys** from GitHub
✅ **No server management** needed
✅ **Built-in authentication** (optional)
✅ **Custom domains** (with paid plan)
✅ **Instant updates** on git push
✅ **No credit card** required

---

## Complete Architecture Example

### Free Tier Setup ($0/month)
```
GitHub (Free)
    ↓
Streamlit Cloud (Free) - Dashboard
    ↓ API calls
Render.com (Free) - FastAPI Backend
    ↓
Render PostgreSQL (Free) - Database
```

### Production Setup (~$30/month)
```
GitHub
    ↓
Streamlit Cloud (Private app $200/year)
    ↓ API calls
Heroku (Standard $25/month) - FastAPI
    ↓
Heroku Postgres ($50/month) - Database
```

---

## Alternative: Streamlit Community Cloud Features

### Free Tier
- Unlimited public apps
- 1 GB RAM per app
- GitHub integration
- Community support

### Teams Tier ($250/month)
- Private apps
- Custom domains
- SSO authentication
- Priority support
- More resources

---

## Post-Deployment Checklist

- [ ] Dashboard accessible at `yourapp.streamlit.app`
- [ ] Backend API running (test with `/health`)
- [ ] API_URL configured in Streamlit secrets
- [ ] CORS enabled for Streamlit domain
- [ ] Database initialized
- [ ] Models trained (if needed)
- [ ] All API endpoints responding
- [ ] Dashboard displays data correctly

---

## GitHub Repository Setup

### Create `.gitignore` (if not exists)
```
venv/
__pycache__/
*.pyc
.env
.env.production
.streamlit/secrets.toml
models/*.pkl
logs/
*.log
```

### Create `README.md` for GitHub
```markdown
# Fake Review Detection System

Production-ready fake review detection using ML.

## Live Demo
- Dashboard: https://yourapp.streamlit.app
- API: https://your-api.herokuapp.com/docs

## Quick Start
See GETTING_STARTED.md
```

---

## Monitoring Your Deployment

### Streamlit Cloud
- View logs in Streamlit dashboard
- See app metrics
- Monitor resource usage

### Backend (Render)
- View logs in Render dashboard
- Monitor response times
- Set up alerts

---

## Next Steps After Deployment

1. ✅ Test dashboard at your Streamlit URL
2. ✅ Test API endpoints
3. ✅ Configure custom domain (optional)
4. ✅ Set up monitoring alerts
5. ✅ Share with users!

---

## Support

- Streamlit Docs: https://docs.streamlit.io
- Streamlit Forum: https://discuss.streamlit.io
- Render Docs: https://render.com/docs
- This project: See DEPLOYMENT.md

---

**Estimated Time**: 15-20 minutes total
**Cost**: $0/month (free tier) or $30/month (production)
**Difficulty**: Easy 😊

---

Generated: October 27, 2025
Status: ✅ Ready for Streamlit Deployment
