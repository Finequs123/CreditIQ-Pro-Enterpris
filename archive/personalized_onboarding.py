"""
Personalized Onboarding Experience for CreditIQ Pro
Collects user details to customize scorecard configuration based on their business needs
"""

import streamlit as st
import json
from typing import Dict, Any, List
from datetime import datetime

class PersonalizedOnboarding:
    """Handles personalized onboarding for different types of financial institutions"""
    
    def __init__(self):
        self.loan_types = {
            "Personal Loan": {
                "variables": ["credit_score", "monthly_income", "foir", "employment_tenure", "banking_relationship"],
                "weight_profile": "unsecured_focused"
            },
            "Home Loan": {
                "variables": ["credit_score", "monthly_income", "property_value", "ltv_ratio", "employment_stability"],
                "weight_profile": "secured_focused"
            },
            "Loan Against Property": {
                "variables": ["property_value", "ltv_ratio", "rental_income", "credit_score", "business_stability"],
                "weight_profile": "asset_backed"
            },
            "Gold Loan": {
                "variables": ["gold_purity", "gold_weight", "ltv_ratio", "repayment_capacity"],
                "weight_profile": "commodity_backed"
            },
            "Business Loan": {
                "variables": ["business_vintage", "turnover", "profit_margins", "gst_compliance", "banking_turnover"],
                "weight_profile": "business_focused"
            },
            "Vehicle Loan": {
                "variables": ["vehicle_value", "down_payment", "monthly_income", "credit_score", "insurance_status"],
                "weight_profile": "auto_finance"
            },
            "Education Loan": {
                "variables": ["course_fee", "institution_ranking", "co_applicant_income", "collateral_value"],
                "weight_profile": "education_focused"
            },
            "Credit Card": {
                "variables": ["monthly_income", "credit_score", "existing_cards", "spending_pattern"],
                "weight_profile": "revolving_credit"
            }
        }
        
        self.institution_types = {
            "NBFC": {
                "focus": "Risk-adjusted pricing and portfolio management",
                "typical_products": ["Personal Loan", "Business Loan", "Vehicle Loan"],
                "data_availability": "moderate_to_high"
            },
            "Bank": {
                "focus": "Regulatory compliance and comprehensive risk assessment",
                "typical_products": ["Home Loan", "Personal Loan", "Credit Card", "Business Loan"],
                "data_availability": "high"
            },
            "Microfinance Institution": {
                "focus": "Financial inclusion and group lending",
                "typical_products": ["Micro Business Loan", "Group Loan"],
                "data_availability": "limited"
            },
            "Fintech": {
                "focus": "Digital lending and instant approvals",
                "typical_products": ["Personal Loan", "Pay Later", "Credit Card"],
                "data_availability": "digital_high"
            },
            "DSA/Agent": {
                "focus": "Lead generation and preliminary assessment",
                "typical_products": ["Personal Loan", "Home Loan", "Business Loan"],
                "data_availability": "variable"
            },
            "Housing Finance Company": {
                "focus": "Property-backed lending",
                "typical_products": ["Home Loan", "Loan Against Property"],
                "data_availability": "property_focused"
            },
            "Gold Loan Company": {
                "focus": "Commodity-backed quick lending",
                "typical_products": ["Gold Loan"],
                "data_availability": "minimal_required"
            }
        }
        
        self.data_categories = {
            "Core Credit Variables": {
                "variables": ["credit_score", "credit_history", "enquiry_count", "credit_utilization"],
                "availability": "High - Usually available from Credit Bureaus",
                "importance": "Critical for all loan types"
            },
            "Income & Employment": {
                "variables": ["monthly_income", "employment_tenure", "job_type", "company_stability"],
                "availability": "High - Standard KYC requirement",
                "importance": "Essential for repayment capacity"
            },
            "Banking Behavior": {
                "variables": ["account_vintage", "avg_monthly_balance", "bounce_frequency", "banking_relationship"],
                "availability": "Medium - Requires bank statement analysis",
                "importance": "Strong predictor of financial discipline"
            },
            "Behavioral Analytics": {
                "variables": ["loan_completion_ratio", "payment_history", "default_history"],
                "availability": "Medium - Internal data or bureau reports",
                "importance": "Excellent for risk prediction"
            },
            "Geographic & Social": {
                "variables": ["address_stability", "geographic_risk", "social_score"],
                "availability": "Low to Medium - Specialized data providers",
                "importance": "Good for portfolio risk management"
            },
            "Digital Footprint": {
                "variables": ["mobile_vintage", "digital_engagement", "app_usage_pattern"],
                "availability": "High for Fintech, Low for traditional",
                "importance": "Emerging predictor for digital lending"
            }
        }

