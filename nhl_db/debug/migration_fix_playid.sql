-- Migration to fix playId column type from INT to BIGINT
-- This is needed because concatenating game_id (2025020076) with eventId
-- produces values that exceed INT max (2,147,483,647)

-- Drop foreign key constraints that reference playId
-- (There are none in the schema, so this section is commented out)

-- Alter the column type
ALTER TABLE plays MODIFY COLUMN playId BIGINT PRIMARY KEY;

-- Verify the change
DESCRIBE plays;

