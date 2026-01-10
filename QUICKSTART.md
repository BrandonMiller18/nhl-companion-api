# Quick Start Guide - NHL Companion API

This guide will help you get the API service running locally for testing.

## Prerequisites

- Python 3.11+
- MySQL database running locally
- Database populated with data (see DB CLI service)

## Quick Setup

### 1. Install Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example environment file
cp env.example .env

# Edit .env with your values
# Windows: notepad .env
# Mac/Linux: nano .env
```

Required values in `.env`:
```env
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your-mysql-password
DB_NAME=nhl

API_BEARER_TOKEN=test-token-12345
API_HOST=0.0.0.0
API_PORT=8001
```

### 3. Verify Database Connection

```bash
python -c "from nhl_db.db import get_db_connection; conn = get_db_connection(); print('Connected!'); conn.close()"
```

If this succeeds, you're ready to run the API!

### 4. Start the API Server

```bash
python api_app.py
```

You should see:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8001
```

### 5. Test the API

**Health Check** (no auth required):
```bash
curl http://localhost:8001/health
```

**Get Active Teams** (requires auth):
```bash
curl -H "Authorization: Bearer test-token-12345" http://localhost:8001/api/teams/active
```

**View API Documentation**:
- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc

## Testing with the Test Script

```bash
# Make sure API is running first
python test_api.py
```

This will test all endpoints and show you the results.

## Common Issues

### "Can't connect to MySQL server"

**Solution**: 
- Make sure MySQL is running
- Check DB_HOST, DB_PORT in .env
- Verify credentials with: `mysql -u root -p`

### "Environment variable DB_NAME is required"

**Solution**: 
- Make sure .env file exists
- Check all required variables are set
- Restart the API after changing .env

### "Invalid authentication credentials"

**Solution**: 
- Check Authorization header format: `Bearer <token>`
- Verify token matches API_BEARER_TOKEN in .env

### Port Already in Use

**Solution**:
- Change API_PORT in .env to a different port (e.g., 8002)
- Or stop the process using port 8001

## Next Steps

1. **Populate Database**: Use the DB CLI service to sync data
2. **Test Frontend**: Connect the frontend to this API
3. **Deploy**: Follow README.md for Heroku deployment

## Development Tips

### Auto-reload on Code Changes

The API runs with `reload=True` by default, so it will automatically restart when you change code.

### Viewing Logs

Logs are printed to console by default. To enable file logging:

```env
LOG_TO_FILE=true
```

Then check `logs/nhl_companion.log`

### Testing Individual Endpoints

Use the Swagger UI at http://localhost:8001/docs to:
- See all available endpoints
- Test requests interactively
- View request/response schemas

### Database Queries

To see what data is available:

```bash
mysql -u root -p nhl

# In MySQL:
SELECT COUNT(*) FROM teams;
SELECT COUNT(*) FROM games;
SELECT COUNT(*) FROM players;
SELECT * FROM teams LIMIT 5;
```

## Ready for Production?

See [README.md](README.md) for deployment instructions to Heroku.

