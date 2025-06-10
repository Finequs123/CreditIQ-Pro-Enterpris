"""
Enhanced UI for Modular Scoring Engine with Dynamic Field Mapping
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any, List
from modular_scoring_engine import ModularScoringEngine
from field_mapping_manager import FieldMappingManager, get_dsa_mapping_options
import json

def render_modular_individual_scoring():
    """Render individual scoring with modular engine and dynamic field mapping"""
    st.header("🎯 Individual Application Scoring (Modular Engine)")
    
    # Initialize engines
    modular_engine = ModularScoringEngine()
    mapping_manager = FieldMappingManager()
    
    # DSA Selection
    col1, col2 = st.columns(2)
    with col1:
        use_dsa_mapping = st.checkbox("Use DSA Field Mapping")
    
    dsa_id = None
    field_mapping = {}
    
    if use_dsa_mapping:
        with col2:
            dsa_options = get_dsa_mapping_options()
            if dsa_options:
                selected_dsa = st.selectbox("Select DSA Partner", options=list(dsa_options.keys()))
                dsa_id = dsa_options.get(selected_dsa)
                
                # Get the field mapping for this DSA
                if dsa_id:
                    mapping_data = mapping_manager.get_mapping(dsa_id)
                    if mapping_data:
                        field_mapping = json.loads(mapping_data.get('field_mapping', '{}'))
                        
                        # Show mapping info
                        with st.expander(f"Field Mappings for {selected_dsa}", expanded=False):
                            st.write(f"**Created:** {mapping_data.get('created_at', 'Unknown')}")
                            st.write(f"**Last Updated:** {mapping_data.get('updated_at', 'Unknown')}")
                            st.write("**Field Mappings:**")
                            if field_mapping:
                                for std_field, custom_field in field_mapping.items():
                                    st.write(f"• {std_field.replace('_', ' ').title()} → {custom_field}")
                                st.success(f"✓ {len(field_mapping)} field mappings loaded successfully")
                            else:
                                st.warning("No field mappings found in data")
                    else:
                        st.warning(f"No field mapping found for {selected_dsa}")
            else:
                st.warning("No DSA mappings configured. Go to Field Mapping Management first.")
                return
    
    # Helper function to get display label
    def get_field_label(standard_field, standard_field_key=None):
        if use_dsa_mapping and field_mapping and standard_field_key in field_mapping:
            return field_mapping[standard_field_key]
        return standard_field
    
    # Application Data Input
    st.subheader("Application Data")
    
    # Core Credit Variables
    with st.expander("Core Credit Variables", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            credit_score = st.number_input(
                get_field_label("Credit Score", "credit_score"), 
                min_value=300, max_value=900, value=650
            )
            foir = st.number_input(
                get_field_label("FOIR (%)", "foir"), 
                min_value=0.0, max_value=100.0, value=35.0
            )
            dpd30plus = st.number_input(
                get_field_label("DPD 30+", "dpd30plus"), 
                min_value=0, max_value=10, value=0
            )
        
        with col2:
            enquiry_count = st.number_input(
                get_field_label("Enquiry Count", "enquiry_count"), 
                min_value=0, max_value=20, value=3
            )
            monthly_income = st.number_input(
                get_field_label("Monthly Income (₹)", "monthly_income"), 
                min_value=0, value=50000
            )
    
    # Employment & Banking
    with st.expander("Employment & Banking Details"):
        col1, col2 = st.columns(2)
        
        with col1:
            job_type = st.selectbox(
                get_field_label("Job Type", "job_type"), 
                ["government", "psu", "mnc", "large_corporate", "mid_size_company", "small_company", "self_employed"]
            )
            employment_tenure = st.number_input(
                get_field_label("Employment Tenure (months)", "company_stability"), 
                min_value=0, value=24
            )
            account_vintage = st.number_input(
                get_field_label("Account Vintage (months)", "account_vintage"), 
                min_value=0, value=36
            )
        
        with col2:
            company_stability = st.selectbox(
                get_field_label("Company Stability", "company_stability"), 
                ["excellent", "good", "average", "below_average", "poor"]
            )
            avg_monthly_balance = st.number_input(
                get_field_label("Avg Monthly Balance (₹)", "avg_monthly_balance"), 
                min_value=0, value=25000
            )
            bounce_frequency = st.number_input(
                get_field_label("Bounce Frequency", "bounce_frequency"), 
                min_value=0, value=1
            )
    
    # Score Button
    if st.button("🎯 Calculate Score", type="primary"):
        # Create application data
        application_data = {
            "credit_score": credit_score,
            "foir": foir,
            "dpd30plus": dpd30plus,
            "enquiry_count": enquiry_count,
            "monthly_income": monthly_income,
            "job_type": job_type,
            "employment_tenure": employment_tenure,
            "account_vintage": account_vintage,
            "company_stability": company_stability,
            "avg_monthly_balance": avg_monthly_balance,
            "bounce_frequency": bounce_frequency
        }
        
        # Score the application
        result = modular_engine.score_application(application_data)
        
        if result.get('status') == 'success':
            st.success("✅ Application scored successfully!")
            
            # Display results
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Final Score", f"{result['result']['final_score']:.0f}")
            
            with col2:
                bucket = result['result']['final_bucket']
                bucket_color = {"Low Risk": "🟢", "Medium Risk": "🟡", "High Risk": "🔴"}.get(bucket, "⚪")
                st.metric("Risk Bucket", f"{bucket_color} {bucket}")
            
            with col3:
                decision = result['result']['decision']
                decision_color = {"APPROVED": "🟢", "REJECTED": "🔴", "REVIEW": "🟡"}.get(decision, "⚪")
                st.metric("Decision", f"{decision_color} {decision}")
            
            # Show detailed breakdown
            if 'detailed_scores' in result['result']:
                st.subheader("📊 Detailed Score Breakdown")
                detailed = result['result']['detailed_scores']
                
                breakdown_data = []
                for category, scores in detailed.items():
                    if isinstance(scores, dict):
                        for variable, score in scores.items():
                            breakdown_data.append({
                                "Category": category.replace('_', ' ').title(),
                                "Variable": variable.replace('_', ' ').title(),
                                "Score": score
                            })
                
                if breakdown_data:
                    df = pd.DataFrame(breakdown_data)
                    st.dataframe(df, use_container_width=True)
        else:
            st.error(f"❌ Scoring failed: {result.get('message', 'Unknown error')}")