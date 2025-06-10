"""
Enhanced UI for Modular Scoring Engine with Dynamic Field Mapping
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any, List
from modular_scoring_engine import ModularScoringEngine
from field_mapping_manager import FieldMappingManager, get_dsa_mapping_options
import json

def render_modular_individual_scoring():
    """Render individual scoring with modular engine, dynamic field mapping and additional data sources"""
    st.header("🎯 Individual Application Scoring (Modular Engine)")
    
    # Get company ID from session state
    company_id = st.session_state.get('company_id')
    
    # Initialize engines
    modular_engine = ModularScoringEngine()
    mapping_manager = FieldMappingManager()
    
    # Initialize clean dynamic system for additional data sources
    has_additional_sources = False
    if company_id:
        from clean_dynamic_system import CleanDynamicSystem
        clean_system = CleanDynamicSystem(company_id)
        selected_sources = clean_system.get_company_additional_sources()
        
        # Only show enhancement if company has additional data sources
        if selected_sources:
            has_additional_sources = True
            additional_weight = clean_system.calculate_dynamic_weight(selected_sources)
            st.info(f"✨ Enhanced Modular Scorecard: Your organization has access to {len(selected_sources)} additional data sources with {additional_weight:.1f}% additional weight")
    
    # DSA Selection
    col1, col2 = st.columns(2)
    with col1:
        use_dsa_mapping = st.checkbox("Use DSA Field Mapping")
    
    dsa_id = None
    field_mapping = {}
    
    if use_dsa_mapping:
        with col2:
            dsa_options = get_dsa_mapping_options()
            if dsa_options:
                selected_dsa = st.selectbox("Select DSA Partner", options=list(dsa_options.keys()))
                dsa_id = dsa_options.get(selected_dsa)
                
                # Get the field mapping for this DSA
                if dsa_id:
                    mapping_data = mapping_manager.get_mapping(dsa_id)
                    if mapping_data:
                        field_mapping = mapping_data.get('mapping', {})
                        
                        # Show mapping info
                        with st.expander(f"Field Mappings for {selected_dsa}", expanded=False):
                            st.write(f"**Created:** {mapping_data.get('created_at', 'Unknown')}")
                            st.write(f"**Last Updated:** {mapping_data.get('updated_at', 'Unknown')}")
                            st.write("**Field Mappings:**")
                            if field_mapping:
                                for std_field, custom_field in field_mapping.items():
                                    st.write(f"• {std_field.replace('_', ' ').title()} → {custom_field}")
                                st.success(f"✓ {len(field_mapping)} field mappings loaded successfully")
                            else:
                                st.warning("No field mappings found in data")
                    else:
                        st.warning(f"No field mapping found for {selected_dsa}")
            else:
                st.warning("No DSA mappings configured. Go to Field Mapping Management first.")
                return
    
    # Helper function to get display label
    def get_field_label(standard_field, standard_field_key=None):
        if use_dsa_mapping and field_mapping and standard_field_key and standard_field_key in field_mapping:
            mapped_label = field_mapping[standard_field_key]
            st.write(f"DEBUG: Using mapped label '{mapped_label}' for '{standard_field_key}'")  # Debug line
            return mapped_label
        return standard_field
    
    # Application Data Input
    st.subheader("Application Data")
    
    if use_dsa_mapping and field_mapping:
        # Show ONLY DSA mapped fields
        st.success(f"✅ Using DSA custom fields ({len(field_mapping)} fields)")
        
        col1, col2 = st.columns(2)
        form_data = {}
        field_count = 0
        
        for custom_name, standard_field in field_mapping.items():
            target_col = col1 if field_count % 2 == 0 else col2
            
            with target_col:
                # Dynamic field creation based on standard field type
                if "credit" in standard_field.lower() or "score" in standard_field.lower():
                    form_data[custom_name] = st.number_input(
                        f"📊 {custom_name}",
                        min_value=300,
                        max_value=900,
                        value=650,
                        help=f"Credit score field: {standard_field}"
                    )
                elif "income" in standard_field.lower() or "salary" in standard_field.lower():
                    form_data[custom_name] = st.number_input(
                        f"💰 {custom_name} (₹)",
                        min_value=0,
                        value=50000,
                        help=f"Income field: {standard_field}"
                    )
                elif "dpd" in standard_field.lower() or "overdue" in standard_field.lower() or "past_due" in standard_field.lower():
                    form_data[custom_name] = st.number_input(
                        f"⚠️ {custom_name}",
                        min_value=0,
                        max_value=12,
                        value=0,
                        help=f"Past due field: {standard_field}"
                    )
                elif "default" in standard_field.lower() or "loan" in standard_field.lower() and "count" in standard_field.lower():
                    form_data[custom_name] = st.number_input(
                        f"🔴 {custom_name}",
                        min_value=0,
                        max_value=50,
                        value=0,
                        help=f"Default count field: {standard_field}"
                    )
                elif "mix" in standard_field.lower() or "type" in standard_field.lower():
                    form_data[custom_name] = st.selectbox(
                        f"🏦 {custom_name}",
                        ["personal", "business", "home", "auto", "education", "credit_card"],
                        help=f"Loan type field: {standard_field}"
                    )
                elif "enquiry" in standard_field.lower() or "inquiry" in standard_field.lower():
                    form_data[custom_name] = st.number_input(
                        f"🔍 {custom_name}",
                        min_value=0,
                        max_value=20,
                        value=0,
                        help=f"Enquiry field: {standard_field}"
                    )
                elif "foir" in standard_field.lower() or "ratio" in standard_field.lower():
                    form_data[custom_name] = st.number_input(
                        f"📈 {custom_name} (%)",
                        min_value=0.0,
                        max_value=100.0,
                        value=35.0,
                        help=f"Ratio field: {standard_field}"
                    )
                elif "vintage" in standard_field.lower() or "tenure" in standard_field.lower():
                    form_data[custom_name] = st.number_input(
                        f"📅 {custom_name} (months)",
                        min_value=0,
                        value=24,
                        help=f"Duration field: {standard_field}"
                    )
                elif "balance" in standard_field.lower() or "amount" in standard_field.lower():
                    form_data[custom_name] = st.number_input(
                        f"💳 {custom_name} (₹)",
                        min_value=0,
                        value=25000,
                        help=f"Amount field: {standard_field}"
                    )
                elif "job" in standard_field.lower() or "employment" in standard_field.lower():
                    form_data[custom_name] = st.selectbox(
                        f"💼 {custom_name}",
                        ["government", "private", "self_employed", "business"],
                        help=f"Employment field: {standard_field}"
                    )
                else:
                    # Default text input for unknown field types
                    form_data[custom_name] = st.text_input(
                        f"📝 {custom_name}",
                        value="",
                        help=f"Custom field: {standard_field}"
                    )
            
            field_count += 1
    
    else:
        # Show standard fields when DSA mapping is not used
        with st.expander("Core Credit Variables", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                credit_score = st.number_input(
                    "Credit Score", 
                    min_value=300, max_value=900, value=650
                )
                foir = st.number_input(
                    "FOIR (%)", 
                    min_value=0.0, max_value=100.0, value=35.0
                )
                dpd30plus = st.number_input(
                    "DPD 30+", 
                    min_value=0, max_value=10, value=0
                )
            
            with col2:
                enquiry_count = st.number_input(
                    "Enquiry Count", 
                    min_value=0, max_value=20, value=3
                )
                monthly_income = st.number_input(
                    "Monthly Income (₹)", 
                    min_value=0, value=50000
                )
        
        # Employment & Banking (only show for standard mode)
        with st.expander("Employment & Banking Details"):
            col1, col2 = st.columns(2)
            
            with col1:
                job_type = st.selectbox(
                    "Job Type", 
                    ["government", "psu", "mnc", "large_corporate", "mid_size_company", "small_company", "self_employed"]
                )
                employment_tenure = st.number_input(
                    "Employment Tenure (months)", 
                    min_value=0, value=24
                )
                account_vintage = st.number_input(
                    "Account Vintage (months)", 
                    min_value=0, value=36
                )
            
            with col2:
                company_stability = st.selectbox(
                    "Company Stability", 
                    ["excellent", "good", "average", "below_average", "poor"]
                )
                avg_monthly_balance = st.number_input(
                    "Avg Monthly Balance (₹)", 
                    min_value=0, value=25000
                )
                bounce_frequency = st.number_input(
                    "Bounce Frequency", 
                    min_value=0, value=1
                )
        
        # Additional Variables (only show for standard mode)
        with st.expander("Additional Risk Variables"):
            col1, col2 = st.columns(2)
            
            with col1:
                credit_vintage = st.number_input("Credit Vintage (months)", min_value=0, value=48)
                mobile_number_vintage = st.number_input("Mobile Vintage (months)", min_value=0, value=60)
                digital_engagement = st.number_input("Digital Engagement Score", min_value=0.0, max_value=100.0, value=65.0)
                unsecured_loan_amount = st.number_input("Unsecured Loan Amount (₹)", min_value=0, value=200000)
            
            with col2:
                loan_completion_ratio = st.number_input("Loan Completion Ratio", min_value=0.0, max_value=1.0, value=0.85)
                defaulted_loans = st.number_input("Defaulted Loans", min_value=0, value=0)
                outstanding_amount_percent = st.number_input("Outstanding Amount %", min_value=0.0, max_value=100.0, value=45.0)
                our_lender_exposure = st.number_input("Our Lender Exposure (₹)", min_value=0, value=0)
        
        # Render clean dynamic additional data source fields ONLY if company has them configured
        additional_data = {}
        if has_additional_sources:
            from clean_dynamic_system import render_clean_dynamic_scorecard
            additional_data = render_clean_dynamic_scorecard(company_id)
    
    # Score Application
    if st.button("Score Application", type="primary"):
        # Prepare application data
        applicant_data = {
            "credit_score": credit_score,
            "foir": foir,
            "dpd30plus": dpd30plus,
            "enquiry_count": enquiry_count,
            "monthly_income": monthly_income,
            "job_type": job_type,
            "employment_tenure": employment_tenure,
            "company_stability": company_stability,
            "account_vintage": account_vintage,
            "avg_monthly_balance": avg_monthly_balance,
            "bounce_frequency": bounce_frequency,
            "credit_vintage": credit_vintage,
            "mobile_number_vintage": mobile_number_vintage,
            "digital_engagement": digital_engagement,
            "unsecured_loan_amount": unsecured_loan_amount,
            "loan_completion_ratio": loan_completion_ratio,
            "defaulted_loans": defaulted_loans,
            "outstanding_amount_percent": outstanding_amount_percent,
            "our_lender_exposure": our_lender_exposure,
            "loan_mix_type": "mixed_balanced",
            "geographic_risk": "low",
            "channel_type": "direct"
        }
        
        # Add additional data source fields
        applicant_data.update(additional_data)
        
        # Score using modular engine (enhanced with additional data sources if available)
        if company_id and has_additional_sources:
            # Use clean dynamic system for scoring with additional data sources
            from clean_dynamic_system import CleanDynamicSystem
            clean_system = CleanDynamicSystem(company_id)
            additional_result = clean_system.calculate_additional_score(additional_data)
            
            # Use Legacy Engine with company ID for comprehensive scoring
            from scoring_engine import LoanScoringEngine
            legacy_engine = LoanScoringEngine(company_id=company_id)
            result = legacy_engine.score_application(applicant_data)
            
            # Convert to modular format for display consistency
            result = {
                "final_score": result['final_score'],
                "bucket": result['final_bucket'],
                "decision": result['decision'],
                "total_weight": "Enhanced",
                "variable_breakdown": result.get('variable_scores', {}),
                "additional_breakdown": result.get('additional_score_breakdown', {})
            }
        else:
            # Use standard modular engine
            result = modular_engine.score_application_modular(applicant_data, dsa_id)
        
        # Display results
        render_modular_scoring_results(result, applicant_data)

def render_modular_scoring_results(result: Dict[str, Any], applicant_data: Dict[str, Any]):
    """Render modular scoring results with transparency"""
    
    st.subheader("📊 Scoring Results")
    
    # Main results
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Final Score", f"{result['final_score']:.1f}%")
    
    with col2:
        bucket_color = {"A": "🟢", "B": "🟡", "C": "🟠", "D": "🔴"}
        st.metric("Risk Bucket", f"{bucket_color.get(result['bucket'], '⚪')} {result['bucket']}")
    
    with col3:
        decision_color = {
            "Approve": "✅",
            "Conditional Approve": "⚠️", 
            "Review Required": "⏳",
            "Decline": "❌"
        }
        st.metric("Decision", f"{decision_color.get(result['decision'], '❓')} {result['decision']}")
    
    with col4:
        if result.get('additional_breakdown') and result['additional_breakdown'].get('additional_score', 0) > 0:
            st.metric("Additional Weight", f"{result['additional_breakdown']['additional_weight']:.1f}%")
        else:
            st.metric("Total Weight", result['total_weight'])
    
    # Enhanced metrics for additional data sources
    if result.get('additional_breakdown') and result['additional_breakdown'].get('additional_score', 0) > 0:
        st.subheader("📈 Enhanced Scoring Details")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Base Score", f"{result.get('base_score', result['final_score'] - result['additional_breakdown']['additional_score']):.1f}")
        with col2:
            st.metric("Additional Score", f"{result['additional_breakdown']['additional_score']:.1f}")
        with col3:
            st.metric("Enhancement Factor", f"{(result['additional_breakdown']['additional_score'] / result['final_score'] * 100):.1f}%")
    
    # Variable-wise breakdown
    st.subheader("🔍 Variable-wise Score Breakdown")
    
    # Create detailed breakdown
    breakdown_data = []
    for var_name, details in result['variable_details'].items():
        breakdown_data.append({
            "Variable": var_name.replace('_', ' ').title(),
            "Input Value": details['value'],
            "Score": f"{details['score']:.2f}",
            "Weight": details['weight'],
            "Weighted Score": f"{details['weighted_score']:.2f}",
            "Status": details['reason']
        })
    
    breakdown_df = pd.DataFrame(breakdown_data)
    
    # Color code by status
    def highlight_status(row):
        if row['Status'] == 'Scored':
            return ['background-color: #d4edda'] * len(row)
        elif row['Status'] == 'Fallback applied':
            return ['background-color: #fff3cd'] * len(row)
        else:
            return ['background-color: #f8d7da'] * len(row)
    
    st.dataframe(breakdown_df.style.apply(highlight_status, axis=1), use_container_width=True)
    
    # Visual breakdown
    col1, col2 = st.columns(2)
    
    with col1:
        # Score distribution pie chart
        fig_pie = px.pie(
            values=[details['weighted_score'] for details in result['variable_details'].values()],
            names=[var.replace('_', ' ').title() for var in result['variable_details'].keys()],
            title="Score Contribution by Variable"
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # Status distribution
        status_counts = breakdown_df['Status'].value_counts()
        fig_status = px.bar(
            x=status_counts.index,
            y=status_counts.values,
            title="Variable Status Distribution",
            color=status_counts.index,
            color_discrete_map={
                'Scored': '#28a745',
                'Fallback applied': '#ffc107',
                'Missing field': '#dc3545'
            }
        )
        st.plotly_chart(fig_status, use_container_width=True)

def render_modular_bulk_upload():
    """Render bulk upload with modular scoring engine"""
    st.header("📁 Bulk Upload (Modular Engine)")
    
    # Initialize engines
    modular_engine = ModularScoringEngine()
    
    # DSA Selection
    col1, col2 = st.columns(2)
    with col1:
        use_dsa_mapping = st.checkbox("Use DSA Field Mapping", value=True)
    
    dsa_id = None
    if use_dsa_mapping:
        with col2:
            dsa_options = get_dsa_mapping_options()
            if dsa_options:
                selected_dsa = st.selectbox("Select DSA Partner", options=list(dsa_options.keys()))
                dsa_id = dsa_options.get(selected_dsa)
            else:
                st.warning("No DSA mappings configured. Processing with standard field names.")
    
    # File upload
    uploaded_file = st.file_uploader("Upload CSV file", type=['csv'])
    
    if uploaded_file:
        try:
            # Read CSV
            df = pd.read_csv(uploaded_file)
            
            st.success(f"File uploaded successfully! Found {len(df)} applications.")
            
            # Show original columns
            with st.expander("Original CSV Columns"):
                st.write(list(df.columns))
            
            # Apply field mapping if selected
            if dsa_id:
                mapping_manager = FieldMappingManager()
                mapping = mapping_manager.get_mapping(dsa_id)
                if mapping:
                    df_mapped = df.rename(columns=mapping)
                    with st.expander("After Field Mapping"):
                        st.write(list(df_mapped.columns))
                        mapped_vars = [col for col in df_mapped.columns if col in modular_engine.scoring_registry.keys()]
                        st.write(f"Mapped variables: {len(mapped_vars)}/{len(modular_engine.scoring_registry)}")
                    df = df_mapped
            
            # Preview data
            with st.expander("Data Preview"):
                st.dataframe(df.head(10), use_container_width=True)
            
            # Processing options
            col1, col2 = st.columns(2)
            with col1:
                batch_size = st.slider("Batch Size", min_value=100, max_value=5000, value=1000)
            with col2:
                include_details = st.checkbox("Include Variable Details", value=True)
            
            # Process applications
            if st.button("Process Applications", type="primary"):
                with st.spinner("Processing applications..."):
                    progress_bar = st.progress(0)
                    
                    # Process in batches
                    all_results = []
                    total_batches = (len(df) + batch_size - 1) // batch_size
                    
                    for i in range(0, len(df), batch_size):
                        batch_df = df.iloc[i:i+batch_size].copy()
                        
                        # Process batch
                        batch_results = modular_engine.process_bulk_applications_modular(batch_df, dsa_id)
                        all_results.append(batch_results)
                        
                        # Update progress
                        progress = (i + batch_size) / len(df)
                        progress_bar.progress(min(progress, 1.0))
                    
                    # Combine results
                    final_results = pd.concat(all_results, ignore_index=True)
                    
                    progress_bar.progress(1.0)
                    st.success(f"Processing complete! Processed {len(final_results)} applications.")
                    
                    # Display results
                    render_modular_bulk_results(final_results, include_details)
                    
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")

def render_modular_bulk_results(results_df: pd.DataFrame, include_details: bool = True):
    """Render bulk processing results with analytics"""
    
    st.subheader("📈 Processing Results")
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Applications", len(results_df))
    
    with col2:
        avg_score = results_df['final_score'].mean()
        st.metric("Average Score", f"{avg_score:.1f}%")
    
    with col3:
        approval_rate = len(results_df[results_df['decision'].isin(['Approve', 'Conditional Approve'])]) / len(results_df) * 100
        st.metric("Approval Rate", f"{approval_rate:.1f}%")
    
    with col4:
        modular_count = len(results_df[results_df['scoring_method'] == 'modular'])
        st.metric("Modular Scored", modular_count)
    
    # Distribution charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Score distribution
        fig_hist = px.histogram(
            results_df, 
            x='final_score', 
            nbins=20,
            title="Score Distribution",
            labels={'final_score': 'Final Score (%)', 'count': 'Number of Applications'}
        )
        st.plotly_chart(fig_hist, use_container_width=True)
    
    with col2:
        # Decision distribution
        decision_counts = results_df['decision'].value_counts()
        fig_pie = px.pie(
            values=decision_counts.values,
            names=decision_counts.index,
            title="Decision Distribution"
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    # Bucket analysis
    bucket_analysis = results_df.groupby('bucket').agg({
        'final_score': ['count', 'mean', 'std'],
        'decision': lambda x: x.value_counts().to_dict()
    }).round(2)
    
    st.subheader("Risk Bucket Analysis")
    st.dataframe(bucket_analysis, use_container_width=True)
    
    # Detailed results
    if include_details:
        st.subheader("Detailed Results")
        
        # Filter options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            bucket_filter = st.multiselect("Filter by Bucket", 
                                         options=results_df['bucket'].unique(),
                                         default=results_df['bucket'].unique())
        
        with col2:
            decision_filter = st.multiselect("Filter by Decision",
                                           options=results_df['decision'].unique(),
                                           default=results_df['decision'].unique())
        
        with col3:
            score_range = st.slider("Score Range", 
                                  min_value=0.0, 
                                  max_value=100.0, 
                                  value=(0.0, 100.0))
        
        # Apply filters
        filtered_df = results_df[
            (results_df['bucket'].isin(bucket_filter)) &
            (results_df['decision'].isin(decision_filter)) &
            (results_df['final_score'] >= score_range[0]) &
            (results_df['final_score'] <= score_range[1])
        ]
        
        st.dataframe(filtered_df, use_container_width=True)
        
        # Download option
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="Download Results CSV",
            data=csv,
            file_name=f"modular_scoring_results_{len(filtered_df)}_applications.csv",
            mime="text/csv"
        )

def render_modular_scoring_config():
    """Render modular scoring configuration display"""
    st.header("⚙️ Modular Scoring Configuration")
    
    modular_engine = ModularScoringEngine()
    config = modular_engine.get_scoring_configuration()
    
    # Overview
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Variables", config['total_variables'])
    
    with col2:
        st.metric("Total Weight", config['total_weight'])
    
    with col3:
        st.metric("Scoring Method", "Modular")
    
    # Variable details
    st.subheader("Variable Configuration")
    
    config_data = []
    for var_name, var_config in config['variables'].items():
        config_data.append({
            "Variable": var_name.replace('_', ' ').title(),
            "Weight": var_config['weight'],
            "Fallback Score": var_config['fallback_score'],
            "Function": var_config['function_name']
        })
    
    config_df = pd.DataFrame(config_data)
    st.dataframe(config_df, use_container_width=True)
    
    # Weight distribution chart
    fig = px.bar(
        config_df,
        x='Variable',
        y='Weight',
        title="Weight Distribution Across Variables",
        color='Weight',
        color_continuous_scale='viridis'
    )
    fig.update_xaxes(tickangle=45)
    st.plotly_chart(fig, use_container_width=True)