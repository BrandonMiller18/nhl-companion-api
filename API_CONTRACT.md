# NHL Companion API Contract

## Overview

This document defines the complete API contract for the NHL Companion backend service. It is intended for frontend developers and AI code generation tools to understand the exact data structures, endpoints, and behaviors of the API.

**Base URL:** `http://localhost:8000` (development) or your production URL

**API Version:** 1.0.0

**Authentication:** Bearer Token (required for all endpoints except `/health`)

---

## Table of Contents

1. [Authentication](#authentication)
2. [Common Response Patterns](#common-response-patterns)
3. [Data Models](#data-models)
4. [Endpoints](#endpoints)
5. [Error Handling](#error-handling)
6. [Usage Patterns](#usage-patterns)

---

## Authentication

### Bearer Token Authentication

All API endpoints (except `/health`) require a bearer token in the `Authorization` header.

**Header Format:**
```
Authorization: Bearer <token>
```

**Example:**
```javascript
const headers = {
  'Authorization': 'Bearer your-secret-token-here',
  'Content-Type': 'application/json'
};
```

### Authentication Errors

If authentication fails, the API returns:
- **Status Code:** `401 Unauthorized`
- **Response Body:**
```json
{
  "detail": "Invalid authentication credentials"
}
```

---

## Common Response Patterns

### Success Responses

- **Status Code:** `200 OK`
- **Content-Type:** `application/json`
- **Body:** JSON object or array matching the endpoint's response model

### Empty Results

When a query returns no results (e.g., no players for a team, no games on a date):
- **Status Code:** `200 OK`
- **Body:** Empty array `[]`

### Not Found

When a specific resource doesn't exist (e.g., game ID not found):
- **Status Code:** `404 Not Found`
- **Body:**
```json
{
  "detail": "Game 2025020001 not found"
}
```

---

## Data Models

### TeamResponse

Represents an NHL team.

```typescript
interface TeamResponse {
  teamId: number;              // Unique team identifier
  teamName: string;            // Team name (e.g., "Blues")
  teamCity: string | null;     // Team city (e.g., "St. Louis")
  teamAbbrev: string | null;   // Team abbreviation (e.g., "STL")
  teamIsActive: boolean;       // Whether team is currently active
  teamLogoUrl: string | null;  // URL to team logo image
}
```

**Example:**
```json
{
  "teamId": 19,
  "teamName": "Blues",
  "teamCity": "St. Louis",
  "teamAbbrev": "STL",
  "teamIsActive": true,
  "teamLogoUrl": "https://assets.nhle.com/logos/nhl/svg/STL_dark.svg"
}
```

**Field Notes:**
- `teamId`: Use this as the primary identifier for all team-related operations
- `teamIsActive`: `false` for historical/defunct teams (e.g., Atlanta Thrashers)
- `teamLogoUrl`: May be `null` for some historical teams

---

### PlayerResponse

Represents an NHL player.

```typescript
interface PlayerResponse {
  playerId: number;                 // Unique player identifier
  playerTeamId: number | null;      // Current team ID (FK to TeamResponse)
  playerFirstName: string;          // Player's first name
  playerLastName: string;           // Player's last name
  playerNumber: number | null;      // Jersey number
  playerPosition: string | null;    // Position code (e.g., "C", "LW", "D", "G")
  playerHeadshotUrl: string | null; // URL to player headshot image
  playerHomeCity: string | null;    // Player's birthplace city
  playerHomeCountry: string | null; // Player's birthplace country (3-letter code)
}
```

**Example:**
```json
{
  "playerId": 8478402,
  "playerTeamId": 19,
  "playerFirstName": "Jordan",
  "playerLastName": "Binnington",
  "playerNumber": 50,
  "playerPosition": "G",
  "playerHeadshotUrl": "https://assets.nhle.com/mugs/nhl/20252026/STL/8478402.png",
  "playerHomeCity": "Richmond Hill",
  "playerHomeCountry": "CAN"
}
```

**Field Notes:**
- `playerPosition`: Common values are `"C"` (center), `"LW"` (left wing), `"RW"` (right wing), `"D"` (defense), `"G"` (goalie)
- `playerNumber`: May be `null` for players without assigned numbers
- `playerTeamId`: May be `null` for free agents or retired players
- `playerHomeCountry`: Uses 3-letter ISO codes (e.g., "USA", "CAN", "SWE", "RUS")

---

### GameResponse

Represents an NHL game with basic details.

```typescript
interface GameResponse {
  gameId: number;                    // Unique game identifier
  gameSeason: number;                // Season year (YYYYMMDD format, e.g., 20252026)
  gameType: number;                  // Game type code
  gameDateTimeUtc: string;           // Game date/time in ISO 8601 UTC format
  gameVenue: string | null;          // Venue name
  gameHomeTeamId: number;            // Home team ID (FK to TeamResponse)
  gameAwayTeamId: number;            // Away team ID (FK to TeamResponse)
  gameState: string;                 // Game state
  gamePeriod: number | null;         // Current/final period number
  gameClock: string | null;          // Game clock (MM:SS format)
  gameHomeScore: number;             // Home team score
  gameAwayScore: number;             // Away team score
  gameHomeSOG: number;               // Home team shots on goal
  gameAwaySOG: number;               // Away team shots on goal
  homeTeamName: string | null;       // Home team name (denormalized)
  homeTeamAbbrev: string | null;     // Home team abbreviation (denormalized)
  awayTeamName: string | null;       // Away team name (denormalized)
  awayTeamAbbrev: string | null;     // Away team abbreviation (denormalized)
}
```

**Example:**
```json
{
  "gameId": 2025020076,
  "gameSeason": 20252026,
  "gameType": 2,
  "gameDateTimeUtc": "2025-10-15T23:00:00",
  "gameVenue": "Enterprise Center",
  "gameHomeTeamId": 19,
  "gameAwayTeamId": 54,
  "gameState": "FINAL",
  "gamePeriod": 3,
  "gameClock": "00:00",
  "gameHomeScore": 4,
  "gameAwayScore": 3,
  "gameHomeSOG": 32,
  "gameAwaySOG": 28,
  "homeTeamName": "Blues",
  "homeTeamAbbrev": "STL",
  "awayTeamName": "Golden Knights",
  "awayTeamAbbrev": "VGK"
}
```

**Field Notes:**
- `gameType`: `2` = Regular Season, `3` = Playoffs, `1` = Preseason
- `gameState`: Common values are `"FUT"` (future/scheduled), `"LIVE"` (in progress), `"CRIT"` (nearing end), `"FINAL"` (completed), `"OFF"` (official final)
- `gameDateTimeUtc`: Always in UTC timezone, ISO 8601 format. Convert to local time in frontend.
- `gamePeriod`: `1-3` for regulation, `4+` for overtime periods. `null` if game hasn't started.
- `gameClock`: Format is `"MM:SS"` (e.g., `"12:34"`). `"00:00"` when period ends. `null` if game hasn't started.
- Team name/abbrev fields: Denormalized for convenience to avoid additional lookups

---

### PlayResponse

Represents a single play-by-play event in a game.

```typescript
interface PlayResponse {
  playId: number;                      // Unique play identifier (global)
  playGameId: number;                  // Game ID this play belongs to
  playIndex: number;                   // Sequential index within the game
  playTeamId: number | null;           // Team ID associated with play
  playPrimaryPlayerId: number | null;  // Primary player involved
  playLosingPlayerId: number | null;   // Losing player (for faceoffs)
  playSecondaryPlayerId: number | null;// Secondary player (assists, etc.)
  playTertiaryPlayerId: number | null; // Tertiary player (second assist, etc.)
  playPeriod: number;                  // Period number
  playTime: string;                    // Time in period (MM:SS)
  playTimeReamaining: string;          // Time remaining in period (MM:SS)
  playType: string;                    // Type of play event
  playZone: number | null;             // Zone code
  playXCoord: number | null;           // X coordinate on ice
  playYCoord: number | null;           // Y coordinate on ice
}
```

**Example:**
```json
{
  "playId": 20250200760054,
  "playGameId": 2025020076,
  "playIndex": 54,
  "playTeamId": 19,
  "playPrimaryPlayerId": 8478402,
  "playLosingPlayerId": null,
  "playSecondaryPlayerId": 8477474,
  "playTertiaryPlayerId": 8480012,
  "playPeriod": 1,
  "playTime": "05:23",
  "playTimeReamaining": "14:37",
  "playType": "GOAL",
  "playZone": 2,
  "playXCoord": 89,
  "playYCoord": -12
}
```

**Field Notes:**
- `playId`: Globally unique across all games (concatenation of gameId + eventId)
- `playIndex`: Sequential within a game, starts at 1
- `playType`: Common values include:
  - `"FACEOFF"` - Face-off
  - `"SHOT"` - Shot on goal
  - `"GOAL"` - Goal scored
  - `"MISSED_SHOT"` - Shot missed net
  - `"BLOCKED_SHOT"` - Shot blocked
  - `"HIT"` - Body check/hit
  - `"GIVEAWAY"` - Giveaway
  - `"TAKEAWAY"` - Takeaway
  - `"PENALTY"` - Penalty
  - `"STOPPAGE"` - Play stoppage
  - `"PERIOD_START"` - Period start
  - `"PERIOD_END"` - Period end
- `playZone`: `1` = Defensive, `2` = Neutral, `3` = Offensive (relative to playTeamId)
- `playXCoord`, `playYCoord`: Ice rink coordinates. Origin varies by data source. May be `null` for non-location events.
- Player IDs: Reference `PlayerResponse.playerId`. May be `null` if not applicable to the play type.

---

### GameDetailResponse

Represents a complete game with all play-by-play data.

```typescript
interface GameDetailResponse {
  game: GameResponse;      // Game details
  plays: PlayResponse[];   // Array of all plays in the game
}
```

**Example:**
```json
{
  "game": {
    "gameId": 2025020076,
    "gameSeason": 20252026,
    "gameType": 2,
    "gameDateTimeUtc": "2025-10-15T23:00:00",
    "gameVenue": "Enterprise Center",
    "gameHomeTeamId": 19,
    "gameAwayTeamId": 54,
    "gameState": "FINAL",
    "gamePeriod": 3,
    "gameClock": "00:00",
    "gameHomeScore": 4,
    "gameAwayScore": 3,
    "gameHomeSOG": 32,
    "gameAwaySOG": 28,
    "homeTeamName": "Blues",
    "homeTeamAbbrev": "STL",
    "awayTeamName": "Golden Knights",
    "awayTeamAbbrev": "VGK"
  },
  "plays": [
    {
      "playId": 20250200760001,
      "playGameId": 2025020076,
      "playIndex": 1,
      "playTeamId": 19,
      "playPrimaryPlayerId": 8478402,
      "playLosingPlayerId": 8477956,
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
    // ... more plays
  ]
}
```

**Field Notes:**
- `plays` array is sorted by `playPeriod` and `playIndex`
- Array may be empty for games that haven't started or have no recorded plays
- Typical game has 200-400 plays

---

## Endpoints

### 1. Health Check

**Purpose:** Verify API is running. No authentication required.

```
GET /health
```

**Authentication:** None required

**Query Parameters:** None

**Response:** `200 OK`

```typescript
interface HealthResponse {
  status: string;   // "healthy"
  service: string;  // "NHL Companion API"
  version: string;  // "1.0.0"
}
```

**Example Response:**
```json
{
  "status": "healthy",
  "service": "NHL Companion API",
  "version": "1.0.0"
}
```

**Frontend Usage:**
- Use for initial connection testing
- Use for health monitoring/status checks
- No need to include auth token

---

### 2. Get All Teams

**Purpose:** Retrieve all NHL teams (active and inactive).

```
GET /api/teams
```

**Authentication:** Required (Bearer Token)

**Query Parameters:** None

**Response:** `200 OK`

```typescript
TeamResponse[]
```

**Example Response:**
```json
[
  {
    "teamId": 1,
    "teamName": "Devils",
    "teamCity": "New Jersey",
    "teamAbbrev": "NJD",
    "teamIsActive": true,
    "teamLogoUrl": "https://assets.nhle.com/logos/nhl/svg/NJD_dark.svg"
  },
  {
    "teamId": 19,
    "teamName": "Blues",
    "teamCity": "St. Louis",
    "teamAbbrev": "STL",
    "teamIsActive": true,
    "teamLogoUrl": "https://assets.nhle.com/logos/nhl/svg/STL_dark.svg"
  }
  // ... more teams
]
```

**Frontend Usage:**
- Use to populate team selection dropdowns
- Cache response for the session (teams rarely change)
- Filter by `teamIsActive` if you only want current teams
- Use `teamId` for all subsequent team-related queries

**Typical Response Size:** 30-40 teams

---

### 3. Get Active Teams

**Purpose:** Retrieve only currently active NHL teams.

```
GET /api/teams/active
```

**Authentication:** Required (Bearer Token)

**Query Parameters:** None

**Response:** `200 OK`

```typescript
TeamResponse[]
```

**Example Response:**
```json
[
  {
    "teamId": 19,
    "teamName": "Blues",
    "teamCity": "St. Louis",
    "teamAbbrev": "STL",
    "teamIsActive": true,
    "teamLogoUrl": "https://assets.nhle.com/logos/nhl/svg/STL_dark.svg"
  }
  // ... more active teams
]
```

**Frontend Usage:**
- Use when you only need current NHL teams
- Preferred over `/api/teams` for most UI scenarios
- Cache response for the session

**Typical Response Size:** 32 teams (current NHL size)

---

### 4. Get Games by Date

**Purpose:** Retrieve all games scheduled for a specific date.

```
GET /api/games?date={YYYY-MM-DD}
```

**Authentication:** Required (Bearer Token)

**Query Parameters:**

| Parameter | Type | Required | Format | Description |
|-----------|------|----------|--------|-------------|
| `date` | string | Yes | `YYYY-MM-DD` | Date to query (e.g., "2025-01-15") |

**Response:** `200 OK`

```typescript
GameResponse[]
```

**Example Request:**
```
GET /api/games?date=2025-10-15
```

**Example Response:**
```json
[
  {
    "gameId": 2025020076,
    "gameSeason": 20252026,
    "gameType": 2,
    "gameDateTimeUtc": "2025-10-15T23:00:00",
    "gameVenue": "Enterprise Center",
    "gameHomeTeamId": 19,
    "gameAwayTeamId": 54,
    "gameState": "FINAL",
    "gamePeriod": 3,
    "gameClock": "00:00",
    "gameHomeScore": 4,
    "gameAwayScore": 3,
    "gameHomeSOG": 32,
    "gameAwaySOG": 28,
    "homeTeamName": "Blues",
    "homeTeamAbbrev": "STL",
    "awayTeamName": "Golden Knights",
    "awayTeamAbbrev": "VGK"
  }
  // ... more games for this date
]
```

**Empty Result:**
```json
[]
```

**Validation Error (422):**
```json
{
  "detail": "Invalid request parameters",
  "errors": [
    {
      "loc": ["query", "date"],
      "msg": "string does not match regex \"^\\d{4}-\\d{2}-\\d{2}$\"",
      "type": "value_error.str.regex"
    }
  ]
}
```

**Frontend Usage:**
- Use for daily schedule views
- Date must be in `YYYY-MM-DD` format (ISO 8601)
- Returns empty array if no games scheduled
- Games are sorted by `gameDateTimeUtc`
- Convert `gameDateTimeUtc` from UTC to user's local timezone for display
- Poll this endpoint periodically to update live game states

**Typical Response Size:** 0-16 games per date (varies by season)

---

### 5. Get Players by Team

**Purpose:** Retrieve all players for a specific team.

```
GET /api/teams/{team_id}/players
```

**Authentication:** Required (Bearer Token)

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `team_id` | integer | Yes | Team ID from TeamResponse |

**Response:** `200 OK`

```typescript
PlayerResponse[]
```

**Example Request:**
```
GET /api/teams/19/players
```

**Example Response:**
```json
[
  {
    "playerId": 8478402,
    "playerTeamId": 19,
    "playerFirstName": "Jordan",
    "playerLastName": "Binnington",
    "playerNumber": 50,
    "playerPosition": "G",
    "playerHeadshotUrl": "https://assets.nhle.com/mugs/nhl/20252026/STL/8478402.png",
    "playerHomeCity": "Richmond Hill",
    "playerHomeCountry": "CAN"
  },
  {
    "playerId": 8477474,
    "playerTeamId": 19,
    "playerFirstName": "Robert",
    "playerLastName": "Thomas",
    "playerNumber": 18,
    "playerPosition": "C",
    "playerHeadshotUrl": "https://assets.nhle.com/mugs/nhl/20252026/STL/8477474.png",
    "playerHomeCity": "Aurora",
    "playerHomeCountry": "CAN"
  }
  // ... more players
]
```

**Empty Result (no players for team):**
```json
[]
```

**Frontend Usage:**
- Use to display team rosters
- Players are sorted alphabetically by last name, then first name
- Group by `playerPosition` for organized roster display
- Use `playerHeadshotUrl` for player images (may be null)
- Cache response per team for the session

**Typical Response Size:** 20-30 players per team

---

### 6. Get Player by ID

**Purpose:** Retrieve detailed information for a specific player.

```
GET /api/players/{player_id}
```

**Authentication:** Required (Bearer Token)

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `player_id` | integer | Yes | Player ID from PlayerResponse |

**Response:** `200 OK`

```typescript
PlayerResponse
```

**Example Request:**
```
GET /api/players/8478402
```

**Example Response:**
```json
{
  "playerId": 8478402,
  "playerTeamId": 19,
  "playerFirstName": "Jordan",
  "playerLastName": "Binnington",
  "playerNumber": 50,
  "playerPosition": "G",
  "playerHeadshotUrl": "https://assets.nhle.com/mugs/nhl/20252026/STL/8478402.png",
  "playerHomeCity": "Richmond Hill",
  "playerHomeCountry": "CAN"
}
```

**Not Found (404):**
```json
{
  "detail": "Player 8478402 not found"
}
```

**Frontend Usage:**
- Use to get detailed information about a specific player
- Useful when you have a player ID from play-by-play data
- Can be used to display player profiles or details
- Cache response for the session to avoid repeated lookups

**Typical Response Size:** < 1 KB

---

### 7. Get Game Detail


**Purpose:** Retrieve complete game information including all play-by-play data.

```
GET /api/games/{game_id}
```

**Authentication:** Required (Bearer Token)

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `game_id` | integer | Yes | Game ID from GameResponse |

**Response:** `200 OK`

```typescript
GameDetailResponse
```

**Example Request:**
```
GET /api/games/2025020076
```

**Example Response:**
```json
{
  "game": {
    "gameId": 2025020076,
    "gameSeason": 20252026,
    "gameType": 2,
    "gameDateTimeUtc": "2025-10-15T23:00:00",
    "gameVenue": "Enterprise Center",
    "gameHomeTeamId": 19,
    "gameAwayTeamId": 54,
    "gameState": "FINAL",
    "gamePeriod": 3,
    "gameClock": "00:00",
    "gameHomeScore": 4,
    "gameAwayScore": 3,
    "gameHomeSOG": 32,
    "gameAwaySOG": 28,
    "homeTeamName": "Blues",
    "homeTeamAbbrev": "STL",
    "awayTeamName": "Golden Knights",
    "awayTeamAbbrev": "VGK"
  },
  "plays": [
    {
      "playId": 20250200760001,
      "playGameId": 2025020076,
      "playIndex": 1,
      "playTeamId": 19,
      "playPrimaryPlayerId": 8478402,
      "playLosingPlayerId": 8477956,
      "playSecondaryPlayerId": null,
      "playTertiaryPlayerId": null,
      "playPeriod": 1,
      "playTime": "00:00",
      "playTimeReamaining": "20:00",
      "playType": "FACEOFF",
      "playZone": 2,
      "playXCoord": 0,
      "playYCoord": 0
    }
    // ... 200-400 more plays
  ]
}
```

**Not Found (404):**
```json
{
  "detail": "Game 2025020076 not found"
}
```

**Frontend Usage:**
- Use for detailed game views with play-by-play
- Response can be large (200-400 plays per game)
- Consider pagination or virtualization for play list display
- Filter plays by `playType` for specific event types (e.g., only goals)
- Group plays by `playPeriod` for period-by-period view
- For live games, poll this endpoint to get updated plays
- Use player IDs to fetch player details from cached team rosters

**Typical Response Size:** Large (200-400 plays), ~50-200KB

---

## Error Handling

### HTTP Status Codes

| Code | Meaning | When It Occurs |
|------|---------|----------------|
| `200` | OK | Successful request |
| `401` | Unauthorized | Invalid or missing bearer token |
| `404` | Not Found | Resource doesn't exist (e.g., game ID not found) |
| `422` | Unprocessable Entity | Invalid request parameters (e.g., bad date format) |
| `500` | Internal Server Error | Unexpected server error |

### Error Response Format

All errors return a JSON object with a `detail` field:

```typescript
interface ErrorResponse {
  detail: string;              // Human-readable error message
  errors?: ValidationError[];  // Optional: validation errors (422 only)
}

interface ValidationError {
  loc: string[];    // Location of error (e.g., ["query", "date"])
  msg: string;      // Error message
  type: string;     // Error type
}
```

### Common Error Scenarios

#### 1. Missing Authentication

**Request:**
```
GET /api/teams
// No Authorization header
```

**Response:** `401 Unauthorized`
```json
{
  "detail": "Invalid authentication credentials"
}
```

#### 2. Invalid Date Format

**Request:**
```
GET /api/games?date=2025/01/15
```

**Response:** `422 Unprocessable Entity`
```json
{
  "detail": "Invalid request parameters",
  "errors": [
    {
      "loc": ["query", "date"],
      "msg": "string does not match regex \"^\\d{4}-\\d{2}-\\d{2}$\"",
      "type": "value_error.str.regex"
    }
  ]
}
```

#### 3. Game Not Found

**Request:**
```
GET /api/games/9999999999
```

**Response:** `404 Not Found`
```json
{
  "detail": "Game 9999999999 not found"
}
```

#### 4. Server Error

**Response:** `500 Internal Server Error`
```json
{
  "detail": "An unexpected error occurred"
}
```

### Frontend Error Handling Strategy

```typescript
async function fetchGames(date: string): Promise<GameResponse[]> {
  try {
    const response = await fetch(
      `${API_BASE}/api/games?date=${date}`,
      {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      }
    );

    if (!response.ok) {
      if (response.status === 401) {
        // Handle authentication error - redirect to login
        throw new Error('Authentication failed');
      } else if (response.status === 404) {
        // Resource not found
        const error = await response.json();
        throw new Error(error.detail);
      } else if (response.status === 422) {
        // Validation error
        const error = await response.json();
        throw new Error(error.detail);
      } else {
        // Other errors
        throw new Error('An unexpected error occurred');
      }
    }

    return await response.json();
  } catch (error) {
    // Handle network errors
    console.error('API request failed:', error);
    throw error;
  }
}
```

---

## Usage Patterns

### Pattern 1: Display Daily Schedule

**Goal:** Show all games for a selected date with team information.

**Steps:**
1. Fetch games for date: `GET /api/games?date=2025-01-15`
2. Display each game using embedded team names/abbreviations
3. No additional API calls needed (team info is denormalized)

**Code Example:**
```typescript
const games = await fetchGames('2025-01-15');

games.forEach(game => {
  console.log(`${game.awayTeamAbbrev} @ ${game.homeTeamAbbrev}`);
  console.log(`Score: ${game.awayScore} - ${game.homeScore}`);
  console.log(`State: ${game.gameState}`);
});
```

---

### Pattern 2: Display Team Roster

**Goal:** Show complete roster for a selected team.

**Steps:**
1. Fetch active teams: `GET /api/teams/active`
2. User selects a team
3. Fetch players: `GET /api/teams/{team_id}/players`
4. Group players by position and display

**Code Example:**
```typescript
const teams = await fetchActiveTeams();
const selectedTeamId = 19; // User selection

const players = await fetchPlayersByTeam(selectedTeamId);

// Group by position
const forwards = players.filter(p => 
  ['C', 'LW', 'RW'].includes(p.playerPosition || '')
);
const defensemen = players.filter(p => p.playerPosition === 'D');
const goalies = players.filter(p => p.playerPosition === 'G');
```

---

### Pattern 3: Live Game Updates

**Goal:** Display live game with real-time updates.

**Steps:**
1. Fetch game detail: `GET /api/games/{game_id}`
2. Display game info and plays
3. If `gameState === "LIVE"`, poll every 5-10 seconds
4. Update UI with new plays and scores

**Code Example:**
```typescript
let pollInterval: NodeJS.Timeout | null = null;

async function startLiveGameTracking(gameId: number) {
  const updateGame = async () => {
    const gameDetail = await fetchGameDetail(gameId);
    
    // Update UI with game state
    updateGameUI(gameDetail.game);
    updatePlaysUI(gameDetail.plays);
    
    // Stop polling if game is final
    if (gameDetail.game.gameState === 'FINAL' && pollInterval) {
      clearInterval(pollInterval);
      pollInterval = null;
    }
  };
  
  // Initial fetch
  await updateGame();
  
  // Poll every 10 seconds if live
  const initialDetail = await fetchGameDetail(gameId);
  if (initialDetail.game.gameState === 'LIVE') {
    pollInterval = setInterval(updateGame, 10000);
  }
}
```

---

### Pattern 4: Game Detail with Player Names

**Goal:** Show play-by-play with player names (not just IDs).

**Steps:**
1. Fetch game detail: `GET /api/games/{game_id}`
2. Extract unique team IDs from game
3. Fetch players for both teams: `GET /api/teams/{team_id}/players`
4. Create player lookup map
5. Display plays with player names

**Code Example:**
```typescript
const gameDetail = await fetchGameDetail(gameId);
const game = gameDetail.game;

// Fetch players for both teams
const [homePlayers, awayPlayers] = await Promise.all([
  fetchPlayersByTeam(game.gameHomeTeamId),
  fetchPlayersByTeam(game.gameAwayTeamId)
]);

// Create player lookup
const playerMap = new Map<number, PlayerResponse>();
[...homePlayers, ...awayPlayers].forEach(player => {
  playerMap.set(player.playerId, player);
});

// Display plays with player names
gameDetail.plays.forEach(play => {
  const primaryPlayer = play.playPrimaryPlayerId 
    ? playerMap.get(play.playPrimaryPlayerId)
    : null;
  
  if (primaryPlayer) {
    console.log(
      `${play.playType}: ${primaryPlayer.playerFirstName} ${primaryPlayer.playerLastName}`
    );
  }
});
```

---

### Pattern 5: Scoreboard Widget

**Goal:** Display compact scoreboard for all games on a date.

**Steps:**
1. Fetch games for date: `GET /api/games?date=2025-01-15`
2. Display compact view with scores and state
3. For live games, poll periodically to update scores

**Code Example:**
```typescript
async function updateScoreboard(date: string) {
  const games = await fetchGames(date);
  
  games.forEach(game => {
    const isLive = game.gameState === 'LIVE';
    const isFinal = game.gameState === 'FINAL';
    
    renderGameCard({
      away: {
        abbrev: game.awayTeamAbbrev,
        score: game.awayScore
      },
      home: {
        abbrev: game.homeTeamAbbrev,
        score: game.homeScore
      },
      state: game.gameState,
      period: game.gamePeriod,
      clock: game.gameClock,
      isLive: isLive
    });
  });
  
  // Poll if any games are live
  const hasLiveGames = games.some(g => g.gameState === 'LIVE');
  if (hasLiveGames) {
    setTimeout(() => updateScoreboard(date), 10000);
  }
}
```

---

## Data Relationships

### Entity Relationship Diagram

```
TeamResponse (1) ----< (N) PlayerResponse
     |                        |
     |                        |
     +----< GameResponse >----+
                |
                |
                +----< PlayResponse
```

### Key Relationships

1. **Team → Players**: One team has many players
   - Use `TeamResponse.teamId` = `PlayerResponse.playerTeamId`

2. **Team → Games**: One team plays in many games (as home or away)
   - Use `TeamResponse.teamId` = `GameResponse.gameHomeTeamId` OR `GameResponse.gameAwayTeamId`

3. **Game → Plays**: One game has many plays
   - Use `GameResponse.gameId` = `PlayResponse.playGameId`

4. **Player → Plays**: One player can be involved in many plays
   - Use `PlayerResponse.playerId` = `PlayResponse.playPrimaryPlayerId` (or secondary/tertiary)

---

## Best Practices for Frontend

### 1. Caching Strategy

**Cache these responses:**
- `/api/teams` or `/api/teams/active` - Cache for entire session (rarely changes)
- `/api/teams/{team_id}/players` - Cache per team for session

**Don't cache these responses:**
- `/api/games?date={date}` - Poll for live updates
- `/api/games/{game_id}` - Poll for live games

### 2. Polling Guidelines

**For live games:**
- Poll every 5-10 seconds during `gameState === "LIVE"`
- Stop polling when `gameState === "FINAL"` or `"OFF"`
- Use exponential backoff on errors

**For scoreboards:**
- Poll every 30-60 seconds for date-based game lists
- Only poll if any games are live

### 3. Date Handling

**Always:**
- Store dates in ISO 8601 format (`YYYY-MM-DD`)
- Convert `gameDateTimeUtc` from UTC to user's local timezone for display
- Validate date format before sending to API

**Example:**
```typescript
// Format date for API
const apiDate = new Date().toISOString().split('T')[0]; // "2025-01-15"

// Convert UTC to local for display
const gameTime = new Date(game.gameDateTimeUtc);
const localTime = gameTime.toLocaleString();
```

### 4. Error Handling

**Always handle:**
- 401 errors → Redirect to authentication/login
- 404 errors → Show "not found" message
- 422 errors → Show validation error to user
- 500 errors → Show generic error, retry with backoff
- Network errors → Show offline message

### 5. Performance Optimization

**For large datasets:**
- Use virtualization for long play lists (200-400 items)
- Implement pagination or "load more" for plays
- Debounce search/filter inputs

**For images:**
- Lazy load player headshots and team logos
- Use placeholder images while loading
- Handle missing images gracefully (null URLs)

---

## TypeScript Type Definitions

Complete TypeScript definitions for use in frontend applications:

```typescript
// ============================================================================
// API Response Models
// ============================================================================

export interface TeamResponse {
  teamId: number;
  teamName: string;
  teamCity: string | null;
  teamAbbrev: string | null;
  teamIsActive: boolean;
  teamLogoUrl: string | null;
}

export interface PlayerResponse {
  playerId: number;
  playerTeamId: number | null;
  playerFirstName: string;
  playerLastName: string;
  playerNumber: number | null;
  playerPosition: string | null;
  playerHeadshotUrl: string | null;
  playerHomeCity: string | null;
  playerHomeCountry: string | null;
}

export interface GameResponse {
  gameId: number;
  gameSeason: number;
  gameType: number;
  gameDateTimeUtc: string;
  gameVenue: string | null;
  gameHomeTeamId: number;
  gameAwayTeamId: number;
  gameState: string;
  gamePeriod: number | null;
  gameClock: string | null;
  gameHomeScore: number;
  gameAwayScore: number;
  gameHomeSOG: number;
  gameAwaySOG: number;
  homeTeamName: string | null;
  homeTeamAbbrev: string | null;
  awayTeamName: string | null;
  awayTeamAbbrev: string | null;
}

export interface PlayResponse {
  playId: number;
  playGameId: number;
  playIndex: number;
  playTeamId: number | null;
  playPrimaryPlayerId: number | null;
  playLosingPlayerId: number | null;
  playSecondaryPlayerId: number | null;
  playTertiaryPlayerId: number | null;
  playPeriod: number;
  playTime: string;
  playTimeReamaining: string;
  playType: string;
  playZone: number | null;
  playXCoord: number | null;
  playYCoord: number | null;
}

export interface GameDetailResponse {
  game: GameResponse;
  plays: PlayResponse[];
}

export interface HealthResponse {
  status: string;
  service: string;
  version: string;
}

export interface ErrorResponse {
  detail: string;
  errors?: ValidationError[];
}

export interface ValidationError {
  loc: string[];
  msg: string;
  type: string;
}

// ============================================================================
// API Client Configuration
// ============================================================================

export interface ApiConfig {
  baseUrl: string;
  bearerToken: string;
  timeout?: number;
}

// ============================================================================
// Enums and Constants
// ============================================================================

export enum GameState {
  FUTURE = 'FUT',
  LIVE = 'LIVE',
  FINAL = 'FINAL',
  OFFICIAL = 'OFF'
}

export enum GameType {
  PRESEASON = 1,
  REGULAR_SEASON = 2,
  PLAYOFFS = 3
}

export enum PlayerPosition {
  CENTER = 'C',
  LEFT_WING = 'LW',
  RIGHT_WING = 'RW',
  DEFENSE = 'D',
  GOALIE = 'G'
}

export enum PlayType {
  FACEOFF = 'FACEOFF',
  SHOT = 'SHOT',
  GOAL = 'GOAL',
  MISSED_SHOT = 'MISSED_SHOT',
  BLOCKED_SHOT = 'BLOCKED_SHOT',
  HIT = 'HIT',
  GIVEAWAY = 'GIVEAWAY',
  TAKEAWAY = 'TAKEAWAY',
  PENALTY = 'PENALTY',
  STOPPAGE = 'STOPPAGE',
  PERIOD_START = 'PERIOD_START',
  PERIOD_END = 'PERIOD_END'
}
```

---

## Appendix: Quick Reference

### All Endpoints Summary

| Endpoint | Method | Auth | Purpose |
|----------|--------|------|---------|
| `/health` | GET | No | Health check |
| `/api/teams` | GET | Yes | All teams |
| `/api/teams/active` | GET | Yes | Active teams only |
| `/api/games` | GET | Yes | Games by date |
| `/api/teams/{team_id}/players` | GET | Yes | Team roster |
| `/api/players/{player_id}` | GET | Yes | Player by ID |
| `/api/games/{game_id}` | GET | Yes | Game + plays |

### Common Response Sizes

| Endpoint | Typical Size | Notes |
|----------|--------------|-------|
| `/health` | < 1 KB | Tiny |
| `/api/teams` | 5-10 KB | 30-40 teams |
| `/api/teams/active` | 5-8 KB | 32 teams |
| `/api/games?date=...` | 5-20 KB | 0-16 games |
| `/api/teams/{id}/players` | 10-30 KB | 20-30 players |
| `/api/players/{id}` | < 1 KB | Single player |
| `/api/games/{id}` | 50-200 KB | Large (200-400 plays) |

### Date/Time Formats

| Field | Format | Example | Notes |
|-------|--------|---------|-------|
| Query param `date` | `YYYY-MM-DD` | `2025-01-15` | ISO 8601 date |
| `gameDateTimeUtc` | ISO 8601 | `2025-10-15T23:00:00` | UTC timezone |
| `gameClock` | `MM:SS` | `12:34` | Minutes:seconds |
| `playTime` | `MM:SS` | `05:23` | Time in period |
| `playTimeReamaining` | `MM:SS` | `14:37` | Time remaining |

---

**Document Version:** 1.0.0  
**Last Updated:** 2025-12-19  
**API Version:** 1.0.0

