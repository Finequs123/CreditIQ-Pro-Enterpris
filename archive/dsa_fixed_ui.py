"""
DSA Field Scoring - Final Working Version
Shows ONLY the fields you mapped with their custom names
"""

import streamlit as st
import sqlite3
import json
from typing import Dict, Any

def get_finolet_mapping():
    """Get the exact Finolet mapping from database"""
    try:
        conn = sqlite3.connect('field_mappings.db')
        cursor = conn.cursor()
        cursor.execute("SELECT mapping_config FROM field_mappings WHERE dsa_id = 'Finolet01' AND is_active = 1")
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0]:
            return json.loads(result[0])
        return None
    except:
        return None

def render_dsa_fixed_scoring():
    """Render DSA scoring with ONLY mapped fields"""
    st.header("🎯 DSA Partner Loan Scoring")
    
    # Get the mapping
    field_mapping = get_finolet_mapping()
    
    if not field_mapping:
        st.error("No DSA field mapping found")
        return
    
    st.success(f"✅ Loaded {len(field_mapping)} custom fields for Finolet")
    
    # Show the mapping
    with st.expander("📋 Field Mappings", expanded=False):
        for custom_name, standard_field in field_mapping.items():
            st.write(f"• **{custom_name}** → {standard_field}")
    
    # Create form with ONLY the mapped fields
    st.subheader("📝 Application Data")
    
    with st.form("finolet_scoring"):
        form_data = {}
        
        col1, col2 = st.columns(2)
        field_count = 0
        
        for custom_name, standard_field in field_mapping.items():
            target_col = col1 if field_count % 2 == 0 else col2
            
            with target_col:
                if custom_name == "Cr_Score":
                    form_data[custom_name] = st.number_input(
                        f"🎯 {custom_name}",
                        min_value=300,
                        max_value=900,
                        value=650,
                        help="Credit score"
                    )
                elif custom_name == "DPD30+":
                    form_data[custom_name] = st.number_input(
                        f"⚠️ {custom_name}",
                        min_value=0,
                        max_value=10,
                        value=0,
                        help="Days past due 30+"
                    )
                elif custom_name == "M_Income":
                    form_data[custom_name] = st.number_input(
                        f"💰 {custom_name}",
                        min_value=0,
                        value=50000,
                        help="Monthly income"
                    )
                elif custom_name == "Loan Mix":
                    form_data[custom_name] = st.selectbox(
                        f"🏦 {custom_name}",
                        ["personal", "business", "home", "auto", "education"],
                        help="Type of loan"
                    )
                elif custom_name == "Loan Default Nos":
                    form_data[custom_name] = st.number_input(
                        f"🔴 {custom_name}",
                        min_value=0,
                        max_value=20,
                        value=0,
                        help="Number of defaulted loans"
                    )
                else:
                    form_data[custom_name] = st.text_input(
                        f"📝 {custom_name}",
                        value="",
                        help=f"Enter {custom_name}"
                    )
            
            field_count += 1
        
        # Submit button
        submitted = st.form_submit_button(
            "🎯 Calculate Score",
            type="primary",
            use_container_width=True
        )
    
    if submitted:
        st.markdown("---")
        st.subheader("📊 Scoring Results")
        
        # Calculate simple score
        score = 0
        if form_data.get("Cr_Score"):
            score += (form_data["Cr_Score"] - 300) / 600 * 300
        if form_data.get("M_Income"):
            score += min(form_data["M_Income"] / 100000, 1) * 200
        if form_data.get("DPD30+") == 0:
            score += 150
        if form_data.get("Loan Default Nos") == 0:
            score += 100
        
        final_score = int(min(850, max(300, score + 300)))
        
        # Display results
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Credit Score", final_score)
        with col2:
            bucket = "Excellent" if final_score >= 750 else "Good" if final_score >= 650 else "Fair" if final_score >= 550 else "Poor"
            st.metric("Risk Bucket", bucket)
        with col3:
            decision = "Auto Approve" if final_score >= 750 else "Approve" if final_score >= 650 else "Manual Review" if final_score >= 550 else "Decline"
            st.metric("Decision", decision)
        
        # Show submitted data
        st.subheader("📄 Submitted Data")
        for custom_name, value in form_data.items():
            st.write(f"**{custom_name}:** {value}")

if __name__ == "__main__":
    render_dsa_fixed_scoring()