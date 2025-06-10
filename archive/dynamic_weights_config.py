"""
Dynamic Weights Configuration System
Automatically creates weight configuration sections based on company's selected additional data sources
"""

import streamlit as st
import sqlite3
import json
from typing import Dict, List, Any, Optional

class DynamicWeightsConfig:
    """Manages dynamic weight configuration based on company's additional data sources"""
    
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
                sources = json.loads(result[0])
                return [s for s in sources if s != 'None']
            return []
            
        except Exception as e:
            print(f"Error getting additional sources: {e}")
            return []
    
    def get_additional_data_variables(self, source_name: str) -> Dict[str, Dict]:
        """Get variables for specific additional data source"""
        variables = {
            "GST Data": {
                "gst_turnover": {
                    "name": "GST Annual Turnover",
                    "description": "Company's annual turnover as per GST records",
                    "weight": 0.015,  # 1.5%
                    "type": "numeric"
                },
                "gst_compliance": {
                    "name": "GST Compliance Score",
                    "description": "GST filing compliance and consistency",
                    "weight": 0.010,  # 1.0%
                    "type": "categorical"
                },
                "gst_filing_frequency": {
                    "name": "GST Filing Frequency",
                    "description": "Regularity of GST filings",
                    "weight": 0.008,  # 0.8%
                    "type": "categorical"
                },
                "gst_refund_claims": {
                    "name": "GST Refund Claims",
                    "description": "Amount and frequency of GST refund claims",
                    "weight": 0.007,  # 0.7%
                    "type": "numeric"
                }
            },
            "ITR Data": {
                "itr_income": {
                    "name": "Annual Income (ITR)",
                    "description": "Annual income as declared in Income Tax Returns",
                    "weight": 0.020,  # 2.0%
                    "type": "numeric"
                },
                "itr_compliance": {
                    "name": "Tax Filing Compliance",
                    "description": "Timeliness and consistency of tax filings",
                    "weight": 0.012,  # 1.2%
                    "type": "categorical"
                },
                "itr_consistency": {
                    "name": "Income Consistency",
                    "description": "Consistency of income across tax years",
                    "weight": 0.010,  # 1.0%
                    "type": "categorical"
                },
                "itr_assets": {
                    "name": "Declared Assets Value",
                    "description": "Total value of assets declared in ITR",
                    "weight": 0.008,  # 0.8%
                    "type": "numeric"
                }
            },
            "Utility Bills": {
                "utility_payment_history": {
                    "name": "Utility Payment History",
                    "description": "Timeliness of utility bill payments",
                    "weight": 0.015,  # 1.5%
                    "type": "categorical"
                },
                "utility_consumption": {
                    "name": "Consumption Pattern",
                    "description": "Stability of utility consumption",
                    "weight": 0.010,  # 1.0%
                    "type": "categorical"
                },
                "utility_address_stability": {
                    "name": "Address Stability",
                    "description": "Duration at current address",
                    "weight": 0.015,  # 1.5%
                    "type": "numeric"
                }
            },
            "Telecom Data": {
                "telecom_usage_pattern": {
                    "name": "Usage Pattern",
                    "description": "Telecom usage behavior analysis",
                    "weight": 0.012,  # 1.2%
                    "type": "categorical"
                },
                "telecom_payment_method": {
                    "name": "Payment Method",
                    "description": "Preferred payment method for telecom bills",
                    "weight": 0.008,  # 0.8%
                    "type": "categorical"
                },
                "telecom_plan_stability": {
                    "name": "Plan Stability",
                    "description": "Consistency in telecom plan selection",
                    "weight": 0.010,  # 1.0%
                    "type": "categorical"
                }
            },
            "Social Media": {
                "social_activity_level": {
                    "name": "Activity Level",
                    "description": "Level of social media activity",
                    "weight": 0.008,  # 0.8%
                    "type": "categorical"
                },
                "social_network_quality": {
                    "name": "Network Quality",
                    "description": "Quality and type of social connections",
                    "weight": 0.012,  # 1.2%
                    "type": "categorical"
                },
                "social_stability_score": {
                    "name": "Profile Stability Score",
                    "description": "Stability and consistency of social media profile",
                    "weight": 0.010,  # 1.0%
                    "type": "numeric"
                }
            },
            "App Usage": {
                "financial_app_usage": {
                    "name": "Financial App Usage",
                    "description": "Usage patterns of financial applications",
                    "weight": 0.015,  # 1.5%
                    "type": "categorical"
                },
                "shopping_app_behavior": {
                    "name": "Shopping App Behavior",
                    "description": "Shopping patterns and behavior analysis",
                    "weight": 0.010,  # 1.0%
                    "type": "categorical"
                },
                "app_diversity_score": {
                    "name": "App Diversity Score",
                    "description": "Diversity of applications used",
                    "weight": 0.015,  # 1.5%
                    "type": "numeric"
                }
            }
        }
        
        return variables.get(source_name, {})
    
    def save_additional_weights(self, weights_data: Dict[str, float]):
        """Save additional data source weights to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create table if not exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS additional_weights_config (
                    company_id INTEGER PRIMARY KEY,
                    weights_config TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Save weights configuration
            cursor.execute("""
                INSERT OR REPLACE INTO additional_weights_config 
                (company_id, weights_config, updated_at) 
                VALUES (?, ?, CURRENT_TIMESTAMP)
            """, (self.company_id, json.dumps(weights_data)))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error saving additional weights: {e}")
            return False
    
    def load_additional_weights(self) -> Dict[str, float]:
        """Load additional data source weights from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Ensure table exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS additional_weights_config (
                    company_id INTEGER PRIMARY KEY,
                    weights_config TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                SELECT weights_config FROM additional_weights_config 
                WHERE company_id = ?
            """, (self.company_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result and result[0]:
                return json.loads(result[0])
            return {}
            
        except Exception as e:
            print(f"Error loading additional weights: {e}")
            return {}
    
    def render_additional_weights_config(self):
        """Render dynamic weights configuration sections for company's additional data sources"""
        selected_sources = self.get_company_additional_sources()
        
        if not selected_sources:
            st.info("No additional data sources configured for your organization.")
            return {}
        
        st.subheader("🎯 Additional Data Sources Weights")
        st.write(f"Configure weights for your organization's {len(selected_sources)} selected additional data sources:")
        
        # Load existing weights
        existing_weights = self.load_additional_weights()
        all_weights = {}
        
        # Create tabs for each additional data source
        if len(selected_sources) == 1:
            # Single source - no tabs needed
            source = selected_sources[0]
            source_weights = self._render_source_weights_section(source, existing_weights)
            all_weights.update(source_weights)
        else:
            # Multiple sources - use tabs
            tabs = st.tabs([f"📊 {source}" for source in selected_sources])
            
            for i, source in enumerate(selected_sources):
                with tabs[i]:
                    source_weights = self._render_source_weights_section(source, existing_weights)
                    all_weights.update(source_weights)
        
        # Save weights button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("💾 Save Additional Data Weights", type="primary", use_container_width=True):
                if self.save_additional_weights(all_weights):
                    st.success("✅ Additional data weights saved successfully!")
                    st.rerun()
                else:
                    st.error("❌ Failed to save weights. Please try again.")
        
        return all_weights
    
    def _render_source_weights_section(self, source_name: str, existing_weights: Dict[str, float]) -> Dict[str, float]:
        """Render weights configuration section for specific data source"""
        variables = self.get_additional_data_variables(source_name)
        
        if not variables:
            st.warning(f"No variables configured for {source_name}")
            return {}
        
        st.write(f"**{source_name}** - Configure individual variable weights:")
        
        weights = {}
        total_weight = 0
        
        # Create columns for better layout
        cols = st.columns(2)
        
        for i, (var_key, var_config) in enumerate(variables.items()):
            with cols[i % 2]:
                # Get existing weight or default
                current_weight = existing_weights.get(f"{source_name}_{var_key}", var_config["weight"])
                
                # Convert to percentage for display
                weight_percent = current_weight * 100
                
                new_weight = st.number_input(
                    f"**{var_config['name']}**",
                    min_value=0.0,
                    max_value=10.0,
                    value=weight_percent,
                    step=0.1,
                    format="%.1f",
                    help=var_config["description"],
                    key=f"weight_{source_name}_{var_key}"
                )
                
                # Convert back to decimal
                weights[f"{source_name}_{var_key}"] = new_weight / 100
                total_weight += new_weight / 100
        
        # Show total weight for this source
        st.metric(f"Total Weight for {source_name}", f"{total_weight * 100:.1f}%")
        
        if total_weight > 0.12:  # 12% maximum
            st.warning(f"⚠️ Total weight for {source_name} exceeds 12%. Consider reducing individual weights.")
        
        return weights
    
    def get_all_weights_for_scoring(self) -> Dict[str, float]:
        """Get all weights (core + additional) for scoring engine"""
        # Load core weights
        try:
            import json
            with open("scoring_weights.json", "r") as f:
                core_weights = json.load(f)
        except:
            # Default core weights
            core_weights = {
                "credit_score": 0.155,
                "foir": 0.126,
                "dpd30plus": 0.097,
                "enquiry_count": 0.087,
                "monthly_income": 0.078,
                "age": 0.058,
                "credit_vintage": 0.068,
                "loan_mix": 0.039,
                "loan_completion_ratio": 0.058,
                "defaulted_loans": 0.087,
                "job_type": 0.021,
                "employment_tenure": 0.044,
                "company_stability": 0.013,
                "account_vintage": 0.029,
                "avg_monthly_balance": 0.058,
                "bounce_frequency": 0.043,
                "geographic_risk": 0.013,
                "mobile_number_vintage": 0.034,
                "digital_engagement": 0.034,
                "unsecured_loan_amount": 0.065,
                "outstanding_amount_percent": 0.065,
                "our_lender_exposure": 0.065,
                "channel_type": 0.013
            }
        
        # Load additional weights
        additional_weights = self.load_additional_weights()
        
        # Combine weights
        all_weights = {**core_weights, **additional_weights}
        
        return all_weights

def render_dynamic_weights_configuration(company_id: int):
    """Main function to render dynamic weights configuration"""
    if not company_id:
        st.warning("Company ID required for weights configuration.")
        return
    
    weights_config = DynamicWeightsConfig(company_id)
    
    # Render core weights sections (existing functionality)
    st.header("⚖️ Scoring Weights Configuration")
    
    # Core Credit Variables section
    with st.expander("🎯 Core Credit Variables (Total: ~50%)", expanded=False):
        st.write("Primary credit assessment variables with the highest impact on scoring.")
        # Core weights configuration would go here
    
    # Behavioral Analytics section  
    with st.expander("📊 Behavioral Analytics (Total: ~30%)", expanded=False):
        st.write("Banking behavior and financial stability indicators.")
        # Behavioral weights configuration would go here
    
    # Geographic & Social section
    with st.expander("🌍 Geographic & Social (Total: ~8%)", expanded=False):
        st.write("Location-based risk and social indicators.")
        # Geographic weights configuration would go here
    
    # Exposure & Intent section
    with st.expander("⚠️ Exposure & Intent (Total: ~12%)", expanded=False):
        st.write("Risk exposure and application intent indicators.")
        # Exposure weights configuration would go here
    
    # Dynamic Additional Data Sources sections
    st.markdown("---")
    weights_config.render_additional_weights_config()