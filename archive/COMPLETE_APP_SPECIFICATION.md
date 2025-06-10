# LoanScoreAI v6.3 - Complete End-to-End Application Specification

## Overview
LoanScoreAI is an enterprise-grade credit risk assessment platform with dual-user authentication, modular scoring engines, and comprehensive variable management. Built with Streamlit, SQLite databases, and Python.

## System Architecture

### Core Components
1. **Authentication System** - Database-driven dual-user model
2. **Scoring Engines** - Legacy and Modular risk assessment frameworks
3. **Variable Management** - Dynamic scorecard configuration with 20+ variables
4. **Data Management** - SQLite databases for users, configurations, and results
5. **Analytics** - Performance monitoring, A/B testing, bulk processing

### File Structure
```
├── simple_app.py                          # Main Streamlit application
├── personalized_onboarding.py             # Admin user creation & company setup
├── backend_auth_system.py                 # Database authentication system
├── comprehensive_scorecard_config.py      # Complete variable management
├── complete_variable_definitions.py       # All 20 variables with scoring bands
├── dynamic_scorecard.py                   # Variable configuration manager
├── scoring_engine.py                      # Core scoring algorithms
├── modular_scoring_engine.py              # Advanced modular scoring
├── database.py                            # Data persistence layer
├── user_management.db                     # User & company database
├── loan_scoring.db                        # Scoring results database
└── scoring_weights.json                   # Variable weights configuration
```

## Authentication System

### Dual-User Model
1. **Admin Users (Finequsadmin)**
   - Create companies through personalized onboarding
   - Define company-specific configurations
   - Access: Company management, user creation, system configuration

2. **Company Users**
   - Login with admin-created credentials
   - Access company-specific scoring interface
   - Access: Scoring, analytics, bulk processing for their company only

### Database Schema

#### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    company_id INTEGER,
    user_type TEXT CHECK(user_type IN ('admin', 'company_user')),
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies (id)
);
```

#### Companies Table
```sql
CREATE TABLE companies (
    id INTEGER PRIMARY KEY,
    company_name TEXT NOT NULL,
    industry TEXT,
    company_size TEXT,
    risk_appetite TEXT,
    additional_data_sources TEXT, -- JSON array
    onboarding_data TEXT,         -- JSON object
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Scoring System

### Variable Categories (100% Weight Distribution)
1. **Core Credit Variables (40% Weight)**
   - Credit Score (12%) - CIBIL/credit bureau score
   - FOIR (7%) - Fixed Obligation to Income Ratio
   - DPD30Plus History (6%) - Days Past Due tracking
   - Credit Enquiry Count (5%) - Recent credit applications
   - Age Analysis (3%) - Borrower age assessment
   - Monthly Income (7%) - Absolute income capacity

2. **Behavioral Analytics (25% Weight)**
   - Credit Vintage (6%) - Credit system experience
   - Loan Mix Type (5%) - Product sophistication
   - Loan Completion Ratio (7%) - Digital journey completion
   - Defaulted Loans Count (7%) - Historical reliability

3. **Employment Stability (15% Weight)**
   - Job Type (6%) - Employment category assessment
   - Employment Tenure (5%) - Job stability duration
   - Company Stability (4%) - Employer reliability

4. **Banking Behavior (10% Weight)**
   - Account Vintage (3%) - Banking relationship age
   - Average Monthly Balance (4%) - Liquidity assessment
   - Bounce Frequency (3%) - Payment discipline

5. **Geographic & Social Factors (5% Weight)**
   - Geographic Risk (2%) - Location-based assessment
   - Mobile Number Vintage (2%) - Digital stability
   - Digital Engagement Score (1%) - Digital literacy

6. **Exposure & Intent (5% Weight)**
   - Unsecured Loan Amount (2%) - Current debt burden
   - Outstanding Amount Percentage (1%) - Credit utilization
   - Our Lender Exposure (1%) - Existing relationship
   - Channel Type (1%) - Application source quality

### Scoring Methodology

#### Individual Variable Scoring
Each variable has predefined scoring bands with scientific basis:

**Example: Credit Score Variable**
```python
"credit_score": {
    "display_name": "Credit Score",
    "category": "Core Credit Variables",
    "weight": 12.0,
    "scientific_basis": "Most predictive single variable for default probability",
    "score_bands": [
        {"min": 750, "max": 900, "score": 1.0, "description": "Premium borrowers"},
        {"min": 700, "max": 749, "score": 0.8, "description": "Good borrowers"},
        {"min": 650, "max": 699, "score": 0.6, "description": "Average borrowers"},
        {"min": 600, "max": 649, "score": 0.3, "description": "Below average"},
        {"min": 300, "max": 599, "score": 0.0, "description": "High risk"}
    ]
}
```

#### Final Score Calculation
```python
def calculate_final_score(form_data, weights):
    total_score = 0
    for variable, value in form_data.items():
        variable_score = get_variable_score(variable, value)
        weighted_score = variable_score * weights[variable] / 100
        total_score += weighted_score
    
    return min(max(total_score * 100, 0), 100)  # 0-100 scale
```

#### Risk Decision Matrix
```python
def get_risk_decision(final_score):
    if final_score >= 70:
        return "APPROVE", "Low Risk"
    elif final_score >= 50:
        return "REVIEW", "Medium Risk"
    else:
        return "REJECT", "High Risk"
```

## Application Flow

### Admin Workflow
1. **Login** → Admin authentication check
2. **Company Creation** → Personalized onboarding form
3. **Data Source Selection** → Choose additional data sources (GST, ITR, Utility Bills)
4. **Risk Configuration** → Set risk appetite and thresholds
5. **User Creation** → Generate company users with credentials
6. **System Monitoring** → Access to all company analytics

### Company User Workflow
1. **Login** → Company-specific authentication
2. **Dashboard** → Company-specific interface with selected data sources
3. **Individual Scoring** → Single application assessment
4. **Bulk Processing** → CSV upload for multiple applications
5. **Analytics** → Historical data, performance metrics
6. **Configuration** → Adjust weights within company parameters

### Scoring Workflow
1. **Data Input** → Form fields based on company's selected variables
2. **Validation** → Input validation and clearance checks
3. **Scoring** → Apply variable-specific scoring bands
4. **Weight Application** → Apply company-specific or AI-optimized weights
5. **Final Calculation** → Aggregate weighted scores
6. **Decision** → Risk decision based on score thresholds
7. **Storage** → Save results to database
8. **Display** → Show detailed breakdown and recommendations

## Database Operations

### User Management Database (user_management.db)
```python
class BackendAuthSystem:
    def create_company(self, company_data):
        # Insert company with onboarding configuration
        
    def create_company_user(self, company_id, user_data):
        # Create user linked to specific company
        
    def authenticate_user(self, username, password):
        # Validate credentials and return user context
```

### Scoring Database (loan_scoring.db)
```python
class DatabaseManager:
    def save_individual_result(self, applicant_data, result):
        # Store individual scoring results
        
    def save_bulk_results(self, results, session_id):
        # Store bulk processing results
        
    def get_historical_data(self, company_id):
        # Retrieve company-specific historical data
```

## Features & Functionality

### 1. Individual Scoring
- Dynamic form generation based on company's data sources
- Real-time score calculation
- Detailed breakdown by category
- Risk decision with reasoning
- Clearance checks (DPD30+, defaulted loans)

### 2. Bulk Processing
- CSV upload with template download
- Batch processing with progress tracking
- Results summary with statistics
- Export functionality
- Error handling for invalid data

### 3. Analytics & Reporting
- Historical performance trends
- Score distribution analysis
- Approval rate tracking
- Risk category breakdown
- Company-specific metrics

### 4. Configuration Management
- Weight adjustment interface
- Variable activation/deactivation
- Threshold configuration
- AI-suggested weight optimization
- Configuration history tracking

### 5. A/B Testing Framework
- Create scoring configuration tests
- Traffic split management
- Statistical significance testing
- Performance comparison
- Winner determination

## Technical Implementation

### Streamlit Application Structure
```python
def main():
    # Session state initialization
    initialize_session_state()
    
    # Authentication check
    if not st.session_state.get('authenticated'):
        render_login()
        return
    
    # User-specific interface
    if st.session_state.user_type == 'admin':
        render_admin_interface()
    else:
        render_company_interface()

def render_company_interface():
    # Sidebar navigation
    render_sidebar()
    
    # Main content based on selection
    if menu_selection == "Individual Scoring":
        render_individual_scoring()
    elif menu_selection == "Bulk Upload":
        render_bulk_upload()
    # ... other options
```

### Dynamic Form Generation
```python
def render_scoring_form(company_id):
    # Get company's selected data sources
    data_sources = get_company_data_sources(company_id)
    
    # Generate form fields
    form_data = {}
    for variable in get_variables_for_sources(data_sources):
        form_data[variable] = render_input_field(variable)
    
    return form_data
```

### Scoring Engine Integration
```python
class ScoringEngine:
    def score_application(self, form_data, weights):
        # Apply variable scoring
        variable_scores = {}
        for variable, value in form_data.items():
            variable_scores[variable] = self.calculate_variable_score(variable, value)
        
        # Calculate weighted final score
        final_score = self.calculate_weighted_score(variable_scores, weights)
        
        # Apply business rules
        decision = self.apply_business_rules(form_data, final_score)
        
        return {
            'final_score': final_score,
            'variable_scores': variable_scores,
            'decision': decision,
            'clearance_passed': self.check_clearance(form_data)
        }
```

## Security & Data Integrity

### Authentication Security
- Secure password hashing using werkzeug
- Session-based authentication
- Company-specific data isolation
- Admin privilege separation

### Data Validation
- Input validation for all form fields
- Type checking and range validation
- SQL injection prevention
- Error handling and logging

### Database Security
- Parameterized queries
- Transaction management
- Data backup procedures
- Access logging

## Configuration Files

### Scoring Weights (scoring_weights.json)
```json
{
    "credit_score": 12.0,
    "foir": 7.0,
    "dpd30plus": 6.0,
    "enquiry_count": 5.0,
    "age": 3.0,
    "monthly_income": 7.0,
    // ... all 20 variables
}
```

### Variable Definitions Structure
```python
COMPLETE_VARIABLE_DEFINITIONS = {
    "variable_id": {
        "display_name": "Human readable name",
        "category": "Category name",
        "weight": 0.0,
        "scientific_basis": "Risk correlation explanation",
        "data_type": "integer|float|text",
        "input_type": "number|selectbox|slider",
        "score_bands": [
            {
                "min": 0, "max": 100,
                "score": 1.0,
                "description": "Band description"
            }
        ]
    }
}
```

## API Integration Capabilities

### REST API Endpoints
- `/api/score` - Individual application scoring
- `/api/bulk-score` - Bulk processing
- `/api/config` - Get scoring configuration
- `/api/health` - System health check

### Webhook Support
- Application scored events
- Configuration changes
- System alerts
- Performance thresholds

## Performance & Monitoring

### Metrics Tracking
- Scoring latency
- Approval rates by category
- System performance
- User activity
- Error rates

### Logging System
- Application logs
- Database query logs
- User action logs
- Error tracking
- Performance metrics

## Deployment Configuration

### Streamlit Configuration (.streamlit/config.toml)
```toml
[server]
headless = true
address = "0.0.0.0"
port = 5000

[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
```

### Dependencies (pyproject.toml)
```toml
[tool.uv.dependencies]
python = ">=3.11"
streamlit = "*"
pandas = "*"
plotly = "*"
openpyxl = "*"
scikit-learn = "*"
numpy = "*"
scipy = "*"
joblib = "*"
```

## Usage Examples

### Creating a Company (Admin)
```python
company_data = {
    "company_name": "TechCorp Ltd",
    "industry": "Technology",
    "company_size": "Medium (50-200 employees)",
    "risk_appetite": "Moderate",
    "additional_data_sources": ["GST Data", "ITR Data"]
}
auth_system.create_company(company_data)
```

### Scoring an Application
```python
application_data = {
    "credit_score": 720,
    "foir": 35.5,
    "monthly_income": 50000,
    "age": 32,
    "job_type": "Private Company (MNC)"
    # ... other fields
}

result = scoring_engine.score_application(application_data, weights)
# Returns: {'final_score': 75.2, 'decision': 'APPROVE', ...}
```

### Bulk Processing
```python
# Upload CSV with multiple applications
df = pd.read_csv('applications.csv')
results = []

for _, row in df.iterrows():
    result = scoring_engine.score_application(row.to_dict(), weights)
    results.append(result)

# Save bulk results
db_manager.save_bulk_results(results, session_id)
```

## Error Handling

### Common Error Scenarios
1. **Authentication Failures** - Invalid credentials, session timeout
2. **Data Validation Errors** - Invalid input types, out-of-range values
3. **Database Errors** - Connection issues, constraint violations
4. **Scoring Errors** - Missing variables, calculation failures
5. **File Processing Errors** - Invalid CSV format, missing columns

### Error Recovery
- Graceful degradation for non-critical features
- User-friendly error messages
- Automatic retry mechanisms
- Data recovery procedures
- Logging for debugging

## Extensibility

### Adding New Variables
1. Define in `complete_variable_definitions.py`
2. Add scoring logic in `scoring_engine.py`
3. Update form generation
4. Modify weight distribution

### New Data Sources
1. Add to onboarding configuration
2. Define variable mappings
3. Implement data validation
4. Update scoring calculations

### Custom Scoring Models
1. Implement in `modular_scoring_engine.py`
2. Add configuration interface
3. Integrate with existing workflow
4. Maintain backward compatibility

## Summary

LoanScoreAI v6.3 is a comprehensive credit risk assessment platform that provides:

- **Dual-user authentication** with admin and company user roles
- **Scientific scoring methodology** using 20 variables across 6 categories
- **Dynamic configuration** based on company-specific data sources
- **Comprehensive analytics** and performance monitoring
- **Scalable architecture** supporting individual and bulk processing
- **Enterprise features** including A/B testing, API integration, and audit trails

The system maintains complete data integrity, provides detailed audit trails, and supports enterprise-scale operations while remaining user-friendly for non-technical users.