def render_personalized_onboarding():
    """Render the personalized onboarding experience"""
    
    if 'onboarding_completed' in st.session_state and st.session_state.onboarding_completed:
        return True
    
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <h1 style="color: #1f77b4; font-size: 2.5rem; margin-bottom: 1rem;">
            🎯 Welcome to CreditIQ Pro
        </h1>
        <p style="font-size: 1.2rem; color: #666; margin-bottom: 2rem;">
            Let's personalize your credit scoring experience based on your business needs
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    onboarding = PersonalizedOnboarding()
    
    # Progress indicator
    progress_steps = ["Institution Details", "Loan Products", "Data Assessment", "Scorecard Preference"]
    current_step = st.session_state.get('onboarding_step', 0)
    
    # Progress bar
    progress_percentage = (current_step + 1) / len(progress_steps)
    st.progress(progress_percentage)
    
    cols = st.columns(len(progress_steps))
    for i, step in enumerate(progress_steps):
        with cols[i]:
            if i <= current_step:
                st.markdown(f"✅ **{step}**")
            else:
                st.markdown(f"⭕ {step}")
    
    st.markdown("---")
    
    # Step 1: Institution Details
    if current_step == 0:
        render_institution_details(onboarding)
    
    # Step 2: Loan Products
    elif current_step == 1:
        render_loan_products(onboarding)
    
    # Step 3: Data Assessment
    elif current_step == 2:
        render_data_assessment(onboarding)
    
    # Step 4: Scorecard Preference
    elif current_step == 3:
        render_scorecard_preference(onboarding)
    
    return False

