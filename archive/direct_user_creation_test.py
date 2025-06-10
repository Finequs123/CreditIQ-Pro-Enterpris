#!/usr/bin/env python3

import sqlite3
import hashlib
from datetime import datetime

def create_test_user():
    """Directly create a test user in the database"""
    print("Creating test user 'finraja' directly in database...")
    
    try:
        conn = sqlite3.connect('user_management.db')
        cursor = conn.cursor()
        
        # Hash the password
        password = "Password321#"
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        # First check what columns exist in companies table
        cursor.execute("PRAGMA table_info(companies)")
        columns = cursor.fetchall()
        print("Companies table structure:")
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
        
        # Create a test company first
        print("Creating test company...")
        cursor.execute("""
        INSERT OR IGNORE INTO companies (company_name, is_active, registration_date)
        VALUES (?, ?, ?)
        """, ("FinRaja Test Company", True, datetime.now().isoformat()))
        
        # Get the company ID
        cursor.execute("SELECT id FROM companies WHERE company_name = ?", ("FinRaja Test Company",))
        company_result = cursor.fetchone()
        if not company_result:
            print("Error: Could not create or find test company")
            return False
        
        company_id = company_result[0]
        print(f"Company created with ID: {company_id}")
        
        # Create the user
        print("Creating user...")
        cursor.execute("""
        INSERT INTO users (username, password_hash, company_id, is_active, created_date)
        VALUES (?, ?, ?, ?, ?)
        """, ("finraja", password_hash, company_id, True, datetime.now().isoformat()))
        
        user_id = cursor.lastrowid
        print(f"User created with ID: {user_id}")
        
        conn.commit()
        conn.close()
        
        print("✅ User creation successful!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating user: {e}")
        return False

def verify_user():
    """Verify the user was created correctly"""
    print("\n=== Verifying User Creation ===")
    
    try:
        conn = sqlite3.connect('user_management.db')
        cursor = conn.cursor()
        
        cursor.execute("""
        SELECT u.id, u.username, u.company_id, c.company_name, u.is_active
        FROM users u
        JOIN companies c ON u.company_id = c.id
        WHERE u.username = ?
        """, ("finraja",))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            user_id, username, company_id, company_name, is_active = result
            print(f"✅ User found:")
            print(f"   ID: {user_id}")
            print(f"   Username: {username}")
            print(f"   Company: {company_name} (ID: {company_id})")
            print(f"   Active: {is_active}")
            return True
        else:
            print("❌ User not found")
            return False
            
    except Exception as e:
        print(f"❌ Error verifying user: {e}")
        return False

def test_authentication():
    """Test if authentication works"""
    print("\n=== Testing Authentication ===")
    
    try:
        import sqlite3
        import hashlib
        
        # Check what password hash is stored and company status
        conn = sqlite3.connect('user_management.db')
        cursor = conn.cursor()
        cursor.execute("""
        SELECT u.password_hash, u.is_active, c.is_active, c.company_name
        FROM users u
        JOIN companies c ON u.company_id = c.id
        WHERE u.username = ?
        """, ("finraja",))
        result = cursor.fetchone()
        stored_hash, user_active, company_active, company_name = result
        print(f"Stored hash: {stored_hash[:20]}...")
        print(f"User active: {user_active}")
        print(f"Company active: {company_active}")
        print(f"Company name: {company_name}")
        
        # Check what hash our system generates
        password = "Password321#"
        generated_hash = hashlib.sha256(password.encode()).hexdigest()
        print(f"Generated hash: {generated_hash[:20]}...")
        print(f"Hashes match: {stored_hash == generated_hash}")
        
        conn.close()
        
        # Now test with auth system
        from user_auth_system import UserAuthSystem
        auth_system = UserAuthSystem()
        
        result = auth_system.authenticate_company_user("finraja", "Password321#")
        
        if result:
            print("✅ Authentication successful!")
            print(f"   User: {result}")
            return True
        else:
            print("❌ Authentication failed")
            return False
            
    except Exception as e:
        print(f"❌ Error testing authentication: {e}")
        return False

if __name__ == "__main__":
    print("=== Direct User Creation Test ===")
    
    # Step 1: Verify user exists
    verify_user()
    
    # Step 2: Test authentication
    test_authentication()