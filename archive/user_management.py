"""
User Management System for CreditIQ Pro
Handles company registration, login persistence, and multi-tenant architecture
"""

import sqlite3
import streamlit as st
import hashlib
import json
from datetime import datetime
from typing import Dict, List, Optional, Any

class UserManager:
    """Manages user registration, authentication, and company profiles"""
    
    def __init__(self, db_path: str = "user_management.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize user management database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Companies table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS companies (
                company_id TEXT PRIMARY KEY,
                company_name TEXT NOT NULL,
                contact_email TEXT NOT NULL,
                phone_number TEXT,
                address TEXT,
                registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                onboarding_completed BOOLEAN DEFAULT FALSE,
                user_preferences TEXT,
                scoring_engine_preference TEXT DEFAULT 'legacy',
                is_active BOOLEAN DEFAULT TRUE
            )
        """)
        
        # Users table (for multiple users per company)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                company_id TEXT NOT NULL,
                username TEXT NOT NULL,
                email TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT,
                role TEXT DEFAULT 'user',
                last_login TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES companies (company_id)
            )
        """)
        
        # Sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_sessions (
                session_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                company_id TEXT NOT NULL,
                login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def hash_password(self, password: str) -> str:
        """Hash password for secure storage"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register_company(self, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """Register a new company"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Generate company ID
            company_id = f"COMP_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Insert company
            cursor.execute("""
                INSERT INTO companies (company_id, company_name, contact_email, phone_number, address)
                VALUES (?, ?, ?, ?, ?)
            """, (
                company_id,
                company_data['company_name'],
                company_data['contact_email'],
                company_data.get('phone_number', ''),
                company_data.get('address', '')
            ))
            
            # Create default admin user
            user_id = f"USER_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            password_hash = self.hash_password(company_data['admin_password'])
            
            cursor.execute("""
                INSERT INTO users (user_id, company_id, username, email, password_hash, full_name, role)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                company_id,
                company_data['admin_username'],
                company_data['contact_email'],
                password_hash,
                company_data.get('admin_name', company_data['admin_username']),
                'admin'
            ))
            
            conn.commit()
            
            return {
                'success': True,
                'company_id': company_id,
                'user_id': user_id,
                'message': 'Company registered successfully'
            }
            
        except Exception as e:
            conn.rollback()
            return {
                'success': False,
                'message': f'Registration failed: {str(e)}'
            }
        finally:
            conn.close()
    
    def authenticate_user(self, username: str, password: str) -> Dict[str, Any]:
        """Authenticate user login"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        password_hash = self.hash_password(password)
        
        cursor.execute("""
            SELECT u.user_id, u.company_id, u.full_name, u.role, c.company_name, c.onboarding_completed
            FROM users u
            JOIN companies c ON u.company_id = c.company_id
            WHERE u.username = ? AND u.password_hash = ? AND u.is_active = TRUE AND c.is_active = TRUE
        """, (username, password_hash))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            user_id, company_id, full_name, role, company_name, onboarding_completed = result
            
            # Create session
            session_id = self.create_session(user_id, company_id)
            
            return {
                'success': True,
                'session_id': session_id,
                'user_id': user_id,
                'company_id': company_id,
                'full_name': full_name,
                'role': role,
                'company_name': company_name,
                'onboarding_completed': bool(onboarding_completed)
            }
        else:
            return {
                'success': False,
                'message': 'Invalid username or password'
            }
    
    def create_session(self, user_id: str, company_id: str) -> str:
        """Create user session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        session_id = f"SESSION_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{user_id}"
        
        # Deactivate old sessions
        cursor.execute("""
            UPDATE user_sessions SET is_active = FALSE WHERE user_id = ?
        """, (user_id,))
        
        # Create new session
        cursor.execute("""
            INSERT INTO user_sessions (session_id, user_id, company_id)
            VALUES (?, ?, ?)
        """, (session_id, user_id, company_id))
        
        # Update last login
        cursor.execute("""
            UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE user_id = ?
        """, (user_id,))
        
        conn.commit()
        conn.close()
        
        return session_id
    
    def validate_session(self, session_id: str) -> Dict[str, Any]:
        """Validate active session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT s.user_id, s.company_id, u.full_name, u.role, c.company_name, c.onboarding_completed
            FROM user_sessions s
            JOIN users u ON s.user_id = u.user_id
            JOIN companies c ON s.company_id = c.company_id
            WHERE s.session_id = ? AND s.is_active = TRUE
        """, (session_id,))
        
        result = cursor.fetchone()
        
        if result:
            # Update last activity
            cursor.execute("""
                UPDATE user_sessions SET last_activity = CURRENT_TIMESTAMP WHERE session_id = ?
            """, (session_id,))
            conn.commit()
            
            user_id, company_id, full_name, role, company_name, onboarding_completed = result
            
            conn.close()
            return {
                'valid': True,
                'user_id': user_id,
                'company_id': company_id,
                'full_name': full_name,
                'role': role,
                'company_name': company_name,
                'onboarding_completed': bool(onboarding_completed)
            }
        else:
            conn.close()
            return {'valid': False}
    
    def complete_onboarding(self, company_id: str, preferences: Dict[str, Any]):
        """Mark onboarding as completed and save preferences"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE companies 
            SET onboarding_completed = TRUE, 
                user_preferences = ?,
                scoring_engine_preference = ?
            WHERE company_id = ?
        """, (
            json.dumps(preferences),
            preferences.get('recommended_engine', 'legacy'),
            company_id
        ))
        
        conn.commit()
        conn.close()
    
    def logout_user(self, session_id: str):
        """Logout user and deactivate session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE user_sessions SET is_active = FALSE WHERE session_id = ?
        """, (session_id,))
        
        conn.commit()
        conn.close()
    
    def get_company_list(self) -> List[Dict[str, Any]]:
        """Get list of all registered companies (for admin purposes)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT company_id, company_name, contact_email, registration_date, 
                   onboarding_completed, is_active
            FROM companies
            ORDER BY registration_date DESC
        """)
        
        companies = []
        for row in cursor.fetchall():
            companies.append({
                'company_id': row[0],
                'company_name': row[1],
                'contact_email': row[2],
                'registration_date': row[3],
                'onboarding_completed': bool(row[4]),
                'is_active': bool(row[5])
            })
        
        conn.close()
        return companies

def render_login_page():
    """Render login/registration page"""
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 15px; margin-bottom: 30px; text-align: center;">
        <h1 style="color: white; margin: 0; font-size: 36px;">🎯 CreditIQ Pro</h1>
        <p style="color: #e8f4f8; margin: 10px 0 0 0; font-size: 18px;">Enterprise Credit Risk Assessment Platform</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Login", "Register Company"])
    
    user_manager = UserManager()
    
    with tab1:
        st.subheader("Company Login")
        
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            login_button = st.form_submit_button("Login")
            
            if login_button:
                if username and password:
                    auth_result = user_manager.authenticate_user(username, password)
                    
                    if auth_result['success']:
                        # Store session data
                        st.session_state.session_id = auth_result['session_id']
                        st.session_state.user_id = auth_result['user_id']
                        st.session_state.company_id = auth_result['company_id']
                        st.session_state.company_name = auth_result['company_name']
                        st.session_state.user_role = auth_result['role']
                        st.session_state.onboarding_completed = auth_result['onboarding_completed']
                        st.session_state.authenticated = True
                        
                        st.success(f"Welcome back, {auth_result['full_name']}!")
                        st.rerun()
                    else:
                        st.error(auth_result['message'])
                else:
                    st.error("Please enter both username and password")
    
    with tab2:
        st.subheader("Register New Company")
        
        with st.form("registration_form"):
            company_name = st.text_input("Company Name*")
            contact_email = st.text_input("Contact Email*")
            phone_number = st.text_input("Phone Number")
            address = st.text_area("Address")
            
            st.markdown("**Admin User Account**")
            admin_name = st.text_input("Admin Full Name*")
            admin_username = st.text_input("Admin Username*")
            admin_password = st.text_input("Admin Password*", type="password")
            confirm_password = st.text_input("Confirm Password*", type="password")
            
            register_button = st.form_submit_button("Register Company")
            
            if register_button:
                if all([company_name, contact_email, admin_name, admin_username, admin_password]):
                    if admin_password != confirm_password:
                        st.error("Passwords do not match")
                    else:
                        company_data = {
                            'company_name': company_name,
                            'contact_email': contact_email,
                            'phone_number': phone_number,
                            'address': address,
                            'admin_name': admin_name,
                            'admin_username': admin_username,
                            'admin_password': admin_password
                        }
                        
                        result = user_manager.register_company(company_data)
                        
                        if result['success']:
                            st.success(f"Company registered successfully! Company ID: {result['company_id']}")
                            st.info("Please login with your admin credentials to complete setup.")
                        else:
                            st.error(result['message'])
                else:
                    st.error("Please fill in all required fields marked with *")

def check_authentication():
    """Check if user is authenticated and return session data"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        return False
    
    # Validate session if exists
    if 'session_id' in st.session_state:
        user_manager = UserManager()
        session_data = user_manager.validate_session(st.session_state.session_id)
        
        if session_data['valid']:
            # Update session state with latest data
            st.session_state.onboarding_completed = session_data['onboarding_completed']
            return True
        else:
            # Invalid session, clear and redirect to login
            clear_session()
            return False
    
    return False

def clear_session():
    """Clear session data"""
    for key in ['authenticated', 'session_id', 'user_id', 'company_id', 'company_name', 'user_role', 'onboarding_completed']:
        if key in st.session_state:
            del st.session_state[key]

def logout_user():
    """Logout current user"""
    if 'session_id' in st.session_state:
        user_manager = UserManager()
        user_manager.logout_user(st.session_state.session_id)
    
    clear_session()
    st.rerun()

def show_onboarding_required():
    """Check if onboarding is required for this company"""
    return not st.session_state.get('onboarding_completed', False)

def complete_onboarding_process(preferences: Dict[str, Any]):
    """Complete onboarding process"""
    user_manager = UserManager()
    user_manager.complete_onboarding(st.session_state.company_id, preferences)
    st.session_state.onboarding_completed = True