#!/usr/bin/env python
"""Apply migration to fix playId column type"""
from nhl_db.db import get_db_connection

def apply_migration():
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        
        print("Checking current playId column type...")
        cur.execute("DESCRIBE plays")
        for row in cur.fetchall():
            if row[0] == 'playId':
                print(f"  Current: {row[0]} {row[1]}")
        
        print("\nAltering playId column from INT to BIGINT...")
        cur.execute("ALTER TABLE plays MODIFY COLUMN playId BIGINT")
        print("  [OK] Column altered successfully")
        
        print("\nVerifying new column type...")
        cur.execute("DESCRIBE plays")
        for row in cur.fetchall():
            if row[0] == 'playId':
                print(f"  New: {row[0]} {row[1]}")
        
        print("\nClearing invalid plays (those with truncated IDs)...")
        cur.execute("DELETE FROM plays WHERE playId = 2147483647")
        deleted = cur.rowcount
        print(f"  [OK] Deleted {deleted} invalid plays")
        
        cur.close()
        print("\n[OK] Migration completed successfully!")
        
    except Exception as e:
        print(f"\n[ERROR] Migration failed: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    apply_migration()

