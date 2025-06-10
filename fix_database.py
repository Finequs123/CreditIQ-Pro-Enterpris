#!/usr/bin/env python3
import sqlite3
import os

def fix_database():
    # Remove the problematic database
    if os.path.exists('creditiq_simple.db'):
        os.remove('creditiq_simple.db')
        print("Removed old database")
    
    # Create new database with correct structure
    conn = sqlite3.connect('creditiq_simple.db')
    cursor = conn.cursor()
    
    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL,
            company_id INTEGER,
            created_by TEXT,
            last_login TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies (id)
        )
    """)
    
    # Companies table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            created_by TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Scorecards table with correct column names
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scorecards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            configuration TEXT NOT NULL,
            weights TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies (id)
        )
    """)
    
    # Admin accounts table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admin_setup (
            id INTEGER PRIMARY KEY,
            is_initialized BOOLEAN DEFAULT FALSE,
            setup_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()
    print("Database recreated with correct structure")

if __name__ == "__main__":
    fix_database()