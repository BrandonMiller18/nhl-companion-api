# NHL Companion API Setup Guide

## Quick Start

### 1. Install Dependencies

```powershell
pip install -r requirements.txt
```

This will install:
- FastAPI (web framework)
- Uvicorn (ASGI server)
- Pydantic (data validation)
- And existing dependencies (requests, mysql-connector-python, python-dotenv)

### 2. Configure Environment Variables

Add the following to your `.env` file at `services/.env`:

```env
# Database Configuration (existing)
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=
DB_NAME=nhl

# API Configuration (new - required for API service)
API_BEARER_TOKEN=your-secret-token-here
API_HOST=0.0.0.0  # Optional, defaults to 0.0.0.0
API_PORT=8000     # Optional, defaults to 8000
```

**Important:** Generate a secure random token for `API_BEARER_TOKEN` in production:

```powershell
# PowerShell - generate a random token
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 3. Start the API Server

```powershell
# From the /db directory
python api_app.py

# Or use uvicorn directly with custom settings
uvicorn api_app:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Access the API

- **Interactive Docs (Swagger UI):** http://localhost:8000/docs
- **Alternative Docs (ReDoc):** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/health

## API Endpoints

All endpoints (except `/health`) require bearer token authentication.

### Authentication

Include the bearer token in the `Authorization` header:

```
Authorization: Bearer your-secret-token-here
```

### Available Endpoints

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/health` | GET | Health check | No |
| `/api/teams` | GET | Get all teams | Yes |
| `/api/teams/active` | GET | Get only active teams | Yes |
| `/api/games?date=YYYY-MM-DD` | GET | Get games for a specific date | Yes |
| `/api/teams/{team_id}/players` | GET | Get all players for a team | Yes |
| `/api/games/{game_id}` | GET | Get game details with play-by-play data | Yes |

## Usage Examples

### Using cURL

```bash
# Health check (no auth required)
curl http://localhost:8000/health

# Get all teams
curl -H "Authorization: Bearer your-secret-token-here" \
  http://localhost:8000/api/teams

# Get active teams only
curl -H "Authorization: Bearer your-secret-token-here" \
  http://localhost:8000/api/teams/active

# Get games for a specific date
curl -H "Authorization: Bearer your-secret-token-here" \
  "http://localhost:8000/api/games?date=2025-01-15"

# Get players for a team (e.g., team ID 19)
curl -H "Authorization: Bearer your-secret-token-here" \
  http://localhost:8000/api/teams/19/players

# Get game details with play-by-play
curl -H "Authorization: Bearer your-secret-token-here" \
  http://localhost:8000/api/games/2025020001
```

### Using Python requests

```python
import requests

API_BASE = "http://localhost:8000"
TOKEN = "your-secret-token-here"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

# Get all teams
response = requests.get(f"{API_BASE}/api/teams", headers=HEADERS)
teams = response.json()

# Get games for a date
response = requests.get(
    f"{API_BASE}/api/games",
    params={"date": "2025-01-15"},
    headers=HEADERS
)
games = response.json()

# Get game details
response = requests.get(
    f"{API_BASE}/api/games/2025020001",
    headers=HEADERS
)
game_detail = response.json()
```

### Using JavaScript/TypeScript

```javascript
const API_BASE = "http://localhost:8000";
const TOKEN = "your-secret-token-here";

// Get all teams
const response = await fetch(`${API_BASE}/api/teams`, {
  headers: {
    "Authorization": `Bearer ${TOKEN}`
  }
});
const teams = await response.json();

