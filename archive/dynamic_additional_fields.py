"""
Dynamic Additional Fields Renderer
Renders additional data source fields based on company onboarding preferences
"""

import streamlit as st
from additional_data_scoring import AdditionalDataScoring
from typing import Dict, Any, List

class DynamicAdditionalFields:
    """Handles dynamic rendering of additional data source fields"""
    
    def __init__(self, company_id: int):
        self.company_id = company_id
        self.additional_scorer = AdditionalDataScoring()
        self.additional_config = self.additional_scorer.get_additional_variables_for_company(company_id)
    
    def render_additional_fields(self) -> Dict[str, Any]:
        """Render additional fields based on company's selected data sources"""
        additional_data = {}
        
        if not self.additional_config['variables']:
            return additional_data
        
        # Add a tab for additional data sources
        st.markdown("---")
        st.subheader("📊 Additional Data Sources")
        st.info(f"Your organization has access to {len(self.additional_config['selected_sources'])} additional data sources")
        
        # Create tabs for each additional data source
        if len(self.additional_config['selected_sources']) == 1:
            # Single tab
            source_name = self.additional_config['selected_sources'][0]
            st.markdown(f"### {source_name}")
            additional_data.update(self._render_source_fields(source_name))
        else:
            # Multiple tabs
            tabs = st.tabs(self.additional_config['selected_sources'])
            for i, source_name in enumerate(self.additional_config['selected_sources']):
                with tabs[i]:
                    additional_data.update(self._render_source_fields(source_name))
        
        return additional_data
    
    def _render_source_fields(self, source_name: str) -> Dict[str, Any]:
        """Render fields for a specific data source"""
        source_data = {}
        
        if source_name not in self.additional_config['variables']:
            return source_data
        
        variables = self.additional_config['variables'][source_name]['variables']
        
        # Create columns for better layout
        col1, col2 = st.columns(2)
        field_count = 0
        
        for var_key, var_config in variables.items():
            target_col = col1 if field_count % 2 == 0 else col2
            
            with target_col:
                if var_config['type'] == 'numeric':
                    value = st.number_input(
                        var_config['name'],
                        min_value=var_config.get('min_value', 0),
                        max_value=var_config.get('max_value', 1000000),
                        value=var_config.get('min_value', 0),
                        key=f"additional_{var_key}",
                        help=f"Weight: {var_config['weight']:.1f}%"
                    )
                elif var_config['type'] == 'categorical':
                    value = st.selectbox(
                        var_config['name'],
                        options=var_config['options'],
                        key=f"additional_{var_key}",
                        help=f"Weight: {var_config['weight']:.1f}%"
                    )
                else:
                    value = st.text_input(
                        var_config['name'],
                        key=f"additional_{var_key}",
                        help=f"Weight: {var_config['weight']:.1f}%"
                    )
                
                source_data[var_key] = value
            
            field_count += 1
        
        return source_data
    
    def get_field_descriptions(self) -> Dict[str, str]:
        """Get descriptions for additional fields"""
        descriptions = {}
        
        field_descriptions = {
            # ITR Data
            "annual_income_itr": "Annual income as declared in Income Tax Returns",
            "income_consistency": "Consistency of income over the last 3 years (0-100%)",
            "tax_payment_regularity": "Pattern of tax payment compliance",
            "income_growth_rate": "Year-over-year income growth percentage",
            "tax_compliance_score": "Overall tax compliance rating (0-100)",
            "declared_assets_value": "Total value of assets declared in ITR",
            
            # GST Data
            "monthly_gst_turnover": "Average monthly GST turnover",
            "gst_payment_consistency": "GST payment regularity score (0-100%)",
            "business_stability_score": "Overall business stability assessment (0-100)",
            "revenue_growth_trend": "Business revenue growth trend percentage",
            "gst_compliance_rating": "GST compliance quality rating",
            
            # Utility Bills
            "payment_consistency_score": "Utility bill payment consistency (0-100%)",
            "average_monthly_consumption": "Average monthly utility bill amount",
            "payment_delay_frequency": "How often utility payments are delayed",
            "address_stability": "Number of months at current address",
            "lifestyle_spending_indicator": "Lifestyle spending pattern category",
            
            # Telecom Data
            "bill_payment_regularity": "Telecom bill payment consistency (0-100%)",
            "usage_pattern_consistency": "Mobile usage pattern stability (0-100%)",
            "location_consistency": "Location consistency based on mobile data (0-100%)",
            "plan_stability": "Frequency of plan changes",
            
            # Social Media
            "digital_footprint_maturity": "Maturity of digital presence (0-100)",
            "social_network_stability": "Stability of social connections (0-100)",
            "professional_network_quality": "Quality of professional connections",
            "lifestyle_consistency": "Consistency in lifestyle indicators (0-100)",
            
            # App Usage
            "financial_app_engagement": "Engagement with financial apps (0-100)",
            "digital_literacy_score": "Digital literacy assessment (0-100)",
            "payment_app_usage": "Frequency of digital payment app usage",
            "digital_transaction_behavior": "Quality of digital transaction patterns"
        }
        
        for source_name, source_config in self.additional_config['variables'].items():
            for var_key, var_config in source_config['variables'].items():
                descriptions[var_key] = field_descriptions.get(var_key, var_config['name'])
        
        return descriptions
    
    def display_additional_score_breakdown(self, additional_breakdown: Dict[str, Any]):
        """Display breakdown of additional data source scores"""
        if not additional_breakdown or not additional_breakdown.get('source_scores'):
            return
        
        st.subheader("📊 Additional Data Sources Score Breakdown")
        
        # Overall additional score
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Additional Score", f"{additional_breakdown['additional_score']:.1f}")
        with col2:
            st.metric("Additional Weight", f"{additional_breakdown['additional_weight']:.1f}%")
        
        # Source-wise breakdown
        for source_name, source_data in additional_breakdown['source_scores'].items():
            with st.expander(f"{source_name} - Score: {source_data['score']:.1f}"):
                st.write(f"**Weight Contribution:** {source_data['weight']:.1f}%")
                
                # Show individual field scores if available
                source_config = self.additional_config['variables'].get(source_name, {})
                if 'variables' in source_config:
                    st.write("**Field Contributions:**")
                    for var_key, var_config in source_config['variables'].items():
                        st.write(f"• {var_config['name']}: {var_config['weight']:.1f}% weight")
        
        # Missing fields warning
        if additional_breakdown.get('missing_fields'):
            st.warning("⚠️ Some additional data fields were missing and fallback scores were used:")
            for field in additional_breakdown['missing_fields']:
                st.write(f"• {field}")