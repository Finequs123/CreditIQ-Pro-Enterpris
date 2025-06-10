import streamlit as st
import json
import os

def render_weights_configuration():
    """Simple working weights configuration"""
    st.header("⚖️ Scoring Weights Configuration")
    
    # Default weights - Comprehensive 20-variable scorecard (Total = 100%)
    default_weights = {
        # Core Credit Variables (40% - Most Critical)
        "credit_score": 12,  # Highest individual weight
        "foir": 7,
        "dpd30plus": 6,
        "enquiry_count": 5,
        "age": 3,
        "monthly_income": 7,
        
        # Behavioral Analytics (25% - High Impact)
        "credit_vintage": 6,
        "loan_mix_type": 5,
        "loan_completion_ratio": 7,
        "defaulted_loans": 7,
        
        # Employment Stability (15% - Medium-High Impact)
        "job_type": 6,
        "employment_tenure": 5,
        "company_stability": 4,
        
        # Banking Behavior (10% - Medium Impact)
        "account_vintage": 3,
        "avg_monthly_balance": 4,
        "bounce_frequency": 3,
        
        # Geographic & Social Factors (5% - Lower Impact)
        "geographic_risk": 2,
        "mobile_number_vintage": 2,
        "digital_engagement": 1,
        
        # Exposure & Intent (5% - Contextual)
        "unsecured_loan_amount": 2,
        "outstanding_amount_percent": 1,
        "our_lender_exposure": 1,
        "channel_type": 1
    }
    
    st.write("Configure the weights for each scoring variable (percentages):")
    
    # Create tabs for organized layout
    tab1, tab2, tab3 = st.tabs(["🏦 Core Credit & Behavioral", "💼 Employment & Banking", "🌍 Geographic & Social"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🏦 Core Credit Variables (35%)")
            credit_score = st.slider("Credit Score", 0, 20, default_weights["credit_score"])
            foir = st.slider("FOIR", 0, 15, default_weights["foir"])
            dpd30plus = st.slider("DPD 30+", 0, 15, default_weights["dpd30plus"])
            enquiry_count = st.slider("Enquiry Count", 0, 10, default_weights["enquiry_count"])
            age = st.slider("Age", 0, 8, default_weights["age"])
            monthly_income = st.slider("Monthly Income", 0, 15, default_weights["monthly_income"])
            
        with col2:
            st.subheader("🧠 Behavioral Analytics (20%)")
            credit_vintage = st.slider("Credit Vintage", 0, 10, default_weights["credit_vintage"])
            loan_mix_type = st.slider("Loan Mix Type", 0, 10, default_weights["loan_mix_type"])
            loan_completion_ratio = st.slider("Completion Ratio", 0, 10, default_weights["loan_completion_ratio"])
            defaulted_loans = st.slider("Defaulted Loans", 0, 10, default_weights["defaulted_loans"])
    
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("💼 Employment Stability (15%)")
            job_type = st.slider("Job Type", 0, 10, default_weights["job_type"])
            employment_tenure = st.slider("Employment Tenure", 0, 8, default_weights["employment_tenure"])
            company_stability = st.slider("Company Stability", 0, 6, default_weights["company_stability"])
            
            st.subheader("💳 Banking Behavior (10%)")
            account_vintage = st.slider("Account Vintage", 0, 6, default_weights["account_vintage"])
            avg_monthly_balance = st.slider("Avg Monthly Balance", 0, 8, default_weights["avg_monthly_balance"])
            bounce_frequency = st.slider("Bounce Frequency", 0, 8, default_weights["bounce_frequency"])
        
        with col2:
            st.subheader("💰 Exposure & Intent (12%)")
            unsecured_loan_amount = st.slider("Unsecured Amount", 0, 8, default_weights["unsecured_loan_amount"])
            outstanding_amount_percent = st.slider("Outstanding %", 0, 8, default_weights["outstanding_amount_percent"])
            our_lender_exposure = st.slider("Our Exposure", 0, 5, default_weights["our_lender_exposure"])
            channel_type = st.slider("Channel Type", 0, 6, default_weights["channel_type"])
    
    with tab3:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🌍 Geographic & Social Factors (8%)")
            geographic_risk = st.slider("Geographic Risk", 0, 6, default_weights["geographic_risk"])
            mobile_number_vintage = st.slider("Mobile Number Vintage", 0, 4, default_weights["mobile_number_vintage"])
            digital_engagement = st.slider("Digital Engagement", 0, 4, default_weights["digital_engagement"])
    
    # Calculate total for all 20 variables
    total = (credit_score + foir + dpd30plus + enquiry_count + age + monthly_income + 
             credit_vintage + loan_mix_type + loan_completion_ratio + defaulted_loans +
             job_type + employment_tenure + company_stability + account_vintage + 
             avg_monthly_balance + bounce_frequency + geographic_risk + mobile_number_vintage +
             digital_engagement + unsecured_loan_amount + outstanding_amount_percent + 
             our_lender_exposure + channel_type)
    
    # Display total with color coding
    if total == 100:
        st.success(f"✅ Total Weight: {total}%")
    else:
        st.error(f"⚠️ Total Weight: {total}% (Should be 100%)")
    
    # Save button
    if st.button("💾 Save Configuration", type="primary"):
        config = {
            # Core Credit Variables
            "credit_score": credit_score / 100,
            "foir": foir / 100,
            "dpd30plus": dpd30plus / 100,
            "enquiry_count": enquiry_count / 100,
            "age": age / 100,
            "monthly_income": monthly_income / 100,
            # Behavioral Analytics
            "credit_vintage": credit_vintage / 100,
            "loan_mix_type": loan_mix_type / 100,
            "loan_completion_ratio": loan_completion_ratio / 100,
            "defaulted_loans": defaulted_loans / 100,
            # Employment Stability
            "job_type": job_type / 100,
            "employment_tenure": employment_tenure / 100,
            "company_stability": company_stability / 100,
            # Banking Behavior
            "account_vintage": account_vintage / 100,
            "avg_monthly_balance": avg_monthly_balance / 100,
            "bounce_frequency": bounce_frequency / 100,
            # Geographic & Social
            "geographic_risk": geographic_risk / 100,
            "mobile_number_vintage": mobile_number_vintage / 100,
            "digital_engagement": digital_engagement / 100,
            # Exposure & Intent
            "unsecured_loan_amount": unsecured_loan_amount / 100,
            "outstanding_amount_percent": outstanding_amount_percent / 100,
            "our_lender_exposure": our_lender_exposure / 100,
            "channel_type": channel_type / 100
        }
        
        with open("scoring_weights.json", "w") as f:
            json.dump(config, f, indent=2)
        
        st.success("Configuration saved successfully!")
    
    return True