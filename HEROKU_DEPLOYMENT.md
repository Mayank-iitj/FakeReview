# 🚀 HEROKU DEPLOYMENT GUIDE

## Prerequisites Installed ✅
- Git (just installed)
- Heroku CLI (just installed)

## Files Created for Heroku ✅
- `Procfile` - Tells Heroku how to run the app
- `runtime.txt` - Specifies Python version

---

## Deployment Steps

### Step 1: Restart Your Terminal
**IMPORTANT**: Close and reopen PowerShell for Git and Heroku to be available.

### Step 2: Login to Heroku
```powershell
heroku login
```
This will open your browser for authentication.

### Step 3: Initialize Git Repository
```powershell
cd d:\fake-review-detector
git init
git add .
git commit -m "Initial commit - Fake Review Detection System"
```

### Step 4: Create Heroku App
```powershell
heroku create fake-review-detector-app
```
Note: If name is taken, Heroku will suggest alternatives.

### Step 5: Add PostgreSQL Database
```powershell
heroku addons:create heroku-postgresql:essential-0
```
This creates a PostgreSQL database (free tier: hobby-dev or paid: essential-0).

### Step 6: Set Environment Variables
```powershell
# Generate a secret key
$secret = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | ForEach-Object {[char]$_})

# Set environment variables
heroku config:set JWT_SECRET_KEY=$secret
heroku config:set ENVIRONMENT=production
heroku config:set PREDICTION_THRESHOLD=0.5
heroku config:set USE_BERT=False
heroku config:set API_WORKERS=2
```

### Step 7: Deploy to Heroku
```powershell
git push heroku main
```
Or if you're on master branch:
```powershell
git push heroku master
```

### Step 8: Initialize Database
```powershell
heroku run python scripts/init_db.py
```

### Step 9: Scale Dynos (Optional)
```powershell
# Start with 1 dyno (free tier)
heroku ps:scale web=1

# Or upgrade for better performance
heroku ps:scale web=2
```

### Step 10: Open Your App
```powershell
heroku open
```

### Step 11: View Logs
```powershell
heroku logs --tail
```

---

## Quick Commands Reference

| Task | Command |
|------|---------|
| View app URL | `heroku info` |
| View logs | `heroku logs --tail` |
| Restart app | `heroku restart` |
| Run command | `heroku run <command>` |
| Access database | `heroku pg:psql` |
| View config | `heroku config` |
| Set config | `heroku config:set KEY=value` |

---

## After Deployment

Your app will be available at:
```
https://fake-review-detector-app.herokuapp.com
```

API Documentation:
```
https://fake-review-detector-app.herokuapp.com/docs
```

Health Check:
```
https://fake-review-detector-app.herokuapp.com/health
```

---

## Troubleshooting

### Issue: "No web processes running"
```powershell
heroku ps:scale web=1
```

### Issue: Database connection error
```powershell
# Check database URL is set
heroku config:get DATABASE_URL

# Restart app
heroku restart
```

### Issue: Out of memory
```powershell
# Upgrade dyno type
heroku ps:type hobby
# or
heroku ps:type standard-1x
```

### Issue: App crashes on startup
```powershell
# View logs for errors
heroku logs --tail

# Check recent releases
heroku releases

# Rollback if needed
heroku rollback
```

---

## Cost Estimate

### Free Tier (Eco Dynos)
- Basic dyno: $5/month (550 hours)
- PostgreSQL Mini: $5/month (10,000 rows)
- **Total**: ~$10/month

### Production Tier
- Standard-1X dyno: $25/month
- PostgreSQL Essential-0: $50/month
- **Total**: ~$75/month

---

## Next Steps After Deployment

1. ✅ Test all API endpoints at `/docs`
2. ✅ Verify database connectivity
3. ✅ Train models: `heroku run python scripts/train_model.py`
4. ✅ Set up custom domain (optional)
5. ✅ Configure monitoring alerts
6. ✅ Set up automated backups

---

## Complete Deployment Script (After Terminal Restart)

Copy and run this in PowerShell:

```powershell
# Navigate to project
cd d:\fake-review-detector

# Login to Heroku
heroku login

# Initialize git
git init
git add .
git commit -m "Initial deployment"

# Create Heroku app
heroku create fake-review-detector-app

# Add PostgreSQL
heroku addons:create heroku-postgresql:mini

# Set environment variables
$secret = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | ForEach-Object {[char]$_})
heroku config:set JWT_SECRET_KEY=$secret
heroku config:set ENVIRONMENT=production
heroku config:set USE_BERT=False
heroku config:set API_WORKERS=2

# Deploy
git push heroku main

# Initialize database
heroku run python scripts/init_db.py

# Open app
heroku open

# View logs
heroku logs --tail
```

---

## Important Notes

⚠️ **Before deploying, update requirements.txt** to remove heavy dependencies if using free tier:
- Comment out `torch` if not using BERT
- Consider lighter ML models for free tier

⚠️ **Database**: Heroku provides DATABASE_URL automatically, no need to set it manually.

⚠️ **File storage**: Heroku has ephemeral filesystem. Use S3 for model storage in production.

⚠️ **Scraping**: May need additional buildpacks for Chrome/Selenium:
```powershell
heroku buildpacks:add heroku/python
heroku buildpacks:add https://github.com/heroku/heroku-buildpack-google-chrome
heroku buildpacks:add https://github.com/heroku/heroku-buildpack-chromedriver
```

---

Generated: October 27, 2025
Status: ✅ Ready for Heroku Deployment
