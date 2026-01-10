# NHL Companion API

FastAPI-based REST API for accessing NHL game, team, and player data.

## Overview

This service provides a public API for accessing NHL data stored in a MySQL database. It includes endpoints for:
- Teams (active and all)
- Games (by date and timezone)
- Players (by team and by ID)
- Game details with play-by-play data

## Architecture

The API service includes:
- **FastAPI application** (`api_app.py`) - Main application entry point
- **API routes** (`api/router.py`) - Endpoint definitions
- **Database package** (`nhl_db/`) - Database access layer shared with DB CLI service
  - `repositories/` - Data access layer
  - `config.py` - Environment configuration
  - `db.py` - Database connection management
  - `logging_config.py` - Logging setup

## Local Development Setup

### Prerequisites

- Python 3.11+
- MySQL database (local or remote)
- Git

### Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd nhl-companion-api
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp env.example .env
# Edit .env with your database credentials and API token
```

5. Generate a secure API token:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Running Locally

```bash
python api_app.py
```

The API will be available at `http://localhost:8000`

API documentation:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Testing

```bash
# Install test dependencies if needed
pip install pytest pytest-asyncio httpx

# Run tests
python test_api.py
```

## Deployment to Heroku

### Prerequisites

- Heroku account
- Heroku CLI installed
- Git repository

### Deployment Steps

1. Create a Heroku app:
```bash
heroku create your-app-name
```

2. Add MySQL add-on (choose one):
```bash
# Option 1: ClearDB (free tier available)
heroku addons:create cleardb:ignite

# Option 2: JawsDB (free tier available)
heroku addons:create jawsdb:kitefin
```

3. Get database credentials:
```bash
# For ClearDB
heroku config:get CLEARDB_DATABASE_URL

# For JawsDB
heroku config:get JAWSDB_URL
```

4. Set environment variables:
```bash
# Parse the database URL and set individual variables
heroku config:set DB_HOST=<host>
heroku config:set DB_PORT=3306
heroku config:set DB_USER=<user>
heroku config:set DB_PASSWORD=<password>
heroku config:set DB_NAME=<database>

# Set API token
heroku config:set API_BEARER_TOKEN=<your-secure-token>
```

5. Deploy:
```bash
git push heroku main
```

6. Verify deployment:
```bash
heroku logs --tail
heroku open /health
```

### Environment Variables

Required environment variables for production:

- `DB_HOST` - MySQL host
- `DB_PORT` - MySQL port (usually 3306)
- `DB_USER` - MySQL username
- `DB_PASSWORD` - MySQL password
- `DB_NAME` - MySQL database name
- `API_BEARER_TOKEN` - Bearer token for API authentication
- `PORT` - Automatically set by Heroku

Optional:
- `LOG_TO_FILE` - Set to "true" for file logging (default: false, uses stdout)

## API Authentication

All endpoints (except `/health`) require Bearer token authentication:

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" https://your-app.herokuapp.com/api/teams/active
```

## API Endpoints

### Health Check
- `GET /health` - No authentication required

### Teams
- `GET /api/teams` - Get all teams
- `GET /api/teams/active` - Get active teams only

### Games
- `GET /api/games?date=YYYY-MM-DD&timezone=America/New_York` - Get games by date

### Players
- `GET /api/teams/{team_id}/players` - Get players by team
- `GET /api/players/{player_id}` - Get player by ID

### Game Details
- `GET /api/games/{game_id}` - Get game details with play-by-play

## Database Schema

The API expects the following database schema (managed by the DB CLI service):
- `teams` - NHL teams
- `games` - Game schedule and results
- `players` - Player information
- `plays` - Play-by-play data

## CORS Configuration

By default, CORS is configured to allow all origins (`allow_origins=["*"]`). 

**For production**, update `api_app.py` to specify your frontend domain:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-domain.vercel.app"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)
```

## Monitoring and Logs

### Heroku Logs
```bash
heroku logs --tail
heroku logs --source app
```

### Health Check
```bash
curl https://your-app.herokuapp.com/health
```

## Troubleshooting

### Database Connection Issues
- Verify database credentials in Heroku config vars
- Check if MySQL add-on is provisioned
- Test connection from Heroku console: `heroku run python -c "from nhl_db.db import get_db_connection; get_db_connection()"`

### Authentication Errors
- Verify `API_BEARER_TOKEN` is set in Heroku config
- Ensure frontend is using the correct token

### Import Errors
- The `nhl_db` package is included in this repository
- No sys.path manipulation needed - imports work directly

## Related Repositories

- **Frontend**: NHL Companion Frontend (Next.js on Vercel)
- **DB CLI**: NHL Companion DB CLI (data sync service on Heroku)

## License

MIT