// Get games for a date
const gamesResponse = await fetch(
  `${API_BASE}/api/games?date=2025-01-15`,
  {
    headers: {
      "Authorization": `Bearer ${TOKEN}`
    }
  }
);
const games = await gamesResponse.json();
```

## Response Formats

### Team Response

```json
{
  "teamId": 19,
  "teamName": "Blues",
  "teamCity": "St. Louis",
  "teamAbbrev": "STL",
  "teamIsActive": true,
  "teamLogoUrl": "https://..."
}
```

### Player Response

```json
{
  "playerId": 8478402,
  "playerTeamId": 19,
  "playerFirstName": "Jordan",
  "playerLastName": "Binnington",
  "playerNumber": 50,
  "playerPosition": "G",
  "playerHeadshotUrl": "https://...",
  "playerHomeCity": "Richmond Hill",
  "playerHomeCountry": "CAN"
}
```

### Game Response

```json
{
  "gameId": 2025020001,
  "gameSeason": 20252026,
  "gameType": 2,
  "gameDateTimeUtc": "2025-10-08T23:00:00",
  "gameVenue": "T-Mobile Arena",
  "gameHomeTeamId": 54,
  "gameAwayTeamId": 28,
  "gameState": "final",
  "gamePeriod": 3,
  "gameClock": "00:00",
  "gameHomeScore": 4,
  "gameAwayScore": 2,
  "gameHomeSOG": 32,
  "gameAwaySOG": 28,
  "homeTeamName": "Golden Knights",
  "homeTeamAbbrev": "VGK",
  "awayTeamName": "Avalanche",
  "awayTeamAbbrev": "COL"
}
```

### Game Detail Response (with plays)

```json
{
  "game": {
    "gameId": 2025020001,
    "gameSeason": 20252026,
    ...
  },
  "plays": [
    {
      "playId": 20250200010001,
      "playGameId": 2025020001,
      "playIndex": 1,
      "playTeamId": 54,
      "playPrimaryPlayerId": 8478402,
      "playLosingPlayerId": null,
      "playSecondaryPlayerId": null,
      "playTertiaryPlayerId": null,
      "playPeriod": 1,
      "playTime": "00:00",
      "playTimeReamaining": "20:00",
      "playType": "FACEOFF",
      "playZone": 2,
      "playXCoord": 0,
      "playYCoord": 0
    },
    ...
  ]
}
```

## Error Responses

The API returns standard HTTP status codes with JSON error messages:

### 401 Unauthorized

```json
{
  "detail": "Invalid authentication credentials"
}
```

### 404 Not Found

```json
{
  "detail": "Game 2025020001 not found"
}
```

### 422 Unprocessable Entity

```json
{
  "detail": "Invalid request parameters",
  "errors": [...]
}
```

### 500 Internal Server Error

```json
{
  "detail": "An unexpected error occurred"
}
```

## Production Deployment

### Security Considerations

1. **Use a strong bearer token:** Generate a cryptographically secure random token
2. **Configure CORS:** Update the `allow_origins` in `api_app.py` to restrict access to specific domains
3. **Use HTTPS:** Deploy behind a reverse proxy (nginx, Caddy) with SSL/TLS
4. **Rate limiting:** Consider adding rate limiting middleware for production
5. **Logging:** Monitor API access logs for suspicious activity

### Running in Production

```bash
# Use production-grade ASGI server
uvicorn api_app:app --host 0.0.0.0 --port 8000 --workers 4

# Or use gunicorn with uvicorn workers
gunicorn api_app:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Systemd Service (Linux)

Create `/etc/systemd/system/nhl-api.service`:

```ini
[Unit]
Description=NHL Companion API
After=network.target mysql.service

[Service]
Type=notify
User=www-data
WorkingDirectory=/path/to/nhlcompanion/services/db
Environment="PATH=/path/to/venv/bin"
EnvironmentFile=/path/to/.env
ExecStart=/path/to/venv/bin/uvicorn api_app:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

## Troubleshooting

### Import Errors

If you see import errors for `fastapi`, `uvicorn`, or `pydantic`:

```powershell
pip install -r requirements.txt
```

### Database Connection Errors

Verify your database configuration in `.env`:
- Ensure MySQL is running
- Check credentials are correct
- Verify database exists and schema is loaded

### Authentication Errors

- Ensure `API_BEARER_TOKEN` is set in `.env`
- Verify the token matches in your API requests
- Check the `Authorization` header format: `Bearer <token>`

### Port Already in Use

If port 8000 is already in use:

```powershell
# Use a different port
uvicorn api_app:app --host 0.0.0.0 --port 8080

# Or set API_PORT in .env
API_PORT=8080
```

## Architecture

```
External Service
    ↓ (Bearer Token)
FastAPI Application (api_app.py)
    ↓
API Router (nhl_db/api/router.py)
    ↓ (Authentication)
Bearer Token Auth (nhl_db/api/auth.py)
    ↓ (Validated)
Repository Layer (nhl_db/repositories/*.py)
    ↓
MySQL Database
```

## File Structure

```
services/db/
├── api_app.py                    # FastAPI application entry point
├── nhl_db/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── models.py            # Pydantic response models
│   │   ├── auth.py              # Bearer token authentication
│   │   └── router.py            # API endpoints
│   ├── repositories/
│   │   ├── teams_repo.py        # Team queries
│   │   ├── games_repo.py        # Game queries
│   │   ├── players_repo.py      # Player queries
│   │   └── plays_repo.py        # Play queries
│   └── ...
└── requirements.txt              # Python dependencies
```

