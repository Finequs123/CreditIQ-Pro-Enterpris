"""
Simplified Additional Data Fields Interface
Replaces hardcoded ITR data with flexible additional data collection
"""

import streamlit as st
from dynamic_additional_weight import DynamicAdditionalWeight
from typing import Dict, Any

class SimplifiedAdditionalFields:
    """Simplified interface for collecting additional data"""
    
    def __init__(self, company_id: int):
        self.company_id = company_id
        self.weight_manager = DynamicAdditionalWeight()
        self.weight_config = self.weight_manager.calculate_dynamic_weight(company_id)
    
    def render_additional_fields(self) -> Dict[str, Any]:
        """Render simplified additional data collection interface"""
        additional_data = {}
        
        if not self.weight_config['has_additional_sources']:
            return additional_data
        
        # Show dynamic weight info
        st.markdown("---")
        st.subheader("📊 Additional Data Sources")
        
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"Selected Sources: {', '.join(self.weight_config['selected_sources'])}")
        with col2:
            st.info(f"Additional Weight: {self.weight_config['additional_weight']:.1f}%")
        
        # Simplified data collection based on selected sources
        st.markdown("### Additional Information")
        st.write("Please provide additional data to enhance scoring accuracy:")
        
        # Create flexible fields based on source types
        for source in self.weight_config['selected_sources']:
            with st.expander(f"{source} Information", expanded=True):
                additional_data.update(self._render_source_fields(source))
        
        return additional_data
    
    def _render_source_fields(self, source_name: str) -> Dict[str, Any]:
        """Render simplified fields for each data source"""
        source_data = {}
        
        if source_name == "ITR Data":
            col1, col2 = st.columns(2)
            with col1:
                source_data['annual_income'] = st.number_input(
                    "Annual Income (₹)", 
                    min_value=0, 
                    value=300000,
                    key=f"itr_income_{self.company_id}"
                )
                source_data['tax_compliance'] = st.selectbox(
                    "Tax Compliance Status",
                    ["Excellent", "Good", "Average", "Below Average"],
                    key=f"itr_compliance_{self.company_id}"
                )
            with col2:
                source_data['income_consistency'] = st.slider(
                    "Income Consistency (0-100)",
                    0, 100, 75,
                    key=f"itr_consistency_{self.company_id}"
                )
                source_data['declared_assets'] = st.number_input(
                    "Declared Assets Value (₹)",
                    min_value=0,
                    value=500000,
                    key=f"itr_assets_{self.company_id}"
                )
        
        elif source_name == "GST Data":
            col1, col2 = st.columns(2)
            with col1:
                source_data['monthly_turnover'] = st.number_input(
                    "Monthly GST Turnover (₹)",
                    min_value=0,
                    value=200000,
                    key=f"gst_turnover_{self.company_id}"
                )
                source_data['gst_compliance'] = st.selectbox(
                    "GST Compliance Rating",
                    ["Excellent", "Good", "Average", "Below Average"],
                    key=f"gst_compliance_{self.company_id}"
                )
            with col2:
                source_data['business_stability'] = st.slider(
                    "Business Stability Score (0-100)",
                    0, 100, 70,
                    key=f"gst_stability_{self.company_id}"
                )
                source_data['payment_behavior'] = st.selectbox(
                    "Payment Behavior",
                    ["Always On Time", "Mostly On Time", "Occasional Delays", "Frequent Delays"],
                    key=f"gst_payment_{self.company_id}"
                )
        
        elif source_name == "Utility Bills":
            col1, col2 = st.columns(2)
            with col1:
                source_data['payment_regularity'] = st.selectbox(
                    "Utility Payment Regularity",
                    ["Always On Time", "Mostly On Time", "Occasional Delays", "Frequent Delays"],
                    key=f"utility_regularity_{self.company_id}"
                )
                source_data['address_stability'] = st.slider(
                    "Address Stability (months)",
                    0, 120, 24,
                    key=f"utility_stability_{self.company_id}"
                )
            with col2:
                source_data['consumption_pattern'] = st.selectbox(
                    "Consumption Pattern",
                    ["Consistent", "Seasonal", "Irregular"],
                    key=f"utility_pattern_{self.company_id}"
                )
                source_data['service_type'] = st.multiselect(
                    "Connected Services",
                    ["Electricity", "Gas", "Water", "Internet", "Cable"],
                    default=["Electricity"],
                    key=f"utility_services_{self.company_id}"
                )
        
        elif source_name == "Telecom Data":
            col1, col2 = st.columns(2)
            with col1:
                source_data['account_vintage'] = st.slider(
                    "Telecom Account Vintage (months)",
                    0, 120, 36,
                    key=f"telecom_vintage_{self.company_id}"
                )
                source_data['payment_behavior'] = st.selectbox(
                    "Payment Behavior",
                    ["Always On Time", "Mostly On Time", "Occasional Delays", "Frequent Delays"],
                    key=f"telecom_payment_{self.company_id}"
                )
            with col2:
                source_data['usage_pattern'] = st.selectbox(
                    "Usage Pattern",
                    ["Heavy User", "Regular User", "Light User"],
                    key=f"telecom_usage_{self.company_id}"
                )
                source_data['plan_type'] = st.selectbox(
                    "Plan Type",
                    ["Postpaid", "Prepaid"],
                    key=f"telecom_plan_{self.company_id}"
                )
        
        elif source_name == "Social Media":
            col1, col2 = st.columns(2)
            with col1:
                source_data['digital_footprint'] = st.slider(
                    "Digital Footprint Score (0-100)",
                    0, 100, 60,
                    key=f"social_footprint_{self.company_id}"
                )
                source_data['network_quality'] = st.selectbox(
                    "Professional Network Quality",
                    ["Excellent", "Good", "Average", "Below Average"],
                    key=f"social_network_{self.company_id}"
                )
            with col2:
                source_data['activity_level'] = st.selectbox(
                    "Social Media Activity",
                    ["Very Active", "Active", "Moderate", "Low"],
                    key=f"social_activity_{self.company_id}"
                )
                source_data['profile_completeness'] = st.slider(
                    "Profile Completeness (%)",
                    0, 100, 80,
                    key=f"social_completeness_{self.company_id}"
                )
        
        elif source_name == "App Usage":
            col1, col2 = st.columns(2)
            with col1:
                source_data['financial_apps'] = st.multiselect(
                    "Financial Apps Used",
                    ["Banking Apps", "Payment Apps", "Investment Apps", "Budget Apps"],
                    default=["Banking Apps"],
                    key=f"app_financial_{self.company_id}"
                )
                source_data['usage_frequency'] = st.selectbox(
                    "App Usage Frequency",
                    ["Daily", "Weekly", "Monthly", "Rarely"],
                    key=f"app_frequency_{self.company_id}"
                )
            with col2:
                source_data['digital_literacy'] = st.slider(
                    "Digital Literacy Score (0-100)",
                    0, 100, 70,
                    key=f"app_literacy_{self.company_id}"
                )
                source_data['transaction_volume'] = st.selectbox(
                    "Digital Transaction Volume",
                    ["High", "Medium", "Low"],
                    key=f"app_volume_{self.company_id}"
                )
        
        return source_data
    
    def display_weight_breakdown(self, score_breakdown: Dict[str, Any]):
        """Display dynamic weight breakdown"""
        if not score_breakdown or score_breakdown.get('additional_score', 0) == 0:
            return
        
        st.subheader("📈 Additional Data Score Breakdown")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Additional Score", f"{score_breakdown['additional_score']:.2f}")
        with col2:
            st.metric("Weight Applied", f"{score_breakdown['additional_weight']:.1f}%")
        with col3:
            st.metric("Sources Used", score_breakdown['breakdown']['sources_count'])
        
        if score_breakdown['breakdown']['selected_sources']:
            st.write("**Sources Contributing:**")
            for source in score_breakdown['breakdown']['selected_sources']:
                st.write(f"• {source}")