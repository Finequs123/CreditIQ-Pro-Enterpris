"""
Complete Variable Definitions with Scientific Analysis
All 20 core variables with detailed scoring bands and scientific basis
"""

COMPLETE_VARIABLE_DEFINITIONS = {
    # Core Credit Variables (40% Weight)
    "credit_score": {
        "display_name": "Credit Score",
        "category": "Core Credit Variables",
        "weight": 12.0,
        "scientific_basis": "Most predictive single variable for default probability",
        "data_type": "integer",
        "input_type": "number",
        "score_bands": [
            {"min": 750, "max": 900, "score": 1.0, "description": "Premium borrowers"},
            {"min": 700, "max": 749, "score": 0.8, "description": "Good borrowers"},
            {"min": 650, "max": 699, "score": 0.6, "description": "Average borrowers"},
            {"min": 600, "max": 649, "score": 0.3, "description": "Below average"},
            {"min": 300, "max": 599, "score": 0.0, "description": "High risk"}
        ]
    },
    "foir": {
        "display_name": "FOIR - Fixed Obligation to Income Ratio",
        "category": "Core Credit Variables",
        "weight": 7.0,
        "scientific_basis": "Measures debt burden capacity",
        "data_type": "float",
        "input_type": "number",
        "score_bands": [
            {"min": 0, "max": 35, "score": 1.0, "description": "Healthy debt load"},
            {"min": 36, "max": 45, "score": 0.6, "description": "Manageable"},
            {"min": 46, "max": 55, "score": 0.3, "description": "Stretched"},
            {"min": 56, "max": 100, "score": 0.0, "description": "Over-leveraged"}
        ]
    },
    "dpd30plus": {
        "display_name": "DPD30Plus History",
        "category": "Core Credit Variables",
        "weight": 6.0,
        "scientific_basis": "Recent payment behavior predictor",
        "data_type": "integer",
        "input_type": "number",
        "score_bands": [
            {"min": 0, "max": 0, "score": 1.0, "description": "Excellent discipline"},
            {"min": 1, "max": 1, "score": 0.5, "description": "Minor issue"},
            {"min": 2, "max": 50, "score": 0.0, "description": "Clearance failure"}
        ]
    },
    "enquiry_count": {
        "display_name": "Credit Enquiry Count",
        "category": "Core Credit Variables",
        "weight": 5.0,
        "scientific_basis": "Credit hunger indicator",
        "data_type": "integer",
        "input_type": "number",
        "score_bands": [
            {"min": 0, "max": 1, "score": 1.0, "description": "Low credit seeking"},
            {"min": 2, "max": 3, "score": 0.6, "description": "Moderate seeking"},
            {"min": 4, "max": 50, "score": 0.2, "description": "High credit hunger"}
        ]
    },
    "age": {
        "display_name": "Age Analysis",
        "category": "Core Credit Variables",
        "weight": 3.0,
        "scientific_basis": "Income stability and experience correlation",
        "data_type": "integer",
        "input_type": "number",
        "score_bands": [
            {"min": 26, "max": 35, "score": 1.0, "description": "Prime earning age"},
            {"min": 36, "max": 45, "score": 0.8, "description": "Established career"},
            {"min": 21, "max": 25, "score": 0.6, "description": "Transitional phases"},
            {"min": 46, "max": 55, "score": 0.6, "description": "Transitional phases"},
            {"min": 56, "max": 60, "score": 0.4, "description": "Pre-retirement risk"}
        ]
    },
    "monthly_income": {
        "display_name": "Monthly Income",
        "category": "Core Credit Variables",
        "weight": 7.0,
        "scientific_basis": "Absolute repayment capacity",
        "data_type": "integer",
        "input_type": "number",
        "score_bands": [
            {"min": 30000, "max": 1000000, "score": 1.0, "description": "Strong capacity"},
            {"min": 20000, "max": 29999, "score": 0.6, "description": "Moderate capacity"},
            {"min": 18000, "max": 19999, "score": 0.4, "description": "Limited capacity"},
            {"min": 15000, "max": 17999, "score": 0.3, "description": "Minimum viable"}
        ]
    },
    
    # Behavioral Analytics (25% Weight)
    "credit_vintage": {
        "display_name": "Credit Vintage",
        "category": "Behavioral Analytics",
        "weight": 6.0,
        "scientific_basis": "Credit system experience and familiarity",
        "data_type": "integer",
        "input_type": "number",
        "score_bands": [
            {"min": 61, "max": 500, "score": 1.0, "description": "Seasoned borrower"},
            {"min": 37, "max": 60, "score": 0.8, "description": "Experienced"},
            {"min": 25, "max": 36, "score": 0.6, "description": "Moderate experience"},
            {"min": 13, "max": 24, "score": 0.4, "description": "Limited experience"},
            {"min": 7, "max": 12, "score": 0.2, "description": "New to credit"},
            {"min": 0, "max": 6, "score": 0.0, "description": "Very new"}
        ]
    },
    "loan_mix_type": {
        "display_name": "Loan Mix Type",
        "category": "Behavioral Analytics",
        "weight": 5.0,
        "scientific_basis": "Product sophistication and digital comfort",
        "data_type": "text",
        "input_type": "selectbox",
        "score_bands": [
            {"value": "PL/HL/CC", "score": 1.0, "description": "High sophistication"},
            {"value": "Gold + Consumer Durable", "score": 0.6, "description": "Moderate sophistication"},
            {"value": "Agri/Other loans", "score": 0.4, "description": "Basic products"},
            {"value": "Only Gold", "score": 0.3, "description": "Limited experience"}
        ]
    },
    "loan_completion_ratio": {
        "display_name": "Loan Completion Ratio",
        "category": "Behavioral Analytics",
        "weight": 7.0,
        "scientific_basis": "Strong predictor of digital journey completion",
        "data_type": "float",
        "input_type": "number",
        "score_bands": [
            {"min": 70, "max": 100, "score": 1.0, "description": "High completion intent"},
            {"min": 40, "max": 69, "score": 0.6, "description": "Moderate completion intent"},
            {"min": 0, "max": 39, "score": 0.3, "description": "Low completion intent"}
        ]
    },
    "defaulted_loans": {
        "display_name": "Defaulted Loans Count",
        "category": "Behavioral Analytics",
        "weight": 7.0,
        "scientific_basis": "Historical reliability indicator",
        "data_type": "integer",
        "input_type": "number",
        "score_bands": [
            {"min": 0, "max": 0, "score": 1.0, "description": "Clean history"},
            {"min": 1, "max": 50, "score": 0.0, "description": "Clearance failure"}
        ]
    },
    
    # Employment Stability (15% Weight)
    "job_type": {
        "display_name": "Job Type",
        "category": "Employment Stability",
        "weight": 6.0,
        "scientific_basis": "Income stability and employment security",
        "data_type": "text",
        "input_type": "selectbox",
        "score_bands": [
            {"value": "Government/PSU", "score": 1.0, "description": "Highest stability"},
            {"value": "Private Company (MNC)", "score": 0.9, "description": "High stability"},
            {"value": "Private Company (Local)", "score": 0.7, "description": "Moderate stability"},
            {"value": "Self Employed Professional", "score": 0.6, "description": "Variable income"},
            {"value": "Business Owner", "score": 0.5, "description": "Entrepreneurial risk"},
            {"value": "Freelancer/Contract", "score": 0.3, "description": "Irregular income"}
        ]
    },
    "employment_tenure": {
        "display_name": "Employment Tenure",
        "category": "Employment Stability",
        "weight": 5.0,
        "scientific_basis": "Job security and income continuity",
        "data_type": "integer",
        "input_type": "number",
        "score_bands": [
            {"min": 60, "max": 500, "score": 1.0, "description": "Very stable"},
            {"min": 36, "max": 59, "score": 0.8, "description": "Stable"},
            {"min": 24, "max": 35, "score": 0.6, "description": "Moderately stable"},
            {"min": 12, "max": 23, "score": 0.4, "description": "Building stability"},
            {"min": 6, "max": 11, "score": 0.2, "description": "New role"},
            {"min": 0, "max": 5, "score": 0.0, "description": "Probationary risk"}
        ]
    },
    "company_stability": {
        "display_name": "Company Stability",
        "category": "Employment Stability",
        "weight": 4.0,
        "scientific_basis": "Employer reliability and continuity",
        "data_type": "text",
        "input_type": "selectbox",
        "score_bands": [
            {"value": "Fortune 500", "score": 1.0, "description": "Market leaders"},
            {"value": "Large Enterprise", "score": 0.9, "description": "Established companies"},
            {"value": "Mid-size Company", "score": 0.7, "description": "Growing businesses"},
            {"value": "Small Company", "score": 0.5, "description": "Higher volatility"},
            {"value": "Startup", "score": 0.3, "description": "Entrepreneurial risk"},
            {"value": "Unknown", "score": 0.1, "description": "Information gap"}
        ]
    },
    
    # Banking Behavior (10% Weight)
    "account_vintage": {
        "display_name": "Account Vintage",
        "category": "Banking Behavior",
        "weight": 3.0,
        "scientific_basis": "Banking relationship stability",
        "data_type": "integer",
        "input_type": "number",
        "score_bands": [
            {"min": 60, "max": 500, "score": 1.0, "description": "Long-term relationship"},
            {"min": 36, "max": 59, "score": 0.8, "description": "Established relationship"},
            {"min": 24, "max": 35, "score": 0.6, "description": "Developing relationship"},
            {"min": 12, "max": 23, "score": 0.4, "description": "New relationship"},
            {"min": 0, "max": 11, "score": 0.2, "description": "Recent account"}
        ]
    },
    "average_monthly_balance": {
        "display_name": "Average Monthly Balance",
        "category": "Banking Behavior",
        "weight": 4.0,
        "scientific_basis": "Liquidity and financial buffer",
        "data_type": "integer",
        "input_type": "number",
        "score_bands": [
            {"min": 100000, "max": 10000000, "score": 1.0, "description": "High liquidity"},
            {"min": 50000, "max": 99999, "score": 0.8, "description": "Good liquidity"},
            {"min": 25000, "max": 49999, "score": 0.6, "description": "Moderate liquidity"},
            {"min": 10000, "max": 24999, "score": 0.4, "description": "Basic liquidity"},
            {"min": 5000, "max": 9999, "score": 0.2, "description": "Low liquidity"},
            {"min": 0, "max": 4999, "score": 0.0, "description": "Minimal liquidity"}
        ]
    },
    "bounce_frequency": {
        "display_name": "Bounce Frequency",
        "category": "Banking Behavior",
        "weight": 3.0,
        "scientific_basis": "Payment discipline and account management",
        "data_type": "integer",
        "input_type": "number",
        "score_bands": [
            {"min": 0, "max": 0, "score": 1.0, "description": "Perfect discipline"},
            {"min": 1, "max": 2, "score": 0.7, "description": "Minor issues"},
            {"min": 3, "max": 5, "score": 0.4, "description": "Moderate issues"},
            {"min": 6, "max": 10, "score": 0.2, "description": "Significant issues"},
            {"min": 11, "max": 100, "score": 0.0, "description": "Poor management"}
        ]
    },
    
    # Geographic & Social Factors (5% Weight)
    "geographic_risk": {
        "display_name": "Geographic Risk",
        "category": "Geographic & Social",
        "weight": 2.0,
        "scientific_basis": "Location-based economic stability and infrastructure",
        "data_type": "text",
        "input_type": "selectbox",
        "score_bands": [
            {"value": "Metro Tier 1", "score": 1.0, "description": "Best infrastructure"},
            {"value": "Metro Tier 2", "score": 0.8, "description": "Good infrastructure"},
            {"value": "Urban", "score": 0.7, "description": "Moderate infrastructure"},
            {"value": "Semi-Urban", "score": 0.5, "description": "Basic infrastructure"},
            {"value": "Rural", "score": 0.3, "description": "Limited infrastructure"},
            {"value": "Remote", "score": 0.1, "description": "Minimal infrastructure"}
        ]
    },
    "mobile_number_vintage": {
        "display_name": "Mobile Number Vintage",
        "category": "Geographic & Social",
        "weight": 2.0,
        "scientific_basis": "Digital stability and identity consistency",
        "data_type": "integer",
        "input_type": "number",
        "score_bands": [
            {"min": 60, "max": 500, "score": 1.0, "description": "Very stable identity"},
            {"min": 36, "max": 59, "score": 0.8, "description": "Stable identity"},
            {"min": 24, "max": 35, "score": 0.6, "description": "Moderate stability"},
            {"min": 12, "max": 23, "score": 0.4, "description": "Developing stability"},
            {"min": 0, "max": 11, "score": 0.2, "description": "New/changed number"}
        ]
    },
    "digital_engagement_score": {
        "display_name": "Digital Engagement Score",
        "category": "Geographic & Social",
        "weight": 1.0,
        "scientific_basis": "Digital literacy and completion probability",
        "data_type": "integer",
        "input_type": "number",
        "score_bands": [
            {"min": 80, "max": 100, "score": 1.0, "description": "High digital comfort"},
            {"min": 60, "max": 79, "score": 0.8, "description": "Good digital comfort"},
            {"min": 40, "max": 59, "score": 0.6, "description": "Moderate digital comfort"},
            {"min": 20, "max": 39, "score": 0.4, "description": "Limited digital comfort"},
            {"min": 0, "max": 19, "score": 0.2, "description": "Poor digital comfort"}
        ]
    },
    
    # Exposure & Intent (5% Weight)
    "unsecured_loan_amount": {
        "display_name": "Unsecured Loan Amount",
        "category": "Exposure & Intent",
        "weight": 2.0,
        "scientific_basis": "Current unsecured debt burden",
        "data_type": "integer",
        "input_type": "number",
        "score_bands": [
            {"min": 0, "max": 0, "score": 0.6, "description": "No unsecured loans"},
            {"min": 1, "max": 49999, "score": 0.8, "description": "Low burden"},
            {"min": 50000, "max": 100000, "score": 1.0, "description": "Optimal range"},
            {"min": 100001, "max": 10000000, "score": 0.6, "description": "High burden"}
        ]
    },
    "outstanding_amount_percentage": {
        "display_name": "Outstanding Amount Percentage",
        "category": "Exposure & Intent",
        "weight": 1.0,
        "scientific_basis": "Credit utilization pattern",
        "data_type": "float",
        "input_type": "number",
        "score_bands": [
            {"min": 0, "max": 29, "score": 1.0, "description": "Healthy utilization"},
            {"min": 30, "max": 60, "score": 0.6, "description": "Moderate utilization"},
            {"min": 61, "max": 100, "score": 0.3, "description": "High utilization"}
        ]
    },
    "our_lender_exposure": {
        "display_name": "Our Lender Exposure",
        "category": "Exposure & Intent",
        "weight": 1.0,
        "scientific_basis": "Existing relationship indicator",
        "data_type": "integer",
        "input_type": "number",
        "score_bands": [
            {"min": 1, "max": 10000000, "score": 1.0, "description": "Existing customer"},
            {"min": 0, "max": 0, "score": 0.0, "description": "New customer"}
        ]
    },
    "channel_type": {
        "display_name": "Channel Type",
        "category": "Exposure & Intent",
        "weight": 1.0,
        "scientific_basis": "Application source quality and completion intent",
        "data_type": "text",
        "input_type": "selectbox",
        "score_bands": [
            {"value": "Merchant/Referral", "score": 1.0, "description": "Higher intent and guided support"},
            {"value": "Digital/Other", "score": 0.5, "description": "Standard self-service intent"}
        ]
    }
}

def get_complete_variable_definitions():
    """Get complete variable definitions with all details"""
    return COMPLETE_VARIABLE_DEFINITIONS

def get_variables_by_category():
    """Get variables organized by category with weight totals"""
    categories = {}
    
    for var_id, var_data in COMPLETE_VARIABLE_DEFINITIONS.items():
        category = var_data['category']
        if category not in categories:
            categories[category] = []
        categories[category].append({
            'variable_id': var_id,
            **var_data
        })
    
    # Calculate category weights
    category_weights = {}
    for category, variables in categories.items():
        total_weight = sum(var['weight'] for var in variables)
        category_weights[category] = total_weight
    
    return categories, category_weights