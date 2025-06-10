"""
CreditIQ Pro User Authentication System
Supports Admin and Company-specific user management
"""

import streamlit as st
import sqlite3
import hashlib
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Tuple

class UserAuthSystem:
    """Complete user authentication and company management system"""
    
    def __init__(self, db_path: str = "user_management.db"):
        self.db_path = db_path
        self.init_database()
        self.setup_admin_user()
    
    def init_database(self):
        """Initialize user management database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Admin users table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS admin_users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE
        )
        """)
        
        # Companies table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS companies (
            id TEXT PRIMARY KEY,
            company_name TEXT UNIQUE NOT NULL,
            institution_type TEXT NOT NULL,
            primary_location TEXT,
            created_by TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE,
            FOREIGN KEY (created_by) REFERENCES admin_users (id)
        )
        """)
        
        # Company users table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS company_users (
            id TEXT PRIMARY KEY,
            company_id TEXT NOT NULL,
            username TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT,
            email TEXT,
            role TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE,
            FOREIGN KEY (company_id) REFERENCES companies (id),
            UNIQUE(company_id, username)
        )
        """)
        
        # User sessions table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_sessions (
            session_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            user_type TEXT NOT NULL,
            company_id TEXT,
            login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE
        )
        """)
        
        conn.commit()
        conn.close()
    
    def setup_admin_user(self):
        """Setup default admin user"""
        admin_username = "Finequsadmin"
        admin_password = "Password321#"
        
        if not self.admin_exists(admin_username):
            self.create_admin_user(admin_username, admin_password)
    
    def hash_password(self, password: str) -> str:
        """Hash password with salt"""
        salt = "creditiq_pro_salt_2025"
        return hashlib.sha256((password + salt).encode()).hexdigest()
    
    def admin_exists(self, username: str) -> bool:
        """Check if admin user exists"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM admin_users WHERE username = ?", (username,))
        exists = cursor.fetchone()[0] > 0
        conn.close()
        return exists
    
    def create_admin_user(self, username: str, password: str) -> str:
        """Create admin user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        admin_id = str(uuid.uuid4())
        password_hash = self.hash_password(password)
        
        cursor.execute("""
        INSERT INTO admin_users (id, username, password_hash)
        VALUES (?, ?, ?)
        """, (admin_id, username, password_hash))
        
        conn.commit()
        conn.close()
        return admin_id
    
    def authenticate_admin(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate admin user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        password_hash = self.hash_password(password)
        cursor.execute("""
        SELECT id, username FROM admin_users 
        WHERE username = ? AND password_hash = ? AND is_active = TRUE
        """, (username, password_hash))
        
        result = cursor.fetchone()
        
        if result:
            admin_id, username = result
            # Update last login
            cursor.execute("""
            UPDATE admin_users SET last_login = CURRENT_TIMESTAMP 
            WHERE id = ?
            """, (admin_id,))
            conn.commit()
            
            conn.close()
            return {
                'id': admin_id,
                'username': username,
                'type': 'admin'
            }
        
        conn.close()
        return None
    
    def create_company(self, company_data: Dict, admin_id: str) -> str:
        """Create new company"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        company_id = str(uuid.uuid4())
        
        cursor.execute("""
        INSERT INTO companies (id, company_name, institution_type, primary_location, created_by)
        VALUES (?, ?, ?, ?, ?)
        """, (
            company_id,
            company_data['company_name'],
            company_data['institution_type'],
            company_data.get('primary_location', ''),
            admin_id
        ))
        
        conn.commit()
        conn.close()
        return company_id
    
    def create_company_user(self, company_id: str, user_data: Dict) -> str:
        """Create company user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        password_hash = self.hash_password(user_data['password'])
        
        cursor.execute("""
        INSERT INTO users (username, password_hash, company_id, is_active, created_date)
        VALUES (?, ?, ?, ?, ?)
        """, (
            user_data['username'],
            password_hash,
            company_id,
            True,
            datetime.now().isoformat()
        ))
        
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return str(user_id)
    
    def authenticate_company_user(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate company user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        password_hash = self.hash_password(password)
        cursor.execute("""
        SELECT u.id, u.username, u.company_id, c.company_name
        FROM users u
        JOIN companies c ON u.company_id = c.id
        WHERE u.username = ? AND u.password_hash = ? AND u.is_active = 1 AND c.is_active = 1
        """, (username, password_hash))
        
        result = cursor.fetchone()
        
        if result:
            user_id, username, company_id, company_name = result
            conn.close()
            return {
                'id': user_id,
                'username': username,
                'company_id': company_id,
                'company_name': company_name,
                'type': 'company_user'
            }
        
        conn.close()
        return None
    
    def get_all_companies(self) -> List[Dict]:
        """Get all active companies"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
        SELECT id, company_name, institution_type, created_at
        FROM companies 
        WHERE is_active = TRUE
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
    
    def get_company_by_id(self, company_id: str) -> Optional[Dict]:
        """Get company details by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
        SELECT id, company_name, institution_type, primary_location
        FROM companies 
        WHERE id = ? AND is_active = TRUE
        """, (company_id,))
        
        result = cursor.fetchone()
        
        if result:
            conn.close()
            return {
                'id': result[0],
                'company_name': result[1],
                'institution_type': result[2],
                'primary_location': result[3]
            }
        
        conn.close()
        return None

