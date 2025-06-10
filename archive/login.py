import streamlit as st

def render_login_page():
    """Render professional login page"""
    
    # Custom CSS for login page
    st.markdown("""
    <style>
    .login-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: -1rem;
        padding: 2rem;
    }
    
    .login-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 3rem;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
        width: 100%;
        max-width: 450px;
        text-align: center;
    }
    
    .login-logo {
        font-size: 4rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }
    
    .login-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1a202c;
        margin-bottom: 0.5rem;
    }
    
    .login-subtitle {
        color: #64748b;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    
    .login-form {
        margin: 2rem 0;
    }
    
    .input-group {
        margin-bottom: 1.5rem;
        text-align: left;
    }
    
    .input-label {
        display: block;
        font-weight: 600;
        color: #374151;
        margin-bottom: 0.5rem;
    }
    
    .stTextInput > div > div > input {
        border-radius: 12px;
        border: 2px solid #e5e7eb;
        padding: 0.75rem 1rem;
        font-size: 1rem;
        transition: all 0.3s ease;
        background-color: #f9fafb;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        background-color: white;
    }
    
    .login-button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-size: 1.1rem;
        font-weight: 600;
        width: 100%;
        margin-top: 1rem;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .login-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4);
    }
    
    .login-features {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1rem;
        margin-top: 2rem;
        text-align: left;
    }
    
    .feature-item {
        display: flex;
        align-items: center;
        color: #64748b;
        font-size: 0.9rem;
    }
    
    .feature-icon {
        margin-right: 0.5rem;
        color: #10b981;
    }
    
    .security-badge {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-top: 1rem;
        display: inline-block;
    }
    
    .footer-text {
        color: #9ca3af;
        font-size: 0.8rem;
        margin-top: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Login container
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('''
        <div class="login-card">
            <div class="login-logo">🎯</div>
            <h1 class="login-title">LoanScoreAI</h1>
            <p class="login-subtitle">AI-Driven Credit Risk Assessment Platform</p>
            
            <div class="login-features">
                <div class="feature-item">
                    <span class="feature-icon">✓</span>
                    Advanced Analytics
                </div>
                <div class="feature-item">
                    <span class="feature-icon">✓</span>
                    Real-time Scoring
                </div>
                <div class="feature-item">
                    <span class="feature-icon">✓</span>
                    Bulk Processing
                </div>
                <div class="feature-item">
                    <span class="feature-icon">✓</span>
                    Secure Platform
                </div>
            </div>
            
            <div class="security-badge">
                🔒 Bank-Grade Security
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        # Login form
        with st.form("login_form", clear_on_submit=False):
            st.markdown("### 🔐 Login to Continue")
            
            username = st.text_input("👤 User ID", placeholder="Enter your User ID")
            password = st.text_input("🔑 Password", type="password", placeholder="Enter your password")
            
            login_submitted = st.form_submit_button("🚀 Sign In to LoanScoreAI", type="primary", use_container_width=True)
            
            if login_submitted:
                if username == "Finequs" and password == "Password321#":
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials. Please check your User ID and Password.")
        
        st.markdown('''
        <div class="footer-text">
            Powered by Advanced ML Algorithms | Finequs Financial Solutions<br>
            © 2024 LoanScoreAI. All rights reserved.
        </div>
        ''', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def check_authentication():
    """Check if user is authenticated"""
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    
    return st.session_state.logged_in

def logout():
    """Handle user logout"""
    st.session_state.logged_in = False
    st.session_state.username = None
    st.rerun()