def render_institution_details(onboarding):
    """Render institution details collection"""
    
    st.subheader("🏢 Tell us about your institution")
    
    # Check if this is a company user updating preferences (not admin creating new company)
    user_type = st.session_state.get('user_type', '')
    is_company_user = user_type == 'company_user'
    existing_company_name = ''
    
    # For company users, get their existing company name
    if is_company_user:
        try:
            import sqlite3
            conn = sqlite3.connect('user_management.db')
            cursor = conn.cursor()
            username = st.session_state.get('username', '')
            cursor.execute("SELECT c.company_name FROM companies c JOIN users u ON c.id = u.company_id WHERE u.username = ?", (username,))
            result = cursor.fetchone()
            if result:
                existing_company_name = result[0]
            conn.close()
        except:
            pass
    
    col1, col2 = st.columns(2)
    
    with col1:
        institution_type = st.selectbox(
            "What type of financial institution are you?",
            options=list(onboarding.institution_types.keys()),
            help="This helps us understand your typical business model and requirements"
        )
        
        # Company name field - pre-populate and disable for company users
        if is_company_user and existing_company_name:
            company_name = st.text_input(
                "Company/Institution Name",
                value=existing_company_name,
                disabled=True,
                help="Company name cannot be changed. Contact admin to modify company details."
            )
        else:
            company_name = st.text_input(
                "Company/Institution Name",
                placeholder="e.g., ABC Financial Services"
            )
        
        primary_location = st.selectbox(
            "Primary Operating Location",
            ["Pan India", "Metro Cities", "Tier 1 Cities", "Tier 2 Cities", "Tier 3 Cities", "Rural Areas"]
        )
    
    with col2:
        # Show institution-specific information
        if institution_type:
            institution_info = onboarding.institution_types[institution_type]
            
            st.info(f"""
            **Typical Focus:** {institution_info['focus']}
            
            **Common Products:** {', '.join(institution_info['typical_products'])}
            
            **Data Availability:** {institution_info['data_availability'].replace('_', ' ').title()}
            """)
        
        monthly_volume = st.selectbox(
            "Approximate Monthly Application Volume",
            ["< 100", "100 - 500", "500 - 1,000", "1,000 - 5,000", "5,000 - 10,000", "> 10,000"]
        )
        
        current_process = st.selectbox(
            "Current Credit Assessment Process",
            ["Manual Review", "Basic Scorecards", "Advanced Analytics", "AI/ML Models", "No Formal Process"]
        )
    
    # User credential creation section for admin
    user_type = st.session_state.get('user_type')
    # Check if admin AND company_name is "New Company"
    is_admin_creating = (user_type == 'admin' and 
                        st.session_state.get('company_name') == 'New Company')
    user_data_valid = True
    
    if is_admin_creating:
        st.markdown("---")
        st.subheader("👤 Create Company User Account")
        st.write("Create login credentials for this company's users")
        
        user_col1, user_col2 = st.columns([1, 1])
        
        with user_col1:
            user_username = st.text_input(
                "Username",
                placeholder="e.g., fineqususer",
                help="Username for login (must be unique)"
            )
        
        with user_col2:
            user_password = st.text_input(
                "Password",
                type="password",
                placeholder="Create a secure password",
                help="Minimum 8 characters"
            )
        
        # Basic validation
        if user_password and len(user_password) < 8:
            st.warning("⚠️ Password must be at least 8 characters long")
            user_data_valid = False
        
        # Check if both fields are filled (simplified logic)
        if not (user_username and user_password):
            user_data_valid = False
        elif user_password and len(user_password) >= 8:
            user_data_valid = True
        
        # Store user data in session for next step - always store if both fields exist
        if user_username and user_password:
            st.session_state.new_user_data = {
                'username': user_username,
                'password': user_password,
                'role': 'user'
            }
            # Show confirmation when data is stored
            if user_data_valid:
                st.success(f"✅ User account ready: {user_username}")
        else:
            # Clear if incomplete
            if 'new_user_data' in st.session_state:
                del st.session_state.new_user_data
    
    # Navigation
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("❌ Exit Setup", use_container_width=True, help="Return to main application without saving"):
            # Check user type to determine exit behavior
            user_type = st.session_state.get('user_type', 'normal_user')
            
            if user_type == "admin":
                # Admin users: logout completely
                st.session_state.logged_in = False
                st.session_state.username = ""
                st.session_state.user_type = ""
                if 'onboarding_step' in st.session_state:
                    del st.session_state.onboarding_step
                if 'onboarding_data' in st.session_state:
                    del st.session_state.onboarding_data
                st.success("Admin logged out successfully")
                st.rerun()
            else:
                # Normal users: return to landing page
                st.session_state.onboarding_completed = True
                st.session_state.preferences_update_mode = False
                st.session_state.force_onboarding = False
                if 'onboarding_step' in st.session_state:
                    del st.session_state.onboarding_step
                if 'onboarding_data' in st.session_state:
                    del st.session_state.onboarding_data
                # Ensure user has a basic profile to prevent blank screen
                if 'user_profile' not in st.session_state or not st.session_state.user_profile:
                    company_name = st.session_state.get('company_name', 'Default Company')
                    st.session_state.user_profile = {
                        'company_name': company_name,
                        'institution_type': 'NBFC',
                        'selected_approach': 'hybrid'
                    }
                st.rerun()
    
    with col3:
        # For admin, require both company and user data
        next_disabled = not institution_type or not company_name
        if is_admin_creating:
            next_disabled = next_disabled or not user_data_valid
            
        if st.button("Next: Loan Products →", type="primary", disabled=next_disabled, use_container_width=True):
            st.session_state.onboarding_data = {
                'institution_type': institution_type,
                'company_name': company_name,
                'primary_location': primary_location,
                'monthly_volume': monthly_volume,
                'current_process': current_process
            }
            st.session_state.onboarding_step = 1
            st.rerun()

