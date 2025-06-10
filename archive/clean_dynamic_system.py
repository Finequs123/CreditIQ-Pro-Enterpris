"""
Clean Dynamic Weight System - Complete Implementation
Removes all hardcoded ITR data and implements truly dynamic additional data sources
"""

import streamlit as st
import sqlite3
from typing import Dict, List, Any, Optional

class CleanDynamicSystem:
    """Clean implementation of dynamic additional data weight system"""
    
    def __init__(self, company_id: int):
        self.company_id = company_id
        self.db_path = "user_management.db"
        
    def get_company_additional_sources(self) -> List[str]:
        """Get selected additional data sources for company"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT additional_data_sources FROM companies 
                WHERE id = ?
            """, (self.company_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result and result[0]:
                import json
                sources = json.loads(result[0])
                # Filter out 'None' if present
                return [s for s in sources if s != 'None']
            return []
            
        except Exception as e:
            print(f"Error getting additional sources: {e}")
            return []
    
    def calculate_dynamic_weight(self, selected_sources: List[str]) -> float:
        """Calculate additional weight based on number of selected sources"""
        if not selected_sources:
            return 0.0
        
        # Dynamic weight calculation: 2% per source, max 12%
        base_weight_per_source = 2.0
        max_weight = 12.0
        
        calculated_weight = len(selected_sources) * base_weight_per_source
        return min(calculated_weight, max_weight)
    
    def render_dynamic_additional_fields(self) -> Dict[str, Any]:
        """Render additional data fields based on company's selected sources"""
        selected_sources = self.get_company_additional_sources()
        
        if not selected_sources:
            return {}
        
        additional_weight = self.calculate_dynamic_weight(selected_sources)
        
        # Show information about additional weight
        st.info(f"✨ Enhanced Scorecard: Your organization has {len(selected_sources)} additional data sources selected, adding {additional_weight:.1f}% additional weight to the scoring")
        
        # Create dynamic tabs for each selected source
        if len(selected_sources) == 1:
            # Single source - no tabs needed
            return self._render_source_fields(selected_sources[0])
        else:
            # Multiple sources - use tabs
            tabs = st.tabs([f"📊 {source}" for source in selected_sources])
            all_data = {}
            
            for i, source in enumerate(selected_sources):
                with tabs[i]:
                    source_data = self._render_source_fields(source)
                    all_data.update(source_data)
            
            return all_data
    
    def _render_source_fields(self, source_name: str) -> Dict[str, Any]:
        """Render fields for specific data source"""
        data = {}
        
        if source_name == "GST Data":
            st.subheader("📋 GST Information")
            col1, col2 = st.columns(2)
            
            with col1:
                data[f'gst_turnover_{self.company_id}'] = st.number_input(
                    "GST Annual Turnover (₹)", 
                    min_value=0, 
                    value=1000000, 
                    step=100000,
                    key=f"gst_turnover_{self.company_id}"
                )
                data[f'gst_compliance_{self.company_id}'] = st.selectbox(
                    "GST Compliance Score", 
                    ["Excellent", "Good", "Average", "Poor"],
                    key=f"gst_compliance_{self.company_id}"
                )
            
            with col2:
                data[f'gst_filing_frequency_{self.company_id}'] = st.selectbox(
                    "GST Filing Frequency", 
                    ["Monthly", "Quarterly", "Irregular"],
                    key=f"gst_filing_{self.company_id}"
                )
                data[f'gst_refund_claims_{self.company_id}'] = st.number_input(
                    "GST Refund Claims (₹)", 
                    min_value=0, 
                    value=0,
                    key=f"gst_refund_{self.company_id}"
                )
        
        elif source_name == "ITR Data":
            st.subheader("📄 Income Tax Information")
            col1, col2 = st.columns(2)
            
            with col1:
                data[f'itr_income_{self.company_id}'] = st.number_input(
                    "Annual Income (ITR) (₹)", 
                    min_value=0, 
                    value=600000, 
                    step=50000,
                    key=f"itr_income_{self.company_id}"
                )
                data[f'itr_compliance_{self.company_id}'] = st.selectbox(
                    "Tax Filing Compliance", 
                    ["Always on time", "Occasionally late", "Frequently late", "Non-compliant"],
                    key=f"itr_compliance_{self.company_id}"
                )
            
            with col2:
                data[f'itr_consistency_{self.company_id}'] = st.selectbox(
                    "Income Consistency", 
                    ["Very consistent", "Mostly consistent", "Variable", "Highly variable"],
                    key=f"itr_consistency_{self.company_id}"
                )
                data[f'itr_assets_{self.company_id}'] = st.number_input(
                    "Declared Assets Value (₹)", 
                    min_value=0, 
                    value=0,
                    key=f"itr_assets_{self.company_id}"
                )
        
        elif source_name == "Utility Bills":
            st.subheader("⚡ Utility Bill Analysis")
            col1, col2 = st.columns(2)
            
            with col1:
                data[f'utility_payment_history_{self.company_id}'] = st.selectbox(
                    "Payment History", 
                    ["Always on time", "Occasionally late", "Frequently late"],
                    key=f"utility_payment_{self.company_id}"
                )
                data[f'utility_consumption_{self.company_id}'] = st.selectbox(
                    "Consumption Pattern", 
                    ["Stable", "Increasing", "Decreasing", "Irregular"],
                    key=f"utility_consumption_{self.company_id}"
                )
            
            with col2:
                data[f'utility_address_stability_{self.company_id}'] = st.number_input(
                    "Address Stability (months)", 
                    min_value=0, 
                    max_value=600, 
                    value=24,
                    key=f"utility_address_{self.company_id}"
                )
        
        elif source_name == "Telecom Data":
            st.subheader("📞 Telecom Usage Analysis")
            col1, col2 = st.columns(2)
            
            with col1:
                data[f'telecom_usage_pattern_{self.company_id}'] = st.selectbox(
                    "Usage Pattern", 
                    ["Heavy user", "Moderate user", "Light user"],
                    key=f"telecom_usage_{self.company_id}"
                )
                data[f'telecom_payment_method_{self.company_id}'] = st.selectbox(
                    "Payment Method", 
                    ["Auto-pay", "Online", "Offline"],
                    key=f"telecom_payment_{self.company_id}"
                )
            
            with col2:
                data[f'telecom_plan_stability_{self.company_id}'] = st.selectbox(
                    "Plan Stability", 
                    ["Same plan >1 year", "Same plan 6-12 months", "Frequent changes"],
                    key=f"telecom_plan_{self.company_id}"
                )
        
        elif source_name == "Social Media":
            st.subheader("📱 Social Media Insights")
            col1, col2 = st.columns(2)
            
            with col1:
                data[f'social_activity_level_{self.company_id}'] = st.selectbox(
                    "Activity Level", 
                    ["High", "Medium", "Low"],
                    key=f"social_activity_{self.company_id}"
                )
                data[f'social_network_quality_{self.company_id}'] = st.selectbox(
                    "Network Quality", 
                    ["Professional network", "Mixed network", "Personal only"],
                    key=f"social_network_{self.company_id}"
                )
            
            with col2:
                data[f'social_stability_score_{self.company_id}'] = st.number_input(
                    "Profile Stability Score (0-100)", 
                    min_value=0, 
                    max_value=100, 
                    value=75,
                    key=f"social_stability_{self.company_id}"
                )
        
        elif source_name == "App Usage":
            st.subheader("📲 App Usage Patterns")
            col1, col2 = st.columns(2)
            
            with col1:
                data[f'financial_app_usage_{self.company_id}'] = st.selectbox(
                    "Financial App Usage", 
                    ["Frequent", "Moderate", "Minimal"],
                    key=f"financial_app_{self.company_id}"
                )
                data[f'shopping_app_behavior_{self.company_id}'] = st.selectbox(
                    "Shopping App Behavior", 
                    ["Premium buyer", "Deal seeker", "Occasional buyer"],
                    key=f"shopping_app_{self.company_id}"
                )
            
            with col2:
                data[f'app_diversity_score_{self.company_id}'] = st.number_input(
                    "App Diversity Score (0-100)", 
                    min_value=0, 
                    max_value=100, 
                    value=60,
                    key=f"app_diversity_{self.company_id}"
                )
        
        return data
    
    def calculate_additional_score(self, additional_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate score contribution from additional data"""
        selected_sources = self.get_company_additional_sources()
        
        if not selected_sources or not additional_data:
            return {
                'additional_score': 0,
                'additional_weight_percent': 0,
                'breakdown': {},
                'has_additional_data': False
            }
        
        total_weight = self.calculate_dynamic_weight(selected_sources)
        
        # Simple scoring: normalize and average all additional data points
        scores = []
        breakdown = {}
        
        for key, value in additional_data.items():
            if value is not None:
                if isinstance(value, (int, float)):
                    # Normalize numeric values to 0-1 scale
                    normalized = min(1.0, max(0.0, value / 100))
                    scores.append(normalized)
                elif isinstance(value, str):
                    # Convert categorical values to scores
                    if value in ["Excellent", "Always on time", "Very consistent", "Heavy user", "High", "Professional network"]:
                        scores.append(1.0)
                    elif value in ["Good", "Occasionally late", "Mostly consistent", "Moderate user", "Medium", "Mixed network"]:
                        scores.append(0.7)
                    elif value in ["Average", "Frequently late", "Variable", "Light user", "Low", "Personal only"]:
                        scores.append(0.4)
                    else:
                        scores.append(0.2)
                
                breakdown[key] = scores[-1] if scores else 0
        
        # Calculate final additional score
        if scores:
            avg_score = sum(scores) / len(scores)
            additional_score = (total_weight / 100) * avg_score * 100  # Convert to percentage points
        else:
            additional_score = 0
        
        return {
            'additional_score': additional_score,
            'additional_weight_percent': total_weight,
            'breakdown': breakdown,
            'has_additional_data': True,
            'data_sources': selected_sources,
            'fields_count': len(additional_data)
        }

def render_clean_dynamic_scorecard(company_id: int):
    """Render scorecard with clean dynamic additional data system"""
    if not company_id:
        return {}
    
    # Initialize clean dynamic system
    clean_system = CleanDynamicSystem(company_id)
    
    # Check if company has additional data sources
    selected_sources = clean_system.get_company_additional_sources()
    
    if not selected_sources:
        return {}
    
    # Render additional fields based on company configuration
    st.subheader("🎯 Additional Data Sources")
    st.write(f"Your organization has selected **{len(selected_sources)}** additional data sources for enhanced scoring:")
    st.write(", ".join([f"**{source}**" for source in selected_sources]))
    
    # Render the dynamic fields
    additional_data = clean_system.render_dynamic_additional_fields()
    
    return additional_data