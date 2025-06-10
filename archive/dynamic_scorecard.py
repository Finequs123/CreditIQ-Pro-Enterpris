import json
import sqlite3
from typing import Dict, List, Any, Optional
from datetime import datetime
import streamlit as st

class DynamicScorecardManager:
    """Manages dynamic scorecard variables, bands, and weights"""
    
    def __init__(self, db_path: str = "scorecard_config.db"):
        self.db_path = db_path
        self.init_database()
        
    def init_database(self):
        """Initialize database for dynamic scorecard configuration"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Variables configuration table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scorecard_variables (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                variable_id TEXT UNIQUE NOT NULL,
                display_name TEXT NOT NULL,
                category TEXT NOT NULL,
                weight REAL NOT NULL,
                data_type TEXT NOT NULL,
                input_type TEXT NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                is_required BOOLEAN DEFAULT 1,
                min_value REAL,
                max_value REAL,
                default_value TEXT,
                help_text TEXT,
                scientific_basis TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')
        
        # Score bands table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS score_bands (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                variable_id TEXT NOT NULL,
                band_order INTEGER NOT NULL,
                threshold_min REAL,
                threshold_max REAL,
                operator TEXT NOT NULL,
                score REAL NOT NULL,
                label TEXT NOT NULL,
                description TEXT,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY (variable_id) REFERENCES scorecard_variables (variable_id)
            )
        ''')
        
        # Categories table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scorecard_categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_name TEXT UNIQUE NOT NULL,
                display_order INTEGER NOT NULL,
                total_weight REAL NOT NULL,
                color_code TEXT,
                icon TEXT,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        conn.commit()
        conn.close()
        
        # Initialize with default variables if empty
        try:
            if self.get_variables_count() == 0:
                self._load_default_variables()
        except:
            # If tables don't exist yet, skip initialization
            pass
    
    def get_variables_count(self) -> int:
        """Get total count of variables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM scorecard_variables")
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    def _load_default_variables(self):
        """Load default 20-variable scorecard"""
        default_categories = [
            {"category_name": "Core Credit Variables", "display_order": 1, "total_weight": 35.0, "color_code": "#e74c3c", "icon": "📊"},
            {"category_name": "Behavioral Analytics", "display_order": 2, "total_weight": 20.0, "color_code": "#f39c12", "icon": "🧠"},
            {"category_name": "Employment Stability", "display_order": 3, "total_weight": 15.0, "color_code": "#8b4513", "icon": "💼"},
            {"category_name": "Banking Behavior", "display_order": 4, "total_weight": 10.0, "color_code": "#3498db", "icon": "🏦"},
            {"category_name": "Exposure & Intent", "display_order": 5, "total_weight": 12.0, "color_code": "#e67e22", "icon": "💰"},
            {"category_name": "Geographic & Social", "display_order": 6, "total_weight": 8.0, "color_code": "#27ae60", "icon": "🌍"}
        ]
        
        for category in default_categories:
            self.add_category(category)
        
        default_variables = [
            # Core Credit Variables (35%)
            {
                "variable_id": "credit_score",
                "display_name": "Credit Score",
                "category": "Core Credit Variables",
                "weight": 10.0,
                "data_type": "integer",
                "input_type": "number",
                "min_value": -1,
                "max_value": 900,
                "default_value": "650",
                "help_text": "CIBIL/Experian credit score (-1 for no credit history)",
                "scientific_basis": "Primary indicator of credit worthiness and default probability",
                "score_bands": [
                    {"threshold_min": 750, "threshold_max": None, "operator": ">=", "score": 1.0, "label": "Excellent", "description": "Very low default risk"},
                    {"threshold_min": 700, "threshold_max": 749, "operator": "range", "score": 0.8, "label": "Good", "description": "Low default risk"},
                    {"threshold_min": 650, "threshold_max": 699, "operator": "range", "score": 0.6, "label": "Fair", "description": "Moderate risk"},
                    {"threshold_min": 600, "threshold_max": 649, "operator": "range", "score": 0.4, "label": "Poor", "description": "High risk"},
                    {"threshold_min": 0, "threshold_max": 599, "operator": "range", "score": 0.2, "label": "Very Poor", "description": "Very high risk"},
                    {"threshold_min": -1, "threshold_max": -1, "operator": "==", "score": 0.3, "label": "No History", "description": "Limited credit data"}
                ]
            },
            {
                "variable_id": "foir",
                "display_name": "FOIR",
                "category": "Core Credit Variables",
                "weight": 8.0,
                "data_type": "float",
                "input_type": "number",
                "min_value": 0.0,
                "max_value": 2.0,
                "default_value": "0.4",
                "help_text": "Fixed Obligation to Income Ratio",
                "scientific_basis": "Measures debt burden and repayment capacity",
                "score_bands": [
                    {"threshold_min": 0.0, "threshold_max": 0.3, "operator": "range", "score": 1.0, "label": "Low Burden", "description": "Excellent repayment capacity"},
                    {"threshold_min": 0.31, "threshold_max": 0.5, "operator": "range", "score": 0.7, "label": "Moderate", "description": "Good repayment capacity"},
                    {"threshold_min": 0.51, "threshold_max": 0.7, "operator": "range", "score": 0.4, "label": "High Burden", "description": "Limited capacity"},
                    {"threshold_min": 0.71, "threshold_max": None, "operator": ">=", "score": 0.1, "label": "Overextended", "description": "Very limited capacity"}
                ]
            },
            {
                "variable_id": "dpd30plus",
                "display_name": "DPD 30+",
                "category": "Core Credit Variables",
                "weight": 6.0,
                "data_type": "integer",
                "input_type": "number",
                "min_value": 0,
                "max_value": 20,
                "default_value": "0",
                "help_text": "Days Past Due 30+ count in last 12 months",
                "scientific_basis": "Direct indicator of payment behavior and default risk",
                "score_bands": [
                    {"threshold_min": 0, "threshold_max": 0, "operator": "==", "score": 1.0, "label": "Perfect", "description": "No late payments"},
                    {"threshold_min": 1, "threshold_max": 2, "operator": "range", "score": 0.6, "label": "Occasional", "description": "Minor issues"},
                    {"threshold_min": 3, "threshold_max": 5, "operator": "range", "score": 0.3, "label": "Concerning", "description": "Payment issues"},
                    {"threshold_min": 6, "threshold_max": None, "operator": ">=", "score": 0.1, "label": "Poor", "description": "Serious payment issues"}
                ]
            },
            {
                "variable_id": "enquiry_count",
                "display_name": "Enquiry Count",
                "category": "Core Credit Variables",
                "weight": 6.0,
                "data_type": "integer",
                "input_type": "number",
                "min_value": 0,
                "max_value": 50,
                "default_value": "2",
                "help_text": "Credit enquiries in last 6 months",
                "scientific_basis": "Indicates credit hunger and potential overextension",
                "score_bands": [
                    {"threshold_min": 0, "threshold_max": 2, "operator": "range", "score": 1.0, "label": "Conservative", "description": "Low credit seeking"},
                    {"threshold_min": 3, "threshold_max": 5, "operator": "range", "score": 0.7, "label": "Moderate", "description": "Normal activity"},
                    {"threshold_min": 6, "threshold_max": 10, "operator": "range", "score": 0.4, "label": "Active", "description": "High credit seeking"},
                    {"threshold_min": 11, "threshold_max": None, "operator": ">=", "score": 0.1, "label": "Excessive", "description": "Credit hungry"}
                ]
            },
            {
                "variable_id": "age",
                "display_name": "Age",
                "category": "Core Credit Variables",
                "weight": 3.0,
                "data_type": "integer",
                "input_type": "number",
                "min_value": 18,
                "max_value": 80,
                "default_value": "30",
                "help_text": "Applicant's age in years",
                "scientific_basis": "Age indicates financial stability and earning potential",
                "score_bands": [
                    {"threshold_min": 25, "threshold_max": 45, "operator": "range", "score": 1.0, "label": "Prime", "description": "Peak earning years"},
                    {"threshold_min": 22, "threshold_max": 24, "operator": "range", "score": 0.7, "label": "Young Professional", "description": "Establishing career"},
                    {"threshold_min": 46, "threshold_max": 55, "operator": "range", "score": 0.8, "label": "Experienced", "description": "Stable career"},
                    {"threshold_min": 18, "threshold_max": 21, "operator": "range", "score": 0.4, "label": "Very Young", "description": "Limited experience"},
                    {"threshold_min": 56, "threshold_max": 80, "operator": "range", "score": 0.5, "label": "Senior", "description": "Pre-retirement"}
                ]
            },
            {
                "variable_id": "monthly_income",
                "display_name": "Monthly Income",
                "category": "Core Credit Variables",
                "weight": 2.0,
                "data_type": "float",
                "input_type": "number",
                "min_value": 0,
                "max_value": None,
                "default_value": "25000",
                "help_text": "Gross monthly income in INR",
                "scientific_basis": "Absolute repayment capacity indicator",
                "score_bands": [
                    {"threshold_min": 50000, "threshold_max": None, "operator": ">=", "score": 1.0, "label": "High Income", "description": "Strong repayment capacity"},
                    {"threshold_min": 30000, "threshold_max": 49999, "operator": "range", "score": 0.8, "label": "Good Income", "description": "Good capacity"},
                    {"threshold_min": 20000, "threshold_max": 29999, "operator": "range", "score": 0.6, "label": "Moderate", "description": "Moderate capacity"},
                    {"threshold_min": 15000, "threshold_max": 19999, "operator": "range", "score": 0.3, "label": "Minimum", "description": "Minimum viable"},
                    {"threshold_min": 0, "threshold_max": 14999, "operator": "range", "score": 0.1, "label": "Low Income", "description": "Limited capacity"}
                ]
            },
            # Behavioral Analytics (20%)
            {
                "variable_id": "credit_vintage_months",
                "display_name": "Credit Vintage",
                "category": "Behavioral Analytics",
                "weight": 6.0,
                "data_type": "integer",
                "input_type": "number",
                "min_value": 0,
                "max_value": 600,
                "default_value": "48",
                "help_text": "Credit history length in months",
                "scientific_basis": "Longer credit history indicates experience and stability",
                "score_bands": [
                    {"threshold_min": 60, "threshold_max": None, "operator": ">=", "score": 1.0, "label": "Seasoned", "description": "Long credit history"},
                    {"threshold_min": 24, "threshold_max": 59, "operator": "range", "score": 0.7, "label": "Established", "description": "Good history"},
                    {"threshold_min": 12, "threshold_max": 23, "operator": "range", "score": 0.5, "label": "Building", "description": "Limited history"},
                    {"threshold_min": 0, "threshold_max": 11, "operator": "range", "score": 0.2, "label": "New", "description": "Very limited"}
                ]
            },
            {
                "variable_id": "loan_mix_type",
                "display_name": "Loan Mix Type",
                "category": "Behavioral Analytics",
                "weight": 4.0,
                "data_type": "text",
                "input_type": "selectbox",
                "default_value": "PL/HL/CC",
                "help_text": "Type of existing loan portfolio",
                "scientific_basis": "Diverse credit mix shows financial sophistication",
                "score_bands": [
                    {"threshold_min": None, "threshold_max": None, "operator": "==", "score": 1.0, "label": "PL/HL/CC", "description": "Diversified portfolio"},
                    {"threshold_min": None, "threshold_max": None, "operator": "==", "score": 0.8, "label": "Gold + Consumer Durable", "description": "Secured mix"},
                    {"threshold_min": None, "threshold_max": None, "operator": "==", "score": 0.6, "label": "Only Gold", "description": "Secured only"},
                    {"threshold_min": None, "threshold_max": None, "operator": "==", "score": 0.4, "label": "Agri/Other loans", "description": "Specialized"}
                ]
            },
            {
                "variable_id": "loan_completion_ratio",
                "display_name": "Completion Ratio",
                "category": "Behavioral Analytics",
                "weight": 5.0,
                "data_type": "float",
                "input_type": "number",
                "min_value": 0.0,
                "max_value": 1.0,
                "default_value": "0.7",
                "help_text": "Ratio of loans completed successfully",
                "scientific_basis": "Track record of loan completion indicates reliability",
                "score_bands": [
                    {"threshold_min": 0.8, "threshold_max": 1.0, "operator": "range", "score": 1.0, "label": "Excellent", "description": "Great track record"},
                    {"threshold_min": 0.6, "threshold_max": 0.79, "operator": "range", "score": 0.7, "label": "Good", "description": "Solid performance"},
                    {"threshold_min": 0.4, "threshold_max": 0.59, "operator": "range", "score": 0.5, "label": "Average", "description": "Mixed track record"},
                    {"threshold_min": 0.0, "threshold_max": 0.39, "operator": "range", "score": 0.2, "label": "Poor", "description": "Concerning pattern"}
                ]
            },
            {
                "variable_id": "defaulted_loans",
                "display_name": "Defaulted Loans",
                "category": "Behavioral Analytics", 
                "weight": 5.0,
                "data_type": "integer",
                "input_type": "number",
                "min_value": 0,
                "max_value": 20,
                "default_value": "0",
                "help_text": "Number of previously defaulted loans",
                "scientific_basis": "Past defaults strongly predict future default risk",
                "score_bands": [
                    {"threshold_min": 0, "threshold_max": 0, "operator": "==", "score": 1.0, "label": "Clean", "description": "No defaults"},
                    {"threshold_min": 1, "threshold_max": 1, "operator": "==", "score": 0.3, "label": "Single Default", "description": "One-time issue"},
                    {"threshold_min": 2, "threshold_max": None, "operator": ">=", "score": 0.1, "label": "Multiple", "description": "Pattern of defaults"}
                ]
            },
            # Employment Stability (15%)
            {
                "variable_id": "job_type",
                "display_name": "Job Type",
                "category": "Employment Stability",
                "weight": 5.0,
                "data_type": "text",
                "input_type": "selectbox",
                "default_value": "Government/PSU",
                "help_text": "Type of employment",
                "scientific_basis": "Job stability varies by employment type",
                "score_bands": [
                    {"threshold_min": None, "threshold_max": None, "operator": "==", "score": 1.0, "label": "Government/PSU", "description": "Highest stability"},
                    {"threshold_min": None, "threshold_max": None, "operator": "==", "score": 0.8, "label": "Private Company (MNC)", "description": "Good stability"},
                    {"threshold_min": None, "threshold_max": None, "operator": "==", "score": 0.6, "label": "Private Company (Local)", "description": "Moderate stability"},
                    {"threshold_min": None, "threshold_max": None, "operator": "==", "score": 0.4, "label": "Self Employed Professional", "description": "Variable income"},
                    {"threshold_min": None, "threshold_max": None, "operator": "==", "score": 0.3, "label": "Business Owner", "description": "Business risk"},
                    {"threshold_min": None, "threshold_max": None, "operator": "==", "score": 0.2, "label": "Freelancer/Contract", "description": "Low stability"}
                ]
            },
            {
                "variable_id": "employment_tenure_months",
                "display_name": "Employment Tenure",
                "category": "Employment Stability",
                "weight": 5.0,
                "data_type": "integer",
                "input_type": "number",
                "min_value": 0,
                "max_value": 600,
                "default_value": "36",
                "help_text": "Employment tenure in months",
                "scientific_basis": "Longer tenure indicates job stability",
                "score_bands": [
                    {"threshold_min": 60, "threshold_max": None, "operator": ">=", "score": 1.0, "label": "Very Stable", "description": "Long tenure"},
                    {"threshold_min": 24, "threshold_max": 59, "operator": "range", "score": 0.8, "label": "Stable", "description": "Good tenure"},
                    {"threshold_min": 12, "threshold_max": 23, "operator": "range", "score": 0.6, "label": "Moderate", "description": "Average tenure"},
                    {"threshold_min": 6, "threshold_max": 11, "operator": "range", "score": 0.4, "label": "New", "description": "Recent job"},
                    {"threshold_min": 0, "threshold_max": 5, "operator": "range", "score": 0.2, "label": "Very New", "description": "Very recent"}
                ]
            },
            {
                "variable_id": "company_stability",
                "display_name": "Company Stability",
                "category": "Employment Stability",
                "weight": 5.0,
                "data_type": "text",
                "input_type": "selectbox",
                "default_value": "Fortune 500",
                "help_text": "Employer company stability",
                "scientific_basis": "Company stability affects job security",
                "score_bands": [
                    {"threshold_min": None, "threshold_max": None, "operator": "==", "score": 1.0, "label": "Fortune 500", "description": "Highest stability"},
                    {"threshold_min": None, "threshold_max": None, "operator": "==", "score": 0.8, "label": "Large Enterprise", "description": "Very stable"},
                    {"threshold_min": None, "threshold_max": None, "operator": "==", "score": 0.6, "label": "Mid-size Company", "description": "Moderate stability"},
                    {"threshold_min": None, "threshold_max": None, "operator": "==", "score": 0.4, "label": "Small Company", "description": "Lower stability"},
                    {"threshold_min": None, "threshold_max": None, "operator": "==", "score": 0.2, "label": "Startup", "description": "High risk"},
                    {"threshold_min": None, "threshold_max": None, "operator": "==", "score": 0.3, "label": "Unknown", "description": "Unclear stability"}
                ]
            },
            # Banking Behavior (10%)
            {
                "variable_id": "bank_account_vintage_months",
                "display_name": "Account Vintage",
                "category": "Banking Behavior",
                "weight": 3.0,
                "data_type": "integer",
                "input_type": "number",
                "min_value": 0,
                "max_value": 600,
                "default_value": "24",
                "help_text": "Primary bank account age in months",
                "scientific_basis": "Account vintage indicates banking relationship stability",
                "score_bands": [
                    {"threshold_min": 60, "threshold_max": None, "operator": ">=", "score": 1.0, "label": "Long Relationship", "description": "Established banking"},
                    {"threshold_min": 24, "threshold_max": 59, "operator": "range", "score": 0.7, "label": "Established", "description": "Good relationship"},
                    {"threshold_min": 12, "threshold_max": 23, "operator": "range", "score": 0.5, "label": "Moderate", "description": "Building relationship"},
                    {"threshold_min": 0, "threshold_max": 11, "operator": "range", "score": 0.3, "label": "New", "description": "New relationship"}
                ]
            },
            {
                "variable_id": "avg_monthly_balance",
                "display_name": "Avg Monthly Balance",
                "category": "Banking Behavior",
                "weight": 4.0,
                "data_type": "float",
                "input_type": "number",
                "min_value": 0,
                "max_value": None,
                "default_value": "15000",
                "help_text": "Average monthly bank balance in INR",
                "scientific_basis": "Higher balance indicates financial stability",
                "score_bands": [
                    {"threshold_min": 50000, "threshold_max": None, "operator": ">=", "score": 1.0, "label": "High Balance", "description": "Strong financial position"},
                    {"threshold_min": 25000, "threshold_max": 49999, "operator": "range", "score": 0.8, "label": "Good Balance", "description": "Good financial health"},
                    {"threshold_min": 10000, "threshold_max": 24999, "operator": "range", "score": 0.6, "label": "Moderate", "description": "Average balance"},
                    {"threshold_min": 5000, "threshold_max": 9999, "operator": "range", "score": 0.4, "label": "Low Balance", "description": "Limited liquidity"},
                    {"threshold_min": 0, "threshold_max": 4999, "operator": "range", "score": 0.2, "label": "Very Low", "description": "Poor liquidity"}
                ]
            },
            {
                "variable_id": "bounce_frequency_per_year",
                "display_name": "Bounce Frequency", 
                "category": "Banking Behavior",
                "weight": 3.0,
                "data_type": "integer",
                "input_type": "number",
                "min_value": 0,
                "max_value": 50,
                "default_value": "1",
                "help_text": "Cheque/ECS bounces per year",
                "scientific_basis": "Bounce frequency indicates payment discipline",
                "score_bands": [
                    {"threshold_min": 0, "threshold_max": 0, "operator": "==", "score": 1.0, "label": "No Bounces", "description": "Perfect payment discipline"},
                    {"threshold_min": 1, "threshold_max": 2, "operator": "range", "score": 0.7, "label": "Rare", "description": "Occasional issues"},
                    {"threshold_min": 3, "threshold_max": 5, "operator": "range", "score": 0.4, "label": "Frequent", "description": "Regular issues"},
                    {"threshold_min": 6, "threshold_max": None, "operator": ">=", "score": 0.1, "label": "Very Frequent", "description": "Serious payment issues"}
                ]
            },
            # Exposure & Intent (12%)
            {
                "variable_id": "unsecured_loan_amount",
                "display_name": "Unsecured Amount",
                "category": "Exposure & Intent",
                "weight": 3.0,
                "data_type": "float",
                "input_type": "number",
                "min_value": 0,
                "max_value": None,
                "default_value": "0",
                "help_text": "Total unsecured loan amount in INR",
                "scientific_basis": "Higher unsecured exposure increases risk",
                "score_bands": [
                    {"threshold_min": 0, "threshold_max": 50000, "operator": "range", "score": 1.0, "label": "Low Exposure", "description": "Minimal unsecured debt"},
                    {"threshold_min": 50001, "threshold_max": 200000, "operator": "range", "score": 0.7, "label": "Moderate", "description": "Reasonable exposure"},
                    {"threshold_min": 200001, "threshold_max": 500000, "operator": "range", "score": 0.4, "label": "High Exposure", "description": "Significant debt"},
                    {"threshold_min": 500001, "threshold_max": None, "operator": ">=", "score": 0.1, "label": "Very High", "description": "Excessive exposure"}
                ]
            },
            {
                "variable_id": "outstanding_amount_percent",
                "display_name": "Outstanding %",
                "category": "Exposure & Intent",
                "weight": 3.0,
                "data_type": "float",
                "input_type": "number",
                "min_value": 0.0,
                "max_value": 100.0,
                "default_value": "40.0",
                "help_text": "Outstanding amount as percentage of limit",
                "scientific_basis": "High utilization indicates financial stress",
                "score_bands": [
                    {"threshold_min": 0.0, "threshold_max": 30.0, "operator": "range", "score": 1.0, "label": "Low Utilization", "description": "Conservative usage"},
                    {"threshold_min": 30.1, "threshold_max": 50.0, "operator": "range", "score": 0.7, "label": "Moderate", "description": "Reasonable usage"},
                    {"threshold_min": 50.1, "threshold_max": 75.0, "operator": "range", "score": 0.4, "label": "High Utilization", "description": "Heavy usage"},
                    {"threshold_min": 75.1, "threshold_max": 100.0, "operator": "range", "score": 0.1, "label": "Maxed Out", "description": "Maximum utilization"}
                ]
            },
            {
                "variable_id": "our_lender_exposure",
                "display_name": "Our Exposure",
                "category": "Exposure & Intent",
                "weight": 3.0,
                "data_type": "float",
                "input_type": "number",
                "min_value": 0,
                "max_value": None,
                "default_value": "0",
                "help_text": "Existing exposure with our institution in INR",
                "scientific_basis": "Existing relationship affects risk assessment",
                "score_bands": [
                    {"threshold_min": 0, "threshold_max": 0, "operator": "==", "score": 0.8, "label": "New Customer", "description": "No prior exposure"},
                    {"threshold_min": 1, "threshold_max": 100000, "operator": "range", "score": 1.0, "label": "Low Exposure", "description": "Minimal existing loan"},
                    {"threshold_min": 100001, "threshold_max": 500000, "operator": "range", "score": 0.7, "label": "Moderate", "description": "Reasonable exposure"},
                    {"threshold_min": 500001, "threshold_max": None, "operator": ">=", "score": 0.4, "label": "High Exposure", "description": "Significant existing loan"}
                ]
            },
            {
                "variable_id": "channel_type",
                "display_name": "Channel Type",
                "category": "Exposure & Intent",
                "weight": 3.0,
                "data_type": "text",
                "input_type": "selectbox",
                "default_value": "Merchant/Referral",
                "help_text": "Application acquisition channel",
                "scientific_basis": "Channel type affects application quality",
                "score_bands": [
                    {"threshold_min": None, "threshold_max": None, "operator": "==", "score": 1.0, "label": "Merchant/Referral", "description": "Trusted source"},
                    {"threshold_min": None, "threshold_max": None, "operator": "==", "score": 0.7, "label": "Digital/Other", "description": "Self-sourced"}
                ]
            },
            # Geographic & Social (8%)
            {
                "variable_id": "geographic_location_risk",
                "display_name": "Geographic Risk",
                "category": "Geographic & Social",
                "weight": 4.0,
                "data_type": "text",
                "input_type": "selectbox",
                "default_value": "Low Risk",
                "help_text": "Geographic location risk assessment",
                "scientific_basis": "Location affects default probability",
                "score_bands": [
                    {"threshold_min": None, "threshold_max": None, "operator": "==", "score": 1.0, "label": "Low Risk", "description": "Tier 1 cities"},
                    {"threshold_min": None, "threshold_max": None, "operator": "==", "score": 0.7, "label": "Medium Risk", "description": "Tier 2 cities"},
                    {"threshold_min": None, "threshold_max": None, "operator": "==", "score": 0.4, "label": "High Risk", "description": "Tier 3+ locations"}
                ]
            },
            {
                "variable_id": "mobile_vintage_months",
                "display_name": "Mobile Number Vintage",
                "category": "Geographic & Social",
                "weight": 2.0,
                "data_type": "integer",
                "input_type": "number",
                "min_value": 0,
                "max_value": 240,
                "default_value": "36",
                "help_text": "Mobile number age in months",
                "scientific_basis": "Stable mobile number indicates settled lifestyle",
                "score_bands": [
                    {"threshold_min": 36, "threshold_max": None, "operator": ">=", "score": 1.0, "label": "Stable", "description": "Long-term number"},
                    {"threshold_min": 12, "threshold_max": 35, "operator": "range", "score": 0.7, "label": "Established", "description": "Moderate vintage"},
                    {"threshold_min": 6, "threshold_max": 11, "operator": "range", "score": 0.5, "label": "Recent", "description": "Newer number"},
                    {"threshold_min": 0, "threshold_max": 5, "operator": "range", "score": 0.3, "label": "Very New", "description": "Very recent number"}
                ]
            },
            {
                "variable_id": "digital_engagement_score",
                "display_name": "Digital Engagement",
                "category": "Geographic & Social",
                "weight": 2.0,
                "data_type": "float",
                "input_type": "number",
                "min_value": 0.0,
                "max_value": 10.0,
                "default_value": "5.0",
                "help_text": "Digital engagement score (0-10)",
                "scientific_basis": "Digital engagement indicates tech-savviness and modern banking comfort",
                "score_bands": [
                    {"threshold_min": 8.0, "threshold_max": 10.0, "operator": "range", "score": 1.0, "label": "High Engagement", "description": "Very active digitally"},
                    {"threshold_min": 6.0, "threshold_max": 7.9, "operator": "range", "score": 0.8, "label": "Good Engagement", "description": "Active user"},
                    {"threshold_min": 4.0, "threshold_max": 5.9, "operator": "range", "score": 0.6, "label": "Moderate", "description": "Average usage"},
                    {"threshold_min": 2.0, "threshold_max": 3.9, "operator": "range", "score": 0.4, "label": "Low Engagement", "description": "Limited usage"},
                    {"threshold_min": 0.0, "threshold_max": 1.9, "operator": "range", "score": 0.2, "label": "Minimal", "description": "Very low engagement"}
                ]
            }
        ]
        
        for var_config in default_variables:
            score_bands = var_config.pop('score_bands')
            variable_id = self.add_variable(var_config)
            
            for band_order, band in enumerate(score_bands):
                band['variable_id'] = variable_id
                band['band_order'] = band_order
                self.add_score_band(band)
    
    def add_category(self, category_data: Dict[str, Any]) -> str:
        """Add a new scoring category"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO scorecard_categories 
            (category_name, display_order, total_weight, color_code, icon, is_active)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            category_data['category_name'],
            category_data['display_order'],
            category_data['total_weight'],
            category_data.get('color_code', '#666666'),
            category_data.get('icon', '📊'),
            category_data.get('is_active', True)
        ))
        
        conn.commit()
        conn.close()
        return category_data['category_name']
    
    def add_variable(self, variable_data: Dict[str, Any]) -> str:
        """Add a new scoring variable"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        
        cursor.execute('''
            INSERT OR REPLACE INTO scorecard_variables 
            (variable_id, display_name, category, weight, data_type, input_type, 
             is_active, is_required, min_value, max_value, default_value, 
             help_text, scientific_basis, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            variable_data['variable_id'],
            variable_data['display_name'],
            variable_data['category'],
            variable_data['weight'],
            variable_data['data_type'],
            variable_data['input_type'],
            variable_data.get('is_active', True),
            variable_data.get('is_required', True),
            variable_data.get('min_value'),
            variable_data.get('max_value'),
            variable_data.get('default_value'),
            variable_data.get('help_text', ''),
            variable_data.get('scientific_basis', ''),
            now,
            now
        ))
        
        conn.commit()
        conn.close()
        return variable_data['variable_id']
    
    def add_score_band(self, band_data: Dict[str, Any]):
        """Add a score band for a variable"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO score_bands 
            (variable_id, band_order, threshold_min, threshold_max, operator, 
             score, label, description, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            band_data['variable_id'],
            band_data['band_order'],
            band_data.get('threshold_min'),
            band_data.get('threshold_max'),
            band_data['operator'],
            band_data['score'],
            band_data['label'],
            band_data.get('description', ''),
            band_data.get('is_active', True)
        ))
        
        conn.commit()
        conn.close()
    
    def get_variables(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """Get all active variables with their score bands"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get variables with explicit column names
        if active_only:
            where_clause = "WHERE is_active = 1"
        else:
            where_clause = ""
            
        cursor.execute(f'''
            SELECT id, variable_id, display_name, category, weight, data_type, input_type, 
                   is_active, is_required, min_value, max_value, default_value, 
                   help_text, scientific_basis, created_at, updated_at
            FROM scorecard_variables 
            {where_clause}
            ORDER BY is_active DESC, category, display_name
        ''')
        
        columns = ['id', 'variable_id', 'display_name', 'category', 'weight', 'data_type', 
                  'input_type', 'is_active', 'is_required', 'min_value', 'max_value', 
                  'default_value', 'help_text', 'scientific_basis', 'created_at', 'updated_at']
        
        variables = []
        for row in cursor.fetchall():
            var_dict = dict(zip(columns, row))
            
            # Get score bands for this variable
            cursor.execute('''
                SELECT id, variable_id, band_order, threshold_min, threshold_max, 
                       operator, score, label, description, is_active
                FROM score_bands 
                WHERE variable_id = ? AND is_active = 1 
                ORDER BY band_order
            ''', (var_dict['variable_id'],))
            
            band_columns = ['id', 'variable_id', 'band_order', 'threshold_min', 'threshold_max', 
                           'operator', 'score', 'label', 'description', 'is_active']
            
            bands = []
            for band_row in cursor.fetchall():
                band_dict = dict(zip(band_columns, band_row))
                bands.append(band_dict)
            
            var_dict['score_bands'] = bands
            variables.append(var_dict)
        
        conn.close()
        return variables
    
    def get_active_variables(self) -> List[Dict[str, Any]]:
        """Get only active variables"""
        return self.get_variables(active_only=True)
    
    def get_inactive_variables(self) -> List[Dict[str, Any]]:
        """Get only inactive variables"""
        all_vars = self.get_variables(active_only=False)
        return [v for v in all_vars if not v['is_active']]
    
    def reactivate_variable(self, variable_id: str):
        """Reactivate a deactivated variable"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE scorecard_variables 
            SET is_active = 1, updated_at = ? 
            WHERE variable_id = ?
        ''', (datetime.now().isoformat(), variable_id))
        
        conn.commit()
        conn.close()
    
    def get_categories(self) -> List[Dict[str, Any]]:
        """Get all active categories"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM scorecard_categories 
            WHERE is_active = 1 
            ORDER BY display_order
        ''')
        
        categories = []
        for row in cursor.fetchall():
            cat_dict = dict(zip([col[0] for col in cursor.description], row))
            categories.append(cat_dict)
        
        conn.close()
        return categories
    
    def update_variable_weight(self, variable_id: str, new_weight: float):
        """Update variable weight"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE scorecard_variables 
            SET weight = ?, updated_at = ? 
            WHERE variable_id = ?
        ''', (new_weight, datetime.now().isoformat(), variable_id))
        
        conn.commit()
        conn.close()
    
    def deactivate_variable(self, variable_id: str):
        """Soft delete a variable (make it inactive)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE scorecard_variables 
            SET is_active = 0, updated_at = ? 
            WHERE variable_id = ?
        ''', (datetime.now().isoformat(), variable_id))
        
        conn.commit()
        conn.close()
    
    def get_variable_score(self, variable_id: str, value: Any) -> Dict[str, Any]:
        """Get score for a variable value based on configured bands"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get variable info
        cursor.execute('''
            SELECT * FROM scorecard_variables WHERE variable_id = ? AND is_active = 1
        ''', (variable_id,))
        
        variable = cursor.fetchone()
        if not variable:
            return {"score": 0, "label": "Unknown", "error": "Variable not found"}
        
        # Get score bands
        cursor.execute('''
            SELECT * FROM score_bands 
            WHERE variable_id = ? AND is_active = 1 
            ORDER BY band_order
        ''', (variable_id,))
        
        bands = cursor.fetchall()
        conn.close()
        
        # Convert value to appropriate type
        try:
            if variable[4] == 'integer':  # data_type column
                value = int(float(value))
            elif variable[4] == 'float':
                value = float(value)
        except (ValueError, TypeError):
            return {"score": 0, "label": "Invalid", "error": "Invalid value type"}
        
        # Find matching band
        for band in bands:
            band_dict = dict(zip([
                'id', 'variable_id', 'band_order', 'threshold_min', 'threshold_max', 
                'operator', 'score', 'label', 'description', 'is_active'
            ], band))
            
            if self._value_matches_band(value, band_dict):
                return {
                    "score": band_dict['score'],
                    "label": band_dict['label'],
                    "description": band_dict['description'],
                    "threshold_info": f"{band_dict['threshold_min']}-{band_dict['threshold_max']}"
                }
        
        return {"score": 0, "label": "Out of Range", "error": "Value doesn't match any band"}
    
    def _value_matches_band(self, value: Any, band: Dict[str, Any]) -> bool:
        """Check if value matches a score band"""
        operator = band['operator']
        min_val = band['threshold_min']
        max_val = band['threshold_max']
        
        if operator == '>=':
            return value >= min_val
        elif operator == '<=':
            return value <= max_val
        elif operator == '==':
            return value == min_val
        elif operator == 'range':
            if max_val is None:
                return value >= min_val
            return min_val <= value <= max_val
        
        return False
    
    def generate_form_config(self) -> Dict[str, Any]:
        """Generate form configuration for dynamic UI"""
        variables = self.get_active_variables()
        categories = self.get_categories()
        
        form_config = {
            "categories": categories,
            "variables_by_category": {},
            "total_weight": 0
        }
        
        for var in variables:
            category = var['category']
            if category not in form_config["variables_by_category"]:
                form_config["variables_by_category"][category] = []
            
            form_config["variables_by_category"][category].append({
                "id": var['variable_id'],
                "label": var['display_name'],
                "type": var['input_type'],
                "data_type": var['data_type'],
                "required": var['is_required'],
                "min_value": var['min_value'],
                "max_value": var['max_value'],
                "default_value": var['default_value'],
                "help_text": var['help_text'],
                "weight": var['weight']
            })
            
            form_config["total_weight"] += var['weight']
        
        return form_config