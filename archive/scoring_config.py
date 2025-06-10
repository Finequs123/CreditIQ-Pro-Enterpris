import streamlit as st
import json
import os
from typing import Dict, Any

class ScoringWeightsConfig:
    """Configuration manager for scoring weights"""
    
    def __init__(self, config_file: str = "scoring_weights.json"):
        self.config_file = config_file
        self.default_weights = {
            # Core Credit Variables (40%)
            "credit_score": 0.15,
            "foir": 0.07,
            "dpd30plus": 0.07,
            "enquiry_count": 0.06,
            "occupation": 0.00,
            "company_category": 0.04,
            "age": 0.04,
            "monthly_income": 0.10,
            
            # Behavioral Analytics (25%)
            "credit_vintage": 0.06,
            "loan_mix_type": 0.06,
            "loan_completion_ratio": 0.07,
            "defaulted_loans": 0.08,
            
            # Exposure Metrics (10%)
            "unsecured_loan_amount": 0.05,
            "outstanding_amount_percent": 0.05,
            
            # Intent/Channel Signals (10%)
            "our_lender_exposure": 0.05,
            "channel_type": 0.05,
            
            # Additional AI-supported variables (5%)
            "employment_tenure": 0.01,
            "account_vintage": 0.01,
            "avg_monthly_balance": 0.01,
            "bounce_frequency": 0.01,
            "mobile_number_vintage": 0.01,
            "digital_engagement": 0.00,
            "job_type": 0.00,
            "company_stability": 0.00,
            "geographic_risk": 0.00
        }
        self.load_config()
    
    def load_config(self):
        """Load configuration from file or use defaults"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    self.weights = json.load(f)
            except:
                self.weights = self.default_weights.copy()
        else:
            self.weights = self.default_weights.copy()
    
    def save_config(self):
        """Save current configuration to file"""
        with open(self.config_file, 'w') as f:
            json.dump(self.weights, f, indent=2)
    
    def load_weights_from_json(self):
        """Reload weights from the JSON configuration file"""
        self.load_config()
    
    def reset_to_defaults(self):
        """Reset all weights to default values"""
        self.weights = self.default_weights.copy()
        self.save_config()
    
    def get_weights(self) -> Dict[str, float]:
        """Get current weights"""
        return self.weights.copy()
    
    def update_weight(self, variable: str, weight: float):
        """Update a specific weight"""
        self.weights[variable] = weight
    
    def get_category_totals(self) -> Dict[str, float]:
        """Calculate category totals"""
        categories = {
            "Core Credit": [
                "credit_score", "foir", "dpd30plus", "enquiry_count", 
                "occupation", "company_category", "age", "monthly_income"
            ],
            "Behavioral Analytics": [
                "credit_vintage", "loan_mix_type", "loan_completion_ratio", "defaulted_loans"
            ],
            "Exposure Metrics": [
                "unsecured_loan_amount", "outstanding_amount_percent"
            ],
            "Intent/Channel Signals": [
                "our_lender_exposure", "channel_type"
            ]
        }
        
        totals = {}
        for category, variables in categories.items():
            totals[category] = sum(self.weights.get(var, 0) for var in variables)
        
        return totals

def render_scoring_weights_config():
    """Render the scoring weights configuration interface"""
    st.header("⚖️ Scoring Weights Configuration")
    st.write("Configure the weights for each scoring variable to match your bank's risk appetite and lending criteria.")
    
    # Initialize config manager - always reload to get latest weights from file
    st.session_state.config_manager = ScoringWeightsConfig()
    config = st.session_state.config_manager
    
    # Control buttons
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button("🔄 Reset to Defaults", type="secondary"):
            config.reset_to_defaults()
            st.success("Reset to default weights!")
            st.rerun()
    
    with col2:
        if st.button("💾 Save Configuration", type="primary"):
            config.save_config()
            st.success("Configuration saved!")
    
    # Display current total
    total_weight = sum(config.weights.values())
    with col3:
        if abs(total_weight - 1.0) < 0.001:
            st.success(f"✅ Total Weight: {total_weight:.1%}")
        else:
            st.error(f"⚠️ Total Weight: {total_weight:.1%} (Should be 100%)")
    
    st.markdown("---")
    
    # Configuration tabs
    tab1, tab2, tab3 = st.tabs(["🎛️ Configure Weights", "📊 Category Overview", "📋 Weight Summary"])
    
    with tab1:
        # Core Credit Variables (40% target)
        st.subheader("🏦 Core Credit Variables")
        st.caption("Target allocation: ~40% | These are fundamental credit assessment variables")
        
        col1, col2 = st.columns(2)
        
        with col1:
            config.weights["credit_score"] = st.slider(
                "📈 Credit Score", 
                min_value=0.0, max_value=0.30, 
                value=config.weights["credit_score"], 
                step=0.01, format="%.1%"
            )
            
            config.weights["foir"] = st.slider(
                "📉 FOIR (Fixed Obligation to Income Ratio)", 
                min_value=0.0, max_value=0.20, 
                value=config.weights["foir"], 
                step=0.01, format="%.1%"
            )
            
            config.weights["dpd30plus"] = st.slider(
                "⚠️ DPD 30+ History", 
                min_value=0.0, max_value=0.20, 
                value=config.weights["dpd30plus"], 
                step=0.01, format="%.1%"
            )
            
            config.weights["enquiry_count"] = st.slider(
                "🔍 Credit Enquiry Count", 
                min_value=0.0, max_value=0.15, 
                value=config.weights["enquiry_count"], 
                step=0.01, format="%.1%"
            )
        
        with col2:
            config.weights["occupation"] = st.slider(
                "💼 Occupation Type", 
                min_value=0.0, max_value=0.10, 
                value=config.weights["occupation"], 
                step=0.01, format="%.1%"
            )
            
            config.weights["company_category"] = st.slider(
                "🏢 Company Category", 
                min_value=0.0, max_value=0.10, 
                value=config.weights["company_category"], 
                step=0.01, format="%.1%"
            )
            
            config.weights["age"] = st.slider(
                "🎂 Age", 
                min_value=0.0, max_value=0.10, 
                value=config.weights["age"], 
                step=0.01, format="%.1%"
            )
            
            config.weights["monthly_income"] = st.slider(
                "💰 Monthly Income", 
                min_value=0.0, max_value=0.20, 
                value=config.weights["monthly_income"], 
                step=0.01, format="%.1%"
            )
        
        st.markdown("---")
        
        # Behavioral Analytics (25% target)
        st.subheader("🧠 Behavioral Analytics")
        st.caption("Target allocation: ~25% | Customer behavior and credit history patterns")
        
        col1, col2 = st.columns(2)
        
        with col1:
            config.weights["credit_vintage"] = st.slider(
                "📅 Credit Vintage", 
                min_value=0.0, max_value=0.15, 
                value=config.weights["credit_vintage"], 
                step=0.01, format="%.1%"
            )
            
            config.weights["loan_mix_type"] = st.slider(
                "🏦 Loan Mix Type", 
                min_value=0.0, max_value=0.15, 
                value=config.weights["loan_mix_type"], 
                step=0.01, format="%.1%"
            )
        
        with col2:
            config.weights["loan_completion_ratio"] = st.slider(
                "✅ Loan Completion Ratio", 
                min_value=0.0, max_value=0.15, 
                value=config.weights["loan_completion_ratio"], 
                step=0.01, format="%.1%"
            )
            
            config.weights["defaulted_loans"] = st.slider(
                "❌ Defaulted Loans Count", 
                min_value=0.0, max_value=0.15, 
                value=config.weights["defaulted_loans"], 
                step=0.01, format="%.1%"
            )
        
        st.markdown("---")
        
        # Exposure Metrics (10% target)
        st.subheader("💼 Exposure Metrics")
        st.caption("Target allocation: ~10% | Current financial exposure and obligations")
        
        col1, col2 = st.columns(2)
        
        with col1:
            config.weights["unsecured_loan_amount"] = st.slider(
                "💳 Unsecured Loan Amount", 
                min_value=0.0, max_value=0.15, 
                value=config.weights["unsecured_loan_amount"], 
                step=0.01, format="%.1%"
            )
        
        with col2:
            config.weights["outstanding_amount_percent"] = st.slider(
                "📊 Outstanding Amount Percentage", 
                min_value=0.0, max_value=0.15, 
                value=config.weights["outstanding_amount_percent"], 
                step=0.01, format="%.1%"
            )
        
        st.markdown("---")
        
        # Intent/Channel Signals (10% target)
        st.subheader("📱 Intent/Channel Signals")
        st.caption("Target allocation: ~10% | Application channel and lender relationship")
        
        col1, col2 = st.columns(2)
        
        with col1:
            config.weights["our_lender_exposure"] = st.slider(
                "🏢 Our Lender Exposure", 
                min_value=0.0, max_value=0.15, 
                value=config.weights["our_lender_exposure"], 
                step=0.01, format="%.1%"
            )
        
        with col2:
            config.weights["channel_type"] = st.slider(
                "📱 Channel Type", 
                min_value=0.0, max_value=0.15, 
                value=config.weights["channel_type"], 
                step=0.01, format="%.1%"
            )
    
    with tab2:
        st.subheader("📊 Category Weight Distribution")
        
        category_totals = config.get_category_totals()
        
        # Create visualization
        import plotly.express as px
        import pandas as pd
        
        df_categories = pd.DataFrame([
            {"Category": category, "Weight": weight, "Target": target}
            for (category, weight), target in zip(category_totals.items(), [0.40, 0.25, 0.10, 0.10])
        ])
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Bar chart
            fig_bar = px.bar(
                df_categories, 
                x="Category", 
                y="Weight",
                title="Current Weight Distribution by Category",
                color="Weight",
                color_continuous_scale="viridis"
            )
            fig_bar.update_layout(xaxis_tickangle=-45)
            fig_bar.update_traces(texttemplate='%{y:.1%}', textposition='outside')
            st.plotly_chart(fig_bar, use_container_width=True)
        
        with col2:
            # Pie chart
            fig_pie = px.pie(
                df_categories, 
                values="Weight", 
                names="Category",
                title="Weight Distribution"
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        
        # Category comparison table
        st.subheader("Target vs Current Allocation")
        comparison_data = []
        targets = {"Core Credit": 0.40, "Behavioral Analytics": 0.25, "Exposure Metrics": 0.10, "Intent/Channel Signals": 0.10}
        
        for category, current in category_totals.items():
            target = targets[category]
            variance = current - target
            comparison_data.append({
                "Category": category,
                "Target": f"{target:.1%}",
                "Current": f"{current:.1%}",
                "Variance": f"{variance:+.1%}",
                "Status": "✅ On Target" if abs(variance) < 0.02 else "⚠️ Off Target"
            })
        
        df_comparison = pd.DataFrame(comparison_data)
        st.dataframe(df_comparison, use_container_width=True)
    
    with tab3:
        st.subheader("📋 Complete Weight Summary")
        
        # Detailed weights table
        weights_data = []
        categories = {
            "Core Credit": ["credit_score", "foir", "dpd30plus", "enquiry_count", "occupation", "company_category", "age", "monthly_income"],
            "Behavioral Analytics": ["credit_vintage", "loan_mix_type", "loan_completion_ratio", "defaulted_loans"],
            "Exposure Metrics": ["unsecured_loan_amount", "outstanding_amount_percent"],
            "Intent/Channel Signals": ["our_lender_exposure", "channel_type"]
        }
        
        variable_labels = {
            "credit_score": "Credit Score",
            "foir": "FOIR",
            "dpd30plus": "DPD 30+ History",
            "enquiry_count": "Credit Enquiry Count",
            "occupation": "Occupation Type",
            "company_category": "Company Category",
            "age": "Age",
            "monthly_income": "Monthly Income",
            "credit_vintage": "Credit Vintage",
            "loan_mix_type": "Loan Mix Type",
            "loan_completion_ratio": "Loan Completion Ratio",
            "defaulted_loans": "Defaulted Loans Count",
            "unsecured_loan_amount": "Unsecured Loan Amount",
            "outstanding_amount_percent": "Outstanding Amount %",
            "our_lender_exposure": "Our Lender Exposure",
            "channel_type": "Channel Type"
        }
        
        for category, variables in categories.items():
            for variable in variables:
                weights_data.append({
                    "Category": category,
                    "Variable": variable_labels[variable],
                    "Weight": f"{config.weights[variable]:.1%}",
                    "Weight_Value": config.weights[variable]
                })
        
        df_weights = pd.DataFrame(weights_data)
        st.dataframe(df_weights[["Category", "Variable", "Weight"]], use_container_width=True)
        
        # Export configuration
        st.subheader("📤 Export Configuration")
        col1, col2 = st.columns(2)
        
        with col1:
            config_json = json.dumps(config.weights, indent=2)
            st.download_button(
                label="📥 Download Configuration (JSON)",
                data=config_json,
                file_name="scoring_weights_config.json",
                mime="application/json"
            )
        
        with col2:
            if st.button("📋 Copy to Clipboard"):
                st.code(config_json, language="json")
    
    return config