def render_loan_products(onboarding):
    """Render loan products selection"""
    
    st.subheader("💰 What loan products do you offer?")
    
    # Get recommended products based on institution type
    institution_type = st.session_state.onboarding_data['institution_type']
    recommended_products = onboarding.institution_types[institution_type]['typical_products']
    
    st.write(f"**Recommended for {institution_type}:** {', '.join(recommended_products)}")
    
    # Product selection - filter recommended products to only include those that exist in options
    available_options = list(onboarding.loan_types.keys())
    valid_recommendations = [product for product in recommended_products if product in available_options]
    
    selected_products = st.multiselect(
        "Select all loan products you offer or plan to offer:",
        options=available_options,
        default=valid_recommendations,
        help="You can select multiple products. We'll optimize the scorecard for your primary products."
    )
    
    if selected_products:
        primary_product = st.selectbox(
            "Which is your primary/highest volume product?",
            options=selected_products
        )
        
        # Show product-specific insights
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Selected Products Overview:**")
            for product in selected_products[:3]:  # Show first 3
                product_info = onboarding.loan_types[product]
                st.write(f"• **{product}:** {product_info['weight_profile'].replace('_', ' ').title()}")
        
        with col2:
            if primary_product:
                st.write(f"**Key Variables for {primary_product}:**")
                key_vars = onboarding.loan_types[primary_product]['variables']
                for var in key_vars[:5]:  # Show first 5
                    st.write(f"• {var.replace('_', ' ').title()}")
    
    # Navigation
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("← Back"):
            st.session_state.onboarding_step = 0
            st.rerun()
    
    with col3:
        if st.button("Next: Data Assessment →", type="primary", disabled=not selected_products):
            st.session_state.onboarding_data.update({
                'selected_products': selected_products,
                'primary_product': primary_product if selected_products else None
            })
            st.session_state.onboarding_step = 2
            st.rerun()

def render_data_assessment(onboarding):
    """Render data availability assessment"""
    
    st.subheader("📊 Let's assess your data availability")
    
    st.write("Please indicate what data you typically have access to for your applicants:")
    
    data_availability = {}
    
    for category, info in onboarding.data_categories.items():
        with st.expander(f"**{category}** - {info['importance']}", expanded=True):
            
            availability = st.radio(
                f"Data availability for {category}",
                ["Always Available", "Usually Available", "Sometimes Available", "Rarely Available", "Not Available"],
                key=f"availability_{category}",
                horizontal=True
            )
            
            data_availability[category] = availability
            
            st.caption(f"**Typical Variables:** {', '.join(info['variables'])}")
            st.caption(f"**Market Availability:** {info['availability']}")
    
    # Data quality assessment
    st.subheader("📈 Data Quality & Sources")
    
    col1, col2 = st.columns(2)
    
    with col1:
        bureau_access = st.multiselect(
            "Credit Bureau Access",
            ["CIBIL", "Experian", "Equifax", "CRIF High Mark", "None"],
            help="Select all bureaus you have access to"
        )
        
        bank_statement_analysis = st.selectbox(
            "Bank Statement Analysis Capability",
            ["Advanced (12+ months)", "Standard (6 months)", "Basic (3 months)", "Manual Review Only", "None"]
        )
    
    with col2:
        additional_data = st.multiselect(
            "Additional Data Sources",
            ["GST Data", "ITR Data", "Utility Bills", "Telecom Data", "Social Media", "App Usage", "None"],
            help="Select any additional data sources you use"
        )
        
        data_processing = st.selectbox(
            "Current Data Processing",
            ["Automated with APIs", "Semi-automated", "Manual Entry", "Outsourced", "Minimal Processing"]
        )
    
    # Navigation
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("← Back"):
            st.session_state.onboarding_step = 1
            st.rerun()
    
    with col3:
        if st.button("Next: Scorecard Preference →", type="primary"):
            st.session_state.onboarding_data.update({
                'data_availability': data_availability,
                'bureau_access': bureau_access,
                'bank_statement_analysis': bank_statement_analysis,
                'additional_data': additional_data,
                'data_processing': data_processing
            })
            st.session_state.onboarding_step = 3
            st.rerun()

