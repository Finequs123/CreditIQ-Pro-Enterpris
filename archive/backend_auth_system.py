"""
Backend Authentication System for CreditIQ Pro
Handles proper database operations for admin-created users
"""

import sqlite3
import hashlib
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Tuple

class BackendAuthSystem:
    """Backend authentication system that connects to admin user creation"""
    
    def __init__(self, db_path: str = "user_management.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize complete database structure"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Companies table - matches what admin creates
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT UNIQUE NOT NULL,
            institution_type TEXT NOT NULL,
            primary_location TEXT,
            created_by TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE,
            onboarding_completed BOOLEAN DEFAULT FALSE,
            preferred_loan_types TEXT,
            data_availability_level TEXT,
            risk_appetite TEXT,
            volume_expectation TEXT,
            business_focus TEXT,
            user_preferences TEXT
        )
        """)
        
        # Users table - for company users created by admin
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            company_id INTEGER,
            user_type TEXT NOT NULL DEFAULT 'company_user',
            full_name TEXT,
            email TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE,
            last_login TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies (id)
        )
        """)
        
        # Company configurations - for storing onboarding data
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS company_configurations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER,
            config_type TEXT NOT NULL,
            config_data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE,
            FOREIGN KEY (company_id) REFERENCES companies (id)
        )
        """)
        
        conn.commit()
        conn.close()
    
    def hash_password(self, password: str) -> str:
        """Hash password consistently with admin system"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_company(self, company_data: Dict, admin_id: str = "admin") -> int:
        """Create company from admin interface"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
        INSERT INTO companies (company_name, institution_type, primary_location, created_by, onboarding_completed)
        VALUES (?, ?, ?, ?, ?)
        """, (
            company_data['company_name'],
            company_data['institution_type'],
            company_data.get('primary_location', ''),
            admin_id,
            True
        ))
        
        company_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return company_id
    
    def create_company_user(self, company_id: int, user_data: Dict) -> int:
        """Create company user from admin interface"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        password_hash = self.hash_password(user_data['password'])
        
        cursor.execute("""
        INSERT INTO users (username, password_hash, company_id, user_type, full_name, email)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (
            user_data['username'],
            password_hash,
            company_id,
            'company_user',
            user_data.get('full_name', ''),
            user_data.get('email', '')
        ))
        
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return user_id
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate user against database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        password_hash = self.hash_password(password)
        
        cursor.execute("""
        SELECT u.id, u.username, u.company_id, c.company_name, u.user_type, u.full_name
        FROM users u
        JOIN companies c ON u.company_id = c.id
        WHERE u.username = ? AND u.password_hash = ? AND u.is_active = 1 AND c.is_active = 1
        """, (username, password_hash))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            user_id, username, company_id, company_name, user_type, full_name = result
            return {
                'id': user_id,
                'username': username,
                'company_id': company_id,
                'company_name': company_name,
                'type': user_type,
                'full_name': full_name
            }
        
        return None
    
    def update_last_login(self, user_id: int):
        """Update user's last login timestamp"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
        UPDATE users SET last_login = ? WHERE id = ?
        """, (datetime.now().isoformat(), user_id))
        
        conn.commit()
        conn.close()
    
    def get_companies(self) -> List[Dict]:
        """Get all active companies"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
        SELECT id, company_name, institution_type, created_at
        FROM companies
        WHERE is_active = 1
        ORDER BY company_name
        """)
        
        companies = []
        for row in cursor.fetchall():
            companies.append({
                'id': row[0],
                'company_name': row[1],
                'institution_type': row[2],
                'created_at': row[3]
            })
        
        conn.close()
        return companies
    
    def save_onboarding_data(self, company_id: int, onboarding_data: Dict):
        """Save onboarding configuration data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        import json
        config_data = json.dumps(onboarding_data)
        
        cursor.execute("""
        INSERT INTO company_configurations (company_id, config_type, config_data)
        VALUES (?, ?, ?)
        """, (company_id, 'onboarding', config_data))
        
        # Update company onboarding status
        cursor.execute("""
        UPDATE companies SET onboarding_completed = 1 WHERE id = ?
        """, (company_id,))
        
        conn.commit()
        conn.close()

# Global instance
backend_auth = BackendAuthSystem()