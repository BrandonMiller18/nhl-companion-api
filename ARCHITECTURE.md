# NHL Companion - System Architecture

This document describes the overall architecture of the NHL Companion application.

## System Overview

NHL Companion is a web application for viewing NHL games, teams, and live play-by-play data. The system is split into three independent services:

```
┌─────────────────┐
│   Frontend      │  Next.js on Vercel
│   (Vercel)      │  - User interface
└────────┬────────┘  - Game viewing
         │           - Team browsing
         │ HTTPS
         ▼
┌─────────────────┐
│   API Service   │  FastAPI on Heroku
│   (Heroku)      │  - REST API
└────────┬────────┘  - Authentication
         │           - Data access
         │ SQL
         ▼
┌─────────────────┐
│   MySQL DB      │  Heroku Add-on
│   (Heroku)      │  - Teams
└─────────────────┘  - Games
         ▲           - Players
         │           - Plays
         │ SQL
┌────────┴────────┐
│   DB CLI        │  Python CLI on Heroku
│   (Heroku)      │  - Data sync
└─────────────────┘  - Live monitoring
         │
         │ HTTPS
         ▼
┌─────────────────┐
│   NHL APIs      │  External
│                 │  - Game data
└─────────────────┘  - Player data
```

## Three Independent Repositories

### 1. Frontend Repository (`nhl-companion-frontend`)

**Technology**: Next.js 14 (App Router), TypeScript, Tailwind CSS

**Hosting**: Vercel

**Purpose**: User-facing web application

**Key Features**:
- Server-side rendering for fast page loads
- Client-side interactivity for live updates
- Next.js API routes as proxy layer (keeps API token secure)
- Responsive design

**Dependencies**:
- NHL Companion API (via HTTP)

**Environment Variables**:
- `API_BEARER_TOKEN` - Authentication for API
- `API_BASE_URL` - API service URL
- `NEXT_PUBLIC_ENABLE_TEST_MODE` - Feature flag

### 2. API Repository (`nhl-companion-api`)

**Technology**: FastAPI, Python 3.11+, MySQL Connector

**Hosting**: Heroku

**Purpose**: REST API for data access

**Key Features**:
- RESTful endpoints for teams, games, players, plays
- Bearer token authentication
- CORS configuration for frontend
- Database connection pooling
- Comprehensive error handling

**Includes**:
- `api/` - API endpoints and models
- `nhl_db/` - Database package (shared with DB CLI conceptually)
  - `repositories/` - Data access layer
  - `config.py` - Environment configuration
  - `db.py` - Database connections
  - `logging_config.py` - Logging setup

**Dependencies**:
- MySQL database (via Heroku add-on)

**Environment Variables**:
- `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME` - Database credentials
- `API_BEARER_TOKEN` - Authentication token
- `PORT` - Server port (set by Heroku)

### 3. DB CLI Repository (`nhl-companion-db-cli`)

**Technology**: Python 3.11+, MySQL Connector, Click/argparse

**Hosting**: Heroku (scheduled jobs via Heroku Scheduler)

**Purpose**: Data synchronization and management

**Key Features**:
- Fetch data from NHL external APIs
- Sync teams, players, schedules
- Monitor live games
- Update play-by-play data
- Database schema management

**Includes**:
- `app.py` - CLI entry point
- `nhl_db/` - Database package
  - `commands/` - CLI commands (teams, players, schedule, live)
  - `clients/` - External API clients
  - `repositories/` - Data access layer
  - `mappers/` - Data transformation
  - `services/` - Business logic

**Dependencies**:
- MySQL database (same as API service)
- NHL Web API (external)
- NHL Records API (external)

**Environment Variables**:
- `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME` - Database credentials

## Data Flow

### 1. Data Ingestion (DB CLI → MySQL)

```
NHL APIs → DB CLI Service → MySQL Database
```

1. DB CLI fetches data from NHL APIs
2. Transforms data via mappers
3. Stores in MySQL via repositories
4. Runs on schedule (Heroku Scheduler)

### 2. Data Access (Frontend → API → MySQL)

```
User → Frontend → Next.js API Routes → API Service → MySQL Database
```

1. User requests page in browser
2. Frontend makes request to Next.js API route
3. Next.js API route adds authentication and forwards to API service
4. API service queries MySQL database
5. Data flows back through the chain
6. Frontend renders the data

### 3. Live Game Updates

```
NHL APIs → DB CLI (monitoring) → MySQL → API Service → Frontend (polling)
```

1. DB CLI monitors live games (scheduled job every 10 minutes)
2. Updates play-by-play data in MySQL
3. Frontend polls API service for updates
4. API service returns latest data from MySQL

## Authentication Flow

```
Frontend (.env.local)
  ↓ API_BEARER_TOKEN (server-side only)
Next.js API Route
  ↓ Authorization: Bearer <token>
API Service
  ↓ Validates token
MySQL Database
```

**Security Notes**:
- API token stored server-side only (not in browser)
- Next.js API routes act as secure proxy
- CORS restricts API access to known domains
- Database credentials never exposed to frontend

## Database Schema

### Tables

**teams**
- Team information (id, name, abbreviation, logo, etc.)