def render_login_screen():
    """Render secure login screen"""
    st.markdown("""
    <div style="text-align: center; padding: 3rem 0 2rem 0;">
        <h1 style="color: #1e293b; font-size: 3rem; font-weight: 700; margin-bottom: 0.5rem;">
            🔐 Secure Access Portal
        </h1>
        <p style="color: #64748b; font-size: 1.2rem;">CreditIQ Pro Authentication System</p>
    </div>
    """, unsafe_allow_html=True)
    
    auth_system = UserAuthSystem()
    
    # Login form
    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            with st.form("login_form", clear_on_submit=False):
                st.markdown("### 👤 User Authentication")
                
                username = st.text_input(
                    "👤 User ID",
                    placeholder="Enter your username",
                    help="Admin: Finequsadmin | Company User: Your assigned username"
                )
                
                password = st.text_input(
                    "🔑 Password",
                    type="password",
                    placeholder="Enter your password",
                    help="Enter your secure password"
                )
                
                login_button = st.form_submit_button(
                    "🚀 Access CreditIQ Pro",
                    type="primary",
                    use_container_width=True
                )
                
                if login_button:
                    if username and password:
                        # Try admin authentication first
                        admin_user = auth_system.authenticate_admin(username, password)
                        
                        if admin_user:
                            st.session_state.authenticated_user = admin_user
                            st.session_state.user_type = 'admin'
                            st.success(f"Welcome, Admin {username}!")
                            st.rerun()
                        else:
                            # Try company user authentication
                            company_user = auth_system.authenticate_company_user(username, password)
                            
                            if company_user:
                                st.session_state.authenticated_user = company_user
                                st.session_state.user_type = 'company_user'
                                st.session_state.company_name = company_user['company_name']
                                st.session_state.user_profile = {
                                    'company_name': company_user['company_name'],
                                    'institution_type': company_user['institution_type']
                                }
                                st.session_state.onboarding_completed = True
                                st.success(f"Welcome to {company_user['company_name']}, {company_user['full_name'] or username}!")
                                st.rerun()
                            else:
                                st.error("❌ Invalid username or password. Please try again.")
                    else:
                        st.warning("⚠️ Please enter both username and password.")
    
    # Company selection for admin after login
    if st.session_state.get('user_type') == 'admin' and not st.session_state.get('selected_company_for_admin'):
        st.markdown("---")
        render_admin_company_selection()

def render_admin_company_selection():
    """Render company selection for admin users"""
    st.markdown("### 🏢 Select Company")
    st.info("📋 As an admin, you can create new companies or select existing ones to manage.")
    
    auth_system = UserAuthSystem()
    companies = auth_system.get_all_companies()
    
    # Add "New Company" option
    company_options = ["➕ Create New Company"] + [f"{comp['company_name']} ({comp['institution_type']})" for comp in companies]
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        selected_option = st.selectbox(
            "Choose your company:",
            company_options,
            help="Select an existing company or create a new one"
        )
    
    with col2:
        if st.button("🎯 Access", type="primary", use_container_width=True):
            if selected_option == "➕ Create New Company":
                st.session_state.company_name = "New Company"
                st.session_state.force_onboarding = True
                st.session_state.creating_new_company = True
                # Clear any existing data for new company creation
                if 'onboarding_data' in st.session_state:
                    del st.session_state.onboarding_data
                if 'user_profile' in st.session_state:
                    del st.session_state.user_profile
                if 'onboarding_completed' in st.session_state:
                    del st.session_state.onboarding_completed
                st.session_state.selected_company_for_admin = True
                st.rerun()
            else:
                # Find selected company
                company_name = selected_option.split(" (")[0]
                for comp in companies:
                    if comp['company_name'] == company_name:
                        st.session_state.company_name = comp['company_name']
                        st.session_state.selected_company_id = comp['id']
                        st.session_state.user_profile = {
                            'company_name': comp['company_name'],
                            'institution_type': comp['institution_type']
                        }
                        st.session_state.onboarding_completed = True
                        st.session_state.selected_company_for_admin = True
                        st.success(f"✅ Accessing {comp['company_name']}")
                        st.rerun()
                        break

def render_logout_button():
    """Render logout button in sidebar"""
    if st.session_state.get('authenticated_user'):
        st.sidebar.markdown("---")
        user = st.session_state.authenticated_user
        
        if user['type'] == 'admin':
            st.sidebar.success(f"👨‍💼 Admin: {user['username']}")
        else:
            st.sidebar.success(f"👤 {user['full_name'] or user['username']}")
            st.sidebar.info(f"🏢 {user['company_name']}")
        
        if st.sidebar.button("🚪 Logout", type="secondary", use_container_width=True):
            # Clear all session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

def is_authenticated() -> bool:
    """Check if user is authenticated"""
    return bool(st.session_state.get('authenticated_user'))

def get_current_user() -> Optional[Dict]:
    """Get current authenticated user"""
    return st.session_state.get('authenticated_user')

def is_admin() -> bool:
    """Check if current user is admin"""
    user = get_current_user()
    return user and user.get('type') == 'admin'