def render_scorecard_preference(onboarding):
    """Render scorecard preference selection"""
    
    st.subheader("🎯 Choose your scorecard approach")
    
    # Analyze user's data to make recommendations
    data = st.session_state.onboarding_data
    
    # Recommendation logic
    high_data_availability = sum(1 for avail in data['data_availability'].values() 
                                if avail in ['Always Available', 'Usually Available']) >= 4
    
    has_bureau_access = data.get('bureau_access') and 'None' not in data['bureau_access']
    
    is_sophisticated = data['current_process'] in ['Advanced Analytics', 'AI/ML Models']
    
    # Show recommendations
    if high_data_availability and has_bureau_access and is_sophisticated:
        recommended = "custom"
    elif high_data_availability and has_bureau_access:
        recommended = "hybrid"
    else:
        recommended = "standard"
    
    st.write("**Based on your responses, here are your options:**")
    
    # Option 1: Standard Scorecard
    with st.container():
        col1, col2 = st.columns([1, 3])
        with col1:
            standard_selected = st.radio("", ["Standard Scorecard"], key="standard_option")
        with col2:
            st.write("**🔧 Standard Scientifically-Designed Scorecard**")
            st.write("✅ Ready to use immediately")
            st.write("✅ Based on industry best practices")
            st.write("✅ Covers 22 key risk variables")
            st.write("✅ Proven performance across loan types")
            if recommended == "standard":
                st.success("**Recommended for you** based on your current data setup")
    
    st.markdown("---")
    
    # Option 2: Hybrid Approach
    with st.container():
        col1, col2 = st.columns([1, 3])
        with col1:
            hybrid_selected = st.radio("", ["Hybrid Approach"], key="hybrid_option")
        with col2:
            st.write("**⚖️ Hybrid Approach (Standard + Customization)**")
            st.write("✅ Start with standard scorecard")
            st.write("✅ Customize weights for your products")
            st.write("✅ Add your specific variables")
            st.write("✅ A/B test improvements")
            if recommended == "hybrid":
                st.success("**Recommended for you** based on your data capabilities")
    
    st.markdown("---")
    
    # Option 3: Custom Build
    with st.container():
        col1, col2 = st.columns([1, 3])
        with col1:
            custom_selected = st.radio("", ["Custom Build"], key="custom_option")
        with col2:
            st.write("**🔨 Build from Scratch (Custom)**")
            st.write("✅ Complete control over variables")
            st.write("✅ Industry-specific customization")
            st.write("✅ Advanced ML optimization")
            st.write("⚠️ Requires significant data and time")
            if recommended == "custom":
                st.success("**Recommended for you** based on your advanced capabilities")
    
    # Get selection
    selected_approach = None
    if 'standard_option' in st.session_state and st.session_state.standard_option:
        selected_approach = "standard"
    elif 'hybrid_option' in st.session_state and st.session_state.hybrid_option:
        selected_approach = "hybrid"
    elif 'custom_option' in st.session_state and st.session_state.custom_option:
        selected_approach = "custom"
    
    # Additional preferences
    if selected_approach:
        st.subheader("📋 Final Preferences")
        
        col1, col2 = st.columns(2)
        
        with col1:
            risk_appetite = st.selectbox(
                "Risk Appetite",
                ["Conservative", "Moderate", "Aggressive", "Balanced"]
            )
            
            approval_target = st.slider(
                "Target Approval Rate (%)",
                min_value=10, max_value=90, value=65, step=5
            )
        
        with col2:
            priority_focus = st.selectbox(
                "Primary Focus",
                ["Minimize Defaults", "Maximize Approvals", "Balanced Risk-Return", "Portfolio Growth"]
            )
            
            update_frequency = st.selectbox(
                "Model Update Frequency",
                ["Real-time", "Weekly", "Monthly", "Quarterly", "As Needed"]
            )
    
    # Navigation & Completion
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("← Back"):
            st.session_state.onboarding_step = 2
            st.rerun()
    
    with col3:
        if st.button("Complete Setup 🚀", type="primary", disabled=not selected_approach):
            # Save complete onboarding data
            st.session_state.onboarding_data.update({
                'selected_approach': selected_approach,
                'risk_appetite': risk_appetite if selected_approach else 'Moderate',
                'approval_target': approval_target if selected_approach else 65,
                'priority_focus': priority_focus if selected_approach else 'Balanced Risk-Return',
                'update_frequency': update_frequency if selected_approach else 'Monthly',
                'completed_at': datetime.now().isoformat()
            })
            
            # Handle admin creating new company
            is_admin_creating = (st.session_state.get('user_type') == 'admin' and 
                               (st.session_state.get('creating_new_company') or 
                                st.session_state.get('company_name') == 'New Company'))
            
            if is_admin_creating:
                # Save company and create user account using backend system
                try:
                    from backend_auth_system import backend_auth
                    
                    # Create company
                    company_data = {
                        'company_name': st.session_state.onboarding_data['company_name'],
                        'institution_type': st.session_state.onboarding_data['institution_type'],
                        'primary_location': st.session_state.onboarding_data.get('primary_location', '')
                    }
                    company_id = backend_auth.create_company(company_data, "admin")
                    
                    # Save onboarding configuration
                    backend_auth.save_onboarding_data(company_id, st.session_state.onboarding_data)
                    
                    # Create company user
                    user_data = st.session_state.get('new_user_data', {})
                    
                    if user_data:
                        user_id = backend_auth.create_company_user(company_id, user_data)
                        
                        st.success(f"""
                        ✅ Company Setup Complete!
                        
                        **Company:** {company_data['company_name']} 
                        **User Account Created:** {user_data['username']}
                        
                        The company user can now log in with:
                        - Username: {user_data['username']}
                        - Password: [As set during creation]
                        """)
                        
                        # Clean up temporary session data
                        if 'creating_new_company' in st.session_state:
                            del st.session_state.creating_new_company
                        if 'new_user_data' in st.session_state:
                            del st.session_state.new_user_data
                    else:
                        st.error("No user data found in session. Please ensure you filled in the username and password fields.")
                            
                except Exception as e:
                    st.error(f"Error creating company: {str(e)}")
                    return
            else:
                # Regular user onboarding completion
                company_name = st.session_state.onboarding_data.get('company_name', '')
                if company_name:
                    try:
                        import sqlite3
                        import json
                        conn = sqlite3.connect('user_management.db')
                        cursor = conn.cursor()
                        
                        # Convert onboarding data to JSON for storage
                        preferences_json = json.dumps(st.session_state.onboarding_data)
                        engine_preference = st.session_state.onboarding_data.get('selected_approach', 'legacy')
                        if engine_preference == 'standard':
                            engine_preference = 'legacy'
                        elif engine_preference == 'advanced':
                            engine_preference = 'modular'
                        
                        # Insert or update company with preferences
                        cursor.execute('''
                            INSERT OR REPLACE INTO companies 
                            (company_name, is_active, registration_date, onboarding_completed, user_preferences, scoring_engine_preference)
                            VALUES (?, 1, ?, 1, ?, ?)
                        ''', (company_name, datetime.now().isoformat(), preferences_json, engine_preference))
                        
                        conn.commit()
                        conn.close()
                    except Exception as e:
                        st.warning(f"Could not save company to database: {e}")
            
            st.session_state.onboarding_completed = True
            st.session_state.user_profile = st.session_state.onboarding_data
            
            # Show completion message and immediately continue
            st.success("Setup completed! Welcome to your personalized CreditIQ Pro experience.")
            
            # Initialize default mode based on their preference
            if selected_approach == "standard":
                st.session_state.selected_mode = "Individual Scoring"
            else:
                st.session_state.selected_mode = "Individual Scoring (Modular)"
            
            # Clear onboarding step to prevent re-showing
            if 'onboarding_step' in st.session_state:
                del st.session_state.onboarding_step
            
            st.rerun()

def get_user_profile():
    """Get the user's profile from onboarding data"""
    return st.session_state.get('user_profile', {})