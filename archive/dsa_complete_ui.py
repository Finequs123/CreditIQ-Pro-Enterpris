"""
Complete DSA Field Scoring Interface - Full Rebuild
Shows only mapped fields with custom names and full scoring functionality
"""

import streamlit as st
import sqlite3
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

class DSAScoringEngine:
    """Complete DSA scoring engine with field mapping support"""
    
    def __init__(self):
        self.db_path = "field_mappings.db"
        self.scoring_weights = {
            "credit_score": 0.25,
            "monthly_income": 0.20,
            "foir": 0.15,
            "enquiry_count": 0.10,
            "dpd_30_plus": 0.10,
            "job_stability": 0.08,
            "loan_mix": 0.05,
            "completion_ratio": 0.04,
            "account_vintage": 0.03
        }
    
    def get_dsa_mappings(self) -> Dict[str, str]:
        """Get all available DSA mappings"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT dsa_id, dsa_name FROM field_mappings WHERE is_active = 1")
            mappings = cursor.fetchall()
            conn.close()
            if mappings:
                return {f"{name} ({dsa_id})": dsa_id for dsa_id, name in mappings}
            else:
                return {}
        except Exception as e:
            st.error(f"Database error: {str(e)}")
            return {}
    
    def get_field_mapping(self, dsa_id: str) -> Optional[Dict[str, Any]]:
        """Get field mapping for specific DSA"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT dsa_name, mapping_config, created_at, updated_at 
                FROM field_mappings WHERE dsa_id = ? AND is_active = 1
            """, (dsa_id,))
            result = cursor.fetchone()
            conn.close()
            
            if result:
                # result[1] is mapping_config column
                mapping_config = json.loads(result[1]) if result[1] else {}
                return {
                    'dsa_name': result[0],
                    'mapping': mapping_config,
                    'created_at': result[2],
                    'updated_at': result[3]
                }
            return None
        except Exception as e:
            st.error(f"Database error: {str(e)}")
            return None
    
    def calculate_score(self, form_data: Dict[str, Any], field_mapping: Dict[str, str]) -> Dict[str, Any]:
        """Calculate loan score based on form data"""
        score = 0
        details = {}
        
        # Reverse mapping: custom_name -> standard_field
        reverse_mapping = {v: k for k, v in field_mapping.items()}
        
        for custom_name, value in form_data.items():
            standard_field = reverse_mapping.get(custom_name)
            if not standard_field:
                continue
                
            field_score = self._calculate_field_score(standard_field, value)
            weight = self.scoring_weights.get(standard_field, 0.01)
            weighted_score = field_score * weight
            
            score += weighted_score
            details[custom_name] = {
                'value': value,
                'field_score': field_score,
                'weight': weight,
                'weighted_score': weighted_score
            }
        
        # Normalize to 0-850 scale
        final_score = min(850, max(300, int(score * 850)))
        
        # Determine risk bucket
        if final_score >= 750:
            bucket = "Excellent"
            decision = "Auto Approve"
        elif final_score >= 650:
            bucket = "Good"
            decision = "Approve"
        elif final_score >= 550:
            bucket = "Fair"
            decision = "Manual Review"
        else:
            bucket = "Poor"
            decision = "Decline"
        
        return {
            'final_score': final_score,
            'risk_bucket': bucket,
            'decision': decision,
            'field_details': details,
            'total_fields': len(details)
        }
    
    def _calculate_field_score(self, field: str, value: Any) -> float:
        """Calculate individual field score"""
        try:
            if field == "credit_score":
                return min(1.0, max(0.0, (float(value) - 300) / 550))
            elif field == "monthly_income":
                return min(1.0, float(value) / 100000)
            elif field == "foir":
                return max(0.0, 1.0 - (float(value) / 100))
            elif "enquiry" in field:
                return max(0.0, 1.0 - (float(value) / 10))
            elif "dpd" in field:
                return 1.0 if float(value) == 0 else max(0.0, 1.0 - (float(value) / 10))
            elif "completion" in field or "ratio" in field:
                return float(value)
            elif field == "job_stability":
                stability_map = {"excellent": 1.0, "good": 0.8, "average": 0.6, "below_average": 0.4, "poor": 0.2}
                return stability_map.get(str(value).lower(), 0.5)
            elif field == "loan_mix":
                mix_map = {"home": 0.9, "auto": 0.8, "personal": 0.6, "business": 0.7, "education": 0.8}
                return mix_map.get(str(value).lower(), 0.5)
            else:
                return 0.5  # Default neutral score
        except:
            return 0.5

def render_complete_dsa_scoring():
    """Render complete DSA scoring interface"""
    st.header("🎯 DSA Partner Loan Scoring")
    
    # Initialize scoring engine
    engine = DSAScoringEngine()
    
    # Get DSA mappings
    dsa_options = engine.get_dsa_mappings()
    if not dsa_options:
        st.error("❌ No DSA mappings found. Please configure DSA field mappings first.")
        st.info("Go to Field Mapping Management to set up DSA partner configurations.")
        return
    
    # DSA selection
    col1, col2 = st.columns([2, 1])
    with col1:
        selected_dsa_display = st.selectbox(
            "Select DSA Partner",
            options=list(dsa_options.keys()),
            help="Choose the DSA partner for custom field mapping"
        )
    
    with col2:
        st.metric("Available DSAs", len(dsa_options))
    
    dsa_id = dsa_options.get(selected_dsa_display)
    if not dsa_id:
        st.error("Invalid DSA selection")
        return
    
    # Get field mapping
    mapping_data = engine.get_field_mapping(dsa_id)
    if not mapping_data:
        st.error(f"❌ No field mapping found for {selected_dsa_display}")
        return
    
    field_mapping = mapping_data.get('mapping', {})
    if not field_mapping:
        st.error("❌ No field mappings configured for this DSA")
        return
    
    # Display mapping info
    st.success(f"✅ Loaded {len(field_mapping)} custom fields for {mapping_data['dsa_name']}")
    
    with st.expander("📋 Field Mapping Details", expanded=False):
        st.write(f"**DSA Partner:** {mapping_data['dsa_name']}")
        st.write(f"**Last Updated:** {mapping_data['updated_at']}")
        st.write("**Custom Field Mappings:**")
        for custom_name, standard_field in field_mapping.items():
            st.write(f"• **{custom_name}** → `{standard_field}`")
    
    # Create application form
    st.subheader("📝 Application Data Entry")
    
    with st.form("dsa_scoring_form"):
        form_data = {}
        
        # Create columns for better layout
        col1, col2 = st.columns(2)
        
        field_count = 0
        for custom_name, standard_field in field_mapping.items():
            target_col = col1 if field_count % 2 == 0 else col2
            
            with target_col:
                # Render appropriate input based on field type
                if standard_field == "credit_score":
                    form_data[custom_name] = st.number_input(
                        f"🎯 {custom_name}",
                        min_value=300,
                        max_value=900,
                        value=650,
                        help="Credit score (300-900)"
                    )
                elif standard_field == "monthly_income":
                    form_data[custom_name] = st.number_input(
                        f"💰 {custom_name}",
                        min_value=0,
                        value=50000,
                        help="Monthly income in currency"
                    )
                elif "enquiry" in standard_field.lower():
                    form_data[custom_name] = st.number_input(
                        f"🔍 {custom_name}",
                        min_value=0,
                        max_value=20,
                        value=3,
                        help="Number of credit enquiries"
                    )
                elif "foir" in custom_name.lower() or "dsr" in custom_name.lower():
                    form_data[custom_name] = st.number_input(
                        f"📊 {custom_name}",
                        min_value=0.0,
                        max_value=100.0,
                        value=35.0,
                        format="%.2f",
                        help="Debt service ratio as percentage"
                    )
                elif "loan" in custom_name.lower() and ("type" in custom_name.lower() or "mix" in standard_field.lower()):
                    form_data[custom_name] = st.selectbox(
                        f"🏦 {custom_name}",
                        ["personal", "business", "home", "auto", "education"],
                        help="Type of loan"
                    )
                elif "completion" in custom_name.lower() or "ratio" in custom_name.lower():
                    form_data[custom_name] = st.number_input(
                        f"✅ {custom_name}",
                        min_value=0.0,
                        max_value=1.0,
                        value=0.8,
                        format="%.2f",
                        help="Completion ratio (0-1)"
                    )
                elif "dpd" in standard_field.lower() or "defaulted" in custom_name.lower():
                    form_data[custom_name] = st.number_input(
                        f"⚠️ {custom_name}",
                        min_value=0,
                        max_value=10,
                        value=0,
                        help="Days past due count"
                    )
                elif "job" in custom_name.lower() or "stability" in custom_name.lower():
                    form_data[custom_name] = st.selectbox(
                        f"👔 {custom_name}",
                        ["excellent", "good", "average", "below_average", "poor"],
                        help="Job stability rating"
                    )
                elif "vintage" in custom_name.lower():
                    form_data[custom_name] = st.number_input(
                        f"📅 {custom_name}",
                        min_value=0,
                        value=36,
                        help="Account vintage in months"
                    )
                elif "balance" in custom_name.lower():
                    form_data[custom_name] = st.number_input(
                        f"💳 {custom_name}",
                        min_value=0,
                        value=25000,
                        help="Account balance"
                    )
                elif "outstanding" in custom_name.lower():
                    form_data[custom_name] = st.number_input(
                        f"🔴 {custom_name}",
                        min_value=0.0,
                        max_value=100.0,
                        value=65.0,
                        format="%.2f",
                        help="Outstanding percentage"
                    )
                elif "unsecured" in custom_name.lower():
                    form_data[custom_name] = st.number_input(
                        f"💸 {custom_name}",
                        min_value=0,
                        value=200000,
                        help="Unsecured debt amount"
                    )
                else:
                    form_data[custom_name] = st.text_input(
                        f"📝 {custom_name}",
                        value="",
                        help=f"Enter value for {custom_name}"
                    )
            
            field_count += 1
        
        # Submit button
        submitted = st.form_submit_button(
            "🎯 Calculate Loan Score",
            type="primary",
            use_container_width=True
        )
    
    # Process submission
    if submitted:
        st.markdown("---")
        
        # Calculate score
        result = engine.calculate_score(form_data, field_mapping)
        
        # Display results
        st.subheader("📊 Scoring Results")
        
        # Main metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Credit Score", result['final_score'])
        with col2:
            st.metric("Risk Bucket", result['risk_bucket'])
        with col3:
            st.metric("Decision", result['decision'])
        with col4:
            st.metric("Fields Processed", result['total_fields'])
        
        # Score visualization
        if result['final_score'] >= 750:
            score_color = "green"
        elif result['final_score'] >= 650:
            score_color = "blue"
        elif result['final_score'] >= 550:
            score_color = "orange"
        else:
            score_color = "red"
        
        st.markdown(f"""
        <div style="background-color: {score_color}; color: white; padding: 20px; border-radius: 10px; text-align: center; margin: 20px 0;">
            <h2>Final Score: {result['final_score']}</h2>
            <h3>Risk Level: {result['risk_bucket']}</h3>
            <h4>Recommendation: {result['decision']}</h4>
        </div>
        """, unsafe_allow_html=True)
        
        # Detailed breakdown
        with st.expander("📋 Detailed Score Breakdown", expanded=True):
            for custom_name, details in result['field_details'].items():
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.write(f"**{custom_name}**")
                with col2:
                    st.write(f"Value: {details['value']}")
                with col3:
                    st.write(f"Score: {details['field_score']:.2f}")
                with col4:
                    st.write(f"Weighted: {details['weighted_score']:.2f}")
        
        # Application summary
        with st.expander("📄 Application Summary", expanded=False):
            st.write(f"**DSA Partner:** {mapping_data['dsa_name']}")
            st.write(f"**Processing Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            st.write("**Submitted Data:**")
            for custom_name, value in form_data.items():
                st.write(f"• **{custom_name}:** {value}")

if __name__ == "__main__":
    render_complete_dsa_scoring()