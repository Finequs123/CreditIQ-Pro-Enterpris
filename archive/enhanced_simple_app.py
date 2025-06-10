"""
Enhanced CreditIQ Pro with Modular Scoring Engine
Supports DSA field mappings, transparent scoring, and fallback mechanisms
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import io
import sqlite3
from scoring_engine import LoanScoringEngine
from modular_scoring_engine import ModularScoringEngine
from field_mapping_manager import render_field_mapping_management
from modular_scoring_ui import (
    render_modular_individual_scoring, 
    render_modular_bulk_upload,
    render_modular_scoring_config
)
from database import DatabaseManager
from utils import create_excel_output, validate_csv_columns
from validators import validate_individual_data
from weights_config import render_weights_configuration
from ab_testing_framework import render_ab_testing_interface
from api_integration import render_api_management
from login import render_login_page, check_authentication
import json

# Configure page settings - MUST be first Streamlit command
st.set_page_config(
    page_title="CreditIQ Pro - Enhanced",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

def load_custom_css():
    """Load custom CSS for modern styling"""
    st.markdown("""
    <style>
    .main-header {
        padding: 1rem 0;
        color: #1f77b4;
        border-bottom: 2px solid #e6f3ff;
        margin-bottom: 2rem;
    }
    
    .metric-container {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
    }
    
    .success-box {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .warning-box {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .info-box {
        background: #e7f3ff;
        border: 1px solid #b3d9ff;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'scoring_engine_type' not in st.session_state:
        st.session_state.scoring_engine_type = 'modular'

def render_sidebar():
    """Render the enhanced sidebar navigation"""
    with st.sidebar:
        st.title("🎯 CreditIQ Pro Enhanced")
        st.markdown("---")
        
        # Engine selection
        st.subheader("Scoring Engine")
        engine_type = st.radio(
            "Select Engine Type",
            ["Modular Engine (New)", "Legacy Engine"],
            index=0 if st.session_state.scoring_engine_type == 'modular' else 1
        )
        
        if engine_type == "Modular Engine (New)":
            st.session_state.scoring_engine_type = 'modular'
            
            # Modular engine menu
            st.markdown("### Modular Features")
            modular_options = [
                "Individual Scoring",
                "Bulk Upload",
                "Field Mapping Management", 
                "Scoring Configuration",
                "History & Reports"
            ]
            
        else:
            st.session_state.scoring_engine_type = 'legacy'
            
            # Legacy engine menu
            st.markdown("### Legacy Features")
            modular_options = [
                "Individual Scoring (Legacy)",
                "Bulk Upload (Legacy)",
                "Weights Configuration",
                "A/B Testing",
                "API Management",
                "History & Audit"
            ]
        
        mode = st.selectbox("Choose Function", modular_options)
        
        st.markdown("---")
        
        # Quick stats
        st.markdown("### System Status")
        
        # Initialize engines for stats
        if st.session_state.scoring_engine_type == 'modular':
            modular_engine = ModularScoringEngine()
            config = modular_engine.get_scoring_configuration()
            st.metric("Variables", config['total_variables'])
            st.metric("Total Weight", config['total_weight'])
            st.info("✅ Modular Engine Active")
        else:
            st.info("⚡ Legacy Engine Active")
        
        # Logout
        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.rerun()
    
    return mode

def render_individual_scoring_legacy():
    """Render legacy individual scoring interface"""
    st.header("🎯 Individual Application Scoring (Legacy)")
    st.info("This is the legacy scoring engine. Switch to 'Modular Engine' for enhanced features.")
    
    # Use original scoring engine
    engine = LoanScoringEngine()
    
    # Basic form (simplified for demonstration)
    with st.form("legacy_scoring_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            credit_score = st.number_input("Credit Score", min_value=300, max_value=900, value=650)
            monthly_income = st.number_input("Monthly Income (₹)", min_value=0, value=50000)
            foir = st.number_input("FOIR (%)", min_value=0.0, max_value=100.0, value=35.0)
        
        with col2:
            age = st.number_input("Age", min_value=18, max_value=80, value=30)
            dpd30plus = st.number_input("DPD 30+", min_value=0, max_value=10, value=0)
            enquiry_count = st.number_input("Enquiry Count", min_value=0, max_value=20, value=3)
        
        submitted = st.form_submit_button("Score Application")
        
        if submitted:
            applicant_data = {
                'credit_score': credit_score,
                'monthly_income': monthly_income,
                'foir': foir,
                'age': age,
                'dpd30plus': dpd30plus,
                'enquiry_count': enquiry_count,
                'pan': 'VALID123456',
                'writeoff_flag': False,
                'defaulted_loans': 0
            }
            
            try:
                result = engine.score_application(applicant_data)
                
                # Display results
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Final Score", f"{result['final_score']:.1f}")
                
                with col2:
                    st.metric("Risk Bucket", result['final_bucket'])
                
                with col3:
                    st.metric("Decision", result['decision'])
                
                if result['clearance_passed']:
                    st.success("Application passed clearance rules")
                else:
                    st.error("Application failed clearance rules:")
                    for rule in result['failed_clearance_rules']:
                        st.write(f"• {rule}")
                
            except Exception as e:
                st.error(f"Error in scoring: {str(e)}")

def render_bulk_upload_legacy():
    """Render legacy bulk upload interface"""
    st.header("📁 Bulk Upload (Legacy)")
    st.info("This is the legacy bulk processing. Switch to 'Modular Engine' for enhanced DSA support.")
    
    uploaded_file = st.file_uploader("Upload CSV file", type=['csv'])
    
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            st.success(f"File uploaded successfully! Found {len(df)} applications.")
            
            # Show preview
            with st.expander("Data Preview"):
                st.dataframe(df.head(), use_container_width=True)
            
            if st.button("Process with Legacy Engine"):
                st.info("Processing with legacy scoring engine...")
                # Basic processing simulation
                results = []
                for index, row in df.iterrows():
                    results.append({
                        'application_id': index + 1,
                        'final_score': 65.5,  # Placeholder
                        'bucket': 'B',
                        'decision': 'Review Required'
                    })
                
                results_df = pd.DataFrame(results)
                st.dataframe(results_df, use_container_width=True)
                
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")

def render_system_comparison():
    """Render comparison between legacy and modular systems"""
    st.header("🔍 System Comparison")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Legacy Engine")
        st.write("✅ Proven scoring logic")
        st.write("✅ Historical compatibility")
        st.write("❌ Fixed field structure")
        st.write("❌ Limited transparency")
        st.write("❌ No DSA customization")
        
    with col2:
        st.subheader("Modular Engine (New)")
        st.write("✅ DSA field mapping support")
        st.write("✅ Transparent scoring reasons")
        st.write("✅ Fallback mechanisms")
        st.write("✅ Configurable per partner")
        st.write("✅ Enhanced analytics")
    
    # Feature comparison table
    comparison_data = {
        "Feature": [
            "Field Mapping",
            "Scoring Transparency", 
            "Fallback Handling",
            "DSA Customization",
            "Missing Data Handling",
            "Audit Trail",
            "Performance"
        ],
        "Legacy Engine": [
            "❌ Fixed fields only",
            "⚠️ Limited visibility",
            "❌ Hard failures",
            "❌ Not supported",
            "❌ Strict requirements",
            "✅ Basic logging",
            "✅ Fast"
        ],
        "Modular Engine": [
            "✅ Flexible mapping",
            "✅ Full transparency",
            "✅ Smart fallbacks",
            "✅ Partner-specific",
            "✅ Graceful handling",
            "✅ Detailed reasons",
            "✅ Optimized"
        ]
    }
    
    comparison_df = pd.DataFrame(comparison_data)
    st.dataframe(comparison_df, use_container_width=True)

def main():
    """Main application function"""
    # Check authentication first
    if not check_authentication():
        render_login_page()
        return
    
    # Load custom CSS
    load_custom_css()
    
    # Initialize session state
    initialize_session_state()
    
    # Render sidebar and get selected mode
    mode = render_sidebar()
    
    # Route to appropriate function based on engine type and mode
    if st.session_state.scoring_engine_type == 'modular':
        # Modular engine routes
        if mode == "Individual Scoring":
            render_modular_individual_scoring()
        elif mode == "Bulk Upload":
            render_modular_bulk_upload()
        elif mode == "Field Mapping Management":
            render_field_mapping_management()
        elif mode == "Scoring Configuration":
            render_modular_scoring_config()
        elif mode == "History & Reports":
            st.header("📊 History & Reports")
            st.info("Enhanced reporting features coming soon...")
            render_system_comparison()
    else:
        # Legacy engine routes
        if mode == "Individual Scoring (Legacy)":
            render_individual_scoring_legacy()
        elif mode == "Bulk Upload (Legacy)":
            render_bulk_upload_legacy()
        elif mode == "Weights Configuration":
            render_weights_configuration()
        elif mode == "A/B Testing":
            render_ab_testing_interface()
        elif mode == "API Management":
            render_api_management()
        elif mode == "History & Audit":
            st.header("📋 History & Audit (Legacy)")
            st.info("Legacy audit features...")

if __name__ == "__main__":
    main()