"""
DSA Field Scoring - Correctly Working Version
Shows ONLY the 5 mapped fields with their custom names
"""

import streamlit as st
import sqlite3
import json
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

def get_dsa_field_mapping():
    """Get the correct DSA field mapping from database"""
    try:
        conn = sqlite3.connect('field_mappings.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT mapping_config FROM field_mappings 
            WHERE dsa_id = "Finolet01" AND is_active = 1
        ''')
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0]:
            # The mapping is stored as {custom_name: standard_field}
            return json.loads(result[0])
        return None
    except Exception as e:
        st.error(f"Database error: {e}")
        return None

def calculate_dsa_score(form_data):
    """Calculate score using DSA mapped fields"""
    score = 300  # Base score
    
    # Credit Score (30% weight)
    if form_data.get('Cr_Score'):
        credit_component = (form_data['Cr_Score'] - 300) / 600 * 255
        score += credit_component * 0.30
    
    # Monthly Income (13% weight)
    if form_data.get('M_Income'):
        income_component = min(form_data['M_Income'] / 100000, 1) * 255
        score += income_component * 0.13
    
    # DPD30+ (13% weight) - Lower is better
    dpd_component = 255
    if form_data.get('DPD30+', 0) > 0:
        dpd_component = max(0, 255 - (form_data['DPD30+'] * 50))
    score += dpd_component * 0.13
    
    # Loan Mix (28% weight)
    loan_mix_scores = {
        'personal': 200,
        'home': 255,
        'auto': 230,
        'business': 180,
        'credit_card': 150
    }
    if form_data.get('Loan Mix'):
        mix_score = loan_mix_scores.get(form_data['Loan Mix'].lower(), 150)
        score += mix_score * 0.28
    
    # Loan Default Numbers (16% weight) - Lower is better
    default_component = 255
    if form_data.get('Loan Default Nos', 0) > 0:
        default_component = max(0, 255 - (form_data['Loan Default Nos'] * 100))
    score += default_component * 0.16
    
    return int(min(850, max(300, score)))

def get_risk_decision(score):
    """Determine risk decision based on score"""
    if score >= 750:
        return "Auto Approve", "🟢", "#28a745"
    elif score >= 650:
        return "Approve", "🟡", "#ffc107"
    elif score >= 550:
        return "Manual Review", "🟠", "#fd7e14"
    else:
        return "Decline", "🔴", "#dc3545"

def save_dsa_scoring_result(form_data, score, decision):
    """Save DSA scoring result to database"""
    try:
        conn = sqlite3.connect('loan_scoring.db')
        cursor = conn.cursor()
        
        # Create table if not exists
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dsa_scoring_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dsa_id TEXT,
                form_data TEXT,
                score INTEGER,
                decision TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            INSERT INTO dsa_scoring_results (dsa_id, form_data, score, decision)
            VALUES (?, ?, ?, ?)
        ''', ('Finolet01', json.dumps(form_data), score, decision))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error saving result: {e}")
        return False

def render_dsa_field_scoring():
    """Render DSA field scoring interface with only mapped fields"""
    st.title("🎯 DSA Field Scoring")
    st.markdown("Enter loan application data using your custom field names")
    
    # Get field mapping
    field_mapping = get_dsa_field_mapping()
    
    if not field_mapping:
        st.error("❌ No DSA field mappings found. Please configure field mappings first.")
        return
    
    # Show mapping info
    with st.expander("📋 Current Field Mappings", expanded=False):
        st.write("**Your Custom Fields:**")
        for custom_name, standard_field in field_mapping.items():
            st.write(f"• **{custom_name}** → {standard_field.replace('_', ' ').title()}")
    
    # Create form with only mapped fields
    st.subheader("📝 Application Data Entry")
    
    form_data = {}
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Credit Score field
        if 'Cr_Score' in field_mapping:
            form_data['Cr_Score'] = st.number_input(
                "Cr_Score",
                min_value=300,
                max_value=850,
                value=650,
                help="Credit bureau score (300-850)"
            )
        
        # Monthly Income field
        if 'M_Income' in field_mapping:
            form_data['M_Income'] = st.number_input(
                "M_Income (₹)",
                min_value=0,
                max_value=1000000,
                value=50000,
                step=5000,
                help="Monthly income in rupees"
            )
        
        # DPD30+ field
        if 'DPD30+' in field_mapping:
            form_data['DPD30+'] = st.number_input(
                "DPD30+",
                min_value=0,
                max_value=12,
                value=0,
                help="Days past due 30+ in last 12 months"
            )
    
    with col2:
        # Loan Mix field
        if 'Loan Mix' in field_mapping:
            form_data['Loan Mix'] = st.selectbox(
                "Loan Mix",
                options=['Personal', 'Home', 'Auto', 'Business', 'Credit Card'],
                help="Primary loan type"
            )
        
        # Loan Default Numbers field
        if 'Loan Default Nos' in field_mapping:
            form_data['Loan Default Nos'] = st.number_input(
                "Loan Default Nos",
                min_value=0,
                max_value=10,
                value=0,
                help="Number of loan defaults in history"
            )
    
    # Calculate Score Button
    if st.button("🎯 Calculate Loan Score", type="primary", use_container_width=True):
        if all(key in form_data for key in field_mapping.keys()):
            
            # Calculate score
            final_score = calculate_dsa_score(form_data)
            decision, icon, color = get_risk_decision(final_score)
            
            # Display results
            st.success("✅ Scoring completed successfully!")
            
            # Main score display
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col2:
                st.markdown(f"""
                <div style="text-align: center; padding: 20px; border-radius: 10px; 
                           background: linear-gradient(135deg, {color}20, {color}10);">
                    <h1 style="color: {color}; margin: 0;">{final_score}</h1>
                    <h3 style="color: {color}; margin: 5px 0;">{icon} {decision}</h3>
                    <p style="margin: 0; color: #666;">Loan Score</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Score breakdown
            st.subheader("📊 Score Breakdown")
            
            breakdown_data = {
                'Component': ['Credit Score', 'Monthly Income', 'DPD30+', 'Loan Mix', 'Default History'],
                'Weight (%)': [30, 13, 13, 28, 16],
                'Value': [
                    form_data.get('Cr_Score', 0),
                    f"₹{form_data.get('M_Income', 0):,}",
                    form_data.get('DPD30+', 0),
                    form_data.get('Loan Mix', 'N/A'),
                    form_data.get('Loan Default Nos', 0)
                ]
            }
            
            breakdown_df = pd.DataFrame(breakdown_data)
            st.dataframe(breakdown_df, use_container_width=True, hide_index=True)
            
            # Score gauge chart
            fig = go.Figure(go.Indicator(
                mode = "gauge+number+delta",
                value = final_score,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Loan Score"},
                delta = {'reference': 650},
                gauge = {
                    'axis': {'range': [None, 850]},
                    'bar': {'color': color},
                    'steps': [
                        {'range': [300, 550], 'color': "lightgray"},
                        {'range': [550, 650], 'color': "yellow"},
                        {'range': [650, 750], 'color': "lightgreen"},
                        {'range': [750, 850], 'color': "green"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 690
                    }
                }
            ))
            
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            # Save result
            if save_dsa_scoring_result(form_data, final_score, decision):
                st.info("📁 Result saved to database successfully")
            
        else:
            st.error("❌ Please fill in all required fields")

if __name__ == "__main__":
    render_dsa_field_scoring()