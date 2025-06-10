#!/usr/bin/env python3

import sqlite3
import hashlib

def check_user_exists(username):
    """Check if user exists in database"""
    try:
        conn = sqlite3.connect('user_management.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()
        return user
    except Exception as e:
        print(f"Error checking user: {e}")
        return None

def check_all_users():
    """List all users in database"""
    try:
        conn = sqlite3.connect('user_management.db')
        cursor = conn.cursor()
        # First check table structure
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        print("User table structure:")
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
        
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        conn.close()
        return users
    except Exception as e:
        print(f"Error listing users: {e}")
        return []

def test_password(username, password):
    """Test password verification"""
    user = check_user_exists(username)
    if user:
        stored_password = user[3]  # Assuming password is 4th column
        # Test direct match
        if stored_password == password:
            return True, "Direct match"
        # Test hashed match
        hashed = hashlib.sha256(password.encode()).hexdigest()
        if stored_password == hashed:
            return True, "Hashed match"
        return False, f"No match. Stored: {stored_password[:20]}..."
    return False, "User not found"

if __name__ == "__main__":
    print("=== User Management Database Check ===")
    print(f"Checking for user: finraja")
    
    user = check_user_exists('finraja')
    if user:
        print(f"User found: {user}")
        # Test password
        result, msg = test_password('finraja', 'Password321#')
        print(f"Password test: {result} ({msg})")
    else:
        print("User 'finraja' not found")
    
    print("\n=== All Users in Database ===")
    users = check_all_users()
    for user in users:
        print(f"Username: {user[0]}, Company ID: {user[1]}, Role: {user[2]}")