import streamlit as st

# Configure page settings - MUST be first Streamlit command
st.set_page_config(
    page_title="LoanScoreAI v6.0",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import io
import sqlite3
from scoring_engine import LoanScoringEngine
from database import DatabaseManager
from utils import create_excel_output, validate_csv_columns
from validators import validate_individual_data
from login import render_login_page, check_authentication, logout

# Custom CSS for modern styling
def load_custom_css():
    st.markdown("""
    <style>
    .main > div {
        padding-top: 2rem;
    }
    
    .stSidebar {
        background: linear-gradient(180deg, #1e3a8a 0%, #3b82f6 100%);
    }
    
    .stSidebar .sidebar-content {
        background: transparent;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .success-card {
        background: linear-gradient(135deg, #4ade80 0%, #22c55e 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .warning-card {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .danger-card {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .header-title {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    .sub-header {
        color: #64748b;
        text-align: center;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    
    .score-display {
        background: linear-gradient(135deg, #8b5cf6 0%, #a855f7 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin: 1rem 0;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
    }
    
    .bucket-A { background: linear-gradient(135deg, #10b981 0%, #059669 100%); }
    .bucket-B { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); }
    .bucket-C { background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); }
    .bucket-D { background: linear-gradient(135deg, #6b7280 0%, #4b5563 100%); }
    
    .sidebar-title {
        color: white !important;
        font-size: 1.5rem !important;
        font-weight: 600 !important;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    .sidebar-text {
        color: #e5e7eb !important;
        font-size: 0.9rem;
    }
    
    div[data-testid="stSelectbox"] > div > div {
        background-color: #f8fafc;
        border-radius: 8px;
    }
    
    div[data-testid="stNumberInput"] > div > div > input {
        background-color: #f8fafc;
        border-radius: 8px;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    }
    
    .stDownloadButton > button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-weight: 600;
    }
    </style>
    """, unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'scoring_engine' not in st.session_state:
        st.session_state.scoring_engine = LoanScoringEngine()
    if 'db_manager' not in st.session_state:
        st.session_state.db_manager = DatabaseManager()

def render_sidebar():
    """Render the sidebar navigation"""
    st.sidebar.markdown('<h1 class="sidebar-title">🎯 LoanScoreAI v6.0</h1>', unsafe_allow_html=True)
    st.sidebar.markdown("---")
    
    # User info and logout
    if 'username' in st.session_state and st.session_state.username:
        st.sidebar.markdown(f'<div class="sidebar-text"><strong>👤 Welcome, {st.session_state.username}!</strong></div>', unsafe_allow_html=True)
        if st.sidebar.button("🚪 Logout", use_container_width=True):
            logout()
        st.sidebar.markdown("---")
    
    mode = st.sidebar.radio(
        "📊 **Select Mode**",
        ["🔍 Individual Scoring", "📁 Bulk Upload", "📈 Historical Data", "📚 Scoring Guide"],
        format_func=lambda x: x.split(" ", 1)[1]  # Remove emoji from display
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown('<div class="sidebar-text"><strong>About</strong><br>This AI driven scorecard assesses loan applicants, based on disbursement probability and customer\'s ability to complete the entire digital loan application journey.</div>', unsafe_allow_html=True)
    
    # Add some metrics to sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown('<div class="sidebar-text"><strong>📈 Quick Stats</strong></div>', unsafe_allow_html=True)
    
    # Clean up mode name for processing
    clean_mode = mode.split(" ", 1)[1] if " " in mode else mode
    return clean_mode

def render_individual_scoring():
    """Render individual loan application scoring interface"""
    st.markdown('<h1 class="header-title">🔍 Individual Loan Application Scoring</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Enter applicant details to get instant credit scoring and risk assessment</p>', unsafe_allow_html=True)
    
    with st.form("individual_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 👤 Basic Information")
            pan = st.text_input("🆔 PAN Number", placeholder="ABCDE1234F", help="Required field - 10 character alphanumeric")
            age = st.number_input("🎂 Age", min_value=18, max_value=80, value=30)
            monthly_income = st.number_input("💰 Monthly Income (₹)", min_value=0, value=25000, step=1000, help="Gross monthly income")
            
            st.markdown("### 📊 Credit Information")
            credit_score = st.number_input("📈 Credit Score", min_value=-1, max_value=900, value=650, help="Credit bureau score (-1 for no history)")
            foir = st.number_input("📉 FOIR", min_value=0.0, max_value=2.0, value=0.4, step=0.01, help="Fixed Obligation to Income Ratio")
            dpd30plus = st.number_input("⚠️ DPD 30+ Count", min_value=0, max_value=10, value=0, help="Days Past Due 30+ instances")
            enquiry_count = st.number_input("🔍 Enquiry Count", min_value=0, max_value=20, value=2, help="Credit enquiries in last 6 months")
            
        with col2:
            st.markdown("### 🧠 Behavioral Analytics")
            credit_vintage = st.number_input("📅 Credit Vintage (months)", min_value=0, max_value=600, value=48, help="Credit history length in months")
            loan_mix_type = st.selectbox(
                "🏦 Loan Mix Type",
                ["PL/HL/CC", "Gold + Consumer Durable", "Only Gold", "Agri/Other loans"],
                help="Types of loans in credit portfolio"
            )
            loan_completion_ratio = st.number_input("✅ Loan Completion Ratio", min_value=0.0, max_value=1.0, value=0.7, step=0.1, help="Percentage of loans completed successfully")
            defaulted_loans = st.number_input("❌ Defaulted Loans Count", min_value=0, max_value=10, value=0, help="Number of defaulted loans")
            
            st.markdown("### 💼 Exposure & Intent")
            unsecured_loan_amount = st.number_input("💳 Unsecured Loan Amount (₹)", min_value=0, value=0, step=1000, help="Total unsecured loan amount")
            outstanding_amount_percent = st.number_input("📊 Outstanding Amount %", min_value=0.0, max_value=100.0, value=40.0, step=5.0, help="Percentage of outstanding amount")
            our_lender_exposure = st.number_input("🏢 Our Lender Exposure (₹)", min_value=0, value=0, step=1000, help="Existing exposure with our organization")
            channel_type = st.selectbox("📱 Channel Type", ["Merchant/Referral", "Digital/Other"], help="Application channel")
            writeoff_flag = st.checkbox("⚠️ Write-off Flag", help="Has any write-off history")
        
        submitted = st.form_submit_button("🚀 Calculate Score", type="primary", use_container_width=True)
    
    if submitted:
        # Prepare data
        applicant_data = {
            'pan': pan,
            'age': age,
            'monthly_income': monthly_income,
            'credit_score': credit_score,
            'foir': foir,
            'dpd30plus': dpd30plus,
            'enquiry_count': enquiry_count,
            'credit_vintage': credit_vintage,
            'loan_mix_type': loan_mix_type,
            'loan_completion_ratio': loan_completion_ratio,
            'defaulted_loans': defaulted_loans,
            'unsecured_loan_amount': unsecured_loan_amount,
            'outstanding_amount_percent': outstanding_amount_percent / 100,  # Convert to decimal
            'our_lender_exposure': our_lender_exposure,
            'channel_type': channel_type,
            'writeoff_flag': writeoff_flag
        }
        
        # Validate data
        validation_errors = validate_individual_data(applicant_data)
        
        if validation_errors:
            st.error("Validation Errors:")
            for error in validation_errors:
                st.error(f"• {error}")
        else:
            # Process scoring
            result = st.session_state.scoring_engine.score_application(applicant_data)
            
            # Display results
            render_scoring_results(result, applicant_data)
            
            # Save to database
            st.session_state.db_manager.save_individual_result(applicant_data, result)

def render_scoring_results(result, applicant_data):
    """Render scoring results"""
    st.markdown('<div class="success-card"><h2>🎉 Scoring Completed Successfully!</h2></div>', unsafe_allow_html=True)
    
    # Main score display
    bucket_class = f"bucket-{result['final_bucket']}"
    st.markdown(f'''
    <div class="score-display {bucket_class}">
        <h1 style="font-size: 4rem; margin: 0;">{result['final_score']:.1f}</h1>
        <h2 style="margin: 0;">Credit Score</h2>
        <div style="display: flex; justify-content: space-around; margin-top: 1rem;">
            <div>
                <h3>Risk Bucket</h3>
                <h2 style="margin: 0;">{result['final_bucket']}</h2>
            </div>
            <div>
                <h3>Decision</h3>
                <h2 style="margin: 0;">{result['decision']}</h2>
            </div>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    # Clearance rules status
    st.subheader("Clearance Rules")
    if result['clearance_passed']:
        st.success("✅ All clearance rules passed")
    else:
        st.error("❌ Failed clearance rules:")
        for rule in result['failed_clearance_rules']:
            st.error(f"• {rule}")
    
    # Score breakdown
    if result['clearance_passed']:
        st.subheader("Score Breakdown")
        
        score_data = []
        for var, details in result['variable_scores'].items():
            score_data.append({
                'Variable': var,
                'Weight': f"{details['weight']:.1%}",
                'Band Score': f"{details['band_score']:.2f}",
                'Weighted Score': f"{details['weighted_score']:.2f}",
                'Value': str(details['value'])
            })
        
        df_scores = pd.DataFrame(score_data)
        st.dataframe(df_scores, use_container_width=True)
        
        # Post-score movements
        if result['bucket_movements']:
            st.subheader("Bucket Movements")
            for movement in result['bucket_movements']:
                st.info(f"Moved from {movement['from']} to {movement['to']}: {movement['reason']}")
    
    # Generate Excel output
    excel_buffer = create_excel_output([applicant_data], [result], is_bulk=False)
    st.download_button(
        label="Download Results (Excel)",
        data=excel_buffer,
        file_name=f"loan_score_individual_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

def render_bulk_upload():
    """Render bulk upload interface"""
    st.header("Bulk Loan Application Upload")
    
    # Download template
    st.subheader("Step 1: Download Template")
    template_data = {
        'pan': ['ABCDE1234F'],
        'age': [30],
        'monthly_income': [25000],
        'credit_score': [650],
        'foir': [0.4],
        'dpd30plus': [0],
        'enquiry_count': [2],
        'credit_vintage': [48],
        'loan_mix_type': ['PL/HL/CC'],
        'loan_completion_ratio': [0.7],
        'defaulted_loans': [0],
        'unsecured_loan_amount': [50000],
        'outstanding_amount_percent': [0.4],
        'our_lender_exposure': [0],
        'channel_type': ['Merchant/Referral'],
        'writeoff_flag': [False]
    }
    template_df = pd.DataFrame(template_data)
    template_csv = template_df.to_csv(index=False)
    
    st.download_button(
        label="Download CSV Template",
        data=template_csv,
        file_name="loan_application_template.csv",
        mime="text/csv"
    )
    
    # File upload
    st.subheader("Step 2: Upload Your CSV File")
    uploaded_file = st.file_uploader("Choose CSV file", type="csv")
    
    if uploaded_file is not None:
        try:
            # Read CSV
            df = pd.read_csv(uploaded_file)
            
            st.success(f"File uploaded successfully! Found {len(df)} records.")
            
            # Validate columns
            validation_result = validate_csv_columns(df)
            if not validation_result['valid']:
                st.error("CSV validation failed:")
                for error in validation_result['errors']:
                    st.error(f"• {error}")
                return
            
            # Show preview
            st.subheader("Data Preview")
            st.dataframe(df.head(10))
            
            # Process button
            if st.button("Process All Applications", type="primary"):
                process_bulk_applications(df)
                
        except Exception as e:
            st.error(f"Error reading CSV file: {str(e)}")

def process_bulk_applications(df):
    """Process bulk applications"""
    st.subheader("Processing Applications...")
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    results = []
    total_records = len(df)
    
    for idx, row in df.iterrows():
        # Update progress
        progress = (idx + 1) / total_records
        progress_bar.progress(progress)
        status_text.text(f"Processing application {idx + 1} of {total_records}")
        
        # Convert row to dict
        applicant_data = row.to_dict()
        
        # Process scoring
        try:
            result = st.session_state.scoring_engine.score_application(applicant_data)
            results.append({
                'applicant_data': applicant_data,
                'result': result,
                'status': 'success'
            })
        except Exception as e:
            results.append({
                'applicant_data': applicant_data,
                'result': None,
                'status': 'error',
                'error': str(e)
            })
    
    # Save to database
    st.session_state.db_manager.save_bulk_results(results)
    
    # Display summary
    render_bulk_summary(results)

def render_bulk_summary(results):
    """Render bulk processing summary"""
    st.success("Bulk processing completed!")
    
    # Calculate summary statistics
    total_processed = len(results)
    successful = len([r for r in results if r['status'] == 'success'])
    errors = total_processed - successful
    
    successful_results = [r for r in results if r['status'] == 'success']
    bucket_counts = {}
    
    if successful > 0:
        for r in successful_results:
            bucket = r['result']['final_bucket']
            bucket_counts[bucket] = bucket_counts.get(bucket, 0) + 1
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Processed", total_processed)
    with col2:
        st.metric("Successful", successful)
    with col3:
        st.metric("Errors", errors)
    with col4:
        auto_approve = bucket_counts.get('A', 0)
        st.metric("Auto-Approve (A)", auto_approve)
    
    # Bucket distribution chart
    if successful > 0 and bucket_counts:
        st.subheader("Risk Bucket Distribution")
        
        bucket_data = list(bucket_counts.items())
        bucket_df = pd.DataFrame(bucket_data, columns=['Bucket', 'Count'])
        fig = px.bar(bucket_df, x='Bucket', y='Count', 
                     title="Distribution of Risk Buckets",
                     color='Bucket',
                     color_discrete_map={'A': 'green', 'B': 'orange', 'C': 'yellow', 'D': 'red'})
        st.plotly_chart(fig, use_container_width=True)
    
    # Generate Excel output
    if successful > 0:
        applicant_data_list = [r['applicant_data'] for r in successful_results]
        result_list = [r['result'] for r in successful_results]
        
        excel_buffer = create_excel_output(applicant_data_list, result_list, is_bulk=True)
        st.download_button(
            label="Download Results (Excel)",
            data=excel_buffer,
            file_name=f"loan_scores_bulk_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

def render_historical_data():
    """Render historical data interface"""
    st.header("Historical Scoring Data")
    
    # Get historical data
    individual_history = st.session_state.db_manager.get_individual_history()
    bulk_history = st.session_state.db_manager.get_bulk_history()
    
    tab1, tab2 = st.tabs(["Individual Applications", "Bulk Sessions"])
    
    with tab1:
        if individual_history:
            st.subheader(f"Individual Applications ({len(individual_history)} records)")
            
            # Convert to DataFrame for display
            display_data = []
            for record in individual_history:
                display_data.append({
                    'Timestamp': record['timestamp'],
                    'PAN': record['pan'],
                    'Score': record['final_score'],
                    'Bucket': record['final_bucket'],
                    'Decision': record['decision']
                })
            
            df_individual = pd.DataFrame(display_data)
            st.dataframe(df_individual, use_container_width=True)
        else:
            st.info("No individual application history found.")
    
    with tab2:
        if bulk_history:
            st.subheader(f"Bulk Sessions ({len(bulk_history)} sessions)")
            
            # Convert to DataFrame for display
            display_data = []
            for session in bulk_history:
                display_data.append({
                    'Session ID': session['session_id'],
                    'Timestamp': session['timestamp'],
                    'Total Records': session['total_records'],
                    'Successful': session['successful_records'],
                    'Avg Score': session['avg_score']
                })
            
            df_bulk = pd.DataFrame(display_data)
            st.dataframe(df_bulk, use_container_width=True)
        else:
            st.info("No bulk session history found.")

def render_scoring_guide():
    """Render scoring methodology guide"""
    st.header("Scoring Methodology Guide")
    
    st.markdown("""
    ## Overview
    The LoanScoreAI v6.0 scorecard assesses loan applicants based on both intent to repay and probability of disbursement. 
    It uses weighted scoring logic and risk buckets to generate final credit decisions.
    """)
    
    # Scoring Variables
    st.subheader("Scoring Variables & Weights")
    
    variables_data = [
        {"Group": "Core Credit Inputs", "Variable": "Credit Score", "Weight": "15%"},
        {"Group": "Core Credit Inputs", "Variable": "FOIR", "Weight": "7%"},
        {"Group": "Core Credit Inputs", "Variable": "DPD30Plus", "Weight": "7%"},
        {"Group": "Core Credit Inputs", "Variable": "Enquiry Count", "Weight": "6%"},
        {"Group": "Income Stability", "Variable": "Monthly Income", "Weight": "8%"},
        {"Group": "Income Stability", "Variable": "Age", "Weight": "4%"},
        {"Group": "Behavioral Analytics", "Variable": "Credit Vintage", "Weight": "6%"},
        {"Group": "Behavioral Analytics", "Variable": "Loan Mix Type", "Weight": "6%"},
        {"Group": "Behavioral Analytics", "Variable": "Loan Completion Ratio", "Weight": "7%"},
        {"Group": "Behavioral Analytics", "Variable": "Defaulted Loans", "Weight": "6%"},
        {"Group": "Exposure Metrics", "Variable": "Unsecured Loan Amount", "Weight": "5%"},
        {"Group": "Exposure Metrics", "Variable": "Outstanding Amount %", "Weight": "5%"},
        {"Group": "Intent Signals", "Variable": "Our Lender Exposure", "Weight": "5%"},
        {"Group": "Intent Signals", "Variable": "Channel Type", "Weight": "5%"}
    ]
    
    df_variables = pd.DataFrame(variables_data)
    st.dataframe(df_variables, use_container_width=True)
    
    # Clearance Rules
    st.subheader("Clearance Rules (Pre-Score)")
    st.markdown("""
    Applications are automatically declined if they fail any of these rules:
    - PAN is missing
    - Age < 21 or > 60
    - Monthly Income < ₹15,000
    - WriteOffFlag = True
    - DPD30Plus > 2
    - Defaulted Loans > 0
    """)
    
    # Risk Buckets
    st.subheader("Final Risk Buckets")
    
    bucket_data = [
        {"Bucket": "A", "Score Range": "≥ 90", "Decision": "Auto-approve"},
        {"Bucket": "B", "Score Range": "78–89.99", "Decision": "Recommend"},
        {"Bucket": "C", "Score Range": "60–77.99", "Decision": "Refer"},
        {"Bucket": "D", "Score Range": "< 60", "Decision": "Decline"}
    ]
    
    df_buckets = pd.DataFrame(bucket_data)
    st.dataframe(df_buckets, use_container_width=True)

def main():
    """Main application function"""
    # Check authentication first
    if not check_authentication():
        render_login_page()
        return
    
    # Load custom CSS for modern styling
    load_custom_css()
    
    initialize_session_state()
    
    mode = render_sidebar()
    
    if mode == "Individual Scoring":
        render_individual_scoring()
    elif mode == "Bulk Upload":
        render_bulk_upload()
    elif mode == "Historical Data":
        render_historical_data()
    elif mode == "Scoring Guide":
        render_scoring_guide()

if __name__ == "__main__":
    main()
