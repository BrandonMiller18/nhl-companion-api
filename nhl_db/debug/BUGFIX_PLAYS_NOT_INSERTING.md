# Bug Fix: Plays Not Being Inserted to Database

## Problem
When watching game ID 2025020076, only 2 plays were being inserted into the database despite the API returning 268+ plays.

## Root Causes

### 1. Integer Overflow in playId Column
**Issue**: The `playId` column was defined as `INT` (max value: 2,147,483,647) but the mapper concatenates `game_id` + `eventId` as strings, producing values like:
- Game 2025020076, eventId 54 → playId = 20,250,200,7654 (exceeds INT max!)

**Solution**: Changed `playId` column type from `INT` to `BIGINT` in schema.sql and applied migration to existing database.

### 2. Missing Time Data in Plays
**Issue**: The mapper was looking for time data in `periodDescriptor.timeElapsed` and `periodDescriptor.timeRemaining`, but the API returns `None` for these fields. The actual time data is in the top-level `timeInPeriod` and `timeRemaining` fields.

**Solution**: Updated `mappers/plays.py` to:
1. Fallback to `p.get("timeInPeriod")` if periodDescriptor doesn't have time data
2. Fallback to `p.get("timeRemaining")` for remaining time
3. Provide default values ("00:00") for NOT NULL fields when data is missing

## Files Changed

1. **services/db/test/schema.sql**
   - Changed `playId INT PRIMARY KEY` → `playId BIGINT PRIMARY KEY`

2. **services/db/nhl_db/mappers/plays.py**
   - Added fallback logic to extract time from `timeInPeriod` field
   - Added default values for NOT NULL fields (period=0, times="00:00")

3. **services/db/apply_migration.py** (temporary)
   - Migration script to alter existing database column type
   - Can be run again if needed: `python apply_migration.py`

4. **services/db/migration_fix_playid.sql** (reference)
   - SQL migration for manual application if needed

## Verification

After fixes:
- ✓ 270 plays successfully inserted for game 2025020076 (up from 2)
- ✓ All plays have proper time data (playTime, playTimeRemaining)
- ✓ All playId values correctly stored without truncation
- ✓ No database errors

## Testing

Run the update command to test:
```bash
python app.py update-live 2025020076
```

Expected output:
```
Upserted 268 plays
Updated game 2025020076; upserted 268 plays.
```