**players**
- Player information (id, name, position, team, etc.)

**games**
- Game schedule and results
- Scores, state, period, clock, shots on goal

**plays**
- Play-by-play events
- Event type, time, period, players involved, description

## Deployment Architecture

### Production Environment

```
┌──────────────────────────────────────────────────────┐
│                     Vercel                           │
│  ┌────────────────────────────────────────────────┐  │
│  │  Frontend (Next.js)                            │  │
│  │  - Automatic scaling                           │  │
│  │  - Edge network                                │  │
│  │  - SSL/TLS                                     │  │
│  └────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────┘
                         │
                         │ HTTPS
                         ▼
┌──────────────────────────────────────────────────────┐
│                     Heroku                           │
│  ┌────────────────────────────────────────────────┐  │
│  │  API Service (FastAPI)                         │  │
│  │  - Web dyno                                    │  │
│  │  - Auto-scaling available                      │  │
│  └────────────────────────────────────────────────┘  │
│                         │                            │
│                         │ SQL                        │
│                         ▼                            │
│  ┌────────────────────────────────────────────────┐  │
│  │  MySQL Database (ClearDB/JawsDB)               │  │
│  │  - Managed service                             │  │
│  │  - Automatic backups                           │  │
│  └────────────────────────────────────────────────┘  │
│                         ▲                            │
│                         │ SQL                        │
│  ┌────────────────────────────────────────────────┐  │
│  │  DB CLI Service                                │  │
│  │  - Scheduled jobs (Heroku Scheduler)           │  │
│  │  - One-off dynos                               │  │
│  └────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────┘
```

### Scaling Considerations

**Frontend (Vercel)**:
- Automatically scales with traffic
- Edge network for global performance
- No configuration needed

**API Service (Heroku)**:
- Starts with 1 web dyno
- Can scale horizontally (add more dynos)
- Consider upgrading dyno type for better performance

**DB CLI Service (Heroku)**:
- Runs as scheduled jobs (no always-on dyno needed)
- Can run one-off dynos for manual operations
- Cost-effective for batch processing

**Database (MySQL)**:
- Starts with free tier (ClearDB Ignite or JawsDB Kitefin)
- Upgrade for more storage/connections
- Consider connection pooling for high traffic

## Monitoring and Observability

### Logs

**Frontend**: Vercel Dashboard
- Deployment logs
- Function logs
- Real-time log streaming

**API Service**: Heroku Logs
```bash
heroku logs --tail --app your-api-app
```

**DB CLI**: Heroku Logs
```bash
heroku logs --tail --app your-db-cli-app
```

### Health Checks

**API Service**: `GET /health`
- Returns service status
- No authentication required
- Use for uptime monitoring

**Frontend**: Homepage load
- Should display teams grid
- Indicates full stack health

### Metrics

**Vercel**:
- Page load times
- Core Web Vitals
- Bandwidth usage

**Heroku**:
- Dyno metrics (CPU, memory)
- Response times
- Error rates

## Cost Estimation

### Free Tier (Suitable for Development/Small Projects)

- **Vercel**: Free (100 GB bandwidth/month)
- **Heroku API**: Free dyno (sleeps after 30 min inactivity)
- **Heroku DB CLI**: Free (scheduled jobs only)
- **MySQL**: Free tier (ClearDB Ignite: 5 MB, JawsDB Kitefin: 5 MB)

**Total**: $0/month

### Production Tier (Suitable for Real Usage)

- **Vercel**: Free or Pro ($20/month for team features)
- **Heroku API**: Hobby dyno ($7/month, no sleeping)
- **Heroku DB CLI**: Free (scheduled jobs only)
- **MySQL**: Paid tier ($10-20/month for more storage)

**Total**: ~$17-47/month

## Security Best Practices

1. **API Authentication**: Use strong bearer tokens
2. **Environment Variables**: Never commit secrets
3. **CORS**: Restrict to known domains in production
4. **HTTPS**: Enforced by Vercel and Heroku
5. **Database**: Use strong passwords, restrict access
6. **Regular Updates**: Keep dependencies updated

## Disaster Recovery

### Backups

**Database**: 
- Heroku MySQL add-ons include automatic backups
- Consider manual exports for critical data

**Code**:
- All code in Git repositories
- GitHub provides redundancy

### Rollback Procedures

**Frontend**: 
- Vercel: Promote previous deployment to production

**API Service**:
- Heroku: Roll back release via CLI or dashboard

**Database**:
- Restore from Heroku add-on backup

## Future Enhancements

### Potential Improvements

1. **Caching Layer**: Redis for frequently accessed data
2. **Real-time Updates**: WebSockets for live game updates
3. **CDN**: For static assets and images
4. **Database Replicas**: Read replicas for scaling
5. **Monitoring**: Application Performance Monitoring (APM)
6. **CI/CD**: Automated testing and deployment
7. **Feature Flags**: Dynamic feature toggling

## Related Documentation

- Frontend: See `nhl-companion-frontend/README.md`
- API: See `nhl-companion-api/README.md`
- DB CLI: See `nhl-companion-db-cli/README.md`
- Frontend Deployment: See `nhl-companion-frontend/DEPLOYMENT.md`

