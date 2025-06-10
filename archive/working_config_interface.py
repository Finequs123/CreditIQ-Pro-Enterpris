"""
Working Configuration Interface - Professional tabbed layout
Synchronized with Dynamic Configuration system
"""
import streamlit as st
import json
from typing import Dict, Any
from weights_synchronizer import get_synchronized_weights, save_synchronized_weights

def load_current_weights() -> Dict[str, float]:
    """Load weights from synchronized systems (Dynamic Config -> JSON -> Defaults)"""
    return get_synchronized_weights()

def save_weights(weights: Dict[str, float]):
    """Save weights to synchronized systems (JSON + Dynamic Config) and maintain history"""
    # Save to both systems using synchronizer
    success = save_synchronized_weights(weights)
    
    if success:
        # Maintain configuration history (last 3 configurations)
        save_configuration_history(weights)
    else:
        st.error("Failed to save weights to all systems")

def save_configuration_history(weights: Dict[str, float]):
    """Save configuration to history and maintain last 3 versions"""
    import datetime
    
    try:
        with open("config_history.json", "r") as f:
            history = json.load(f)
    except:
        history = []
    
    # Add new configuration with timestamp
    new_config = {
        "timestamp": datetime.datetime.now().isoformat(),
        "weights": weights,
        "total": sum(weights.values()),
        "description": f"Configuration saved at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    }
    
    history.append(new_config)
    
    # Keep only last 3 configurations
    if len(history) > 3:
        history = history[-3:]
    
    with open("config_history.json", "w") as f:
        json.dump(history, f, indent=2)

def load_configuration_history():
    """Load configuration history"""
    try:
        with open("config_history.json", "r") as f:
            return json.load(f)
    except:
        return []

def render_working_config():
    """Render working configuration interface with professional tabs"""
    st.header("⚖️ Scoring Weights Configuration")
    st.write("Configure the weights for each scoring variable to match your bank's risk appetite and lending criteria.")
    
    # Synchronization status
    st.info("🔗 **Synchronized with Dynamic Configuration** - Changes here will automatically sync with the advanced variable management system")
    
    # Load current weights
    current_weights = load_current_weights()
    
    # Control buttons
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button("🔄 Reset to Defaults", type="secondary"):
            # AI-optimized weights from scientific analysis - normalized to exactly 100%
            default_weights = {
                # Core Credit Variables - Total: 32.8%
                "credit_score": 0.107767,          # 10.8%
                "foir": 0.065049,                  # 6.5%
                "dpd30plus": 0.065049,             # 6.5%
                "enquiry_count": 0.056311,         # 5.6%
                "monthly_income": 0.065049,        # 6.5%
                
                # Behavioral Analytics - Total: 14.6%
                "credit_vintage": 0.033010,        # 3.3%
                "loan_mix_type": 0.021359,         # 2.1%
                "loan_completion_ratio": 0.025243, # 2.5%
                "defaulted_loans": 0.065049,       # 6.5%
                
                # Employment Stability - Total: 7.8%
                "job_type": 0.021359,              # 2.1%
                "employment_tenure": 0.043689,     # 4.4%
                "company_stability": 0.012621,     # 1.3%
                
                # Banking Behavior - Total: 13.0%
                "account_vintage": 0.029126,       # 2.9%
                "avg_monthly_balance": 0.058252,   # 5.8%
                "bounce_frequency": 0.042718,      # 4.3%
                
                # Geographic & Social - Total: 8.1%
                "geographic_risk": 0.012621,       # 1.3%
                "mobile_number_vintage": 0.033981, # 3.4%
                "digital_engagement": 0.033981,    # 3.4%
                
                # Exposure & Intent - Total: 20.8%
                "unsecured_loan_amount": 0.065049, # 6.5%
                "outstanding_amount_percent": 0.065049, # 6.5%
                "our_lender_exposure": 0.065049,   # 6.5%
                "channel_type": 0.012621           # 1.3%
            }
            save_weights(default_weights)
            st.success("Reset to original scientifically optimized weights (100%)!")
            st.rerun()
    
    with col2:
        if st.button("💾 Save Configuration", type="primary"):
            save_weights(current_weights)
            st.session_state.weights_updated = True
            st.success("Configuration saved!")
            st.rerun()
    
    # Display current total
    total_weight = sum(current_weights.values())
    with col3:
        if abs(total_weight - 1.0) < 0.001:
            st.success(f"✅ Total Weight: {total_weight:.1%}")
        else:
            st.error(f"⚠️ Total Weight: {total_weight:.1%} (Should be 100%)")
    
    st.markdown("---")
    
    # Configuration tabs
    tab1, tab2 = st.tabs(["🎛️ Configure Weights", "🕒 Configuration History"])
    
    with tab1:
        # Calculate dynamic category totals
        core_credit_total = (current_weights.get("credit_score", 0) + current_weights.get("foir", 0) + 
                           current_weights.get("dpd30plus", 0) + current_weights.get("enquiry_count", 0) + 
                           current_weights.get("monthly_income", 0))
        
        behavioral_total = (current_weights.get("credit_vintage", 0) + current_weights.get("loan_mix_type", 0) + 
                          current_weights.get("loan_completion_ratio", 0) + current_weights.get("defaulted_loans", 0))
        
        st.subheader(f"🏦 Core Credit Variables ({core_credit_total:.1%})")
        col1, col2 = st.columns(2)
        
        with col1:
            current_weights["credit_score"] = st.slider("Credit Score", 0.0, 0.20, current_weights.get("credit_score", 0.107767), 0.001)
            current_weights["foir"] = st.slider("FOIR (Fixed Obligations to Income Ratio)", 0.0, 0.15, current_weights.get("foir", 0.065049), 0.001)
            current_weights["enquiry_count"] = st.slider("Credit Enquiry Count", 0.0, 0.10, current_weights.get("enquiry_count", 0.056311), 0.001)
        
        with col2:
            current_weights["dpd30plus"] = st.slider("DPD 30+ (Days Past Due)", 0.0, 0.15, current_weights.get("dpd30plus", 0.065049), 0.001)
            current_weights["monthly_income"] = st.slider("Monthly Income", 0.0, 0.15, current_weights.get("monthly_income", 0.065049), 0.001)
        
        st.markdown("---")
        
        st.subheader(f"🧠 Behavioral Analytics ({behavioral_total:.1%})")
        col3, col4 = st.columns(2)
        
        with col3:
            current_weights["credit_vintage"] = st.slider("Credit Vintage", 0.0, 0.10, current_weights.get("credit_vintage", 0.033010), 0.001)
            current_weights["loan_mix_type"] = st.slider("Loan Mix Type", 0.0, 0.10, current_weights.get("loan_mix_type", 0.021359), 0.001)
        
        with col4:
            current_weights["loan_completion_ratio"] = st.slider("Loan Completion Ratio", 0.0, 0.10, current_weights.get("loan_completion_ratio", 0.025243), 0.001)
            current_weights["defaulted_loans"] = st.slider("Defaulted Loans History", 0.0, 0.10, current_weights.get("defaulted_loans", 0.065049), 0.001)
        
        st.markdown("---")
        
        # Calculate employment stability total
        employment_total = (current_weights.get("job_type", 0) + current_weights.get("employment_tenure", 0) + 
                          current_weights.get("company_stability", 0))
        
        st.subheader(f"👔 Employment Stability ({employment_total:.1%})")
        col5, col6 = st.columns(2)
        
        with col5:
            current_weights["job_type"] = st.slider("Job Type", 0.0, 0.10, current_weights.get("job_type", 0.021359), 0.001)
            current_weights["employment_tenure"] = st.slider("Employment Tenure", 0.0, 0.08, current_weights.get("employment_tenure", 0.043689), 0.001)
        
        with col6:
            current_weights["company_stability"] = st.slider("Company Stability", 0.0, 0.08, current_weights.get("company_stability", 0.012621), 0.001)
        
        st.markdown("---")
        
        # Calculate banking behavior total
        banking_total = (current_weights.get("account_vintage", 0) + current_weights.get("avg_monthly_balance", 0) + 
                        current_weights.get("bounce_frequency", 0))
        
        st.subheader(f"🏛️ Banking Behavior ({banking_total:.1%})")
        col7, col8 = st.columns(2)
        
        with col7:
            current_weights["account_vintage"] = st.slider("Account Vintage", 0.0, 0.06, current_weights.get("account_vintage", 0.029126), 0.001)
            current_weights["avg_monthly_balance"] = st.slider("Average Monthly Balance", 0.0, 0.10, current_weights.get("avg_monthly_balance", 0.058252), 0.001)
        
        with col8:
            current_weights["bounce_frequency"] = st.slider("Bounce Frequency", 0.0, 0.06, current_weights.get("bounce_frequency", 0.042718), 0.001)
        
        st.markdown("---")
        
        # Calculate geographic & social total
        geographic_total = (current_weights.get("geographic_risk", 0) + current_weights.get("mobile_number_vintage", 0) + 
                          current_weights.get("digital_engagement", 0))
        
        st.subheader(f"🌍 Geographic & Social Factors ({geographic_total:.1%})")
        col9, col10 = st.columns(2)
        
        with col9:
            current_weights["geographic_risk"] = st.slider("Geographic Risk", 0.0, 0.04, current_weights.get("geographic_risk", 0.012621), 0.001)
            current_weights["mobile_number_vintage"] = st.slider("Mobile Number Vintage", 0.0, 0.06, current_weights.get("mobile_number_vintage", 0.033981), 0.001)
        
        with col10:
            current_weights["digital_engagement"] = st.slider("Digital Engagement", 0.0, 0.06, current_weights.get("digital_engagement", 0.033981), 0.001)
        
        st.markdown("---")
        
        # Calculate exposure & intent total
        exposure_total = (current_weights.get("unsecured_loan_amount", 0) + current_weights.get("outstanding_amount_percent", 0) + 
                         current_weights.get("our_lender_exposure", 0) + current_weights.get("channel_type", 0))
        
        st.subheader(f"💰 Exposure & Intent ({exposure_total:.1%})")
        col11, col12 = st.columns(2)
        
        with col11:
            current_weights["unsecured_loan_amount"] = st.slider("Unsecured Loan Amount", 0.0, 0.10, current_weights.get("unsecured_loan_amount", 0.065049), 0.001)
            current_weights["outstanding_amount_percent"] = st.slider("Outstanding Amount %", 0.0, 0.10, current_weights.get("outstanding_amount_percent", 0.065049), 0.001)
        
        with col12:
            current_weights["our_lender_exposure"] = st.slider("Our Lender Exposure", 0.0, 0.10, current_weights.get("our_lender_exposure", 0.065049), 0.001)
            current_weights["channel_type"] = st.slider("Channel Type", 0.0, 0.04, current_weights.get("channel_type", 0.012621), 0.001)
        
        # Add additional data sources sections if company has them configured
        company_id = st.session_state.get('company_id')
        if company_id:
            try:
                from dynamic_weights_config import DynamicWeightsConfig
                weights_config = DynamicWeightsConfig(company_id)
                selected_sources = weights_config.get_company_additional_sources()
                
                if selected_sources:
                    st.markdown("---")
                    st.subheader("📈 Additional Data Sources Configuration")
                    st.write(f"Configure weights for your organization's {len(selected_sources)} additional data sources:")
                    
                    # Load existing additional weights
                    existing_additional_weights = weights_config.load_additional_weights()
                    
                    for source in selected_sources:
                        variables = weights_config.get_additional_data_variables(source)
                        
                        if variables:
                            # Calculate total for this source
                            source_total = sum(existing_additional_weights.get(f"{source}_{var_key}", var_config["weight"]) 
                                             for var_key, var_config in variables.items())
                            
                            st.write(f"**{source} ({source_total:.1%})**")
                            
                            # Create columns for layout
                            col1, col2 = st.columns(2)
                            
                            for i, (var_key, var_config) in enumerate(variables.items()):
                                with col1 if i % 2 == 0 else col2:
                                    # Get existing weight or default
                                    weight_key = f"{source}_{var_key}"
                                    current_weight = existing_additional_weights.get(weight_key, var_config["weight"])
                                    
                                    # Convert to percentage for display
                                    weight_percent = current_weight * 100
                                    
                                    new_weight = st.slider(
                                        f"{var_config['name']}",
                                        min_value=0.0,
                                        max_value=10.0,
                                        value=weight_percent,
                                        step=0.1,
                                        format="%.1f",
                                        help=var_config["description"],
                                        key=f"additional_weight_{source}_{var_key}"
                                    )
                                    
                                    # Update weights dictionary
                                    current_weights[weight_key] = new_weight / 100
                            
                            st.write("")  # Add spacing between sources
                    
                    # Save additional weights button
                    if st.button("💾 Save Additional Data Weights", key="save_additional_weights"):
                        additional_weights = {k: v for k, v in current_weights.items() 
                                            if any(k.startswith(f"{source}_") for source in selected_sources)}
                        
                        if weights_config.save_additional_weights(additional_weights):
                            st.success("Additional data weights saved successfully!")
                            st.rerun()
                        else:
                            st.error("Failed to save additional weights. Please try again.")
                
            except Exception as e:
                st.error(f"Error loading additional data sources: {e}")
                st.info("Additional data sources configuration not available.")
    
    with tab2:
        st.subheader("🕒 Configuration History")
        history = load_configuration_history()
        
        if history:
            st.write("**Last 3 Configurations Used for Scoring:**")
            
            for i, config in enumerate(reversed(history[-3:]), 1):
                with st.expander(f"Configuration {i}: {config['description']} (Total: {config['total']:.1%})"):
                    st.write(f"**Saved:** {config['timestamp']}")
                    
                    # Show weights in organized format with dynamic category totals
                    weights = config['weights']
                    
                    # Calculate dynamic category totals for this configuration
                    core_total = (weights.get("credit_score", 0) + weights.get("foir", 0) + 
                                weights.get("dpd30plus", 0) + weights.get("enquiry_count", 0) + 
                                weights.get("monthly_income", 0))
                    
                    behavioral_total = (weights.get("credit_vintage", 0) + weights.get("loan_mix_type", 0) + 
                                      weights.get("loan_completion_ratio", 0) + weights.get("defaulted_loans", 0))
                    
                    employment_total = (weights.get("job_type", 0) + weights.get("employment_tenure", 0) + 
                                      weights.get("company_stability", 0))
                    
                    banking_total = (weights.get("account_vintage", 0) + weights.get("avg_monthly_balance", 0) + 
                                   weights.get("bounce_frequency", 0))
                    
                    geographic_total = (weights.get("geographic_risk", 0) + weights.get("mobile_number_vintage", 0) + 
                                      weights.get("digital_engagement", 0))
                    
                    exposure_total = (weights.get("unsecured_loan_amount", 0) + weights.get("outstanding_amount_percent", 0) + 
                                    weights.get("our_lender_exposure", 0) + weights.get("channel_type", 0))
                    
                    # Core Credit Variables
                    st.write(f"**Core Credit Variables ({core_total:.1%}):**")
                    core_vars = ['credit_score', 'foir', 'dpd30plus', 'enquiry_count', 'monthly_income']
                    for var in core_vars:
                        if var in weights:
                            st.write(f"• {var.replace('_', ' ').title()}: {weights[var]:.1%}")
                    
                    # Behavioral Analytics
                    st.write(f"**Behavioral Analytics ({behavioral_total:.1%}):**")
                    behavioral_vars = ['credit_vintage', 'loan_mix_type', 'loan_completion_ratio', 'defaulted_loans']
                    for var in behavioral_vars:
                        if var in weights:
                            st.write(f"• {var.replace('_', ' ').title()}: {weights[var]:.1%}")
                    
                    # Employment Stability
                    st.write(f"**Employment Stability ({employment_total:.1%}):**")
                    employment_vars = ['job_type', 'employment_tenure', 'company_stability']
                    for var in employment_vars:
                        if var in weights:
                            st.write(f"• {var.replace('_', ' ').title()}: {weights[var]:.1%}")
                    
                    # Banking Behavior
                    st.write(f"**Banking Behavior ({banking_total:.1%}):**")
                    banking_vars = ['account_vintage', 'avg_monthly_balance', 'bounce_frequency']
                    for var in banking_vars:
                        if var in weights:
                            st.write(f"• {var.replace('_', ' ').title()}: {weights[var]:.1%}")
                    
                    # Geographic & Social
                    st.write(f"**Geographic & Social ({geographic_total:.1%}):**")
                    geo_vars = ['geographic_risk', 'mobile_number_vintage', 'digital_engagement']
                    for var in geo_vars:
                        if var in weights:
                            st.write(f"• {var.replace('_', ' ').title()}: {weights[var]:.1%}")
                    
                    # Exposure & Intent
                    st.write(f"**Exposure & Intent ({exposure_total:.1%}):**")
                    exposure_vars = ['unsecured_loan_amount', 'outstanding_amount_percent', 'our_lender_exposure', 'channel_type']
                    for var in exposure_vars:
                        if var in weights:
                            st.write(f"• {var.replace('_', ' ').title()}: {weights[var]:.1%}")
                    
                    # Button to restore this configuration
                    if st.button(f"🔄 Restore Configuration {i}", key=f"restore_{i}"):
                        save_weights(weights)
                        st.session_state.weights_updated = True
                        st.success(f"Configuration {i} restored successfully!")
                        st.rerun()
        else:
            st.info("No configuration history available yet. Save a configuration to start tracking history.")