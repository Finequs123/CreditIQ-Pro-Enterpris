import sqlite3

conn = sqlite3.connect('creditiq_simple.db')
cursor = conn.cursor()

# Check if scorecards table exists and its structure
try:
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='scorecards'")
    result = cursor.fetchone()
    if result:
        print("Scorecards table structure:")
        print(result[0])
    else:
        print("Scorecards table does not exist")
        
    # Try to get table info
    cursor.execute("PRAGMA table_info(scorecards)")
    columns = cursor.fetchall()
    print("\nColumns:")
    for col in columns:
        print(f"  {col[1]} ({col[2]})")
        
except Exception as e:
    print(f"Error: {e}")
    
conn.close()