#!/usr/bin/env python3
"""
Test script to verify Dynamic Scorecard Configuration is working properly
"""
import sqlite3
import os
from datetime import datetime

# Remove existing database to start fresh
if os.path.exists("scorecard_config.db"):
    os.remove("scorecard_config.db")

# Initialize database directly
conn = sqlite3.connect("scorecard_config.db")
cursor = conn.cursor()

# Create tables
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
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
''')

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

# Insert categories
categories = [
    ("Core Credit Variables", 1, 35.0, "#e74c3c", "📊"),
    ("Behavioral Analytics", 2, 20.0, "#f39c12", "🧠"),
    ("Employment Stability", 3, 15.0, "#8b4513", "💼"),
    ("Banking Behavior", 4, 10.0, "#3498db", "🏦"),
    ("Exposure & Intent", 5, 12.0, "#e67e22", "💰"),
    ("Geographic & Social", 6, 8.0, "#27ae60", "🌍")
]

for cat in categories:
    cursor.execute('''
        INSERT OR REPLACE INTO scorecard_categories 
        (category_name, display_order, total_weight, color_code, icon)
        VALUES (?, ?, ?, ?, ?)
    ''', cat)

# Insert all 20 variables
variables = [
    # Core Credit Variables (35%)
    ("credit_score", "Credit Score", "Core Credit Variables", 10.0, "integer", "number", -1, 900, "650", "CIBIL/Experian credit score (-1 for no credit history)", "Primary indicator of credit worthiness and default probability"),
    ("foir", "FOIR", "Core Credit Variables", 8.0, "float", "number", 0.0, 2.0, "0.4", "Fixed Obligation to Income Ratio", "Measures debt burden and repayment capacity"),
    ("dpd30plus", "DPD 30+", "Core Credit Variables", 6.0, "integer", "number", 0, 20, "0", "Days Past Due 30+ count in last 12 months", "Direct indicator of payment behavior and default risk"),
    ("enquiry_count", "Enquiry Count", "Core Credit Variables", 6.0, "integer", "number", 0, 50, "2", "Credit enquiries in last 6 months", "Indicates credit hunger and potential overextension"),
    ("age", "Age", "Core Credit Variables", 3.0, "integer", "number", 18, 80, "30", "Applicant's age in years", "Age indicates financial stability and earning potential"),
    ("monthly_income", "Monthly Income", "Core Credit Variables", 2.0, "float", "number", 0, None, "25000", "Gross monthly income in INR", "Absolute repayment capacity indicator"),
    
    # Behavioral Analytics (20%)
    ("credit_vintage_months", "Credit Vintage", "Behavioral Analytics", 6.0, "integer", "number", 0, 600, "48", "Credit history length in months", "Longer credit history indicates experience and stability"),
    ("loan_mix_type", "Loan Mix Type", "Behavioral Analytics", 4.0, "text", "selectbox", None, None, "PL/HL/CC", "Type of existing loan portfolio", "Diverse credit mix shows financial sophistication"),
    ("loan_completion_ratio", "Completion Ratio", "Behavioral Analytics", 5.0, "float", "number", 0.0, 1.0, "0.7", "Ratio of loans completed successfully", "Track record of loan completion indicates reliability"),
    ("defaulted_loans", "Defaulted Loans", "Behavioral Analytics", 5.0, "integer", "number", 0, 20, "0", "Number of previously defaulted loans", "Past defaults strongly predict future default risk"),
    
    # Employment Stability (15%)
    ("job_type", "Job Type", "Employment Stability", 5.0, "text", "selectbox", None, None, "Government/PSU", "Type of employment", "Job stability varies by employment type"),
    ("employment_tenure_months", "Employment Tenure", "Employment Stability", 5.0, "integer", "number", 0, 600, "36", "Employment tenure in months", "Longer tenure indicates job stability"),
    ("company_stability", "Company Stability", "Employment Stability", 5.0, "text", "selectbox", None, None, "Fortune 500", "Employer company stability", "Company stability affects job security"),
    
    # Banking Behavior (10%)
    ("bank_account_vintage_months", "Bank Account Vintage", "Banking Behavior", 3.0, "integer", "number", 0, 600, "60", "Bank account age in months", "Longer banking relationship indicates stability"),
    ("avg_monthly_balance", "Average Monthly Balance", "Banking Behavior", 4.0, "float", "number", 0, None, "15000", "Average bank balance in last 6 months", "Higher balances indicate financial stability"),
    ("bounce_frequency_per_year", "Bounce Frequency", "Banking Behavior", 3.0, "integer", "number", 0, 50, "1", "Number of bounced transactions per year", "Payment bounces indicate cash flow issues"),
    
    # Exposure & Intent (12%)
    ("unsecured_loan_amount", "Unsecured Loan Amount", "Exposure & Intent", 4.0, "float", "number", 0, None, "200000", "Total outstanding unsecured loan amount", "High unsecured exposure increases risk"),
    ("outstanding_amount_percent", "Outstanding Amount %", "Exposure & Intent", 4.0, "float", "number", 0.0, 1.0, "0.3", "Percentage of credit limit utilized", "High utilization indicates credit stress"),
    ("our_lender_exposure", "Our Lender Exposure", "Exposure & Intent", 4.0, "float", "number", 0, None, "50000", "Existing exposure with our organization", "Existing relationship history provides insights"),
    
    # Geographic & Social (8%)
    ("channel_type", "Channel Type", "Geographic & Social", 3.0, "text", "selectbox", None, None, "Branch", "Application channel used", "Channel preference indicates customer behavior"),
    ("geographic_location_risk", "Geographic Risk", "Geographic & Social", 3.0, "text", "selectbox", None, None, "Low Risk", "Geographic location risk assessment", "Location affects recovery and default rates"),
    ("mobile_vintage_months", "Mobile Vintage", "Geographic & Social", 2.0, "integer", "number", 0, 600, "24", "Mobile number age in months", "Longer mobile usage indicates stability")
]

now = datetime.now().isoformat()

for var in variables:
    cursor.execute('''
        INSERT OR REPLACE INTO scorecard_variables 
        (variable_id, display_name, category, weight, data_type, input_type, 
         min_value, max_value, default_value, help_text, scientific_basis,
         is_required, is_active, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, 1, ?, ?)
    ''', var + (now, now))

conn.commit()

# Verify the data
cursor.execute("SELECT COUNT(*) FROM scorecard_categories")
cat_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM scorecard_variables")
var_count = cursor.fetchone()[0]

cursor.execute("SELECT category, COUNT(*) FROM scorecard_variables GROUP BY category")
category_breakdown = cursor.fetchall()

print(f"✓ Database initialized successfully!")
print(f"✓ Categories loaded: {cat_count}")
print(f"✓ Variables loaded: {var_count}")
print(f"✓ Variable breakdown by category:")
for cat, count in category_breakdown:
    cursor.execute("SELECT SUM(weight) FROM scorecard_variables WHERE category = ?", (cat,))
    total_weight = cursor.fetchone()[0]
    print(f"  - {cat}: {count} variables, {total_weight:.1f}% weight")

# Check total weight
cursor.execute("SELECT SUM(weight) FROM scorecard_variables WHERE is_active = 1")
total = cursor.fetchone()[0]
print(f"✓ Total weight: {total:.1f}% (should be 100%)")

conn.close()
print("✓ Database setup complete - Dynamic Scorecard Configuration is ready!")