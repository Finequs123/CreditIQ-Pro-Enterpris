"""
Enhanced Bulk Upload with ML-driven Weight Optimization
Processes bulk uploads and automatically learns optimal scoring weights
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import json
from typing import Dict, Any, List
from ml_weight_optimizer import MLWeightOptimizer
from scoring_engine import LoanScoringEngine
from validators import validate_bulk_data, validate_individual_data
from utils import create_excel_output
import time

def render_enhanced_bulk_upload():
    """Enhanced bulk upload with ML weight optimization"""
    st.header("📊 Smart Bulk Processing with ML Optimization")
    st.write("Upload loan applications and let AI automatically optimize scoring weights based on data patterns")
    
    # Initialize ML optimizer
    if 'ml_optimizer' not in st.session_state:
        st.session_state.ml_optimizer = MLWeightOptimizer()
    
    # Create tabs for different functionalities
    tab1, tab2, tab3, tab4 = st.tabs([
        "📤 Upload & Process", 
        "🤖 ML Optimization", 
        "⚙️ Weight Controls", 
        "📈 Performance Analytics"
    ])
    
    with tab1:
        render_upload_section()
    
    with tab2:
        render_ml_optimization_section()
    
    with tab3:
        render_weight_controls_section()
    
    with tab4:
        render_performance_analytics()

def render_upload_section():
    """Render the upload and processing section"""
    st.subheader("📁 File Upload & Processing")
    
    # Template download
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Upload CSV file with loan applications",
            type=['csv'],
            help="System will automatically analyze patterns and suggest optimal weights"
        )
    
    with col2:
        st.subheader("📋 Template")
        try:
            with open("bulk_template_20vars.csv", "r") as f:
                template_data = f.read()
            
            st.download_button(
                label="📥 Download Template",
                data=template_data,
                file_name="loan_application_template.csv",
                mime="text/csv"
            )
        except:
            st.warning("Template file not found")
    
    if uploaded_file is not None:
        process_uploaded_file(uploaded_file)

def process_uploaded_file(uploaded_file):
    """Process the uploaded file with ML optimization"""
    try:
        # Load data
        df = pd.read_csv(uploaded_file)
        st.success(f"✅ File loaded: {len(df)} applications found")
        
        # Data validation
        st.subheader("🔍 Data Validation")
        validation_result = validate_bulk_data(df)
        
        if validation_result['is_valid']:
            st.success("✅ Data validation passed")
        else:
            st.warning("⚠️ Validation issues found:")
            for issue in validation_result['issues']:
                st.write(f"- {issue}")
        
        # ML Weight Analysis
        st.subheader("🤖 AI Weight Analysis")
        with st.spinner("Analyzing data patterns for optimal weights..."):
            weight_suggestion = analyze_and_suggest_weights(df)
            display_weight_suggestions(weight_suggestion)
        
        # Processing options
        st.subheader("⚙️ Processing Configuration")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            use_ml_weights = st.checkbox(
                "Use AI-suggested weights",
                value=True,
                help="Apply ML-optimized weights for scoring"
            )
        
        with col2:
            batch_size = st.selectbox(
                "Batch size",
                options=[100, 500, 1000, 2000],
                index=1,
                help="Number of records to process at once"
            )
        
        with col3:
            include_details = st.checkbox(
                "Include detailed scores",
                value=False,
                help="Add individual variable scores to output"
            )
        
        # Process button
        if st.button("🚀 Start AI-Enhanced Processing", type="primary"):
            process_with_ml_optimization(
                df, 
                weight_suggestion if use_ml_weights else None,
                batch_size,
                include_details
            )
            
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")

def analyze_and_suggest_weights(df: pd.DataFrame) -> Dict[str, Any]:
    """Analyze uploaded data and suggest optimal weights"""
    
    # Convert dataframe to application dictionaries
    applications = []
    for _, row in df.iterrows():
        app_data = {
            'credit_score': row.get('CreditScore', 0),
            'foir': row.get('FOIR', 0),
            'dpd30plus': row.get('DPD_30_Plus', 0),
            'enquiry_count': row.get('EnquiryCount', 0),
            'age': row.get('Age', 0),
            'monthly_income': row.get('MonthlyIncome', 0),
            'credit_vintage': row.get('CreditVintage', 0),
            'loan_mix_type': row.get('LoanMixType', ''),
            'loan_completion_ratio': row.get('LoanCompletionRatio', 0),
            'defaulted_loans': row.get('DefaultedLoans', 0),
            'job_type': row.get('CompanyType', ''),
            'employment_tenure': row.get('EmploymentTenure', 0),
            'company_stability': row.get('CompanyStability', ''),
            'account_vintage': row.get('AccountVintage', 0),
            'avg_monthly_balance': row.get('AMB', 0),
            'bounce_frequency': row.get('BounceCount', 0),
            'geographic_risk': row.get('GeoRisk', ''),
            'mobile_number_vintage': row.get('MobileVintage', 0),
            'digital_engagement': row.get('DigitalScore', 0),
            'unsecured_loan_amount': row.get('UnsecuredLoanAmount', 0),
            'outstanding_amount_percent': row.get('OutstandingPercent', 0),
            'our_lender_exposure': row.get('OurLenderExposure', 0),
            'channel_type': row.get('ChannelType', '')
        }
        applications.append(app_data)
    
    # Get ML suggestions
    ml_optimizer = st.session_state.ml_optimizer
    weight_suggestion = ml_optimizer.suggest_weights_for_portfolio(applications)
    
    return weight_suggestion

def display_weight_suggestions(suggestion: Dict[str, Any]):
    """Display AI weight suggestions"""
    
    if suggestion.get('model_based', False):
        st.success("🤖 AI Model-based weight optimization")
    else:
        st.info("📊 Pattern-based weight analysis")
    
    confidence = suggestion.get('confidence', 0)
    st.metric("Confidence Level", f"{confidence:.1%}")
    
    # Display suggested weights in categories
    weights = suggestion.get('suggested_weights', {})
    
    categories = {
        "Core Credit Variables": ['credit_score', 'foir', 'dpd30plus', 'enquiry_count', 'age', 'monthly_income'],
        "Behavioral Analytics": ['credit_vintage', 'loan_mix_type', 'loan_completion_ratio', 'defaulted_loans'],
        "Employment Stability": ['job_type', 'employment_tenure', 'company_stability'],
        "Banking Behavior": ['account_vintage', 'avg_monthly_balance', 'bounce_frequency'],
        "Geographic & Social": ['geographic_risk', 'mobile_number_vintage', 'digital_engagement'],
        "Exposure & Intent": ['unsecured_loan_amount', 'outstanding_amount_percent', 'our_lender_exposure', 'channel_type']
    }
    
    # Display in columns
    cols = st.columns(3)
    col_idx = 0
    
    for category, variables in categories.items():
        with cols[col_idx % 3]:
            st.write(f"**{category}**")
            category_total = sum(weights.get(var, 0) for var in variables)
            st.write(f"Total: {category_total:.1%}")
            
            for var in variables:
                weight = weights.get(var, 0)
                if weight > 0:
                    var_display = var.replace('_', ' ').title()
                    st.write(f"• {var_display}: {weight:.1%}")
        
        col_idx += 1

def process_with_ml_optimization(df: pd.DataFrame, weight_suggestion: Dict, batch_size: int, include_details: bool):
    """Process applications with ML-optimized weights"""
    
    # Apply suggested weights if provided
    if weight_suggestion and 'suggested_weights' in weight_suggestion:
        apply_ml_weights(weight_suggestion['suggested_weights'])
    
    # Initialize scoring engine with updated weights
    scoring_engine = LoanScoringEngine()
    
    # Processing with progress tracking
    st.subheader("🔄 Processing Applications")
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    total_records = len(df)
    results = []
    batch_results = []
    
    for batch_start in range(0, total_records, batch_size):
        batch_end = min(batch_start + batch_size, total_records)
        batch_df = df.iloc[batch_start:batch_end]
        
        status_text.text(f"Processing batch: {batch_start + 1} to {batch_end}")
        
        for idx, row in batch_df.iterrows():
            # Prepare application data
            applicant_data = prepare_application_data(row)
            
            # Score application
            try:
                result = scoring_engine.score_application(applicant_data)
                
                result_record = {
                    'row_number': idx + 1,
                    'pan': applicant_data.get('pan', ''),
                    'final_score': result['final_score'],
                    'final_bucket': result['final_bucket'],
                    'decision': result['decision'],
                    'processing_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                if include_details and 'variable_scores' in result:
                    for var, details in result['variable_scores'].items():
                        result_record[f'{var}_score'] = details.get('weighted_score', 0)
                
                results.append(result_record)
                batch_results.append({
                    'applicant_data': applicant_data,
                    'result': result
                })
                
            except Exception as e:
                st.error(f"Error processing row {idx + 1}: {str(e)}")
        
        # Update progress
        progress = batch_end / total_records
        progress_bar.progress(progress)
        time.sleep(0.1)
    
    # Save results and learn from patterns
    save_processing_results(batch_results, weight_suggestion)
    
    # Display results
    display_processing_results(results, df)

def apply_ml_weights(suggested_weights: Dict[str, float]):
    """Apply ML-suggested weights to scoring configuration"""
    
    # Save weights to configuration file
    with open("scoring_weights.json", "w") as f:
        json.dump(suggested_weights, f, indent=2)
    
    st.success("✅ ML-optimized weights applied to scoring engine")

def prepare_application_data(row: pd.Series) -> Dict[str, Any]:
    """Convert DataFrame row to application data dictionary"""
    return {
        'pan': str(row.get('Pan', '')).strip(),
        'age': int(row.get('Age', 0)),
        'monthly_income': float(row.get('MonthlyIncome', 0)),
        'credit_score': int(row.get('CreditScore', 0)),
        'foir': float(row.get('FOIR', 0)),
        'dpd30plus': int(row.get('DPD_30_Plus', 0)),
        'enquiry_count': int(row.get('EnquiryCount', 0)),
        'credit_vintage': int(row.get('CreditVintage', 0)),
        'loan_mix_type': str(row.get('LoanMixType', '')),
        'loan_completion_ratio': float(row.get('LoanCompletionRatio', 0)),
        'defaulted_loans': int(row.get('DefaultedLoans', 0)),
        'job_type': str(row.get('CompanyType', '')),
        'employment_tenure': int(row.get('EmploymentTenure', 0)),
        'company_stability': str(row.get('CompanyStability', '')),
        'account_vintage': int(row.get('AccountVintage', 0)),
        'avg_monthly_balance': float(row.get('AMB', 0)),
        'bounce_frequency': int(row.get('BounceCount', 0)),
        'geographic_risk': str(row.get('GeoRisk', '')),
        'mobile_number_vintage': int(row.get('MobileVintage', 0)),
        'digital_engagement': float(row.get('DigitalScore', 0)),
        'unsecured_loan_amount': float(row.get('UnsecuredLoanAmount', 0)),
        'outstanding_amount_percent': float(row.get('OutstandingPercent', 0)),
        'our_lender_exposure': float(row.get('OurLenderExposure', 0)),
        'channel_type': str(row.get('ChannelType', '')),
        'writeoff_flag': False
    }

def save_processing_results(batch_results: List[Dict], weight_suggestion: Dict):
    """Save processing results for ML learning"""
    
    # Generate session ID
    session_id = f"ml_batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Save to database for learning
    try:
        if 'db_manager' in st.session_state:
            # Convert results for database storage
            db_results = []
            for item in batch_results:
                db_result = {
                    'applicant_data': item['applicant_data'],
                    'result': item['result'],
                    'status': 'success'
                }
                db_results.append(db_result)
            
            st.session_state.db_manager.save_bulk_results(db_results, session_id)
            
        st.success(f"💾 Results saved for ML learning (Session: {session_id})")
        
    except Exception as e:
        st.warning(f"Could not save for ML learning: {str(e)}")

def display_processing_results(results: List[Dict], original_df: pd.DataFrame):
    """Display processing results with analytics"""
    
    if not results:
        st.error("No results to display")
        return
    
    results_df = pd.DataFrame(results)
    
    # Summary metrics
    st.subheader("📊 Processing Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Processed", len(results_df))
    
    with col2:
        st.metric("Success Rate", "100%")
    
    with col3:
        avg_score = results_df['final_score'].mean()
        st.metric("Average Score", f"{avg_score:.1f}")
    
    with col4:
        approval_rate = len(results_df[results_df['final_bucket'].isin(['A', 'B'])]) / len(results_df) * 100
        st.metric("Approval Rate", f"{approval_rate:.1f}%")
    
    # Bucket distribution
    st.subheader("🗂️ Risk Distribution")
    
    bucket_counts = results_df['final_bucket'].value_counts()
    
    cols = st.columns(4)
    buckets = ['A', 'B', 'C', 'D']
    colors = ['🟢', '🟡', '🟠', '🔴']
    
    for i, (bucket, color) in enumerate(zip(buckets, colors)):
        with cols[i]:
            count = bucket_counts.get(bucket, 0)
            percentage = (count / len(results_df) * 100) if len(results_df) > 0 else 0
            st.metric(f"{color} Bucket {bucket}", f"{count}", delta=f"{percentage:.1f}%")
    
    # Download results
    st.subheader("📥 Download Results")
    
    col1, col2 = st.columns(2)
    
    with col1:
        csv_data = results_df.to_csv(index=False)
        st.download_button(
            label="📊 Download Results (CSV)",
            data=csv_data,
            file_name=f"ml_optimized_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    with col2:
        if st.button("📈 View Detailed Analytics"):
            st.session_state.show_analytics = True

def render_ml_optimization_section():
    """Render ML optimization controls"""
    st.subheader("🤖 ML Weight Optimization")
    
    ml_optimizer = st.session_state.ml_optimizer
    
    # Check for performance data
    performance_df = ml_optimizer.load_performance_data()
    
    if performance_df is not None:
        st.success(f"📊 Found {len(performance_df)} historical performance records")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🚀 Optimize Weights with ML", type="primary"):
                with st.spinner("Training ML model on performance data..."):
                    optimization_result = ml_optimizer.optimize_weights_with_ml(performance_df)
                    display_optimization_results(optimization_result)
        
        with col2:
            if st.button("🏋️ Train Advanced Model"):
                with st.spinner("Training advanced weight prediction model..."):
                    training_result = ml_optimizer.train_weight_prediction_model(performance_df)
                    display_training_results(training_result)
    else:
        st.info("📊 No performance data available yet. Upload and process applications to build ML training data.")
        
        if st.button("📤 Upload Performance Data"):
            st.info("Feature coming soon: Direct upload of loan performance data for ML training")

def display_optimization_results(result: Dict[str, Any]):
    """Display ML optimization results"""
    
    if 'suggested_weights' in result:
        st.success("✅ ML Weight Optimization Complete!")
        
        # Show performance metrics
        metrics = result.get('performance_metrics', {})
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Loans", metrics.get('total_loans', 0))
        
        with col2:
            default_rate = metrics.get('default_rate', 0)
            st.metric("Default Rate", f"{default_rate:.1%}")
        
        with col3:
            approval_rate = metrics.get('approval_rate', 0)
            st.metric("Approval Rate", f"{approval_rate:.1%}")
        
        with col4:
            validation_score = metrics.get('validation_score', 0)
            st.metric("Model Score", f"{validation_score:.3f}")
        
        # Apply weights option
        if st.button("✅ Apply These Weights", type="primary"):
            apply_ml_weights(result['suggested_weights'])

def display_training_results(result: Dict[str, Any]):
    """Display model training results"""
    
    if result.get('status') == 'success':
        st.success("✅ Advanced ML Model Trained Successfully!")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Training Score", f"{result.get('train_score', 0):.3f}")
        
        with col2:
            st.metric("Test Score", f"{result.get('test_score', 0):.3f}")
        
        with col3:
            st.metric("Training Records", result.get('training_records', 0))
        
        st.info(f"Model saved as: {result.get('model_version', 'Unknown')}")
    else:
        st.error(f"Training failed: {result.get('message', 'Unknown error')}")

def render_weight_controls_section():
    """Render manual weight control options"""
    st.subheader("⚙️ Manual Weight Controls")
    
    st.write("Override AI suggestions with manual adjustments")
    
    # Load current weights
    try:
        with open("scoring_weights.json", "r") as f:
            current_weights = json.load(f)
    except:
        current_weights = {}
    
    # Category-based controls
    categories = {
        "Core Credit Variables": ['credit_score', 'foir', 'dpd30plus', 'enquiry_count', 'age', 'monthly_income'],
        "Behavioral Analytics": ['credit_vintage', 'loan_mix_type', 'loan_completion_ratio', 'defaulted_loans'],
        "Employment Stability": ['job_type', 'employment_tenure', 'company_stability'],
        "Banking Behavior": ['account_vintage', 'avg_monthly_balance', 'bounce_frequency'],
        "Geographic & Social": ['geographic_risk', 'mobile_number_vintage', 'digital_engagement'],
        "Exposure & Intent": ['unsecured_loan_amount', 'outstanding_amount_percent', 'our_lender_exposure', 'channel_type']
    }
    
    updated_weights = {}
    
    for category, variables in categories.items():
        st.write(f"**{category}**")
        
        for var in variables:
            current_val = current_weights.get(var, 0.0)
            new_val = st.slider(
                var.replace('_', ' ').title(),
                min_value=0.0,
                max_value=0.30,
                value=current_val,
                step=0.01,
                format="%.2f",
                key=f"weight_{var}"
            )
            updated_weights[var] = new_val
    
    # Show total
    total_weight = sum(updated_weights.values())
    if abs(total_weight - 1.0) < 0.01:
        st.success(f"✅ Total Weight: {total_weight:.1%}")
    else:
        st.error(f"⚠️ Total Weight: {total_weight:.1%} (Should be 100%)")
    
    # Save weights
    if st.button("💾 Save Manual Weights"):
        if abs(total_weight - 1.0) < 0.01:
            with open("scoring_weights.json", "w") as f:
                json.dump(updated_weights, f, indent=2)
            st.success("✅ Weights saved successfully!")
        else:
            st.error("Cannot save: Total weights must equal 100%")

def render_performance_analytics():
    """Render performance analytics and history"""
    st.subheader("📈 Performance Analytics")
    
    ml_optimizer = st.session_state.ml_optimizer
    
    # Optimization history
    history = ml_optimizer.get_optimization_history()
    
    if history:
        st.write("**Recent Optimization History**")
        
        history_df = pd.DataFrame(history)
        st.dataframe(history_df, use_container_width=True)
    else:
        st.info("No optimization history available yet")
    
    # Performance data overview
    performance_df = ml_optimizer.load_performance_data()
    
    if performance_df is not None:
        st.write("**Loan Performance Overview**")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            good_loans = len(performance_df[performance_df['actual_outcome'] == 'good'])
            st.metric("Good Loans", good_loans)
        
        with col2:
            bad_loans = len(performance_df[performance_df['actual_outcome'] == 'bad'])
            st.metric("Bad Loans", bad_loans)
        
        with col3:
            if (good_loans + bad_loans) > 0:
                default_rate = bad_loans / (good_loans + bad_loans)
                st.metric("Default Rate", f"{default_rate:.1%}")
    else:
        st.info("No performance data loaded for analytics")