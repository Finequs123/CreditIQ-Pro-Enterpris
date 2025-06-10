"""
Quick Preferences Update Interface
Allows users to update key settings without going through full onboarding
"""

import streamlit as st
from typing import Dict, Any

def render_quick_preferences_update():
    """Render quick preferences update modal"""
    
    user_profile = st.session_state.get('user_profile', {})
    
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0;">
        <h2 style="color: #1f77b4; margin-bottom: 1rem;">
            ⚙️ Update Your Preferences
        </h2>
        <p style="color: #666;">Make quick changes to your settings</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick settings form
    with st.form("preferences_update"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Institution Details")
            
            company_name = st.text_input(
                "Company Name",
                value=user_profile.get('company_name', ''),
                help="Your institution name"
            )
            
            institution_type = st.selectbox(
                "Institution Type",
                ["NBFC", "Bank", "Fintech", "DSA/Agent", "Microfinance Institution", "Housing Finance Company", "Gold Loan Company"],
                index=["NBFC", "Bank", "Fintech", "DSA/Agent", "Microfinance Institution", "Housing Finance Company", "Gold Loan Company"].index(user_profile.get('institution_type', 'NBFC'))
            )
            
            primary_location = st.selectbox(
                "Primary Location",
                ["Pan India", "Metro Cities", "Tier 1 Cities", "Tier 2 Cities", "Tier 3 Cities", "Rural Areas"],
                index=["Pan India", "Metro Cities", "Tier 1 Cities", "Tier 2 Cities", "Tier 3 Cities", "Rural Areas"].index(user_profile.get('primary_location', 'Pan India'))
            )
        
        with col2:
            st.subheader("Scorecard Settings")
            
            selected_approach = st.selectbox(
                "Scorecard Approach",
                ["standard", "hybrid", "custom"],
                format_func=lambda x: {
                    "standard": "Standard Scorecard",
                    "hybrid": "Hybrid Approach", 
                    "custom": "Custom Build"
                }[x],
                index=["standard", "hybrid", "custom"].index(user_profile.get('selected_approach', 'hybrid'))
            )
            
            risk_appetite = st.selectbox(
                "Risk Appetite",
                ["Conservative", "Moderate", "Aggressive", "Balanced"],
                index=["Conservative", "Moderate", "Aggressive", "Balanced"].index(user_profile.get('risk_appetite', 'Moderate'))
            )
            
            approval_target = st.slider(
                "Target Approval Rate (%)",
                min_value=10, max_value=90, 
                value=user_profile.get('approval_target', 65),
                step=5
            )
        
        # Action buttons
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.form_submit_button("💾 Update Settings", type="primary", use_container_width=True):
                # Update user profile
                updated_profile = user_profile.copy()
                updated_profile.update({
                    'company_name': company_name,
                    'institution_type': institution_type,
                    'primary_location': primary_location,
                    'selected_approach': selected_approach,
                    'risk_appetite': risk_appetite,
                    'approval_target': approval_target
                })
                
                st.session_state.user_profile = updated_profile
                st.session_state.preferences_update_mode = False
                st.success("Preferences updated successfully!")
                st.rerun()
        
        with col2:
            if st.form_submit_button("🔄 Full Setup", use_container_width=True):
                # Check if this is for a new company
                company_name = st.session_state.get('company_name', '')
                if company_name == "New Company":
                    # Start with company registration for new companies
                    st.session_state.show_company_registration = True
                    st.session_state.preferences_update_mode = False
                    # Clear any existing onboarding data
                    if 'onboarding_data' in st.session_state:
                        del st.session_state.onboarding_data
                    if 'user_profile' in st.session_state:
                        del st.session_state.user_profile
                    if 'onboarding_completed' in st.session_state:
                        del st.session_state.onboarding_completed
                    if 'onboarding_step' in st.session_state:
                        del st.session_state.onboarding_step
                else:
                    # Go to full onboarding for existing companies
                    st.session_state.onboarding_completed = False
                    st.session_state.preferences_update_mode = False
                    st.session_state.force_onboarding = True
                    # Clear all onboarding data to start fresh
                    if 'onboarding_step' in st.session_state:
                        del st.session_state.onboarding_step
                    if 'onboarding_data' in st.session_state:
                        del st.session_state.onboarding_data
                    if 'user_profile' in st.session_state:
                        # Keep basic company info but clear preferences
                        company_name = st.session_state.user_profile.get('company_name', '')
                        st.session_state.user_profile = {'company_name': company_name} if company_name else {}
                st.rerun()
        
        with col3:
            if st.form_submit_button("❌ Cancel", use_container_width=True):
                # Return to main app
                st.session_state.preferences_update_mode = False
                st.rerun()
    
    # Show current settings summary
    if user_profile:
        st.markdown("---")
        st.subheader("Current Settings Summary")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Institution", user_profile.get('institution_type', 'Not set'))
            st.metric("Approach", user_profile.get('selected_approach', 'Not set').title())
        
        with col2:
            st.metric("Risk Appetite", user_profile.get('risk_appetite', 'Not set'))
            st.metric("Target Approval", f"{user_profile.get('approval_target', 0)}%")
        
        with col3:
            products = user_profile.get('selected_products', [])
            st.metric("Products", f"{len(products)} selected" if products else "Not set")
            st.metric("Primary Product", user_profile.get('primary_product', 'Not set'))

def render_preferences_button():
    """Render the preferences update button in sidebar"""
    user_profile = st.session_state.get('user_profile', {})
    
    if user_profile:
        st.sidebar.markdown("### 🏢 Institution Profile")
        
        # Show compact profile info
        with st.sidebar.container():
            st.info(f"""
            **{user_profile.get('company_name', 'Your Company')}**
            {user_profile.get('institution_type', 'Institution')}
            
            Approach: {user_profile.get('selected_approach', 'hybrid').title()}
            Risk: {user_profile.get('risk_appetite', 'Moderate')}
            """)
        
        if st.sidebar.button("⚙️ Update", use_container_width=True, help="Quick settings update"):
            st.session_state.preferences_update_mode = True
            st.rerun()
        
        return True
    
    return False