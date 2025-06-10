#!/usr/bin/env python3
import sqlite3

# Check database structure
def check_database():
    try:
        conn = sqlite3.connect('creditiq_simple.db')
        cursor = conn.cursor()
        
        # Get table info
        cursor.execute("PRAGMA table_info(scorecards)")
        columns = cursor.fetchall()
        print("Scorecards table structure:")
        for col in columns:
            print(f"  {col}")
        
        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='scorecards'")
        exists = cursor.fetchone()
        print(f"\nTable exists: {exists is not None}")
        
        # Check current data
        cursor.execute("SELECT COUNT(*) FROM scorecards")
        count = cursor.fetchone()[0]
        print(f"Records in scorecards: {count}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_database()