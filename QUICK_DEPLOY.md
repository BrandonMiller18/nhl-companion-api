# Quick Deploy to Heroku - TL;DR Version

For those who want to get up and running fast. See `HEROKU_DEPLOYMENT.md` for detailed explanations.

## Prerequisites
- Heroku CLI installed
- GitHub repository with your code
- MySQL database (or plan to use JawsDB/ClearDB add-on)

## Quick Steps

### 1. Login and Create App
```bash
heroku login
cd C:\nhl_companion\nhl-companion-api
heroku create your-app-name
```

### 2. Set Environment Variables
```bash
# Generate API token first
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Set all required variables
heroku config:set DB_HOST=your-db-host
heroku config:set DB_PORT=3306
heroku config:set DB_USER=your-db-user
heroku config:set DB_PASSWORD=your-db-password
heroku config:set DB_NAME=nhl
heroku config:set API_BEARER_TOKEN=your-generated-token
heroku config:set LOG_TO_FILE=false
```

### 3. Deploy
```bash
# Option A: Via Heroku Git
git push heroku main

# Option B: Via GitHub (in Heroku Dashboard)
# Deploy tab → Connect to GitHub → Enable Automatic Deploys → Deploy Branch
```

### 4. Verify
```bash
heroku logs --tail
heroku open /health
```

## Database Quick Setup

### Using JawsDB (Recommended)
```bash
heroku addons:create jawsdb:kitefin
heroku config:get JAWSDB_URL
# Parse the URL and set DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME
```

### Using Existing Database
Just set the environment variables to point to your existing MySQL database.

## Test Your API
```bash
# Health check (no auth)
curl https://your-app-name.herokuapp.com/health

# Authenticated endpoint
curl -H "Authorization: Bearer your-token" \
  https://your-app-name.herokuapp.com/api/v1/teams
```

## Useful Commands
```bash
heroku logs --tail        # View logs
heroku ps                 # Check status
heroku restart            # Restart app
heroku config             # View all config vars
```

## API Documentation
- Swagger UI: `https://your-app-name.herokuapp.com/docs`
- ReDoc: `https://your-app-name.herokuapp.com/redoc`

---

**Done! Your API is live! 🎉**

For troubleshooting and advanced configuration, see `HEROKU_DEPLOYMENT.md`.

