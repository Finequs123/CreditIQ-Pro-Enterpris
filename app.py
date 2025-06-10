"""
CreditIQ Pro Enterprise - Dynamic User Management System
No hardcoded values - Super Admin creates everything
"""

import streamlit as st
import sqlite3
import hashlib
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

# Dynamic Scorecard Configuration Classes
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
        """Load default scorecard variables and categories"""
        default_categories = [
            {"category_name": "Core Credit Variables", "display_order": 1, "total_weight": 35.0, "color_code": "#e74c3c", "icon": "📊"},
            {"category_name": "Behavioral Analytics", "display_order": 2, "total_weight": 20.0, "color_code": "#f39c12", "icon": "🧠"},
            {"category_name": "Employment Stability", "display_order": 3, "total_weight": 15.0, "color_code": "#8b4513", "icon": "💼"},
            {"category_name": "Banking Behavior", "display_order": 4, "total_weight": 10.0, "color_code": "#3498db", "icon": "🏦"},
            {"category_name": "Exposure & Intent", "display_order": 5, "total_weight": 12.0, "color_code": "#e67e22", "icon": "💰"},
            {"category_name": "Geographic & Social", "display_order": 6, "total_weight": 8.0, "color_code": "#27ae60", "icon": "🌍"}
        ]
        
        # Add default categories
        for cat_data in default_categories:
            self.add_category(cat_data)
        
        # Add all 20 default variables exactly as in original
        default_variables = [
            # Core Credit Variables (35%)
            {"variable_id": "credit_score", "display_name": "Credit Score", "category": "Core Credit Variables", "weight": 10.0, "data_type": "integer", "input_type": "number", "min_value": -1, "max_value": 900, "default_value": "650", "help_text": "CIBIL/Experian credit score (-1 for no credit history)", "scientific_basis": "Primary indicator of credit worthiness and default probability", "is_required": True},
            {"variable_id": "foir", "display_name": "FOIR", "category": "Core Credit Variables", "weight": 8.0, "data_type": "float", "input_type": "number", "min_value": 0.0, "max_value": 2.0, "default_value": "0.4", "help_text": "Fixed Obligation to Income Ratio", "scientific_basis": "Measures debt burden and repayment capacity", "is_required": True},
            {"variable_id": "dpd30plus", "display_name": "DPD 30+", "category": "Core Credit Variables", "weight": 6.0, "data_type": "integer", "input_type": "number", "min_value": 0, "max_value": 20, "default_value": "0", "help_text": "Days Past Due 30+ count in last 12 months", "scientific_basis": "Direct indicator of payment behavior and default risk", "is_required": True},
            {"variable_id": "enquiry_count", "display_name": "Enquiry Count", "category": "Core Credit Variables", "weight": 6.0, "data_type": "integer", "input_type": "number", "min_value": 0, "max_value": 50, "default_value": "2", "help_text": "Credit enquiries in last 6 months", "scientific_basis": "Indicates credit hunger and potential overextension", "is_required": True},
            {"variable_id": "age", "display_name": "Age", "category": "Core Credit Variables", "weight": 3.0, "data_type": "integer", "input_type": "number", "min_value": 18, "max_value": 80, "default_value": "30", "help_text": "Applicant's age in years", "scientific_basis": "Age indicates financial stability and earning potential", "is_required": True},
            {"variable_id": "monthly_income", "display_name": "Monthly Income", "category": "Core Credit Variables", "weight": 2.0, "data_type": "float", "input_type": "number", "min_value": 0, "max_value": None, "default_value": "25000", "help_text": "Gross monthly income in INR", "scientific_basis": "Absolute repayment capacity indicator", "is_required": True},
            
            # Behavioral Analytics (20%)
            {"variable_id": "credit_vintage_months", "display_name": "Credit Vintage", "category": "Behavioral Analytics", "weight": 6.0, "data_type": "integer", "input_type": "number", "min_value": 0, "max_value": 600, "default_value": "48", "help_text": "Credit history length in months", "scientific_basis": "Longer credit history indicates experience and stability", "is_required": True},
            {"variable_id": "loan_mix_type", "display_name": "Loan Mix Type", "category": "Behavioral Analytics", "weight": 4.0, "data_type": "text", "input_type": "selectbox", "default_value": "PL/HL/CC", "help_text": "Type of existing loan portfolio", "scientific_basis": "Diverse credit mix shows financial sophistication", "is_required": True},
            {"variable_id": "loan_completion_ratio", "display_name": "Completion Ratio", "category": "Behavioral Analytics", "weight": 5.0, "data_type": "float", "input_type": "number", "min_value": 0.0, "max_value": 1.0, "default_value": "0.7", "help_text": "Ratio of loans completed successfully", "scientific_basis": "Track record of loan completion indicates reliability", "is_required": True},
            {"variable_id": "defaulted_loans", "display_name": "Defaulted Loans", "category": "Behavioral Analytics", "weight": 5.0, "data_type": "integer", "input_type": "number", "min_value": 0, "max_value": 20, "default_value": "0", "help_text": "Number of previously defaulted loans", "scientific_basis": "Past defaults strongly predict future default risk", "is_required": True},
            
            # Employment Stability (15%)
            {"variable_id": "job_type", "display_name": "Job Type", "category": "Employment Stability", "weight": 5.0, "data_type": "text", "input_type": "selectbox", "default_value": "Government/PSU", "help_text": "Type of employment", "scientific_basis": "Job stability varies by employment type", "is_required": True},
            {"variable_id": "employment_tenure_months", "display_name": "Employment Tenure", "category": "Employment Stability", "weight": 5.0, "data_type": "integer", "input_type": "number", "min_value": 0, "max_value": 600, "default_value": "36", "help_text": "Employment tenure in months", "scientific_basis": "Longer tenure indicates job stability", "is_required": True},
            {"variable_id": "company_stability", "display_name": "Company Stability", "category": "Employment Stability", "weight": 5.0, "data_type": "text", "input_type": "selectbox", "default_value": "Fortune 500", "help_text": "Employer company stability", "scientific_basis": "Company stability affects job security", "is_required": True},
            
            # Banking Behavior (10%)
            {"variable_id": "bank_account_vintage_months", "display_name": "Bank Account Vintage", "category": "Banking Behavior", "weight": 3.0, "data_type": "integer", "input_type": "number", "min_value": 0, "max_value": 600, "default_value": "60", "help_text": "Bank account age in months", "scientific_basis": "Longer banking relationship indicates stability", "is_required": True},
            {"variable_id": "avg_monthly_balance", "display_name": "Average Monthly Balance", "category": "Banking Behavior", "weight": 4.0, "data_type": "float", "input_type": "number", "min_value": 0, "max_value": None, "default_value": "15000", "help_text": "Average bank balance in last 6 months", "scientific_basis": "Higher balances indicate financial stability", "is_required": True},
            {"variable_id": "bounce_frequency_per_year", "display_name": "Bounce Frequency", "category": "Banking Behavior", "weight": 3.0, "data_type": "integer", "input_type": "number", "min_value": 0, "max_value": 50, "default_value": "1", "help_text": "Number of bounced transactions per year", "scientific_basis": "Payment bounces indicate cash flow issues", "is_required": True},
            
            # Exposure & Intent (12%)
            {"variable_id": "unsecured_loan_amount", "display_name": "Unsecured Loan Amount", "category": "Exposure & Intent", "weight": 4.0, "data_type": "float", "input_type": "number", "min_value": 0, "max_value": None, "default_value": "200000", "help_text": "Total outstanding unsecured loan amount", "scientific_basis": "High unsecured exposure increases risk", "is_required": True},
            {"variable_id": "outstanding_amount_percent", "display_name": "Outstanding Amount %", "category": "Exposure & Intent", "weight": 4.0, "data_type": "float", "input_type": "number", "min_value": 0.0, "max_value": 1.0, "default_value": "0.3", "help_text": "Percentage of credit limit utilized", "scientific_basis": "High utilization indicates credit stress", "is_required": True},
            {"variable_id": "our_lender_exposure", "display_name": "Our Lender Exposure", "category": "Exposure & Intent", "weight": 4.0, "data_type": "float", "input_type": "number", "min_value": 0, "max_value": None, "default_value": "50000", "help_text": "Existing exposure with our organization", "scientific_basis": "Existing relationship history provides insights", "is_required": True},
            
            # Geographic & Social (8%)
            {"variable_id": "channel_type", "display_name": "Channel Type", "category": "Geographic & Social", "weight": 3.0, "data_type": "text", "input_type": "selectbox", "default_value": "Branch", "help_text": "Application channel used", "scientific_basis": "Channel preference indicates customer behavior", "is_required": True},
            {"variable_id": "geographic_location_risk", "display_name": "Geographic Risk", "category": "Geographic & Social", "weight": 3.0, "data_type": "text", "input_type": "selectbox", "default_value": "Low Risk", "help_text": "Geographic location risk assessment", "scientific_basis": "Location affects recovery and default rates", "is_required": True},
            {"variable_id": "mobile_vintage_months", "display_name": "Mobile Vintage", "category": "Geographic & Social", "weight": 2.0, "data_type": "integer", "input_type": "number", "min_value": 0, "max_value": 600, "default_value": "24", "help_text": "Mobile number age in months", "scientific_basis": "Longer mobile usage indicates stability", "is_required": True}
        ]
        
        for var_data in default_variables:
            self.add_variable(var_data)
    
    def add_category(self, category_data: Dict[str, Any]) -> int:
        """Add new category"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO scorecard_categories (category_name, display_order, total_weight, color_code, icon)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            category_data['category_name'],
            category_data['display_order'],
            category_data['total_weight'],
            category_data.get('color_code', '#666666'),
            category_data.get('icon', '📊')
        ))
        
        category_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return category_id
    
    def add_variable(self, variable_data: Dict[str, Any]) -> int:
        """Add new variable"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        
        cursor.execute('''
            INSERT INTO scorecard_variables 
            (variable_id, display_name, category, weight, data_type, input_type,
             is_required, min_value, max_value, default_value, help_text, 
             scientific_basis, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            variable_data['variable_id'],
            variable_data['display_name'],
            variable_data['category'],
            variable_data['weight'],
            variable_data['data_type'],
            variable_data['input_type'],
            variable_data.get('is_required', True),
            variable_data.get('min_value'),
            variable_data.get('max_value'),
            variable_data.get('default_value', ''),
            variable_data.get('help_text', ''),
            variable_data.get('scientific_basis', ''),
            now,
            now
        ))
        
        variable_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return variable_id
    
    def get_categories(self) -> List[Dict]:
        """Get all active categories"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT category_name, display_order, total_weight, color_code, icon
            FROM scorecard_categories 
            WHERE is_active = 1
            ORDER BY display_order
        ''')
        
        categories = []
        for row in cursor.fetchall():
            categories.append({
                'category_name': row[0],
                'display_order': row[1],
                'total_weight': row[2],
                'color_code': row[3],
                'icon': row[4]
            })
        
        conn.close()
        return categories
    
    def get_active_variables(self) -> List[Dict]:
        """Get all active variables with their score bands"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT variable_id, display_name, category, weight, data_type, input_type,
                   is_required, min_value, max_value, default_value, help_text, 
                   scientific_basis, created_at, updated_at
            FROM scorecard_variables 
            WHERE is_active = 1
            ORDER BY category, weight DESC
        ''')
        
        variables = []
        for row in cursor.fetchall():
            var = {
                'variable_id': row[0],
                'display_name': row[1],
                'category': row[2],
                'weight': row[3],
                'data_type': row[4],
                'input_type': row[5],
                'is_required': row[6],
                'min_value': row[7],
                'max_value': row[8],
                'default_value': row[9],
                'help_text': row[10],
                'scientific_basis': row[11],
                'created_at': row[12],
                'updated_at': row[13],
                'score_bands': self.get_variable_score_bands(row[0])
            }
            variables.append(var)
        
        conn.close()
        return variables
    
    def get_variable_score_bands(self, variable_id: str) -> List[Dict]:
        """Get score bands for a specific variable"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT band_order, threshold_min, threshold_max, operator, score, label, description
            FROM score_bands 
            WHERE variable_id = ? AND is_active = 1
            ORDER BY band_order
        ''', (variable_id,))
        
        bands = []
        for row in cursor.fetchall():
            bands.append({
                'band_order': row[0],
                'threshold_min': row[1],
                'threshold_max': row[2],
                'operator': row[3],
                'score': row[4],
                'label': row[5],
                'description': row[6]
            })
        
        conn.close()
        return bands
    
    def get_inactive_variables(self) -> List[Dict]:
        """Get all inactive variables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT variable_id, display_name, category, weight, data_type, input_type,
                   scientific_basis, updated_at
            FROM scorecard_variables 
            WHERE is_active = 0
            ORDER BY updated_at DESC
        ''')
        
        variables = []
        for row in cursor.fetchall():
            var = {
                'variable_id': row[0],
                'display_name': row[1],
                'category': row[2],
                'weight': row[3],
                'data_type': row[4],
                'input_type': row[5],
                'scientific_basis': row[6],
                'updated_at': row[7],
                'score_bands': self.get_variable_score_bands(row[0])
            }
            variables.append(var)
        
        conn.close()
        return variables
    
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
        """Deactivate a variable"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE scorecard_variables 
            SET is_active = 0, updated_at = ?
            WHERE variable_id = ?
        ''', (datetime.now().isoformat(), variable_id))
        
        conn.commit()
        conn.close()
    
    def reactivate_variable(self, variable_id: str):
        """Reactivate a variable"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE scorecard_variables 
            SET is_active = 1, updated_at = ?
            WHERE variable_id = ?
        ''', (datetime.now().isoformat(), variable_id))
        
        conn.commit()
        conn.close()
    
    def sync_weights_from_file(self) -> bool:
        """Sync weights from scoring_weights.json to database"""
        try:
            import json
            
            # Load weights from JSON file
            try:
                with open("scoring_weights.json", "r") as f:
                    weights = json.load(f)
            except FileNotFoundError:
                return False
            
            # Update database with file weights
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for variable_id, weight in weights.items():
                # Convert decimal to percentage
                weight_percent = weight * 100.0
                
                cursor.execute('''
                    UPDATE scorecard_variables 
                    SET weight = ?, updated_at = ?
                    WHERE variable_id = ? AND is_active = 1
                ''', (weight_percent, datetime.now().isoformat(), variable_id))
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            print(f"Error syncing weights from file: {e}")
            return False
    
    def sync_weights_to_file(self) -> bool:
        """Sync weights from database to scoring_weights.json"""
        try:
            import json
            
            # Get current weights from database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT variable_id, weight FROM scorecard_variables WHERE is_active = 1")
            db_results = cursor.fetchall()
            conn.close()
            
            # Convert to decimal format and normalize
            db_weights = {var_id: weight/100.0 for var_id, weight in db_results}
            total_weight = sum(db_weights.values())
            
            if total_weight > 0:
                normalized_weights = {k: v/total_weight for k, v in db_weights.items()}
            else:
                normalized_weights = db_weights
            
            # Save to JSON file
            with open("scoring_weights.json", "w") as f:
                json.dump(normalized_weights, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Error syncing weights to file: {e}")
            return False

class ICSMCalibrationEngine:
    """Advanced ICSM-Category Management calibration system"""
    
    def __init__(self):
        self.category_mapping = {
            # Map comprehensive ICSM variables to Category Management categories
            "Core Credit Variables": {
                "icsm_contributors": ["credit_score", "income", "debt_ratio", "credit_history", "payment_history"],
                "target_weight": 35.0,
                "primary_drivers": ["credit_score", "income"],
                "credit_expertise": "Traditional credit risk factors - most predictive of default probability"
            },
            "Behavioral Analytics": {
                "icsm_contributors": ["spending_patterns", "transaction_frequency", "account_usage", "financial_behavior", "digital_footprint"],
                "target_weight": 20.0,
                "primary_drivers": ["spending_patterns", "financial_behavior"],
                "credit_expertise": "Digital behavioral patterns and financial management habits"
            },
            "Employment Stability": {
                "icsm_contributors": ["employment", "job_tenure", "income_stability", "employer_type"],
                "target_weight": 15.0,
                "primary_drivers": ["employment", "income_stability"],
                "credit_expertise": "Income stability and repayment capacity assessment"
            },
            "Banking Behavior": {
                "icsm_contributors": ["account_history", "banking_relationship", "account_management", "overdraft_history"],
                "target_weight": 10.0,
                "primary_drivers": ["account_history", "banking_relationship"],
                "credit_expertise": "Banking relationship depth and payment discipline"
            },
            "Exposure & Intent": {
                "icsm_contributors": ["existing_loans", "credit_utilization", "loan_purpose", "collateral_value"],
                "target_weight": 12.0,
                "primary_drivers": ["existing_loans", "credit_utilization"],
                "credit_expertise": "Current debt burden and exposure concentration risk"
            },
            "Geographic & Social": {
                "icsm_contributors": ["location_risk", "social_indicators", "regional_factors", "demographic_data"],
                "target_weight": 8.0,
                "primary_drivers": ["location_risk", "social_indicators"],
                "credit_expertise": "Demographic stability and location-based risk factors"
            }
        }
        
        # Risk factor importance hierarchy based on credit expertise
        self.risk_hierarchy = {
            "Tier 1 - Critical": {
                "variables": ["credit_score", "income", "debt_ratio", "employment"],
                "risk_multiplier": 1.0,
                "description": "Primary default predictors with highest statistical significance"
            },
            "Tier 2 - Important": {
                "variables": ["credit_history", "income_stability", "spending_patterns", "existing_loans"],
                "risk_multiplier": 0.75,
                "description": "Strong predictive variables for risk assessment"
            },
            "Tier 3 - Supporting": {
                "variables": ["job_tenure", "account_history", "credit_utilization", "employer_type"],
                "risk_multiplier": 0.5,
                "description": "Additional context for comprehensive risk evaluation"
            },
            "Tier 4 - Contextual": {
                "variables": ["location_risk", "regional_factors", "demographic_data", "digital_footprint"],
                "risk_multiplier": 0.3,
                "description": "Demographic and behavioral context variables"
            }
        }
    
    def calibrate_icsm_to_categories(self, icsm_weights: Dict[str, float]) -> Dict[str, float]:
        """Intelligently distribute ICSM weights into category structure"""
        category_weights = {}
        
        for category, config in self.category_mapping.items():
            category_total = 0.0
            category_variables = []
            
            # Sum weights of ICSM variables that belong to this category
            for var in config["icsm_contributors"]:
                if var in icsm_weights:
                    category_total += icsm_weights[var]
                    category_variables.append(var)
            
            # Apply risk-based scaling
            scaled_total = self._apply_risk_scaling(category_variables, category_total)
            
            # Apply credit expertise adjustments
            expertise_adjusted = self._apply_expertise_adjustments(category, scaled_total)
            
            category_weights[category] = expertise_adjusted
        
        # Normalize to target category weights while maintaining relative importance
        return self._normalize_to_targets(category_weights)
    
    def _apply_risk_scaling(self, variables: List[str], base_weight: float) -> float:
        """Apply risk hierarchy scaling to category weights"""
        if not variables:
            return base_weight
            
        # Calculate average risk multiplier for variables in this category
        total_multiplier = 0.0
        var_count = 0
        
        for var in variables:
            for tier, tier_config in self.risk_hierarchy.items():
                if var in tier_config["variables"]:
                    total_multiplier += tier_config["risk_multiplier"]
                    var_count += 1
                    break
        
        if var_count == 0:
            return base_weight
            
        avg_multiplier = total_multiplier / var_count
        return base_weight * (1.0 + avg_multiplier * 0.2)  # Scale by 20% based on risk tier
    
    def _apply_expertise_adjustments(self, category: str, weight: float) -> float:
        """Apply credit expertise-based adjustments"""
        expertise_factors = {
            "Core Credit Variables": 1.15,  # Boost traditional credit factors
            "Employment Stability": 1.10,   # Important for repayment capacity
            "Banking Behavior": 1.05,       # Good behavioral indicator
            "Behavioral Analytics": 1.08,   # Historical performance matters
            "Exposure & Intent": 0.95,      # Moderate importance
            "Geographic & Social": 0.90     # Supporting context
        }
        
        return weight * expertise_factors.get(category, 1.0)
    
    def _normalize_to_targets(self, category_weights: Dict[str, float]) -> Dict[str, float]:
        """Normalize weights to approximate target category weights"""
        if not category_weights:
            return {}
            
        # Get target weights
        targets = {cat: config["target_weight"] for cat, config in self.category_mapping.items()}
        
        # Calculate scaling factors
        total_current = sum(category_weights.values())
        total_target = sum(targets.values())
        
        if total_current == 0:
            return targets
        
        # Scale to targets while preserving relative importance
        normalized = {}
        for category, current_weight in category_weights.items():
            target_weight = targets[category]
            # Blend current weight with target (70% current, 30% target)
            blended = (current_weight / total_current) * total_target * 0.7 + target_weight * 0.3
            normalized[category] = max(blended, 0.5)  # Minimum 0.5%
        
        # Final normalization to 100%
        final_total = sum(normalized.values())
        return {k: (v / final_total) * 100 for k, v in normalized.items()}
    
    def apply_icsm_scalability_factors(self, icsm_weights: Dict[str, float]) -> Dict[str, float]:
        """Apply scalability factors to ensure ICSM can handle advanced variable structures"""
        
        # Credit expertise-based scalability adjustments
        scalability_factors = {
            # Tier 1 Critical - Must maintain high weights for ICSM stability
            "credit_score": 1.2,     # Primary default predictor
            "foir": 1.15,            # Key repayment capacity indicator
            "dpd30plus": 1.1,        # Direct delinquency signal
            "monthly_income": 1.1,   # Foundation of repayment ability
            
            # Tier 2 Important - Moderate scaling for balance
            "enquiry_count": 1.0,    # Standard credit appetite indicator
            "employment_tenure_months": 1.0,  # Stability measure
            "loan_completion_ratio": 1.05,    # Performance history
            "defaulted_loans": 1.05, # Risk history
            
            # Tier 3 Supporting - Slight reduction for ICSM simplicity
            "credit_vintage_months": 0.95,    # Supporting credit history
            "avg_monthly_balance": 0.9,       # Banking behavior
            "outstanding_amount_percent": 0.9, # Current exposure
            "company_stability": 0.9,         # Employment quality
            
            # Tier 4 Contextual - Reduced for ICSM focus
            "age": 0.8,              # Demographic context
            "job_type": 0.8,         # Employment type
            "bank_account_vintage_months": 0.85, # Banking relationship
            "loan_mix_type": 0.85,   # Product mix context
            
            # Behavioral variables - Moderate for ICSM compatibility
            "bounce_frequency_per_year": 0.9,
            "geographic_location_risk": 0.8,
            "mobile_vintage_months": 0.75,
            "channel_type": 0.75,
            "unsecured_loan_amount": 0.9,
            "our_lender_exposure": 0.85
        }
        
        # Apply scalability factors
        scaled_weights = {}
        for var, weight in icsm_weights.items():
            factor = scalability_factors.get(var, 1.0)
            scaled_weights[var] = weight * factor
        
        # Ensure minimum thresholds for critical variables (ICSM stability)
        minimum_thresholds = {
            "credit_score": 0.08,    # Minimum 8% for credit score
            "foir": 0.06,            # Minimum 6% for FOIR
            "monthly_income": 0.05,  # Minimum 5% for income
            "dpd30plus": 0.04        # Minimum 4% for delinquency
        }
        
        for var, min_weight in minimum_thresholds.items():
            if var in scaled_weights:
                scaled_weights[var] = max(scaled_weights[var], min_weight)
            else:
                scaled_weights[var] = min_weight
        
        return scaled_weights
    
    def calculate_icsm_score(self, applicant_data: Dict[str, Any], icsm_weights: Dict[str, float]) -> Dict[str, Any]:
        """Calculate ICSM score using proper credit scoring methodology"""
        
        score_components = {}
        total_score = 0.0
        total_possible = 0.0
        
        # Define scoring bands for each ICSM variable based on credit expertise
        scoring_bands = self._get_icsm_scoring_bands()
        
        for variable, weight in icsm_weights.items():
            if variable in applicant_data:
                value = applicant_data[variable]
                
                # Calculate variable score using appropriate scoring method
                if variable in scoring_bands:
                    variable_score = self._calculate_variable_score(variable, value, scoring_bands[variable])
                    weighted_score = variable_score * weight
                    
                    score_components[variable] = {
                        'raw_value': value,
                        'variable_score': variable_score,
                        'weight': weight,
                        'weighted_score': weighted_score,
                        'max_possible': weight * 100  # Maximum possible contribution
                    }
                    
                    total_score += weighted_score
                    total_possible += weight * 100
        
        # Calculate final score as percentage
        final_score = (total_score / total_possible * 100) if total_possible > 0 else 0
        
        # Apply business rules and determine decision
        decision_result = self._apply_icsm_business_rules(final_score, score_components, applicant_data)
        
        return {
            'final_score': round(final_score, 2),
            'score_components': score_components,
            'total_weighted_score': round(total_score, 4),
            'total_possible_score': round(total_possible, 4),
            'decision': decision_result['decision'],
            'risk_bucket': decision_result['risk_bucket'],
            'clearance_passed': decision_result['clearance_passed'],
            'decision_factors': decision_result['factors']
        }
    
    def _get_icsm_scoring_bands(self) -> Dict[str, Dict]:
        """Define scoring bands for ICSM variables based on credit expertise"""
        return {
            'credit_score': {
                'type': 'numeric_bands',
                'bands': [
                    {'min': 750, 'max': 900, 'score': 100, 'label': 'Excellent'},
                    {'min': 700, 'max': 749, 'score': 85, 'label': 'Very Good'},
                    {'min': 650, 'max': 699, 'score': 70, 'label': 'Good'},
                    {'min': 600, 'max': 649, 'score': 55, 'label': 'Fair'},
                    {'min': 550, 'max': 599, 'score': 40, 'label': 'Poor'},
                    {'min': 300, 'max': 549, 'score': 20, 'label': 'Very Poor'}
                ]
            },
            'foir': {
                'type': 'numeric_bands',
                'bands': [
                    {'min': 0, 'max': 0.3, 'score': 100, 'label': 'Excellent'},
                    {'min': 0.31, 'max': 0.4, 'score': 85, 'label': 'Very Good'},
                    {'min': 0.41, 'max': 0.5, 'score': 70, 'label': 'Good'},
                    {'min': 0.51, 'max': 0.6, 'score': 55, 'label': 'Fair'},
                    {'min': 0.61, 'max': 0.75, 'score': 30, 'label': 'Poor'},
                    {'min': 0.76, 'max': 2.0, 'score': 10, 'label': 'Very Poor'}
                ]
            },
            'monthly_income': {
                'type': 'numeric_bands',
                'bands': [
                    {'min': 100000, 'max': 999999, 'score': 100, 'label': 'Very High'},
                    {'min': 75000, 'max': 99999, 'score': 90, 'label': 'High'},
                    {'min': 50000, 'max': 74999, 'score': 80, 'label': 'Good'},
                    {'min': 35000, 'max': 49999, 'score': 70, 'label': 'Average'},
                    {'min': 25000, 'max': 34999, 'score': 60, 'label': 'Below Average'},
                    {'min': 15000, 'max': 24999, 'score': 40, 'label': 'Low'},
                    {'min': 0, 'max': 14999, 'score': 20, 'label': 'Very Low'}
                ]
            },
            'dpd30plus': {
                'type': 'numeric_bands',
                'bands': [
                    {'min': 0, 'max': 0, 'score': 100, 'label': 'No Delinquency'},
                    {'min': 1, 'max': 2, 'score': 70, 'label': 'Minor Issues'},
                    {'min': 3, 'max': 5, 'score': 40, 'label': 'Moderate Risk'},
                    {'min': 6, 'max': 10, 'score': 20, 'label': 'High Risk'},
                    {'min': 11, 'max': 999, 'score': 5, 'label': 'Very High Risk'}
                ]
            },
            'enquiry_count': {
                'type': 'numeric_bands',
                'bands': [
                    {'min': 0, 'max': 2, 'score': 100, 'label': 'Low Appetite'},
                    {'min': 3, 'max': 5, 'score': 80, 'label': 'Moderate Appetite'},
                    {'min': 6, 'max': 10, 'score': 60, 'label': 'High Appetite'},
                    {'min': 11, 'max': 15, 'score': 40, 'label': 'Very High Appetite'},
                    {'min': 16, 'max': 999, 'score': 20, 'label': 'Excessive Appetite'}
                ]
            }
        }
    
    def _calculate_variable_score(self, variable: str, value: Any, scoring_config: Dict) -> float:
        """Calculate score for individual variable using scoring bands"""
        
        if scoring_config['type'] == 'numeric_bands':
            for band in scoring_config['bands']:
                if band['min'] <= value <= band['max']:
                    return band['score']
            # Default to lowest score if outside all bands
            return min(band['score'] for band in scoring_config['bands'])
        
        elif scoring_config['type'] == 'categorical':
            return scoring_config['mapping'].get(str(value), scoring_config.get('default', 50))
        
        return 50  # Default middle score
    
    def _apply_icsm_business_rules(self, final_score: float, score_components: Dict, applicant_data: Dict) -> Dict:
        """Apply business rules to determine final decision"""
        
        # Risk bucket classification
        if final_score >= 75:
            risk_bucket = "Low Risk"
            base_decision = "Approve"
        elif final_score >= 60:
            risk_bucket = "Medium Risk" 
            base_decision = "Conditional Approve"
        elif final_score >= 45:
            risk_bucket = "High Risk"
            base_decision = "Manual Review"
        else:
            risk_bucket = "Very High Risk"
            base_decision = "Decline"
        
        # Critical clearance checks
        clearance_passed = True
        decision_factors = []
        
        # Credit score knockout
        if 'credit_score' in score_components:
            credit_score = score_components['credit_score']['raw_value']
            if credit_score < 550:
                clearance_passed = False
                decision_factors.append("Credit score below minimum threshold (550)")
                base_decision = "Decline"
        
        # FOIR knockout
        if 'foir' in score_components:
            foir = score_components['foir']['raw_value']
            if foir > 0.75:
                clearance_passed = False
                decision_factors.append("FOIR exceeds maximum threshold (75%)")
                base_decision = "Decline"
        
        # DPD knockout
        if 'dpd30plus' in score_components:
            dpd = score_components['dpd30plus']['raw_value']
            if dpd > 10:
                clearance_passed = False
                decision_factors.append("Excessive delinquency history")
                base_decision = "Decline"
        
        # Income adequacy check
        if 'monthly_income' in score_components:
            income = score_components['monthly_income']['raw_value']
            if income < 15000:
                decision_factors.append("Income below recommended minimum")
                if base_decision == "Approve":
                    base_decision = "Conditional Approve"
        
        return {
            'decision': base_decision,
            'risk_bucket': risk_bucket,
            'clearance_passed': clearance_passed,
            'factors': decision_factors
        }

def sync_weights_from_icsm():
    """Enhanced ICSM to Dynamic Scorecard synchronization with intelligent calibration"""
    try:
        import json
        import os
        from datetime import datetime
        
        if not os.path.exists("scoring_weights.json"):
            return False
            
        with open("scoring_weights.json", "r") as f:
            icsm_weights = json.load(f)
        
        # Initialize calibration engine
        calibrator = ICSMCalibrationEngine()
        
        # Step 1: Calibrate ICSM weights to category structure
        category_weights = calibrator.calibrate_icsm_to_categories(icsm_weights)
        
        # Step 2: Distribute category weights to individual variables
        conn = sqlite3.connect("scorecard_config.db")
        cursor = conn.cursor()
        
        updated_count = 0
        redistribution_log = []
        
        for category, target_category_weight in category_weights.items():
            # Get variables in this category
            cursor.execute('''
                SELECT variable_id, weight FROM scorecard_variables 
                WHERE category = ? AND is_active = 1
            ''', (category,))
            category_vars = cursor.fetchall()
            
            if not category_vars:
                continue
            
            # Calculate current total weight in category
            current_total = sum(var[1] for var in category_vars)
            
            if current_total == 0:
                # Equal distribution if no weights exist
                var_weight = target_category_weight / len(category_vars)
                for var_id, _ in category_vars:
                    cursor.execute('''
                        UPDATE scorecard_variables 
                        SET weight = ?, updated_at = ?
                        WHERE variable_id = ? AND is_active = 1
                    ''', (var_weight, datetime.now().isoformat(), var_id))
                    updated_count += 1
                    redistribution_log.append(f"{var_id}: {var_weight:.2f}%")
            else:
                # Proportional redistribution
                scale_factor = target_category_weight / current_total
                for var_id, current_weight in category_vars:
                    new_weight = current_weight * scale_factor
                    cursor.execute('''
                        UPDATE scorecard_variables 
                        SET weight = ?, updated_at = ?
                        WHERE variable_id = ? AND is_active = 1
                    ''', (new_weight, datetime.now().isoformat(), var_id))
                    updated_count += 1
                    redistribution_log.append(f"{var_id}: {current_weight:.2f}% → {new_weight:.2f}%")
        
        # Step 3: Handle ICSM variables not in Category Management
        orphaned_variables = []
        for var_id, weight in icsm_weights.items():
            cursor.execute('''
                SELECT COUNT(*) FROM scorecard_variables 
                WHERE variable_id = ? AND is_active = 1
            ''', (var_id,))
            if cursor.fetchone()[0] == 0:
                orphaned_variables.append((var_id, weight))
        
        conn.commit()
        conn.close()
        
        # Clear session state to force refresh
        if 'dynamic_manager' in st.session_state:
            del st.session_state['dynamic_manager']
        
        # Detailed logging
        print(f"ICSM Sync FROM: Updated {updated_count} variables from {len(icsm_weights)} ICSM weights")
        print(f"Category Distribution: {category_weights}")
        if orphaned_variables:
            print(f"Orphaned ICSM variables (not in Category Management): {[v[0] for v in orphaned_variables]}")
        
        return updated_count > 0
        
    except Exception as e:
        print(f"Error syncing from ICSM: {e}")
        return False

def sync_weights_to_icsm():
    """Enhanced Dynamic Scorecard to ICSM synchronization with intelligent downscaling"""
    try:
        import json
        
        # Initialize calibration engine for reverse mapping
        calibrator = ICSMCalibrationEngine()
        
        conn = sqlite3.connect("scorecard_config.db")
        cursor = conn.cursor()
        
        # Step 1: Get category-wise weight distribution
        cursor.execute('''
            SELECT category, SUM(weight) as category_total, COUNT(*) as var_count
            FROM scorecard_variables 
            WHERE is_active = 1 
            GROUP BY category
            ORDER BY category
        ''')
        category_totals = cursor.fetchall()
        
        # Step 2: Get all active variables with their categories
        cursor.execute('''
            SELECT variable_id, weight, category 
            FROM scorecard_variables 
            WHERE is_active = 1 
            ORDER BY category, weight DESC
        ''')
        all_variables = cursor.fetchall()
        conn.close()
        
        if not all_variables:
            print("No active variables found in database")
            return False
        
        # Step 3: Intelligent ICSM mapping using category aggregation
        icsm_weights = {}
        category_distributions = {}
        
        # Group variables by category for intelligent aggregation
        for var_id, weight, category in all_variables:
            if category not in category_distributions:
                category_distributions[category] = []
            category_distributions[category].append((var_id, weight))
        
        # Step 4: Intelligent mapping between Dynamic Scorecard and ICSM variables
        ds_to_icsm_mapping = {
            # Core Credit Variables mapping
            "credit_score": "credit_score",
            "monthly_income": "monthly_income", 
            "foir": "foir",
            "dpd30plus": "credit_history",  # Map payment behavior
            "enquiry_count": "credit_utilization",  # Map credit appetite
            "age": "demographic_data",  # Map demographic factor
            
            # Behavioral Analytics mapping
            "credit_vintage_months": "account_usage",
            "loan_mix_type": "financial_behavior",
            "loan_completion_ratio": "spending_patterns",
            "defaulted_loans": "financial_behavior",
            
            # Employment Stability mapping
            "job_type": "employer_type",
            "employment_tenure_months": "job_tenure",
            "company_stability": "employment",
            
            # Banking Behavior mapping
            "bank_account_vintage_months": "account_history",
            "avg_monthly_balance": "banking_relationship",
            "bounce_frequency_per_year": "overdraft_history",
            
            # Exposure & Intent mapping
            "unsecured_loan_amount": "existing_loans",
            "outstanding_amount_percent": "credit_utilization",
            "our_lender_exposure": "loan_purpose",
            
            # Geographic & Social mapping
            "channel_type": "social_indicators",
            "geographic_location_risk": "location_risk",
            "mobile_vintage_months": "regional_factors"
        }
        
        # Map Dynamic Scorecard variables to ICSM using intelligent mapping
        for var_id, weight, category in all_variables:
            if var_id in ds_to_icsm_mapping:
                icsm_var = ds_to_icsm_mapping[var_id]
                icsm_weight = weight / 100.0  # Convert percentage to decimal
                icsm_weights[icsm_var] = icsm_weights.get(icsm_var, 0) + icsm_weight
                # Handle unmapped categories - distribute among closest ICSM variables
                print(f"Warning: Category '{category}' not mapped to ICSM variables")
                
                # Default distribution for unmapped categories
                default_vars = ["credit_score", "monthly_income", "foir"]
                default_per_var = category_weight / len(default_vars)
                for var in default_vars:
                    icsm_weights[var] = icsm_weights.get(var, 0) + default_per_var
        
        # Step 5: Apply risk-based weight adjustments to ensure ICSM scalability
        adjusted_weights = calibrator.apply_icsm_scalability_factors(icsm_weights)
        
        # Step 6: Normalize to ensure total weight equals 1.0
        total_weight = sum(adjusted_weights.values())
        if total_weight > 0:
            normalized_weights = {k: v / total_weight for k, v in adjusted_weights.items()}
        else:
            # Fallback to equal distribution among core variables
            core_vars = ["credit_score", "monthly_income", "foir", "dpd30plus", "enquiry_count"]
            normalized_weights = {var: 0.2 for var in core_vars}
        
        # Step 7: Write to scoring_weights.json file (ICSM system)
        with open("scoring_weights.json", "w") as f:
            json.dump(normalized_weights, f, indent=2)
        
        # Step 8: Clear cached session states to force refresh
        if 'scoring_weights' in st.session_state:
            del st.session_state['scoring_weights']
        if 'config_manager' in st.session_state:
            del st.session_state['config_manager']
        
        # Step 9: Generate comprehensive sync report
        print(f"ICSM Sync TO: Exported {len(normalized_weights)} ICSM variables from {len(all_variables)} Category Management variables")
        print(f"Category Aggregation: {len(category_distributions)} categories processed")
        print(f"Total Weight Validation: {sum(normalized_weights.values()):.6f} (should be 1.0)")
        
        # Log weight distribution by risk tier
        risk_tier_totals = {}
        for var, weight in normalized_weights.items():
            for tier, config in calibrator.risk_hierarchy.items():
                if var in config["variables"]:
                    risk_tier_totals[tier] = risk_tier_totals.get(tier, 0) + weight
                    break
        
        print(f"Risk Tier Distribution: {risk_tier_totals}")
        
        return True
        
    except Exception as e:
        print(f"Error syncing to ICSM: {e}")
        return False

def calculate_dynamic_score(form_data: Dict, manager) -> Dict[str, Any]:
    """Calculate overall score using slider-based percentage mapping"""
    
    # Define slider mappings for direct percentage calculation
    slider_mappings = {
        # Core Credit Variables (35% total)
        'credit_score': {'min': 0, 'max': 20, 'weight': 10.0, 'category': 'Core Credit Variables'},
        'foir': {'min': 0, 'max': 15, 'weight': 8.0, 'category': 'Core Credit Variables'},
        'dpd30plus': {'min': 0, 'max': 15, 'weight': 6.0, 'category': 'Core Credit Variables'},
        'enquiry_count': {'min': 0, 'max': 10, 'weight': 6.0, 'category': 'Core Credit Variables'},
        'age': {'min': 0, 'max': 8, 'weight': 3.0, 'category': 'Core Credit Variables'},
        'monthly_income': {'min': 0, 'max': 15, 'weight': 2.0, 'category': 'Core Credit Variables'},
        
        # Behavioral Analytics (20% total)
        'credit_vintage_months': {'min': 0, 'max': 10, 'weight': 6.0, 'category': 'Behavioral Analytics'},
        'loan_mix_type': {'min': 0, 'max': 8, 'weight': 4.0, 'category': 'Behavioral Analytics'},
        'loan_completion_ratio': {'min': 0, 'max': 10, 'weight': 5.0, 'category': 'Behavioral Analytics'},
        'defaulted_loans': {'min': 0, 'max': 10, 'weight': 5.0, 'category': 'Behavioral Analytics'},
        
        # Employment Stability (15% total)
        'job_type': {'min': 0, 'max': 10, 'weight': 5.0, 'category': 'Employment Stability'},
        'employment_tenure_months': {'min': 0, 'max': 10, 'weight': 5.0, 'category': 'Employment Stability'},
        'company_stability': {'min': 0, 'max': 10, 'weight': 5.0, 'category': 'Employment Stability'},
        
        # Banking Behavior (10% total)
        'bank_account_vintage_months': {'min': 0, 'max': 8, 'weight': 3.0, 'category': 'Banking Behavior'},
        'avg_monthly_balance': {'min': 0, 'max': 10, 'weight': 4.0, 'category': 'Banking Behavior'},
        'bounce_frequency_per_year': {'min': 0, 'max': 8, 'weight': 3.0, 'category': 'Banking Behavior'},
        
        # Exposure & Intent (12% total)
        'unsecured_loan_amount': {'min': 0, 'max': 8, 'weight': 3.0, 'category': 'Exposure & Intent'},
        'outstanding_amount_percent': {'min': 0, 'max': 8, 'weight': 3.0, 'category': 'Exposure & Intent'},
        'our_lender_exposure': {'min': 0, 'max': 8, 'weight': 3.0, 'category': 'Exposure & Intent'},
        'channel_type': {'min': 0, 'max': 8, 'weight': 3.0, 'category': 'Exposure & Intent'},
        
        # Geographic & Social (8% total)
        'geographic_risk': {'min': 0, 'max': 10, 'weight': 4.0, 'category': 'Geographic & Social'},
        'mobile_vintage_months': {'min': 0, 'max': 8, 'weight': 2.0, 'category': 'Geographic & Social'},
        'digital_engagement_score': {'min': 0, 'max': 8, 'weight': 2.0, 'category': 'Geographic & Social'}
    }
    
    total_score = 0
    variable_scores = {}
    
    for var_id, config in slider_mappings.items():
        if var_id in form_data:
            slider_value = form_data[var_id]
            max_value = config['max']
            weight = config['weight']
            
            # Direct percentage calculation: (slider_value / max_value) × weight
            earned_percent = (slider_value / max_value) * weight
            total_score += earned_percent
            
            variable_scores[var_id] = {
                "variable_name": var_id.replace('_', ' ').title(),
                "value": slider_value,
                "raw_score": slider_value / max_value,
                "weight": weight,
                "weighted_score": earned_percent / 100,  # Convert to decimal for consistency
                "label": f"{slider_value}/{max_value}",
                "category": config['category']
            }
    
    # Final score is the sum of earned percentages
    final_score = total_score
    
    # Determine risk bucket (using same logic as original)
    if final_score >= 80:
        bucket = "A"
        decision = "Auto-approve"
        risk_level = "Low Risk (<3%)"
    elif final_score >= 65:
        bucket = "B" 
        decision = "Recommend"
        risk_level = "Moderate Risk (3-8%)"
    elif final_score >= 50:
        bucket = "C"
        decision = "Refer for Manual Review"
        risk_level = "High Risk (8-15%)"
    else:
        bucket = "D"
        decision = "Decline"
        risk_level = "Very High Risk (>15%)"
    
    return {
        "final_score": final_score,
        "risk_bucket": bucket,
        "decision": decision,
        "risk_level": risk_level,
        "variable_scores": variable_scores,
        "total_variables": len(slider_mappings),
        "scored_variables": len(variable_scores)
    }

# Page config
st.set_page_config(page_title="CreditIQ Pro Enterprise", page_icon="🏛️", layout="wide")

# CSS
st.markdown("""
<style>
.main-header {
    background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
    padding: 2rem; border-radius: 10px; color: white; margin-bottom: 2rem; text-align: center;
}
.info-box {
    background: #f8fafc; padding: 1rem; border-radius: 8px; border-left: 4px solid #3b82f6;
}
</style>
""", unsafe_allow_html=True)

# Database functions
@st.cache_resource
def init_database():
    """Initialize empty database with tables only"""
    conn = sqlite3.connect("creditiq_dynamic.db", check_same_thread=False)
    cursor = conn.cursor()
    
    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL,
            company_id INTEGER,
            created_by TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Companies table  
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            created_by TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Scorecards table with correct column names
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scorecards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            configuration TEXT NOT NULL,
            weights TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies (id)
        )
    """)
    
    # Admin accounts table (for initial setup)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admin_setup (
            id INTEGER PRIMARY KEY,
            is_initialized BOOLEAN DEFAULT FALSE,
            setup_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    return conn

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_data' not in st.session_state:
    st.session_state.user_data = None
if 'setup_mode' not in st.session_state:
    st.session_state.setup_mode = False

# Get database connection
db = init_database()

def check_system_initialized():
    """Check if system has been initialized with Super Admin"""
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'super_admin'")
    count = cursor.fetchone()[0]
    return count > 0

def create_super_admin(username, password):
    """Create the first Super Admin user"""
    try:
        cursor = db.cursor()
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        cursor.execute("""
            INSERT INTO users (username, password_hash, role, company_id, created_by) 
            VALUES (?, ?, 'super_admin', NULL, 'system')
        """, (username, password_hash))
        
        cursor.execute("INSERT INTO admin_setup (is_initialized) VALUES (TRUE)")
        db.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def authenticate_user(username, password):
    """Authenticate user against database"""
    cursor = db.cursor()
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    cursor.execute("""
        SELECT id, username, role, company_id 
        FROM users 
        WHERE username=? AND password_hash=?
    """, (username, password_hash))
    return cursor.fetchone()

def get_all_companies():
    """Get all companies from database"""
    cursor = db.cursor()
    cursor.execute("SELECT id, name, type FROM companies ORDER BY name")
    return cursor.fetchall()

def get_company_users(company_id):
    """Get all users for a specific company"""
    cursor = db.cursor()
    cursor.execute("""
        SELECT username, role, created_at 
        FROM users 
        WHERE company_id = ? 
        ORDER BY created_at
    """, (company_id,))
    return cursor.fetchall()

def get_company_name(company_id):
    """Get company name by ID"""
    if not company_id:
        return None
    cursor = db.cursor()
    cursor.execute("SELECT name FROM companies WHERE id = ?", (company_id,))
    result = cursor.fetchone()
    return result[0] if result else None

def generate_comprehensive_weights(institution_type, risk_appetite, data_sources, selected_products, primary_product, target_segment):
    """Generate comprehensive weights based on institution profile and business requirements"""
    
    # Base weights by institution type
    base_weights = {
        "NBFC": {"credit_score": 0.35, "income": 0.25, "debt_ratio": 0.20, "employment": 0.15, "credit_history": 0.05},
        "Bank": {"credit_score": 0.30, "income": 0.20, "debt_ratio": 0.25, "employment": 0.15, "credit_history": 0.10},
        "Fintech": {"credit_score": 0.40, "income": 0.30, "debt_ratio": 0.15, "employment": 0.10, "credit_history": 0.05},
        "Microfinance Institution": {"credit_score": 0.20, "income": 0.35, "debt_ratio": 0.15, "employment": 0.20, "credit_history": 0.10},
        "DSA/Agent": {"credit_score": 0.35, "income": 0.25, "debt_ratio": 0.20, "employment": 0.15, "credit_history": 0.05},
        "Housing Finance Company": {"credit_score": 0.25, "income": 0.30, "debt_ratio": 0.20, "employment": 0.15, "credit_history": 0.10},
        "Gold Loan Company": {"credit_score": 0.20, "income": 0.40, "debt_ratio": 0.15, "employment": 0.15, "credit_history": 0.10}
    }
    
    # Get base weights for institution type
    weights = base_weights.get(institution_type, base_weights["NBFC"]).copy()
    
    # Adjust based on risk appetite
    if "Conservative" in risk_appetite:
        weights["credit_score"] += 0.05
        weights["credit_history"] += 0.03
        weights["debt_ratio"] += 0.02
        weights["income"] -= 0.05
        weights["employment"] -= 0.05
    elif "Aggressive" in risk_appetite:
        weights["credit_score"] -= 0.03
        weights["income"] += 0.08
        weights["employment"] += 0.02
        weights["debt_ratio"] -= 0.05
        weights["credit_history"] -= 0.02
    
    # Adjust based on target segment
    if "Prime" in target_segment:
        weights["credit_score"] += 0.05
        weights["credit_history"] += 0.02
    elif "Sub Prime" in target_segment:
        weights["income"] += 0.05
        weights["employment"] += 0.03
        weights["credit_score"] -= 0.05
    
    # Adjust based on primary product type
    if primary_product:
        if "Personal Loan" in primary_product:
            weights["credit_score"] += 0.02
            weights["income"] += 0.02
        elif "Home Loan" in primary_product:
            weights["income"] += 0.05
            weights["employment"] += 0.03
            weights["debt_ratio"] += 0.02
        elif "Business Loan" in primary_product:
            weights["income"] += 0.03
            weights["employment"] += 0.05
        elif "Gold Loan" in primary_product:
            weights["income"] += 0.08
            weights["credit_score"] -= 0.05
    
    # Adjust based on available data sources
    data_boost = min(len(data_sources) * 0.005, 0.03)  # Cap the boost
    
    if any("Credit Bureau" in source for source in data_sources):
        weights["credit_score"] += data_boost
        weights["credit_history"] += data_boost / 2
    
    if any("Bank Statements" in source for source in data_sources):
        weights["income"] += data_boost
        weights["debt_ratio"] += data_boost / 2
    
    if any("Employment" in source for source in data_sources):
        weights["employment"] += data_boost
    
    # Ensure all weights are positive and normalize
    for key in weights:
        weights[key] = max(weights[key], 0.01)  # Minimum 1%
    
    # Normalize to ensure sum equals 1
    total = sum(weights.values())
    normalized_weights = {k: v/total for k, v in weights.items()}
    
    return normalized_weights

def render_initial_setup():
    """Render initial Super Admin setup screen"""
    st.markdown("""
    <div class="main-header">
        <h1>🏛️ CreditIQ Pro Enterprise</h1>
        <p>Initial System Setup</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
        <h3>Welcome to CreditIQ Pro Enterprise</h3>
        <p>Create your Super Admin account to begin using the system.</p>
        <p>The Super Admin will be able to create companies and manage all users.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### Create Super Admin Account")
        
        with st.form("setup_admin"):
            username = st.text_input("Super Admin Username", placeholder="Enter admin username")
            password = st.text_input("Password", type="password", placeholder="Enter secure password")
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm password")
            
            if st.form_submit_button("Create Super Admin", use_container_width=True):
                if not username or not password:
                    st.error("Please fill in all fields")
                elif password != confirm_password:
                    st.error("Passwords do not match")
                elif len(password) < 6:
                    st.error("Password must be at least 6 characters")
                else:
                    if create_super_admin(username, password):
                        st.success("Super Admin created successfully! You can now login.")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("Failed to create admin. Username may already exist.")

def render_login():
    """Render login screen"""
    st.markdown("""
    <div class="main-header">
        <h1>🏛️ CreditIQ Pro Enterprise</h1>
        <p>User Authentication Portal</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### Login")
        
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        
        if st.button("Login", use_container_width=True):
            if username and password:
                user = authenticate_user(username, password)
                if user:
                    st.session_state.authenticated = True
                    st.session_state.user_data = {
                        'id': user[0],
                        'username': user[1], 
                        'role': user[2],
                        'company_id': user[3]
                    }
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
            else:
                st.error("Please enter username and password")

def render_super_admin():
    """Render Super Admin dashboard"""
    # Fixed header with proper logout positioning
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #6C5CE7 0%, #5A4FCF 100%); 
                padding: 1.5rem 2rem; border-radius: 10px; 
                display: flex; justify-content: space-between; align-items: center; 
                margin-bottom: 2rem; color: white;">
        <div>
            <h1 style="margin: 0; font-size: 2rem; font-weight: 300;">🏛️ Super Admin Dashboard</h1>
            <p style="margin: 0.5rem 0 0 0; opacity: 0.9; font-size: 1.1rem;">Welcome, {st.session_state.user_data['username']}</p>
        </div>
        <div style="text-align: right;">
            <span style="font-size: 0.9rem; opacity: 0.8;">System Administrator</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar with navigation and logout
    with st.sidebar:
        st.markdown("### 🏛️ Super Admin")
        st.markdown("**System Functions:**")
        st.markdown("• Create Companies & Users")
        st.markdown("• Manage All Organizations")
        st.markdown("• System Monitoring")
        st.markdown("• User Administration")
        
        st.markdown("---")
        st.markdown("### 📊 System Overview")
        
        # Quick system stats
        cursor = db.cursor()
        cursor.execute("SELECT COUNT(*) FROM companies")
        company_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM users WHERE role != 'super_admin'")
        user_count = cursor.fetchone()[0]
        
        st.markdown(f"**Companies:** {company_count}")
        st.markdown(f"**Total Users:** {user_count}")
        
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True, type="secondary"):
            st.session_state.authenticated = False
            st.session_state.user_data = None
            st.rerun()
    
    # Tabs for different functions
    tab1, tab2, tab3 = st.tabs(["Create Company", "Manage Companies", "System Overview"])
    
    with tab1:
        st.markdown("### Create New Company")
        
        with st.form("create_company"):
            company_name = st.text_input("Company Name", placeholder="Enter company name")
            institution_type = st.selectbox("Institution Type", 
                                          ["Select Type", "NBFC", "Bank", "Fintech", "Microfinance", "Other"])
            
            st.markdown("#### Create Company Users")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Scorecard User**")
                user1_username = st.text_input("Username", key="user1", placeholder="scorecard user login")
                user1_password = st.text_input("Password", type="password", key="pass1", placeholder="user password")
            
            with col2:
                st.markdown("**Scorecard Approver**")
                user2_username = st.text_input("Username", key="user2", placeholder="scorecard approver login")
                user2_password = st.text_input("Password", type="password", key="pass2", placeholder="approver password")
            
            if st.form_submit_button("Create Company & Users"):
                if not all([company_name, institution_type != "Select Type", 
                           user1_username, user1_password, user2_username, user2_password]):
                    st.error("Please fill in all fields")
                elif user1_username == user2_username:
                    st.error("Usernames must be different")
                else:
                    try:
                        cursor = db.cursor()
                        
                        # Create company
                        cursor.execute("""
                            INSERT INTO companies (name, type, created_by) 
                            VALUES (?, ?, ?)
                        """, (company_name, institution_type, st.session_state.user_data['username']))
                        company_id = cursor.lastrowid
                        
                        # Create users
                        hash1 = hashlib.sha256(user1_password.encode()).hexdigest()
                        hash2 = hashlib.sha256(user2_password.encode()).hexdigest()
                        
                        cursor.execute("""
                            INSERT INTO users (username, password_hash, role, company_id, created_by) 
                            VALUES (?, ?, ?, ?, ?)
                        """, (user1_username, hash1, "scorecard_user", company_id, st.session_state.user_data['username']))
                        
                        cursor.execute("""
                            INSERT INTO users (username, password_hash, role, company_id, created_by) 
                            VALUES (?, ?, ?, ?, ?)
                        """, (user2_username, hash2, "scorecard_approver", company_id, st.session_state.user_data['username']))
                        
                        db.commit()
                        st.success(f"Company '{company_name}' and users created successfully!")
                        
                    except sqlite3.IntegrityError as e:
                        st.error("Username already exists. Please choose different usernames.")
                    except Exception as e:
                        st.error(f"Error creating company: {str(e)}")
    
    with tab2:
        st.markdown("### Manage Companies")
        
        companies = get_all_companies()
        if companies:
            for company in companies:
                company_id, name, type_name = company
                
                with st.expander(f"{name} ({type_name})"):
                    st.write(f"**Company ID:** {company_id}")
                    st.write(f"**Type:** {type_name}")
                    
                    users = get_company_users(company_id)
                    if users:
                        st.write("**Users:**")
                        for user in users:
                            username, role, created_at = user
                            st.write(f"- {username} ({role}) - Created: {created_at}")
                    else:
                        st.write("No users found")
        else:
            st.info("No companies created yet")
    
    with tab3:
        st.markdown("### System Overview")
        
        cursor = db.cursor()
        
        # Count statistics
        cursor.execute("SELECT COUNT(*) FROM companies")
        company_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE role != 'super_admin'")
        user_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM scorecards")
        scorecard_count = cursor.fetchone()[0]
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Companies", company_count)
        with col2:
            st.metric("Users", user_count)
        with col3:
            st.metric("Scorecards", scorecard_count)

def render_scorecard_approver():
    """Render Scorecard Approver dashboard"""
    # Get company name for display
    company_name = get_company_name(st.session_state.user_data['company_id'])
    display_name = company_name if company_name else st.session_state.user_data['username']
    
    # Modern compact header
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 1rem 1.5rem; border-radius: 12px; color: white; margin-bottom: 1.5rem;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
        <h2 style="margin: 0; font-size: 1.3rem; font-weight: 500; letter-spacing: 0.5px;">🎯 Scorecard Approver Dashboard</h2>
        <p style="margin: 0.3rem 0 0 0; opacity: 0.9; font-size: 0.9rem;">Welcome, {display_name} • Scorecard Approver</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar with module navigation
    with st.sidebar:
        st.markdown("### 🎯 Modules")
        
        # Module selection radio buttons
        selected_module = st.radio(
            "Select Module:",
            ["ICSM (Default)", "Dynamic Scorecard Config"],
            index=st.session_state.get('selected_module_index', 0),
            key="module_selector"
        )
        
        # Store module selection
        if selected_module == "ICSM (Default)":
            st.session_state.selected_module_index = 0
            st.session_state.current_module = "icsm"
        else:
            st.session_state.selected_module_index = 1
            st.session_state.current_module = "dynamic"
        
        st.markdown("---")
        st.markdown("### 📊 Quick Stats")
        
        # Quick company stats
        company_name = get_company_name(st.session_state.user_data['company_id'])
        if company_name:
            st.markdown(f"**Company:** {company_name}")
        
        # Check scorecard status for sidebar display
        cursor = db.cursor()
        cursor.execute("SELECT * FROM scorecards WHERE company_id=?", (st.session_state.user_data['company_id'],))
        existing = cursor.fetchone()
        
        if existing:
            st.markdown("**Status:** ✅ Scorecard Active")
        else:
            st.markdown("**Status:** ⏳ Setup Required")
        
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True, type="secondary"):
            st.session_state.authenticated = False
            st.session_state.user_data = None
            st.rerun()
    
    # Module routing based on sidebar selection
    current_module = st.session_state.get('current_module', 'icsm')
    
    if current_module == 'icsm':
        # ICSM Module (existing functionality)
        if existing:
            render_scorecard_results(existing)
        else:
            render_personalization_form()
    elif current_module == 'dynamic':
        # Dynamic Scorecard Configuration Module
        render_dynamic_scorecard_module()

def render_scorecard_results(scorecard_data):
    """Render comprehensive scorecard results with detailed explanations"""
    
    # Parse data - handle both old and new column names
    if len(scorecard_data) == 5:
        scorecard_id, company_id, config_json, weights_json, created_at = scorecard_data
    else:
        # Legacy format compatibility
        scorecard_id, company_id, config_json, weights_json = scorecard_data[:4]
        created_at = None
    
    config = json.loads(config_json)
    weights = json.loads(weights_json)
    
    # Header with edit option
    col1, col2 = st.columns([4, 1])
    
    with col1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                    padding: 1rem 1.5rem; border-radius: 12px; color: white; margin-bottom: 1rem;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
            <h3 style="margin: 0; font-size: 1.2rem; font-weight: 500; letter-spacing: 0.5px;">🎯 Your ICSM (Default Scoring Model)</h3>
            <p style="margin: 0.3rem 0 0 0; opacity: 0.9; font-size: 0.85rem;">
                Institution-Calibrated Scoring Model • Your primary risk assessment framework
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("✏️ Edit Configuration", type="secondary", use_container_width=True):
            st.session_state.edit_scorecard = True
            st.rerun()
    
    # Check if editing mode
    if st.session_state.get('edit_scorecard', False):
        render_edit_configuration(scorecard_data)
        return
    
    # Create tabs for organized display - correct order
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Scoring Weights", "📈 Expected Performance", "🏢 Configuration", "🧠 Weight Logic"])
    
    with tab1:
        render_scoring_weights_display(weights, config)
    
    with tab2:
        render_performance_expectations(config, weights)
    
    with tab3:
        render_configuration_summary(config)
    
    with tab4:
        render_weight_logic_explanation(weights, config)

def render_edit_configuration(scorecard_data):
    """Render edit configuration interface"""
    
    # Handle different data formats for compatibility
    if len(scorecard_data) == 5:
        scorecard_id, company_id, config_json, weights_json, created_at = scorecard_data
    else:
        scorecard_id, company_id, config_json, weights_json = scorecard_data[:4]
        created_at = None
    
    config = json.loads(config_json)
    
    # Clean header without duplicate styling
    st.markdown("### ✏️ Edit Configuration")
    st.info("💡 Modify your scorecard settings. Basic institution information cannot be changed.")
    
    # Edit form with current values
    with st.form("edit_configuration_form"):
        st.markdown("### Loan Products & Strategy")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Loan products
            available_products = [
                "Personal Loan", "Home Loan", "Business Loan", "Gold Loan", 
                "Vehicle Loan", "Credit Card", "Education Loan", "Agricultural Loan"
            ]
            
            current_products = config.get('selected_products', [])
            selected_products = st.multiselect(
                "Select Loan Products *",
                available_products,
                default=current_products,
                help="Choose the loan products your institution offers"
            )
            
            if selected_products:
                primary_product = st.selectbox(
                    "Primary Product Focus *",
                    selected_products,
                    index=selected_products.index(config.get('primary_product', selected_products[0])) if config.get('primary_product') in selected_products else 0,
                    help="Your main product for optimization"
                )
            else:
                primary_product = None
        
        with col2:
            # Business goals - fix the options mismatch
            available_goals = [
                "Increase Approval Rates", "Reduce Default Risk", "Accelerate Processing",
                "Expand Market Reach", "Improve Portfolio Quality", "Enhance Customer Experience",
                "Regulatory Compliance", "Cost Optimization"
            ]
            
            # Filter current goals to only include valid options
            current_goals = config.get('business_goals', [])
            valid_current_goals = [goal for goal in current_goals if goal in available_goals]
            
            business_goals = st.multiselect(
                "Business Goals",
                available_goals,
                default=valid_current_goals,
                help="Select your primary business objectives"
            )
        
        st.markdown("### Risk & Strategy Settings")
        
        col3, col4 = st.columns(2)
        
        with col3:
            # Fix selectbox index handling
            risk_options = ["Conservative (Lower Risk)", "Moderate (Balanced)", "Aggressive (Growth Focused)"]
            current_risk = config.get('risk_appetite', 'Moderate (Balanced)')
            risk_index = risk_options.index(current_risk) if current_risk in risk_options else 1
            
            risk_appetite = st.selectbox(
                "Risk Appetite *",
                risk_options,
                index=risk_index,
                help="Your institution's risk tolerance level"
            )
            
            segment_options = ["Prime (Excellent Credit)", "Mixed Portfolio", "Sub Prime (Inclusive Lending)"]
            current_segment = config.get('target_segment', 'Mixed Portfolio')
            segment_index = segment_options.index(current_segment) if current_segment in segment_options else 1
            
            target_segment = st.selectbox(
                "Target Customer Segment *",
                segment_options,
                index=segment_index,
                help="Primary customer segment focus"
            )
            
            approval_target = st.slider(
                "Target Approval Rate (%)",
                min_value=30,
                max_value=85,
                value=config.get('approval_target', 65),
                step=5,
                help="Desired approval rate percentage"
            )
        
        with col4:
            # Fix all selectbox index handling
            automation_options = ["Manual Review", "Semi-Automated", "Highly Automated", "Fully Automated"]
            current_automation = config.get('automation_level', 'Semi-Automated')
            automation_index = automation_options.index(current_automation) if current_automation in automation_options else 1
            
            automation_level = st.selectbox(
                "Automation Level *",
                automation_options,
                index=automation_index,
                help="Level of process automation"
            )
            
            speed_options = ["Thorough Review", "Fast (1 Hour)", "Instant (Real-time)"]
            current_speed = config.get('approval_speed', 'Fast (1 Hour)')
            speed_index = speed_options.index(current_speed) if current_speed in speed_options else 1
            
            approval_speed = st.selectbox(
                "Approval Speed Priority *",
                speed_options,
                index=speed_index,
                help="Speed vs accuracy priority"
            )
            
            focus_options = ["Risk Management", "Growth & Volume", "Customer Experience", "Operational Efficiency"]
            current_focus = config.get('priority_focus', 'Risk Management')
            focus_index = focus_options.index(current_focus) if current_focus in focus_options else 0
            
            priority_focus = st.selectbox(
                "Priority Focus *",
                focus_options,
                index=focus_index,
                help="Primary strategic focus"
            )
        
        st.markdown("### Data Sources Configuration")
        
        col5, col6 = st.columns(2)
        
        with col5:
            # Credit bureau access
            available_bureaus = ["CIBIL", "Experian", "Equifax", "CRIF"]
            bureau_access = st.multiselect(
                "Credit Bureau Access",
                available_bureaus,
                default=config.get('bureau_access', []),
                help="Available credit bureaus"
            )
            
            # Fix bank analysis selectbox
            bank_options = ["Not Available", "Basic Analysis", "Advanced Analytics", "AI-Powered Insights"]
            current_bank = config.get('bank_statement_analysis', 'Not Available')
            bank_index = bank_options.index(current_bank) if current_bank in bank_options else 0
            
            bank_analysis = st.selectbox(
                "Bank Statement Analysis",
                bank_options,
                index=bank_index,
                help="Bank statement analysis capability"
            )
        
        with col6:
            # Additional data sources
            available_additional = [
                "GST Data", "ITR Data", "Utility Bills", "Telecom Data", 
                "Social Media", "App Usage", "Geolocation", "Employment Verification"
            ]
            
            additional_data = st.multiselect(
                "Additional Data Sources",
                available_additional,
                default=config.get('additional_data', []),
                help="Extra data sources for enhanced assessment"
            )
        
        # Form submission buttons
        st.markdown("---")
        col7, col8 = st.columns([1, 1])
        
        with col7:
            submitted = st.form_submit_button("💾 Save Changes", type="primary", use_container_width=True)
        
        with col8:
            cancelled = st.form_submit_button("❌ Cancel", use_container_width=True)
        
        # Handle form submission
        if submitted:
            # Update configuration
            updated_config = config.copy()
            updated_config.update({
                'selected_products': selected_products,
                'primary_product': primary_product,
                'business_goals': business_goals,
                'risk_appetite': risk_appetite,
                'target_segment': target_segment,
                'approval_target': approval_target,
                'automation_level': automation_level,
                'approval_speed': approval_speed,
                'priority_focus': priority_focus,
                'bureau_access': bureau_access,
                'bank_statement_analysis': bank_analysis,
                'additional_data': additional_data
            })
            
            # Regenerate weights
            new_weights = generate_enhanced_weights(
                updated_config, risk_appetite, target_segment, approval_target
            )
            
            # Save to database using existing connection
            cursor = db.cursor()
            cursor.execute("""
                UPDATE scorecards 
                SET configuration = ?, weights = ?, created_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (json.dumps(updated_config), json.dumps(new_weights), scorecard_id))
            db.commit()
            
            st.success("🎯 ICSM configuration updated successfully! Scoring model has been recalibrated based on your changes.")
            st.session_state.edit_scorecard = False
            st.rerun()
        
        if cancelled:
            st.session_state.edit_scorecard = False
            st.rerun()

def render_scoring_weights_display(weights, config):
    """Display ICSM weights using the new category-structured interface"""
    
    # Initialize calibration engine for category mapping
    calibrator = ICSMCalibrationEngine()
    
    st.markdown("""
    <div style="text-align: center; padding: 20px;">
        <h2>🎯 Institution-Calibrated Scoring Model (ICSM)</h2>
        <p style="color: #666;">Your institution's default scoring metrics - scientifically calibrated based on your business profile</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Add ICSM information box
    with st.expander("ℹ️ About Your ICSM", expanded=False):
        st.markdown("""
        **What is ICSM?**
        Your Institution-Calibrated Scoring Model is a scientifically designed credit assessment framework 
        tailored specifically to your institution's characteristics, risk appetite, and business requirements.
        
        **Key Features:**
        - **Scientific Foundation:** Based on Basel III frameworks and credit risk research
        - **Institution-Specific:** Calibrated to your institution type and risk profile
        - **Dynamic Weights:** Automatically adjusts based on available data sources
        - **Category Structure:** Organized into 6 risk categories for systematic assessment
        
        **Important:** This model maintains consistency with your Dynamic Scorecard configuration.
        """)
    
    # Category structure matching Dynamic Scorecard
    categories = [
        {"name": "Core Credit Variables", "icon": "📊", "target": 35.0, "color": "#e74c3c"},
        {"name": "Behavioral Analytics", "icon": "🧠", "target": 20.0, "color": "#9b59b6"},
        {"name": "Employment Stability", "icon": "💼", "target": 15.0, "color": "#8b4513"},
        {"name": "Banking Behavior", "icon": "🏦", "target": 10.0, "color": "#3498db"},
        {"name": "Exposure & Intent", "icon": "💰", "target": 12.0, "color": "#e67e22"},
        {"name": "Geographic & Social", "icon": "🌍", "target": 8.0, "color": "#27ae60"}
    ]
    
    st.markdown("### Current Categories")
    
    # Calculate category totals from weights
    category_totals = {}
    for category_info in categories:
        category_name = category_info["name"]
        if category_name in calibrator.category_mapping:
            total_weight = 0.0
            for var in calibrator.category_mapping[category_name]["icsm_contributors"]:
                total_weight += weights.get(var, 0.0)
            category_totals[category_name] = total_weight * 100  # Convert to percentage
    
    # Render each category with expandable sections
    for category_info in categories:
        category_name = category_info["name"]
        icon = category_info["icon"]
        target_weight = category_info["target"]
        actual_weight = category_totals.get(category_name, 0.0)
        
        # Create expandable section
        with st.expander(f"{icon} {category_name} ({actual_weight:.1f}%)", expanded=False):
            
            # Show category details
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Target Weight:** {target_weight}%")
                st.write(f"**Current Weight:** {actual_weight:.1f}%")
                
                # Weight status indicator
                weight_diff = actual_weight - target_weight
                if abs(weight_diff) < 1.0:
                    st.success("✅ Weight on target")
                elif weight_diff > 0:
                    st.warning(f"⚠️ {weight_diff:.1f}% over target")
                else:
                    st.warning(f"⚠️ {abs(weight_diff):.1f}% under target")
            
            with col2:
                # Show contributing ICSM variables
                if category_name in calibrator.category_mapping:
                    icsm_contributors = calibrator.category_mapping[category_name]["icsm_contributors"]
                    primary_drivers = calibrator.category_mapping[category_name]["primary_drivers"]
                    
                    st.write(f"**ICSM Variables:** {len(icsm_contributors)}")
                    st.write(f"**Primary Drivers:** {len(primary_drivers)}")
            
            # Show individual ICSM variables in this category
            if category_name in calibrator.category_mapping:
                st.markdown("#### Variables in this Category")
                
                icsm_contributors = calibrator.category_mapping[category_name]["icsm_contributors"]
                primary_drivers = calibrator.category_mapping[category_name]["primary_drivers"]
                
                # Sort by weight (descending)
                category_vars = []
                for var in icsm_contributors:
                    if var in weights:
                        category_vars.append((var, weights[var]))
                
                category_vars.sort(key=lambda x: x[1], reverse=True)
                
                # Display variables with progress bars
                for var_name, var_weight in category_vars:
                    var_percentage = var_weight * 100
                    
                    # Determine if primary driver
                    is_primary = var_name in primary_drivers
                    priority_label = "High" if is_primary else "Medium" if var_percentage > 5 else "Low"
                    priority_color = "#e74c3c" if is_primary else "#f39c12" if var_percentage > 5 else "#27ae60"
                    
                    # Create variable display
                    var_col1, var_col2, var_col3 = st.columns([3, 2, 1])
                    
                    with var_col1:
                        st.write(f"**{var_name.replace('_', ' ').title()}**")
                    
                    with var_col2:
                        # Progress bar
                        progress_width = min(var_percentage * 4, 100)  # Scale for display
                        st.markdown(f"""
                        <div style="background-color: #f0f0f0; border-radius: 10px; height: 20px; margin: 5px 0;">
                            <div style="background-color: #3498db; height: 100%; width: {progress_width}%; border-radius: 10px; text-align: center; line-height: 20px; color: white; font-size: 12px;">
                                {var_percentage:.1f}%
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with var_col3:
                        st.markdown(f"<span style='color: {priority_color}'>● {priority_label}</span>", unsafe_allow_html=True)
                
                # Credit expertise note
                st.info(f"**Credit Expertise:** {calibrator.category_mapping[category_name]['credit_expertise']}")
    
    # Weight Distribution Summary
    st.divider()
    st.markdown("### Weight Distribution Summary")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        core_weight = category_totals.get("Core Credit Variables", 0) + category_totals.get("Employment Stability", 0)
        st.metric("Core Variables", f"{core_weight:.1f}%", "Primary risk factors")
    
    with col2:
        behavioral_weight = category_totals.get("Behavioral Analytics", 0) + category_totals.get("Banking Behavior", 0)
        st.metric("Behavioral Data", f"{behavioral_weight:.1f}%", "Enhanced insights")
    
    with col3:
        total_weight = sum(category_totals.values())
        st.metric("Total Weight", f"{total_weight:.1f}%", "Should equal 100%")

def render_configuration_summary(config):
    """Display configuration in a clean, organized format"""
    
    st.markdown("### 🏢 Your Institution Profile")
    
    # Institution overview
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Basic Information")
        st.write(f"**Institution Type:** {config.get('institution_type', 'N/A')}")
        st.write(f"**Company Name:** {config.get('company_name', 'N/A')}")
        st.write(f"**Operating Location:** {config.get('primary_location', 'N/A')}")
        st.write(f"**Monthly Volume:** {config.get('monthly_volume', 'N/A')}")
        st.write(f"**Current Process:** {config.get('current_process', 'N/A')}")
    
    with col2:
        st.markdown("#### Business Strategy")
        st.write(f"**Risk Appetite:** {config.get('risk_appetite', 'N/A')}")
        st.write(f"**Target Segment:** {config.get('target_segment', 'N/A')}")
        st.write(f"**Automation Level:** {config.get('automation_level', 'N/A')}")
        st.write(f"**Approval Speed:** {config.get('approval_speed', 'N/A')}")
        st.write(f"**Priority Focus:** {config.get('priority_focus', 'N/A')}")
    
    # Products and goals
    st.markdown("#### Products & Goals")
    
    col3, col4 = st.columns(2)
    
    with col3:
        selected_products = config.get('selected_products', [])
        if selected_products:
            st.write("**Loan Products:**")
            for product in selected_products:
                st.write(f"• {product}")
        
        primary_product = config.get('primary_product')
        if primary_product:
            st.write(f"**Primary Product:** {primary_product}")
    
    with col4:
        business_goals = config.get('business_goals', [])
        if business_goals:
            st.write("**Business Goals:**")
            for goal in business_goals:
                st.write(f"• {goal}")
    
    # Data capabilities
    st.markdown("#### Data Capabilities")
    
    bureau_access = config.get('bureau_access', [])
    if bureau_access:
        st.write(f"**Credit Bureaus:** {', '.join(bureau_access)}")
    
    bank_analysis = config.get('bank_statement_analysis')
    if bank_analysis:
        st.write(f"**Bank Statement Analysis:** {bank_analysis}")
    
    additional_data = config.get('additional_data', [])
    if additional_data:
        st.write(f"**Additional Data Sources:** {', '.join(additional_data)}")

def render_weight_logic_explanation(weights, config):
    """Provide detailed explanation of weight allocation logic"""
    
    st.markdown("### 🧠 Weight Allocation Logic")
    st.markdown("*Understanding why your scorecard was configured this way*")
    
    institution_type = config.get('institution_type', '')
    risk_appetite = config.get('risk_appetite', '')
    target_segment = config.get('target_segment', '')
    primary_product = config.get('primary_product', '')
    
    # Base logic explanation
    st.markdown("#### 📚 Scientific Foundation")
    
    base_explanations = {
        "NBFC": "NBFCs typically focus on risk-adjusted pricing with moderate regulatory oversight. Higher weight on credit score (35%) and income verification (25%) reflects the need for accurate risk assessment in competitive markets.",
        "Bank": "Banks operate under strict regulatory requirements emphasizing comprehensive risk assessment. Balanced weights across debt ratio (25%) and credit score (30%) ensure regulatory compliance while maintaining portfolio quality.",
        "Fintech": "Digital lenders prioritize speed and automation. Higher credit score weight (40%) and income focus (30%) enable quick decisioning while maintaining risk controls in largely automated processes.",
        "Microfinance Institution": "MFIs focus on financial inclusion for underbanked segments. Higher income weight (35%) and employment stability (20%) reflects the importance of cash flow assessment for borrowers with limited credit history.",
        "Housing Finance Company": "Property-backed lending requires strong income verification (30%) and employment stability assessment (15%) to ensure long-term repayment capacity for high-value, long-tenure loans.",
        "Gold Loan Company": "Asset-backed lending with minimal credit requirements. High income weight (40%) focuses on immediate repayment capacity since gold provides security.",
        "DSA/Agent": "Distribution partners need balanced risk assessment. Standard NBFC-like weights (35% credit score, 25% income) provide reliable preliminary screening."
    }
    
    if institution_type in base_explanations:
        st.info(f"**{institution_type} Logic:** {base_explanations[institution_type]}")
    
    # Risk appetite adjustments
    st.markdown("#### ⚖️ Risk Appetite Adjustments")
    
    if "Conservative" in risk_appetite:
        st.markdown("""
        **Conservative Approach Applied:**
        - ✅ Increased credit score weight (+5%) for proven creditworthiness
        - ✅ Enhanced credit history importance (+3%) for track record validation  
        - ✅ Stronger debt ratio consideration (+2%) for debt capacity assessment
        - ⚠️ Reduced income flexibility (-5%) for stricter income requirements
        """)
    elif "Aggressive" in risk_appetite:
        st.markdown("""
        **Aggressive Growth Strategy Applied:**
        - 📈 Increased income weight (+8%) to capture earning potential
        - 📈 Enhanced employment weight (+2%) for income stability
        - ⚠️ Reduced credit score dependency (-3%) to expand market reach
        - ⚠️ Lower debt ratio weight (-5%) for flexible qualification
        """)
    else:
        st.markdown("**Moderate Balance:** Standard weights maintained for balanced risk-return profile.")
    
    # Target segment adjustments
    st.markdown("#### 🎯 Target Segment Optimization")
    
    if "Prime" in target_segment:
        st.success("**Prime Segment Focus:** Enhanced credit score (+5%) and history (+2%) weights to identify highest quality borrowers.")
    elif "Sub Prime" in target_segment:
        st.warning("**Sub-Prime Inclusion:** Increased income (+5%) and employment (+3%) weights while reducing credit score dependency (-5%) to serve underbanked segments.")
    else:
        st.info("**Mixed Portfolio:** Balanced approach to serve diverse customer segments.")
    
    # Product-specific adjustments
    if primary_product:
        st.markdown("#### 🛍️ Product-Specific Calibration")
        
        product_logic = {
            "Personal Loan": "Unsecured lending requires strong creditworthiness (+2% credit score) and income verification (+2% income) for risk mitigation.",
            "Home Loan": "Long-term secured lending emphasizes income stability (+5% income), employment security (+3% employment), and debt capacity (+2% debt ratio).",
            "Business Loan": "Commercial lending focuses on business income (+3% income) and employment/business stability (+5% employment) for cash flow assessment.",
            "Gold Loan": "Asset-backed lending prioritizes immediate repayment capacity (+8% income) while reducing credit dependency (-5% credit score).",
            "Vehicle Loan": "Secured auto lending balances collateral security with borrower capacity through standard weight distribution.",
            "Credit Card": "Revolving credit requires strong creditworthiness and income assessment for spending power evaluation."
        }
        
        if primary_product in product_logic:
            st.info(f"**{primary_product}:** {product_logic[primary_product]}")
    
    # Additional data impact
    additional_data = config.get('additional_data', [])
    if additional_data:
        st.markdown("#### 📊 Additional Data Enhancement")
        st.success(f"**Enhanced Insights:** {len(additional_data)} additional data sources provide deeper risk assessment, each allocated ~{15/len(additional_data):.1f}% weight for comprehensive evaluation.")
        
        for source in additional_data:
            data_benefits = {
                "GST Data": "Business transaction validation and tax compliance verification",
                "ITR Data": "Income verification and financial stability assessment", 
                "Utility Bills": "Address stability and payment behavior tracking",
                "Telecom Data": "Digital behavior and connectivity patterns",
                "Social Media": "Lifestyle and social stability indicators",
                "App Usage": "Digital engagement and financial behavior patterns"
            }
            
            if source in data_benefits:
                st.write(f"• **{source}:** {data_benefits[source]}")

def render_performance_expectations(config, weights):
    """Show expected performance metrics based on configuration"""
    
    st.markdown("### 📈 Expected Performance")
    st.markdown("*Projected outcomes based on your scorecard configuration*")
    
    # Calculate expected metrics based on configuration
    risk_appetite = config.get('risk_appetite', '')
    target_segment = config.get('target_segment', '')
    approval_target = config.get('approval_target', 65)
    
    # Performance projections
    col1, col2, col3 = st.columns(3)
    
    # Calculate expected approval rate
    base_approval = approval_target if approval_target else 65
    
    if "Conservative" in risk_appetite:
        expected_approval = max(base_approval - 10, 30)
        expected_default = "1.5-2.5%"
        risk_level = "Low"
    elif "Aggressive" in risk_appetite:
        expected_approval = min(base_approval + 15, 85)
        expected_default = "3.5-5.5%"
        risk_level = "Higher"
    else:
        expected_approval = base_approval
        expected_default = "2.5-3.5%"
        risk_level = "Moderate"
    
    with col1:
        st.metric(
            "Expected Approval Rate", 
            f"{expected_approval}%",
            help="Based on your risk appetite and target segment"
        )
    
    with col2:
        st.metric(
            "Projected Default Rate",
            expected_default,
            help="Expected default rate range for your configuration"
        )
    
    with col3:
        st.metric(
            "Risk Level",
            risk_level,
            help="Overall risk profile of your scorecard"
        )
    
    # Segment-specific insights
    st.markdown("#### 🎯 Segment Performance Insights")
    
    if "Prime" in target_segment:
        st.success("""
        **Prime Segment Strategy:**
        - Lower default rates (1-2%) but potentially lower approval rates
        - Higher average loan amounts and better profitability per customer
        - Faster processing due to cleaner credit profiles
        """)
    elif "Sub Prime" in target_segment:
        st.warning("""
        **Sub-Prime Inclusion Strategy:**
        - Higher approval rates but increased default risk (4-6%)
        - Requires active portfolio monitoring and collection strategies
        - Opportunity for market expansion and social impact
        """)
    else:
        st.info("""
        **Mixed Portfolio Approach:**
        - Balanced risk-return profile across customer segments
        - Diversified portfolio reducing concentration risk
        - Flexible strategy adapting to market conditions
        """)
    
    # Operational expectations
    st.markdown("#### ⚡ Operational Impact")
    
    automation_level = config.get('automation_level', '')
    approval_speed = config.get('approval_speed', '')
    
    col4, col5 = st.columns(2)
    
    with col4:
        if "Fully Automated" in automation_level:
            st.success("**High Efficiency:** 90%+ applications processed automatically")
        elif "Highly Automated" in automation_level:
            st.info("**Good Efficiency:** 70-80% automation with exception handling")
        else:
            st.warning("**Manual Review:** Slower processing but higher accuracy")
    
    with col5:
        if "Instant" in approval_speed:
            st.success("**Real-time Decisions:** Sub-minute processing for competitive advantage")
        elif "Fast" in approval_speed:
            st.info("**Quick Processing:** Hour-level decisions balancing speed and accuracy")
        else:
            st.warning("**Thorough Review:** Detailed assessment for complex applications")
    
    # Recommendations
    st.markdown("#### 💡 Optimization Recommendations")
    
    recommendations = []
    
    # Weight-based recommendations
    if weights:
        max_weight_var = max(weights.keys(), key=lambda k: weights[k])
        if weights[max_weight_var] > 0.4:
            recommendations.append(f"Consider diversifying weights - {max_weight_var.replace('_', ' ')} dominates at {weights[max_weight_var]:.1%}")
    
    # Configuration-based recommendations
    additional_data = config.get('additional_data', [])
    if len(additional_data) < 2:
        recommendations.append("Consider adding more data sources for enhanced risk assessment")
    
    if "Manual Review" in config.get('current_process', ''):
        recommendations.append("Gradual automation implementation could improve efficiency")
    
    bureau_access = config.get('bureau_access', [])
    if len(bureau_access) < 2:
        recommendations.append("Multiple bureau access could improve credit assessment accuracy")
    
    if recommendations:
        for rec in recommendations:
            st.write(f"• {rec}")
    else:
        st.success("Your scorecard configuration is well-optimized for your business model!")

def render_personalization_form():
    """Render comprehensive multi-step personalization form matching the original archived design"""
    
    # Initialize session state for onboarding steps
    if 'onboarding_step' not in st.session_state:
        st.session_state.onboarding_step = 0
    if 'onboarding_data' not in st.session_state:
        st.session_state.onboarding_data = {}
    
    # Header with elegant styling
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                border-radius: 15px; margin-bottom: 2rem; color: white;">
        <h1 style="font-size: 2.5rem; margin-bottom: 0.5rem; font-weight: 300;">
            🎯 Tell us about your institution
        </h1>
        <p style="font-size: 1.2rem; opacity: 0.9; margin: 0;">
            Let's create a customized scorecard perfectly tailored to your business needs
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Progress indicator with elegant design
    progress_steps = ["Institution Details", "Loan Products", "Data Assessment", "Scorecard Preference"]
    current_step = st.session_state.onboarding_step
    
    # Progress bar
    progress_percentage = (current_step + 1) / len(progress_steps)
    st.progress(progress_percentage)
    
    # Step indicators
    cols = st.columns(len(progress_steps))
    for i, step in enumerate(progress_steps):
        with cols[i]:
            if i < current_step:
                st.markdown(f"<div style='text-align: center; color: #28a745;'>✅ <strong>{step}</strong></div>", unsafe_allow_html=True)
            elif i == current_step:
                st.markdown(f"<div style='text-align: center; color: #007bff;'>🔵 <strong>{step}</strong></div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div style='text-align: center; color: #6c757d;'>⭕ {step}</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Route to appropriate step
    if current_step == 0:
        render_institution_details_step()
    elif current_step == 1:
        render_loan_products_step()
    elif current_step == 2:
        render_data_assessment_step()
    elif current_step == 3:
        render_scorecard_preference_step()

def render_institution_details_step():
    """Step 1: Institution Details with elegant UI"""
    
    st.markdown("### 🏢 Institution Information")
    st.markdown("*Help us understand your business model and operational context*")
    
    # Institution types with comprehensive details
    institution_types = {
        "NBFC": {
            "focus": "Risk-adjusted pricing and portfolio management",
            "typical_products": ["Personal Loan", "Business Loan", "Vehicle Loan"],
            "data_availability": "Moderate to High"
        },
        "Bank": {
            "focus": "Regulatory compliance and comprehensive risk assessment",
            "typical_products": ["Home Loan", "Personal Loan", "Credit Card", "Business Loan"],
            "data_availability": "High"
        },
        "Microfinance Institution": {
            "focus": "Financial inclusion and group lending",
            "typical_products": ["Micro Business Loan", "Group Loan"],
            "data_availability": "Limited"
        },
        "Fintech": {
            "focus": "Digital lending and instant approvals",
            "typical_products": ["Personal Loan", "Pay Later", "Credit Card"],
            "data_availability": "Digital High"
        },
        "DSA/Agent": {
            "focus": "Lead generation and preliminary assessment",
            "typical_products": ["Personal Loan", "Home Loan", "Business Loan"],
            "data_availability": "Variable"
        },
        "Housing Finance Company": {
            "focus": "Property-backed lending",
            "typical_products": ["Home Loan", "Loan Against Property"],
            "data_availability": "Property Focused"
        },
        "Gold Loan Company": {
            "focus": "Commodity-backed quick lending",
            "typical_products": ["Gold Loan"],
            "data_availability": "Minimal Required"
        }
    }
    
    col1, col2 = st.columns(2)
    
    with col1:
        institution_type = st.selectbox(
            "What type of financial institution are you?",
            options=list(institution_types.keys()),
            help="This helps us understand your typical business model and requirements",
            key="inst_type"
        )
        
        # Get company name for display
        company_name = get_company_name(st.session_state.user_data['company_id'])
        st.text_input(
            "Company/Institution Name",
            value=company_name if company_name else "Your Company",
            disabled=True,
            help="Company name is set by your administrator"
        )
        
        primary_location = st.selectbox(
            "Primary Operating Location",
            ["Pan India", "Metro Cities", "Tier 1 Cities", "Tier 2 Cities", "Tier 3 Cities", "Rural Areas"],
            key="location"
        )
    
    with col2:
        # Show institution-specific information with elegant styling
        if institution_type:
            institution_info = institution_types[institution_type]
            
            st.markdown(f"""
            <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 10px; border-left: 4px solid #007bff;">
                <h4 style="color: #007bff; margin-bottom: 1rem;">About {institution_type}</h4>
                <p><strong>Typical Focus:</strong> {institution_info['focus']}</p>
                <p><strong>Common Products:</strong> {', '.join(institution_info['typical_products'])}</p>
                <p><strong>Data Availability:</strong> {institution_info['data_availability']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        monthly_volume = st.selectbox(
            "Approximate Monthly Application Volume",
            ["< 100", "100 - 500", "500 - 1,000", "1,000 - 5,000", "5,000 - 10,000", "> 10,000"],
            key="volume"
        )
        
        current_process = st.selectbox(
            "Current Credit Assessment Process",
            ["Manual Review", "Basic Scorecards", "Advanced Analytics", "AI/ML Models", "No Formal Process"],
            key="process"
        )
    
    # Navigation
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col3:
        if st.button("Next: Loan Products →", type="primary", disabled=not institution_type):
            st.session_state.onboarding_data.update({
                'institution_type': institution_type,
                'company_name': company_name,
                'primary_location': primary_location,
                'monthly_volume': monthly_volume,
                'current_process': current_process
            })
            st.session_state.onboarding_step = 1
            st.rerun()

def render_loan_products_step():
    """Step 2: Loan Products with enhanced UI"""
    
    st.markdown("### 💰 Loan Products & Business Focus")
    st.markdown("*Tell us about the products you offer and your business priorities*")
    
    # Available loan products with detailed profiles
    loan_products = {
        "Personal Loan": {
            "profile": "Unsecured Focused",
            "variables": ["credit_score", "monthly_income", "foir", "employment_tenure", "banking_relationship"],
            "typical_tenure": "12-60 months"
        },
        "Home Loan": {
            "profile": "Secured Focused", 
            "variables": ["credit_score", "monthly_income", "property_value", "ltv_ratio", "employment_stability"],
            "typical_tenure": "15-30 years"
        },
        "Loan Against Property": {
            "profile": "Asset Backed",
            "variables": ["property_value", "ltv_ratio", "rental_income", "credit_score", "business_stability"],
            "typical_tenure": "10-20 years"
        },
        "Gold Loan": {
            "profile": "Commodity Backed",
            "variables": ["gold_purity", "gold_weight", "ltv_ratio", "repayment_capacity"],
            "typical_tenure": "6-24 months"
        },
        "Business Loan": {
            "profile": "Business Focused",
            "variables": ["business_vintage", "turnover", "profit_margins", "gst_compliance", "banking_turnover"],
            "typical_tenure": "12-84 months"
        },
        "Vehicle Loan": {
            "profile": "Auto Finance",
            "variables": ["vehicle_value", "down_payment", "monthly_income", "credit_score", "insurance_status"],
            "typical_tenure": "12-84 months"
        },
        "Education Loan": {
            "profile": "Education Focused",
            "variables": ["course_fee", "institution_ranking", "co_applicant_income", "collateral_value"],
            "typical_tenure": "5-15 years"
        },
        "Credit Card": {
            "profile": "Revolving Credit",
            "variables": ["monthly_income", "credit_score", "existing_cards", "spending_pattern"],
            "typical_tenure": "Revolving"
        }
    }
    
    # Business goals
    business_goals = [
        "Increase approval rates",
        "Reduce default rates", 
        "Faster decision making",
        "Better risk assessment",
        "Regulatory compliance",
        "Portfolio diversification",
        "Customer acquisition",
        "Operational efficiency"
    ]
    
    # Get recommended products based on institution type
    institution_type = st.session_state.onboarding_data.get('institution_type', '')
    institution_types = {
        "NBFC": ["Personal Loan", "Business Loan", "Vehicle Loan"],
        "Bank": ["Home Loan", "Personal Loan", "Credit Card", "Business Loan"],
        "Microfinance Institution": ["Business Loan"],
        "Fintech": ["Personal Loan", "Credit Card"],
        "DSA/Agent": ["Personal Loan", "Home Loan", "Business Loan"],
        "Housing Finance Company": ["Home Loan", "Loan Against Property"],
        "Gold Loan Company": ["Gold Loan"]
    }
    
    recommended_products = institution_types.get(institution_type, [])
    valid_recommendations = [product for product in recommended_products if product in loan_products.keys()]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"**Recommended for {institution_type}:** {', '.join(recommended_products)}")
        
        selected_products = st.multiselect(
            "Select all loan products you offer or plan to offer:",
            options=list(loan_products.keys()),
            default=valid_recommendations,
            help="You can select multiple products. We'll optimize the scorecard for your primary products."
        )
        
        if selected_products:
            primary_product = st.selectbox(
                "Which is your primary/highest volume product?",
                options=selected_products
            )
        else:
            primary_product = None
        
        selected_goals = st.multiselect(
            "Primary Business Goals",
            options=business_goals,
            default=["Better risk assessment", "Reduce default rates"],
            help="Select your top 3-5 priorities"
        )
    
    with col2:
        if selected_products:
            st.markdown("**Selected Products Overview:**")
            for product in selected_products[:3]:  # Show first 3
                product_info = loan_products[product]
                st.markdown(f"""
                <div style="background: #e9ecef; padding: 1rem; border-radius: 8px; margin-bottom: 0.5rem;">
                    <strong>{product}</strong><br>
                    <small>Profile: {product_info['profile']} | Tenure: {product_info['typical_tenure']}</small>
                </div>
                """, unsafe_allow_html=True)
        
        if primary_product:
            st.markdown(f"**Key Variables for {primary_product}:**")
            key_vars = loan_products[primary_product]['variables']
            for var in key_vars[:5]:  # Show first 5
                st.write(f"• {var.replace('_', ' ').title()}")
    
    # Navigation
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("← Back"):
            st.session_state.onboarding_step = 0
            st.rerun()
    
    with col3:
        if st.button("Next: Data Assessment →", type="primary", disabled=not selected_products):
            st.session_state.onboarding_data.update({
                'selected_products': selected_products,
                'primary_product': primary_product,
                'business_goals': selected_goals
            })
            st.session_state.onboarding_step = 2
            st.rerun()

def render_data_assessment_step():
    """Step 3: Comprehensive Data Assessment"""
    
    st.markdown("### 📊 Data Assessment")
    st.markdown("*Help us understand your data capabilities and sources*")
    
    # Enhanced data categories
    data_categories = {
        "Core Credit Variables": {
            "variables": ["credit_score", "credit_history", "enquiry_count", "credit_utilization"],
            "availability": "High - Usually available from Credit Bureaus",
            "importance": "Critical for all loan types"
        },
        "Income & Employment": {
            "variables": ["monthly_income", "employment_tenure", "job_type", "company_stability"],
            "availability": "High - Standard KYC requirement",
            "importance": "Essential for repayment capacity"
        },
        "Banking Behavior": {
            "variables": ["account_vintage", "avg_monthly_balance", "bounce_frequency", "banking_relationship"],
            "availability": "Medium - Requires bank statement analysis",
            "importance": "Strong predictor of financial discipline"
        },
        "Behavioral Analytics": {
            "variables": ["loan_completion_ratio", "payment_history", "default_history"],
            "availability": "Medium - Internal data or bureau reports",
            "importance": "Excellent for risk prediction"
        },
        "Geographic & Social": {
            "variables": ["address_stability", "geographic_risk", "social_score"],
            "availability": "Low to Medium - Specialized data providers",
            "importance": "Good for portfolio risk management"
        },
        "Digital Footprint": {
            "variables": ["mobile_vintage", "digital_engagement", "app_usage_pattern"],
            "availability": "High for Fintech, Low for traditional",
            "importance": "Emerging predictor for digital lending"
        }
    }
    
    # Data availability assessment
    st.markdown("#### Data Availability Assessment")
    st.write("Please indicate what data you typically have access to:")
    
    data_availability = {}
    
    for category, info in data_categories.items():
        with st.expander(f"**{category}** - {info['importance']}", expanded=True):
            availability = st.radio(
                f"Data availability for {category}",
                ["Always Available", "Usually Available", "Sometimes Available", "Rarely Available", "Not Available"],
                key=f"availability_{category}",
                horizontal=True
            )
            data_availability[category] = availability
            
            st.caption(f"**Typical Variables:** {', '.join(info['variables'])}")
            st.caption(f"**Market Availability:** {info['availability']}")
    
    # Data quality and sources
    st.markdown("#### Data Quality & Sources")
    
    col1, col2 = st.columns(2)
    
    with col1:
        bureau_access = st.multiselect(
            "Credit Bureau Access",
            ["CIBIL", "Experian", "Equifax", "CRIF High Mark"],
            default=["CIBIL"],
            help="Select all bureaus you have access to"
        )
        
        bank_statement_analysis = st.selectbox(
            "Bank Statement Analysis Capability",
            ["Advanced (12+ months)", "Standard (6 months)", "Basic (3 months)", "Manual Review Only", "None"]
        )
    
    with col2:
        additional_data = st.multiselect(
            "Additional Data Sources",
            ["GST Data", "ITR Data", "Utility Bills", "Telecom Data", "Social Media", "App Usage"],
            help="Select any additional data sources you use"
        )
        
        data_processing = st.selectbox(
            "Current Data Processing",
            ["Automated with APIs", "Semi-automated", "Manual Entry", "Outsourced", "Minimal Processing"]
        )
    
    # Navigation
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("← Back"):
            st.session_state.onboarding_step = 1
            st.rerun()
    
    with col3:
        if st.button("Next: Scorecard Preference →", type="primary"):
            st.session_state.onboarding_data.update({
                'data_availability': data_availability,
                'bureau_access': bureau_access,
                'bank_statement_analysis': bank_statement_analysis,
                'additional_data': additional_data,
                'data_processing': data_processing
            })
            st.session_state.onboarding_step = 3
            st.rerun()

def render_scorecard_preference_step():
    """Step 4: Scorecard Preference and Strategy"""
    
    st.markdown("### ⚖️ Scorecard Strategy & Preferences")
    st.markdown("*Define your risk strategy and operational preferences*")
    
    col1, col2 = st.columns(2)
    
    with col1:
        risk_appetite = st.selectbox(
            "Risk Appetite",
            ["Conservative (Low Risk, Lower Returns)", 
             "Moderate (Balanced Risk-Return)", 
             "Aggressive (Higher Risk, Higher Returns)"],
            help="This affects how strict or lenient your scorecard will be"
        )
        
        target_segment = st.selectbox(
            "Target Customer Segment",
            ["Prime (High Credit Score)", 
             "Near Prime (Good Credit)", 
             "Sub Prime (Fair Credit)", 
             "Mixed Portfolio"],
            help="Primary customer segment you want to serve"
        )
        
        approval_target = st.slider(
            "Target Approval Rate (%)",
            min_value=30, max_value=90, value=65, step=5,
            help="What percentage of applications do you want to approve?"
        )
    
    with col2:
        automation_level = st.selectbox(
            "Desired Automation Level",
            ["Fully Manual Review", 
             "Semi-Automated (Human Override)", 
             "Highly Automated (Exception Based)", 
             "Fully Automated"],
            help="How much automation do you want in decision making?"
        )
        
        approval_speed = st.selectbox(
            "Target Approval Speed",
            ["Instant (< 1 minute)", 
             "Fast (< 1 hour)", 
             "Standard (< 24 hours)", 
             "Detailed Review (1-3 days)"],
            help="How quickly do you need to make decisions?"
        )
        
        priority_focus = st.selectbox(
            "Priority Focus",
            ["Minimize Defaults", "Maximize Approvals", "Balanced Risk-Return", "Fast Processing", "Regulatory Compliance"],
            help="What's your primary business priority?"
        )
    
    # Generate comprehensive weights preview
    weights = generate_enhanced_weights(st.session_state.onboarding_data, risk_appetite, target_segment, approval_target)
    
    if weights:
        st.markdown("#### 📊 Your Customized Scorecard Weights")
        st.write("*Based on your responses, here's your personalized scoring model:*")
        
        # Core weights
        st.markdown("**Core Variables:**")
        core_cols = st.columns(4)
        core_vars = ['credit_score', 'income', 'debt_ratio', 'employment', 'credit_history']
        for i, var in enumerate(core_vars):
            if var in weights:
                with core_cols[i % 4]:
                    st.metric(var.replace('_', ' ').title(), f"{weights[var]:.1%}")
        
        # Additional data weights if selected
        additional_data = st.session_state.onboarding_data.get('additional_data', [])
        if additional_data:
            st.markdown("**Additional Data Sources:**")
            add_cols = st.columns(len(additional_data))
            for i, source in enumerate(additional_data):
                weight_key = f"additional_{source.lower().replace(' ', '_')}"
                if weight_key in weights:
                    with add_cols[i]:
                        st.metric(source, f"{weights[weight_key]:.1%}")
    
    # Navigation and completion
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("← Back"):
            st.session_state.onboarding_step = 2
            st.rerun()
    
    with col3:
        if st.button("🚀 Complete Setup", type="primary"):
            # Save complete configuration
            config = st.session_state.onboarding_data.copy()
            config.update({
                'risk_appetite': risk_appetite,
                'target_segment': target_segment,
                'approval_target': approval_target,
                'automation_level': automation_level,
                'approval_speed': approval_speed,
                'priority_focus': priority_focus,
                'created_at': datetime.now().isoformat()
            })
            
            # Save to database
            cursor = db.cursor()
            cursor.execute("""
                INSERT INTO scorecards (company_id, configuration, weights) 
                VALUES (?, ?, ?)
            """, (
                st.session_state.user_data['company_id'], 
                json.dumps(config), 
                json.dumps(weights)
            ))
            db.commit()
            
            # Clear onboarding state
            del st.session_state.onboarding_step
            del st.session_state.onboarding_data
            
            st.success("🎉 Your Institution-Calibrated Scoring Model (ICSM) has been created successfully!")
            st.balloons()
            st.rerun()

def generate_enhanced_weights(onboarding_data, risk_appetite, target_segment, approval_target):
    """Generate comprehensive ICSM weights with full category-based structure"""
    
    institution_type = onboarding_data.get('institution_type', 'NBFC')
    selected_products = onboarding_data.get('selected_products', [])
    primary_product = onboarding_data.get('primary_product')
    additional_data = onboarding_data.get('additional_data', [])
    data_availability = onboarding_data.get('data_availability', {})
    
    # Enterprise-grade ICSM variable structure - No logical duplicates
    # Each variable represents a distinct risk dimension
    category_weights = {
        # Core Credit Variables (38% target) - Consolidated for precision
        "credit_score": 0.18,
        "monthly_income": 0.12, 
        "debt_ratio": 0.04,
        "credit_history": 0.02,
        "foir": 0.02,
        
        # Behavioral Analytics (18% target) - Distinct behavioral metrics  
        "spending_patterns": 0.06,
        "transaction_frequency": 0.04,
        "account_usage": 0.04,
        "financial_behavior": 0.04,
        
        # Employment Stability (15% target) - Comprehensive employment assessment
        "employment": 0.06,
        "job_tenure": 0.04,
        "income_stability": 0.03,
        "employer_type": 0.02,
        
        # Banking Behavior (12% target) - Banking relationship strength
        "account_history": 0.04,
        "banking_relationship": 0.03,
        "account_management": 0.03,
        "overdraft_history": 0.02,
        
        # Exposure & Intent (10% target) - Current financial exposure
        "existing_loans": 0.04,
        "credit_utilization": 0.03,
        "loan_purpose": 0.02,
        "collateral_value": 0.01,
        
        # Geographic & Social (7% target) - Location and social risk
        "location_risk": 0.03,
        "social_indicators": 0.02,
        "regional_factors": 0.01,
        "demographic_data": 0.01
    }
    
    # Institution-specific weight adjustments
    institution_adjustments = {
        "NBFC": {
            "credit_score": 1.2, "income": 1.1, "debt_ratio": 1.1,
            "spending_patterns": 1.0, "employment": 1.0
        },
        "Bank": {
            "credit_score": 1.0, "debt_ratio": 1.3, "account_history": 1.2,
            "banking_relationship": 1.3, "credit_history": 1.2
        },
        "Fintech": {
            "digital_footprint": 1.5, "transaction_frequency": 1.3,
            "spending_patterns": 1.2, "credit_score": 1.1
        },
        "Microfinance Institution": {
            "income": 1.4, "employment": 1.3, "location_risk": 1.2,
            "social_indicators": 1.3, "credit_score": 0.7
        },
        "Housing Finance Company": {
            "income": 1.3, "employment": 1.2, "collateral_value": 1.4,
            "income_stability": 1.3, "job_tenure": 1.2
        },
        "Gold Loan Company": {
            "income": 1.5, "collateral_value": 1.6, "employment": 1.1,
            "credit_score": 0.6, "credit_history": 0.5
        }
    }
    
    # Apply institution-specific adjustments
    if institution_type in institution_adjustments:
        adjustments = institution_adjustments[institution_type]
        for var, weight in category_weights.items():
            category_weights[var] = weight * adjustments.get(var, 1.0)
    
    # Risk appetite adjustments
    if "Conservative" in risk_appetite:
        # Conservative approach emphasizes proven creditworthiness
        risk_multipliers = {
            "credit_score": 1.2, "credit_history": 1.3, "payment_history": 1.2,
            "debt_ratio": 1.15, "account_history": 1.1, "banking_relationship": 1.1,
            "income_stability": 1.1, "job_tenure": 1.1
        }
        for var, multiplier in risk_multipliers.items():
            if var in category_weights:
                category_weights[var] *= multiplier
                
    elif "Aggressive" in risk_appetite:
        # Growth-focused approach emphasizes earning potential
        risk_multipliers = {
            "income": 1.3, "employment": 1.2, "spending_patterns": 1.1,
            "digital_footprint": 1.15, "transaction_frequency": 1.1,
            "credit_score": 0.85, "credit_history": 0.8
        }
        for var, multiplier in risk_multipliers.items():
            if var in category_weights:
                category_weights[var] *= multiplier
    
    # Target segment adjustments
    if "Prime" in target_segment:
        prime_multipliers = {"credit_score": 1.2, "credit_history": 1.15, "payment_history": 1.1}
        for var, multiplier in prime_multipliers.items():
            if var in category_weights:
                category_weights[var] *= multiplier
    elif "Sub Prime" in target_segment:
        subprime_multipliers = {"income": 1.2, "employment": 1.15, "social_indicators": 1.1}
        for var, multiplier in subprime_multipliers.items():
            if var in category_weights:
                category_weights[var] *= multiplier
    
    # Product-specific adjustments
    if primary_product == "Personal Loan":
        product_multipliers = {"credit_score": 1.2, "income": 1.15, "debt_ratio": 1.1, "credit_utilization": 1.15, "existing_loans": 1.1}
    elif primary_product == "Home Loan":
        product_multipliers = {"income": 1.3, "employment": 1.2, "income_stability": 1.25, "job_tenure": 1.2, "collateral_value": 1.3}
    elif primary_product == "Business Loan":
        product_multipliers = {"income": 1.25, "employment": 1.2, "employer_type": 1.3, "financial_behavior": 1.15, "account_management": 1.1}
    elif primary_product == "Gold Loan":
        product_multipliers = {"income": 1.4, "collateral_value": 1.5, "employment": 1.1, "credit_score": 0.7, "credit_history": 0.6}
    else:
        product_multipliers = {}
    
    for var, multiplier in product_multipliers.items():
        if var in category_weights:
            category_weights[var] *= multiplier
    
    # Add additional data source variables if selected
    if additional_data:
        data_source_mapping = {
            "Bank Statements": {"bank_transaction_patterns": 0.03, "cash_flow_analysis": 0.02, "account_behavior": 0.02},
            "GST Data": {"business_turnover": 0.025, "tax_compliance": 0.015, "business_stability": 0.01},
            "ITR Data": {"declared_income": 0.02, "tax_history": 0.015, "income_verification": 0.015},
            "Social Media": {"social_stability": 0.015, "lifestyle_indicators": 0.01, "network_quality": 0.01},
            "Psychometric": {"personality_score": 0.02, "risk_behavior": 0.015, "decision_making": 0.01}
        }
        for source in additional_data:
            if source in data_source_mapping:
                category_weights.update(data_source_mapping[source])
    
    # Normalize weights to ensure they sum to exactly 1.0
    total_weight = sum(category_weights.values())
    normalized_weights = {var: weight / total_weight for var, weight in category_weights.items()}
    
    return normalized_weights

def calculate_risk_multipliers(risk_appetite, target_segment, approval_target):
    """Calculate risk-based multipliers with scientific basis"""
    
    multipliers = {
        "credit_score": 1.0, "income": 1.0, "debt_ratio": 1.0, 
        "employment": 1.0, "credit_history": 1.0
    }
    
    # Risk appetite adjustments based on credit risk literature
    if "Conservative" in risk_appetite:
        # Conservative lenders emphasize proven creditworthiness
        multipliers["credit_score"] = 1.15  # +15% emphasis
        multipliers["credit_history"] = 1.20  # +20% emphasis
        multipliers["debt_ratio"] = 1.10  # +10% emphasis
        multipliers["income"] = 0.90  # -10% de-emphasis
        multipliers["employment"] = 0.95  # -5% de-emphasis
        
    elif "Aggressive" in risk_appetite:
        # Growth-focused lenders emphasize income potential
        multipliers["income"] = 1.25  # +25% emphasis on earning capacity
        multipliers["employment"] = 1.15  # +15% emphasis on job stability
        multipliers["credit_score"] = 0.85  # -15% to expand market reach
        multipliers["debt_ratio"] = 0.90  # -10% for flexibility
        multipliers["credit_history"] = 0.85  # -15% to include new-to-credit
    
    # Target segment adjustments
    if "Prime" in target_segment:
        # Prime segment requires excellent credit profiles
        multipliers["credit_score"] *= 1.20
        multipliers["credit_history"] *= 1.15
        
    elif "Sub Prime" in target_segment:
        # Sub-prime inclusion focuses on current capacity
        multipliers["income"] *= 1.20
        multipliers["employment"] *= 1.15
        multipliers["credit_score"] *= 0.80
    
    # Approval target adjustments
    if approval_target > 70:
        # High approval targets need flexible criteria
        multipliers["income"] *= 1.10
        multipliers["employment"] *= 1.05
        multipliers["credit_score"] *= 0.95
        
    elif approval_target < 50:
        # Conservative approval targets need strict criteria
        multipliers["credit_score"] *= 1.10
        multipliers["debt_ratio"] *= 1.05
        multipliers["credit_history"] *= 1.05
    
    return multipliers

def calculate_product_adjustments(primary_product, selected_products):
    """Calculate product-specific weight adjustments"""
    
    adjustments = {
        "credit_score": 1.0, "income": 1.0, "debt_ratio": 1.0, 
        "employment": 1.0, "credit_history": 1.0
    }
    
    # Product-specific risk characteristics
    product_profiles = {
        "Personal Loan": {
            # Unsecured lending requires strong creditworthiness
            "credit_score": 1.15, "income": 1.10, "debt_ratio": 1.05
        },
        "Home Loan": {
            # Long-term secured lending emphasizes income stability
            "income": 1.20, "employment": 1.15, "debt_ratio": 1.10
        },
        "Business Loan": {
            # Commercial lending focuses on business cash flow
            "income": 1.25, "employment": 1.20, "credit_score": 1.05
        },
        "Gold Loan": {
            # Asset-backed lending prioritizes repayment capacity
            "income": 1.30, "employment": 1.10, "credit_score": 0.85
        },
        "Vehicle Loan": {
            # Auto loans balance collateral with borrower capacity
            "income": 1.15, "employment": 1.10, "debt_ratio": 1.05
        },
        "Credit Card": {
            # Revolving credit requires excellent credit management
            "credit_score": 1.25, "credit_history": 1.20, "debt_ratio": 1.15
        }
    }
    
    if primary_product in product_profiles:
        product_adj = product_profiles[primary_product]
        for variable in adjustments:
            if variable in product_adj:
                adjustments[variable] = product_adj[variable]
    
    return adjustments

def redistribute_for_additional_data(weights, additional_data, data_availability):
    """Properly redistribute weights for additional data sources"""
    
    # Calculate additional data weight pool based on data quality
    base_additional_pool = 0.12  # Base 12% for additional data
    
    # Adjust pool based on data availability and quality
    high_quality_sources = 0
    for source in additional_data:
        # Check data availability ratings
        if source in ["GST Data", "ITR Data"]:  # High-value sources
            high_quality_sources += 1
    
    # Increase pool for high-quality additional data
    additional_pool = min(base_additional_pool + (high_quality_sources * 0.02), 0.20)
    
    # Redistribute core weights proportionally
    core_multiplier = 1 - additional_pool
    for variable in weights:
        weights[variable] *= core_multiplier
    
    # Assign weights to additional data sources based on value
    source_weights = {
        "GST Data": 0.04,      # High value for business verification
        "ITR Data": 0.04,      # High value for income verification
        "Utility Bills": 0.02,  # Moderate value for stability
        "Telecom Data": 0.02,   # Moderate value for behavior
        "Social Media": 0.01,   # Lower value, supplementary
        "App Usage": 0.01      # Lower value, supplementary
    }
    
    # Normalize additional data weights to fit the pool
    total_assigned = sum(source_weights.get(source, 0.015) for source in additional_data)
    scaling_factor = additional_pool / total_assigned if total_assigned > 0 else 1
    
    for source in additional_data:
        weight_key = f"additional_{source.lower().replace(' ', '_')}"
        base_weight = source_weights.get(source, 0.015)
        weights[weight_key] = base_weight * scaling_factor
    
    return weights

def normalize_weights(weights):
    """Ensure weights sum to exactly 1.0"""
    total = sum(weights.values())
    if total > 0:
        for key in weights:
            weights[key] = weights[key] / total
    return weights

def validate_weights(weights, institution_type):
    """Validate weights meet business logic constraints"""
    
    # Ensure no weight is below minimum threshold
    min_weight = 0.05
    for key, value in weights.items():
        if value < min_weight and not key.startswith('additional_'):
            weights[key] = min_weight
    
    # Ensure no single weight dominates (max 50%)
    max_weight = 0.50
    for key, value in weights.items():
        if value > max_weight:
            weights[key] = max_weight
    
    # Re-normalize after validation
    weights = normalize_weights(weights)
    
    return weights

def generate_dynamic_weights(institution_type, risk_appetite, data_sources):
    """Legacy function for backward compatibility"""
    return generate_comprehensive_weights(
        institution_type, risk_appetite, data_sources, 
        [], None, "Mixed Portfolio"
    )

def render_scorecard_user():
    """Render Scorecard User dashboard"""
    # Get company name for display
    company_name = get_company_name(st.session_state.user_data['company_id'])
    display_name = company_name if company_name else st.session_state.user_data['username']
    
    # Modern compact header
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
                padding: 1rem 1.5rem; border-radius: 12px; color: white; margin-bottom: 1.5rem;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
        <h2 style="margin: 0; font-size: 1.3rem; font-weight: 500; letter-spacing: 0.5px;">📊 Scorecard User Dashboard</h2>
        <p style="margin: 0.3rem 0 0 0; opacity: 0.9; font-size: 0.9rem;">Welcome, {display_name} • Scorecard User</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar with Quick Stats and Logout
    with st.sidebar:
        st.markdown("### 📊 Quick Stats")
        
        # Quick company stats
        company_name = get_company_name(st.session_state.user_data['company_id'])
        if company_name:
            st.markdown(f"**Company:** {company_name}")
        
        # Check scorecard status for sidebar display
        cursor = db.cursor()
        cursor.execute("SELECT * FROM scorecards WHERE company_id=?", (st.session_state.user_data['company_id'],))
        scorecard = cursor.fetchone()
        
        if scorecard:
            st.markdown("**Status:** ✅ Ready for Scoring")
        else:
            st.markdown("**Status:** ⚠️ Awaiting Setup")
        
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True, type="secondary"):
            st.session_state.authenticated = False
            st.session_state.user_data = None
            st.rerun()
    
    if scorecard:
        st.success("✅ Company scorecard is available!")
        st.info("Loan scoring functionality will be available here once scorecard is activated.")
        
        # Show scorecard summary
        config = json.loads(scorecard[2])
        st.markdown("#### Your Company's Scorecard Configuration")
        
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Institution Type:** {config.get('institution_type', 'N/A')}")
            st.write(f"**Risk Appetite:** {config.get('risk_appetite', 'N/A')}")
        with col2:
            st.write(f"**Location:** {config.get('location', 'N/A')}")
            st.write(f"**Volume:** {config.get('volume', 'N/A')}")
            
    else:
        st.warning("⚠️ Company scorecard not yet created. Please contact your Scorecard Approver to complete the setup.")

# Main application logic
def main():
    """Main application function"""
    
    # Check if system is initialized
    if not check_system_initialized():
        render_initial_setup()
        return
    
    # Handle authentication
    if not st.session_state.authenticated:
        render_login()
        return
    
    # Route to appropriate dashboard
    role = st.session_state.user_data['role']
    if role == 'super_admin':
        render_super_admin()
    elif role == 'scorecard_approver':
        render_scorecard_approver()
    elif role == 'scorecard_user':
        render_scorecard_user()
    else:
        st.error("Invalid user role")

def render_dynamic_scorecard_module():
    """Render the complete Dynamic Scorecard Configuration module - 100% original implementation"""
    
    st.title("🔧 Dynamic Scorecard Configuration")
    st.markdown("Manage variables, score bands, and weights for your loan scoring model")
    

    
    # Remove duplicate sync controls - these will be in the ICSM Integration tab only
    
    # Initialize manager
    if 'dynamic_manager' not in st.session_state:
        st.session_state.dynamic_manager = DynamicScorecardManager()
    
    manager = st.session_state.dynamic_manager
    
    # Action buttons section
    st.markdown("---")
    col_apply, col_test, col_status = st.columns([1, 1, 2])
    
    with col_apply:
        if st.button("🎯 Apply Scorecard", type="primary", help="Apply current configuration to active scoring system"):
            try:
                # Normalize weights to 100%
                import sqlite3
                import json
                
                # Get current weights from database
                conn = sqlite3.connect("scorecard_config.db")
                cursor = conn.cursor()
                cursor.execute("SELECT variable_id, weight FROM scorecard_variables WHERE is_active = 1")
                db_results = cursor.fetchall()
                conn.close()
                
                # Convert to decimal format and normalize
                db_weights = {var_id: weight/100.0 for var_id, weight in db_results}
                total_weight = sum(db_weights.values())
                
                if total_weight > 0:
                    normalized_weights = {k: v/total_weight for k, v in db_weights.items()}
                else:
                    normalized_weights = db_weights
                
                # Save to JSON file directly
                with open("scoring_weights.json", "w") as f:
                    json.dump(normalized_weights, f, indent=2)
                
                # Update session state to reflect changes
                if 'scoring_weights' in st.session_state:
                    st.session_state.scoring_weights = normalized_weights
                
                st.success("✅ Scorecard configuration applied successfully!")
                st.info("All scoring functions will now use the updated weights.")
                
            except Exception as e:
                st.error(f"Failed to apply scorecard: {str(e)}")
    
    with col_test:
        if st.button("🧪 Test Scorecard", help="Test current configuration with sample data"):
            try:
                # Create test application data
                test_data = {
                    "credit_score": 750,
                    "foir": 0.35,
                    "monthly_income": 50000,
                    "age": 35,
                    "employment_tenure": 24,
                    "dpd30plus": 0,
                    "enquiry_count": 2,
                    "existing_loans": 1,
                    "loan_amount": 500000,
                    "existing_emi": 15000
                }
                
                # Calculate score using existing scoring engine
                import json
                
                # Load current weights
                try:
                    with open("scoring_weights.json", "r") as f:
                        weights = json.load(f)
                except:
                    weights = {}
                
                # Calculate test score
                result = calculate_dynamic_score(test_data, manager)
                
                if result and 'final_score' in result:
                    score = result['final_score']
                    decision = result.get('decision', 'Unknown')
                    bucket = result.get('final_bucket', 'Unknown')
                    
                    st.success(f"🎯 Test Score: {score:.1f}/100")
                    st.info(f"Risk Category: {bucket}")
                    st.write(f"Decision: {decision}")
                else:
                    st.warning("Unable to calculate test score - check scoring configuration")
                    
            except Exception as e:
                st.error(f"Test failed: {str(e)}")
    
    with col_status:
        # Show current weight total
        try:
            import sqlite3
            conn = sqlite3.connect("scorecard_config.db")
            cursor = conn.cursor()
            cursor.execute("SELECT SUM(weight) FROM scorecard_variables WHERE is_active = 1")
            total_weight = cursor.fetchone()[0] or 0
            conn.close()
            
            if abs(total_weight - 100.0) < 0.1:
                st.success(f"✅ Total Weight: {total_weight:.1f}% (Perfect)")
            else:
                st.warning(f"⚠️ Total Weight: {total_weight:.1f}% (Should be 100%)")
                
        except Exception as e:
            st.error("Unable to check weight total")
    
    # Main tabs - Logical flow: Categories → Variables → ICSM Integration → Bands → Weights
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 Category Management",
        "📊 Variable Management", 
        "🔄 ICSM Integration",
        "🎯 Score Bands Configuration",
        "⚖️ Weight Distribution Analysis"
    ])
    
    with tab1:
        render_dynamic_category_management(manager)
    
    with tab2:
        render_dynamic_variable_management(manager)
    
    with tab3:
        # ICSM Integration tab
        st.subheader("🔄 ICSM Integration")
        st.markdown("*Bridge between Dynamic Scorecard Configuration and Institution-Calibrated Scoring Model*")
        
        # Explanation section
        with st.expander("ℹ️ What is ICSM Integration?", expanded=False):
            st.markdown("""
            **ICSM (Institution-Calibrated Scoring Model)** is your company's personalized scoring system based on:
            - Institution type (NBFC, Bank, Fintech, etc.)
            - Risk appetite (Conservative, Moderate, Aggressive)
            - Target customer segment (Prime, Near Prime, Sub Prime)
            - Primary loan products and additional data sources
            
            **Integration Functions:**
            - **Sync FROM ICSM**: Import weights from your company's ICSM setup into Dynamic Scorecard
            - **Sync TO ICSM**: Export Dynamic Scorecard weights back to ICSM system
            - **View Mappings**: See how variables map between both systems
            """)
        
        # Current status section
        st.markdown("### Current Status")
        col1, col2 = st.columns(2)
        
        with col1:
            # Check Dynamic Scorecard status
            variables = manager.get_active_variables()
            total_vars = len(variables)
            total_weight = sum(v['weight'] for v in variables) if variables else 0
            
            st.metric("Dynamic Scorecard Variables", total_vars)
            st.metric("Total Weight", f"{total_weight:.1f}%")
            
            if abs(total_weight - 100) < 0.1:
                st.success("✅ Dynamic Scorecard properly configured")
            else:
                st.warning("⚠️ Dynamic Scorecard needs weight adjustment")
        
        with col2:
            # Check ICSM status
            try:
                import json
                import os
                if os.path.exists("scoring_weights.json"):
                    with open("scoring_weights.json", "r") as f:
                        icsm_weights = json.load(f)
                    icsm_vars = len(icsm_weights)
                    icsm_total = sum(icsm_weights.values()) if icsm_weights else 0
                else:
                    icsm_weights = {}
                    icsm_vars = 0
                    icsm_total = 0
            except:
                icsm_weights = {}
                icsm_vars = 0
                icsm_total = 0
            
            st.metric("ICSM Variables", icsm_vars)
            st.metric("ICSM Total Weight", f"{icsm_total:.1f}")
            
            if icsm_vars > 0:
                st.success("✅ ICSM configuration found")
            else:
                st.warning("⚠️ No ICSM configuration found")
        
        # Synchronization controls
        st.markdown("### Synchronization Controls")
        
        col_from, col_to, col_status = st.columns([1, 1, 2])
        
        with col_from:
            if st.button("⬅️ Sync FROM ICSM", type="secondary", help="Import company ICSM weights into Dynamic Scorecard"):
                if icsm_vars > 0:
                    try:
                        success = sync_weights_from_icsm()
                        if success:
                            st.success("✅ Successfully imported from ICSM")
                            st.rerun()
                        else:
                            st.error("❌ Failed to import from ICSM")
                    except Exception as e:
                        st.error(f"❌ Sync error: {str(e)}")
                else:
                    st.error("❌ No ICSM configuration to import")
        
        with col_to:
            if st.button("➡️ Sync TO ICSM", type="secondary", help="Export Dynamic Scorecard weights to ICSM system"):
                if total_vars > 0:
                    try:
                        success = sync_weights_to_icsm()
                        if success:
                            st.success("✅ Successfully exported to ICSM")
                            st.rerun()
                        else:
                            st.error("❌ Failed to export to ICSM")
                    except Exception as e:
                        st.error(f"❌ Sync error: {str(e)}")
                else:
                    st.error("❌ No Dynamic Scorecard variables to export")
        
        with col_status:
            st.markdown("**Sync Status:**")
            if total_vars > 0 and icsm_vars > 0:
                st.info("🔗 Both systems configured - Ready for sync operations")
            elif total_vars > 0:
                st.warning("⚠️ Only Dynamic Scorecard configured")
            elif icsm_vars > 0:
                st.warning("⚠️ Only ICSM configured") 
            else:
                st.error("❌ Neither system configured")
        
        # Variable mapping display
        if total_vars > 0 or icsm_vars > 0:
            st.markdown("### Variable Mapping")
            
            col_ds, col_icsm = st.columns(2)
            
            with col_ds:
                st.markdown("#### Dynamic Scorecard Variables")
                if variables:
                    # Define proper category ordering to match ICSM structure
                    category_order = [
                        "Core Credit Variables",
                        "Behavioral Analytics", 
                        "Employment Stability",
                        "Banking Behavior",
                        "Exposure & Intent",
                        "Geographic & Social"
                    ]
                    
                    # Group by category
                    categories = {}
                    for var in variables:
                        cat = var['category']
                        if cat not in categories:
                            categories[cat] = []
                        categories[cat].append(var)
                    
                    # Display in proper order
                    for category in category_order:
                        if category in categories:
                            cat_vars = categories[category]
                            with st.expander(f"{category} ({len(cat_vars)} variables)"):
                                for var in cat_vars:
                                    st.write(f"• **{var['display_name']}** ({var['weight']:.1f}%)")
                else:
                    st.info("No Dynamic Scorecard variables found")
            
            with col_icsm:
                st.markdown("#### ICSM Variables")
                if icsm_weights:
                    # Sort by weight
                    sorted_icsm = sorted(icsm_weights.items(), key=lambda x: x[1], reverse=True)
                    
                    # Group by exact same category structure as Dynamic Scorecard - Enterprise-grade precision
                    category_groups = {
                        "Core Credit Variables": ["credit_score", "income", "debt_ratio", "credit_history", "payment_history", 
                                                "foir", "monthly_income", "dpd30plus"],
                        "Behavioral Analytics": ["spending_patterns", "transaction_frequency", "account_usage", "financial_behavior", "digital_footprint"],
                        "Employment Stability": ["employment", "job_tenure", "income_stability", "employer_type"],
                        "Banking Behavior": ["account_history", "banking_relationship", "account_management", "overdraft_history"],
                        "Exposure & Intent": ["existing_loans", "credit_utilization", "loan_purpose", "collateral_value"],
                        "Geographic & Social": ["location_risk", "social_indicators", "regional_factors", "demographic_data"]
                    }
                    
                    # Display in same order as Dynamic Scorecard
                    for group_name in category_order:
                        if group_name in category_groups:
                            group_vars = category_groups[group_name]
                            group_items = [(var, weight) for var, weight in sorted_icsm if var in group_vars]
                            if group_items:
                                with st.expander(f"{group_name} ({len(group_items)} variables)"):
                                    for var, weight in group_items:
                                        percentage = weight * 100 if weight < 1 else weight
                                        st.write(f"• **{var.replace('_', ' ').title()}** ({percentage:.1f}%)")
                    
                    # Show unmapped variables
                    all_mapped = set()
                    for group_vars in category_groups.values():
                        all_mapped.update(group_vars)
                    
                    unmapped = [(var, weight) for var, weight in sorted_icsm if var not in all_mapped]
                    if unmapped:
                        with st.expander(f"Other Variables ({len(unmapped)} variables)"):
                            for var, weight in unmapped:
                                percentage = weight * 100 if weight < 1 else weight
                                st.write(f"• **{var.replace('_', ' ').title()}** ({percentage:.1f}%)")
                else:
                    st.info("No ICSM variables found")
    
    with tab4:
        render_dynamic_score_bands_config(manager)
    
    with tab5:
        render_dynamic_weight_distribution(manager)

def render_dynamic_variable_management(manager):
    """Render variable management interface with 6 fixed category groups"""
    
    st.subheader("📊 Scorecard Variables")
    
    # Get current category weights from database
    categories = manager.get_categories()
    category_weights = {}
    for cat in categories:
        category_weights[cat['category_name']] = cat['total_weight']
    
    # Define the 6 fixed category groups with dynamic weights
    variable_groups = [
        {"name": "Core Credit Variables", "weight": category_weights.get("Core Credit Variables", 35.0), "category_key": "Core Credit Variables"},
        {"name": "Behavioral Analytics", "weight": category_weights.get("Behavioral Analytics", 20.0), "category_key": "Behavioral Analytics"},
        {"name": "Employment Stability", "weight": category_weights.get("Employment Stability", 15.0), "category_key": "Employment Stability"},
        {"name": "Banking Behavior", "weight": category_weights.get("Banking Behavior", 10.0), "category_key": "Banking Behavior"},
        {"name": "Exposure & Intent", "weight": category_weights.get("Exposure & Intent", 12.0), "category_key": "Exposure & Intent"},
        {"name": "Geographic & Social", "weight": category_weights.get("Geographic & Social", 8.0), "category_key": "Geographic & Social"}
    ]
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### Variables by Category Groups")
        variables = manager.get_active_variables()
        
        if variables:
            # Group variables by category and display with target weights
            categories = manager.get_categories()
            
            # Create category groups with target weights
            category_targets = {
                "Core Credit Variables": 35.0,
                "Behavioral Analytics": 20.0,
                "Employment Stability": 15.0,
                "Banking Behavior": 10.0,
                "Exposure & Intent": 12.0,
                "Geographic & Social": 8.0
            }
            
            for category_name, target_weight in category_targets.items():
                # Filter variables for this category
                category_vars = [v for v in variables if category_name in v['category']]
                
                if category_vars:
                    # Calculate current total weight for this category
                    current_total = sum(v['weight'] for v in category_vars)
                    weight_diff = abs(current_total - target_weight)
                    
                    # Show status indicator
                    if weight_diff <= 0.1:
                        status = "✅"
                        status_color = "success"
                    elif current_total > target_weight:
                        status = "🔴"
                        status_color = "error"
                    else:
                        status = "🟡"
                        status_color = "warning"
                    
                    # Category header
                    st.markdown(f"#### {status} {category_name}")
                    st.markdown(f"**Target: {target_weight}% | Current: {current_total:.1f}%**")
                    
                    # Show warning if weights don't match
                    if weight_diff > 0.1:
                        if current_total > target_weight:
                            st.error(f"⚠️ Current weights exceed target by {weight_diff:.1f}%. Please reduce variable weights.")
                        else:
                            st.warning(f"⚠️ Current weights are {weight_diff:.1f}% below target. Please increase variable weights.")
                    
                    # Display variables in this category
                    for i, var in enumerate(category_vars):
                        var_index = variables.index(var)  # Get original index for unique keys
                        col_var, col_weight, col_actions = st.columns([3, 1, 1])
                        
                        with col_var:
                            st.write(f"**{var['display_name']}**")
                            st.caption(f"Type: {var['data_type']} ({var['input_type']})")
                        
                        with col_weight:
                            new_weight = st.number_input(
                                f"Weight %",
                                min_value=0.0,
                                max_value=50.0,
                                value=var['weight'],
                                step=0.1,
                                key=f"weight_cat_{var_index}_{var['variable_id']}"
                            )
                            if new_weight != var['weight']:
                                manager.update_variable_weight(var['variable_id'], new_weight)
                                st.rerun()
                        
                        with col_actions:
                            if st.button("Deactivate", key=f"deact_cat_{var_index}_{var['variable_id']}"):
                                manager.deactivate_variable(var['variable_id'])
                                st.rerun()
                    
                    st.markdown("---")
        else:
            st.info("No variables configured yet")
        
        # Show inactive variables section
        st.markdown("### Inactive Variables")
        inactive_vars = manager.get_inactive_variables()
        if inactive_vars:
            for j, var in enumerate(inactive_vars):
                col_var, col_actions = st.columns([4, 1])
                with col_var:
                    st.write(f"**{var['display_name']}** (Deactivated)")
                    st.caption(f"Category: {var['category']} | Weight: {var['weight']}%")
                with col_actions:
                    if st.button("Reactivate", key=f"react_inactive_{j}_{var['variable_id']}"):
                        manager.reactivate_variable(var['variable_id'])
                        st.rerun()
        else:
            st.info("No inactive variables")
    
    with col2:
        st.markdown("### Add New Variable")
        
        with st.form("add_variable_form"):
            var_id = st.text_input("Variable ID", placeholder="e.g., debt_to_income")
            display_name = st.text_input("Display Name", placeholder="e.g., Debt to Income Ratio")
            
            categories_list = [cat['category_name'] for cat in manager.get_categories()]
            if categories_list:
                category = st.selectbox("Category", categories_list)
            else:
                category = "Core Credit Variables"
                st.info("No categories found. Using default category.")
            
            col_type1, col_type2 = st.columns(2)
            with col_type1:
                data_type = st.selectbox("Data Type", ["integer", "float", "text"])
            with col_type2:
                input_type = st.selectbox("Input Type", ["number", "selectbox", "text_input"])
            
            weight = st.number_input("Weight %", min_value=0.0, max_value=50.0, value=1.0, step=0.5)
            
            col_range1, col_range2 = st.columns(2)
            with col_range1:
                min_value = st.number_input("Min Value", value=0.0) if data_type != "text" else None
            with col_range2:
                max_value = st.number_input("Max Value", value=100.0) if data_type != "text" else None
            
            default_value = st.text_input("Default Value", placeholder="Default input value")
            help_text = st.text_area("Help Text", placeholder="User guidance for this field")
            scientific_basis = st.text_area("Scientific Basis", placeholder="Why this variable matters for credit risk")
            
            is_required = st.checkbox("Required Field", value=True)
            
            if st.form_submit_button("Add Variable"):
                if var_id and display_name:
                    variable_data = {
                        "variable_id": var_id,
                        "display_name": display_name,
                        "category": category,
                        "weight": weight,
                        "data_type": data_type,
                        "input_type": input_type,
                        "min_value": min_value,
                        "max_value": max_value,
                        "default_value": default_value,
                        "help_text": help_text,
                        "scientific_basis": scientific_basis,
                        "is_required": is_required
                    }
                    
                    try:
                        manager.add_variable(variable_data)
                        st.success(f"Variable '{display_name}' added successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error adding variable: {str(e)}")
                else:
                    st.error("Variable ID and Display Name are required")

def render_dynamic_score_bands_config(manager):
    """Render complete score bands configuration interface"""
    
    st.subheader("🎯 Score Bands Configuration")
    st.info("Score bands define how input values are converted to credit scores")
    
    variables = manager.get_active_variables()
    
    if not variables:
        st.info("No active variables found. Add variables first.")
        return
    
    # Select variable to configure
    variable_options = [f"{v['display_name']} ({v['variable_id']})" for v in variables]
    selected_idx = st.selectbox("Select Variable to Configure:", range(len(variable_options)), format_func=lambda x: variable_options[x])
    
    if selected_idx is not None:
        selected_var = variables[selected_idx]
        
        st.markdown(f"### Configuring: {selected_var['display_name']}")
        st.markdown(f"**Category:** {selected_var['category']} | **Weight:** {selected_var['weight']}% | **Type:** {selected_var['data_type']}")
        
        # Show existing score bands
        score_bands = selected_var.get('score_bands', [])
        
        if score_bands:
            st.markdown("#### Current Score Bands")
            for i, band in enumerate(score_bands):
                with st.expander(f"Band {i+1}: {band.get('label', 'Unnamed')} (Score: {band.get('score', 0)})"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Threshold:** {band.get('threshold_min', 'N/A')} - {band.get('threshold_max', 'N/A')}")
                        st.write(f"**Operator:** {band.get('operator', 'N/A')}")
                    with col2:
                        st.write(f"**Score:** {band.get('score', 0)}")
                        st.write(f"**Description:** {band.get('description', 'No description')}")
        else:
            st.info("No score bands configured for this variable")
        
        # Add new score band section
        st.markdown("#### Add New Score Band")
        with st.form(f"add_band_{selected_var['variable_id']}"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                band_label = st.text_input("Band Label", placeholder="e.g., Excellent")
                threshold_min = st.number_input("Min Threshold", value=0.0)
                threshold_max = st.number_input("Max Threshold", value=100.0)
            
            with col2:
                operator = st.selectbox("Operator", ["range", ">=", "<=", "=="])
                score = st.number_input("Score (0-1)", min_value=0.0, max_value=1.0, value=1.0, step=0.1)
                band_order = st.number_input("Band Order", min_value=1, value=len(score_bands) + 1)
            
            with col3:
                description = st.text_area("Description", placeholder="Describe this score band")
            
            if st.form_submit_button("Add Score Band"):
                try:
                    # Add score band to database
                    import sqlite3
                    conn = sqlite3.connect("scorecard_config.db")
                    cursor = conn.cursor()
                    
                    cursor.execute('''
                        INSERT INTO score_bands (variable_id, band_order, threshold_min, threshold_max, 
                                               operator, score, label, description, is_active)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
                    ''', (selected_var['variable_id'], band_order, threshold_min, threshold_max, 
                         operator, score, band_label, description))
                    
                    conn.commit()
                    conn.close()
                    
                    st.success(f"Score band '{band_label}' added successfully!")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Error adding score band: {str(e)}")

def render_dynamic_weight_distribution(manager):
    """Render complete weight distribution analysis"""
    
    st.subheader("⚖️ Weight Distribution Analysis")
    
    variables = manager.get_active_variables()
    categories = manager.get_categories()
    
    if not variables:
        st.info("No active variables found.")
        return
    
    # Calculate current weights by category
    weight_by_category = {}
    total_weight = 0
    
    for var in variables:
        category = var['category']
        weight = var['weight']
        
        if category not in weight_by_category:
            weight_by_category[category] = 0
        weight_by_category[category] += weight
        total_weight += weight
    
    # Display weight distribution
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("#### Category Weight Distribution")
        
        for category in weight_by_category:
            category_weight = weight_by_category[category]
            percentage = (category_weight / total_weight * 100) if total_weight > 0 else 0
            
            # Find category color
            cat_info = next((cat for cat in categories if cat['category_name'] == category), None)
            color = cat_info['color_code'] if cat_info else '#666666'
            expected_weight = cat_info['total_weight'] if cat_info else 0.0
            
            st.markdown(f"""
            <div style="padding: 10px; margin: 5px 0; background: {color}20; border-left: 4px solid {color}; border-radius: 4px;">
                <strong>{category}</strong><br>
                Weight: {category_weight:.1f}% | Expected: {expected_weight:.1f}%
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("#### Weight Validation")
        
        if abs(total_weight - 100) > 0.1:
            st.error(f"Total weight is {total_weight:.1f}% (should be 100%)")
            st.warning("Please adjust variable weights to total exactly 100%")
        else:
            st.success(f"Total weight is {total_weight:.1f}% (Perfect!)")
        
        # Show variables by weight
        st.markdown("#### Variables by Weight")
        sorted_vars = sorted(variables, key=lambda x: x['weight'], reverse=True)
        
        for var in sorted_vars:
            percentage = (var['weight'] / total_weight * 100) if total_weight > 0 else 0
            st.write(f"**{var['display_name']}**: {var['weight']:.1f}% ({percentage:.1f}% of total)")
    
    # Visual chart with plotly
    try:
        import plotly.graph_objects as go
        
        st.markdown("#### Category Performance Chart")
        
        # Create data for chart
        category_names = list(weight_by_category.keys())
        current_weights = [weight_by_category[cat] for cat in category_names]
        target_weights = []
        
        for cat in category_names:
            cat_info = next((c for c in categories if c['category_name'] == cat), None)
            target_weights.append(cat_info['total_weight'] if cat_info else 0)
        
        # Create grouped bar chart
        fig = go.Figure(data=[
            go.Bar(name='Current Weight %', x=category_names, y=current_weights, marker_color='#3498db'),
            go.Bar(name='Target Weight %', x=category_names, y=target_weights, marker_color='#ecf0f1', opacity=0.6)
        ])
        
        fig.update_layout(
            title='Current vs Target Weights by Category',
            xaxis_title='Categories',
            yaxis_title='Weight Percentage',
            barmode='group',
            height=400,
            showlegend=True
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    except ImportError:
        st.info("Install plotly for advanced charts: pip install plotly")

def render_dynamic_category_management(manager):
    """Render complete category management interface"""
    
    st.subheader("📋 Category Management")
    
    categories = manager.get_categories()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### Current Categories")
        
        if categories:
            for cat in categories:
                with st.expander(f"{cat.get('icon', '📋')} {cat['category_name']} ({cat['total_weight']}%)"):
                    st.write(f"**Display Order:** {cat['display_order']}")
                    st.write(f"**Target Weight:** {cat['total_weight']}%")
                    st.write(f"**Color:** {cat.get('color_code', '#666666')}")
                    
                    # Count variables in this category
                    variables = manager.get_active_variables()
                    var_count = len([v for v in variables if v['category'] == cat['category_name']])
                    st.write(f"**Variables:** {var_count}")
                    
                    # Category actions
                    col_edit, col_delete = st.columns(2)
                    with col_edit:
                        if st.button(f"Edit {cat['category_name']}", key=f"edit_{cat['category_name']}"):
                            st.session_state[f"editing_{cat['category_name']}"] = True
                    
                    with col_delete:
                        if st.button(f"Delete {cat['category_name']}", key=f"delete_{cat['category_name']}"):
                            # Only allow deletion if no variables assigned
                            if var_count == 0:
                                try:
                                    import sqlite3
                                    conn = sqlite3.connect("scorecard_config.db")
                                    cursor = conn.cursor()
                                    cursor.execute("DELETE FROM scorecard_categories WHERE category_name = ?", (cat['category_name'],))
                                    conn.commit()
                                    conn.close()
                                    st.success(f"Category '{cat['category_name']}' deleted!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error deleting category: {str(e)}")
                            else:
                                st.error(f"Cannot delete category with {var_count} variables. Remove variables first.")
        else:
            st.info("No categories found.")
    
    with col2:
        st.markdown("### Add New Category")
        
        with st.form("add_category_form"):
            category_name = st.text_input("Category Name", placeholder="e.g., Risk Indicators")
            display_order = st.number_input("Display Order", min_value=1, value=len(categories) + 1)
            total_weight = st.number_input("Target Weight %", min_value=0.0, max_value=100.0, value=10.0)
            
            color_options = {
                "Red": "#e74c3c",
                "Blue": "#3498db", 
                "Green": "#27ae60",
                "Orange": "#e67e22",
                "Purple": "#9b59b6",
                "Brown": "#8b4513"
            }
            color_name = st.selectbox("Color", list(color_options.keys()))
            color_code = color_options[color_name]
            
            icon_options = ["📊", "🧠", "💼", "🏦", "💰", "🌍", "📈", "⚡", "🎯", "🔍"]
            icon = st.selectbox("Icon", icon_options)
            
            if st.form_submit_button("Add Category"):
                if category_name:
                    category_data = {
                        "category_name": category_name,
                        "display_order": display_order,
                        "total_weight": total_weight,
                        "color_code": color_code,
                        "icon": icon
                    }
                    
                    try:
                        manager.add_category(category_data)
                        st.success(f"Category '{category_name}' added successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error adding category: {str(e)}")
                else:
                    st.error("Category name is required")

def render_score_bands_config_full(manager):
    """Render complete score bands configuration interface"""
    
    st.subheader("🎯 Score Bands Configuration")
    st.info("Score bands define how input values are converted to credit scores")
    
    variables = manager.get_active_variables()
    
    if not variables:
        st.info("No active variables found. Add variables first.")
        return
    
    # Select variable to configure
    variable_options = [f"{v['display_name']} ({v['variable_id']})" for v in variables]
    selected_idx = st.selectbox("Select Variable to Configure:", range(len(variable_options)), format_func=lambda x: variable_options[x])
    
    if selected_idx is not None:
        selected_var = variables[selected_idx]
        
        st.markdown(f"### Configuring: {selected_var['display_name']}")
        st.markdown(f"**Category:** {selected_var['category']} | **Weight:** {selected_var['weight']}% | **Type:** {selected_var['data_type']}")
        
        # Show existing score bands
        score_bands = selected_var.get('score_bands', [])
        
        if score_bands:
            st.markdown("#### Current Score Bands")
            for i, band in enumerate(score_bands):
                with st.expander(f"Band {i+1}: {band.get('label', 'Unnamed')} (Score: {band.get('score', 0)})"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Threshold:** {band.get('threshold_min', 'N/A')} - {band.get('threshold_max', 'N/A')}")
                        st.write(f"**Operator:** {band.get('operator', 'N/A')}")
                    with col2:
                        st.write(f"**Score:** {band.get('score', 0)}")
                        st.write(f"**Description:** {band.get('description', 'No description')}")
        else:
            st.info("No score bands configured for this variable")
        
        # Add new score band section
        st.markdown("#### Add New Score Band")
        with st.form(f"add_band_{selected_var['variable_id']}"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                band_label = st.text_input("Band Label", placeholder="e.g., Excellent")
                threshold_min = st.number_input("Min Threshold", value=0.0)
                threshold_max = st.number_input("Max Threshold", value=100.0)
            
            with col2:
                operator = st.selectbox("Operator", ["range", ">=", "<=", "=="])
                score = st.number_input("Score (0-1)", min_value=0.0, max_value=1.0, value=1.0, step=0.1)
                band_order = st.number_input("Band Order", min_value=1, value=len(score_bands) + 1)
            
            with col3:
                description = st.text_area("Description", placeholder="Describe this score band")
            
            if st.form_submit_button("Add Score Band"):
                try:
                    # Add score band to database
                    import sqlite3
                    conn = sqlite3.connect("scorecard_config.db")
                    cursor = conn.cursor()
                    
                    cursor.execute('''
                        INSERT INTO score_bands (variable_id, band_order, threshold_min, threshold_max, 
                                               operator, score, label, description, is_active)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
                    ''', (selected_var['variable_id'], band_order, threshold_min, threshold_max, 
                         operator, score, band_label, description))
                    
                    conn.commit()
                    conn.close()
                    
                    st.success(f"Score band '{band_label}' added successfully!")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Error adding score band: {str(e)}")

def render_weight_distribution_full(manager):
    """Render complete weight distribution analysis"""
    
    st.subheader("⚖️ Weight Distribution Analysis")
    
    variables = manager.get_active_variables()
    categories = manager.get_categories()
    
    if not variables:
        st.info("No active variables found.")
        return
    
    # Calculate current weights by category
    weight_by_category = {}
    total_weight = 0
    
    for var in variables:
        category = var['category']
        weight = var['weight']
        
        if category not in weight_by_category:
            weight_by_category[category] = 0
        weight_by_category[category] += weight
        total_weight += weight
    
    # Display weight distribution
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("#### Category Weight Distribution")
        
        # Define enterprise-grade category ordering
        category_order = [
            "Core Credit Variables",
            "Behavioral Analytics", 
            "Employment Stability",
            "Banking Behavior",
            "Exposure & Intent",
            "Geographic & Social"
        ]
        
        # Display categories in proper order
        for category in category_order:
            if category in weight_by_category:
                category_weight = weight_by_category[category]
                percentage = (category_weight / total_weight * 100) if total_weight > 0 else 0
                
                # Find category color
                cat_info = next((cat for cat in categories if cat['category_name'] == category), None)
                color = cat_info['color_code'] if cat_info else '#666666'
                
                expected_weight = cat_info['total_weight'] if cat_info else 0.0
                st.markdown(f"""
                <div style="padding: 10px; margin: 5px 0; background: {color}20; border-left: 4px solid {color}; border-radius: 4px;">
                    <strong>{category}</strong><br>
                    Weight: {category_weight:.1f}% | Expected: {expected_weight:.1f}%
                </div>
                """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("#### Weight Validation")
        
        if abs(total_weight - 100) > 0.1:
            st.error(f"Total weight is {total_weight:.1f}% (should be 100%)")
            st.warning("Please adjust variable weights to total exactly 100%")
        else:
            st.success(f"Total weight is {total_weight:.1f}% (Perfect!)")
        
        # Show variables by weight
        st.markdown("#### Variables by Weight")
        sorted_vars = sorted(variables, key=lambda x: x['weight'], reverse=True)
        
        for var in sorted_vars:
            percentage = (var['weight'] / total_weight * 100) if total_weight > 0 else 0
            st.write(f"**{var['display_name']}**: {var['weight']:.1f}% ({percentage:.1f}% of total)")
    
    # Visual chart with plotly
    try:
        import plotly.graph_objects as go
        
        st.markdown("#### Category Performance Chart")
        
        # Create data for chart
        category_names = list(weight_by_category.keys())
        current_weights = [weight_by_category[cat] for cat in category_names]
        target_weights = []
        
        for cat in category_names:
            cat_info = next((c for c in categories if c['category_name'] == cat), None)
            target_weights.append(cat_info['total_weight'] if cat_info else 0)
        
        # Create grouped bar chart
        fig = go.Figure(data=[
            go.Bar(name='Current Weight %', x=category_names, y=current_weights, marker_color='#3498db'),
            go.Bar(name='Target Weight %', x=category_names, y=target_weights, marker_color='#ecf0f1', opacity=0.6)
        ])
        
        fig.update_layout(
            title='Current vs Target Weights by Category',
            xaxis_title='Categories',
            yaxis_title='Weight Percentage',
            barmode='group',
            height=400,
            showlegend=True
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    except ImportError:
        st.info("Install plotly for advanced charts: pip install plotly")

def render_category_management_full(manager):
    """Render complete category management interface"""
    
    st.subheader("📋 Category Management")
    
    categories = manager.get_categories()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### Current Categories")
        
        if categories:
            for cat in categories:
                with st.expander(f"{cat.get('icon', '📋')} {cat['category_name']} ({cat['total_weight']}%)"):
                    st.write(f"**Display Order:** {cat['display_order']}")
                    st.write(f"**Target Weight:** {cat['total_weight']}%")
                    st.write(f"**Color:** {cat.get('color_code', '#666666')}")
                    
                    # Count variables in this category
                    variables = manager.get_active_variables()
                    var_count = len([v for v in variables if v['category'] == cat['category_name']])
                    st.write(f"**Variables:** {var_count}")
                    
                    # Category actions
                    col_edit, col_delete = st.columns(2)
                    with col_edit:
                        if st.button(f"Edit {cat['category_name']}", key=f"edit_{cat['category_name']}"):
                            st.session_state[f"editing_{cat['category_name']}"] = True
                    
                    with col_delete:
                        if st.button(f"Delete {cat['category_name']}", key=f"delete_{cat['category_name']}"):
                            # Only allow deletion if no variables assigned
                            if var_count == 0:
                                try:
                                    import sqlite3
                                    conn = sqlite3.connect("scorecard_config.db")
                                    cursor = conn.cursor()
                                    cursor.execute("DELETE FROM scorecard_categories WHERE category_name = ?", (cat['category_name'],))
                                    conn.commit()
                                    conn.close()
                                    st.success(f"Category '{cat['category_name']}' deleted!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error deleting category: {str(e)}")
                            else:
                                st.error(f"Cannot delete category with {var_count} variables. Remove variables first.")
        else:
            st.info("No categories found.")
    
    with col2:
        st.markdown("### Add New Category")
        
        with st.form("add_category_form"):
            category_name = st.text_input("Category Name", placeholder="e.g., Risk Indicators")
            display_order = st.number_input("Display Order", min_value=1, value=len(categories) + 1)
            total_weight = st.number_input("Target Weight %", min_value=0.0, max_value=100.0, value=10.0)
            
            color_options = {
                "Red": "#e74c3c",
                "Blue": "#3498db", 
                "Green": "#27ae60",
                "Orange": "#e67e22",
                "Purple": "#9b59b6",
                "Brown": "#8b4513"
            }
            color_name = st.selectbox("Color", list(color_options.keys()))
            color_code = color_options[color_name]
            
            icon_options = ["📊", "🧠", "💼", "🏦", "💰", "🌍", "📈", "⚡", "🎯", "🔍"]
            icon = st.selectbox("Icon", icon_options)
            
            if st.form_submit_button("Add Category"):
                if category_name:
                    category_data = {
                        "category_name": category_name,
                        "display_order": display_order,
                        "total_weight": total_weight,
                        "color_code": color_code,
                        "icon": icon
                    }
                    
                    try:
                        manager.add_category(category_data)
                        st.success(f"Category '{category_name}' added successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error adding category: {str(e)}")
                else:
                    st.error("Category name is required")

def render_score_bands_config(manager):
    """Render score bands configuration interface"""
    
    st.subheader("🎯 Score Bands Configuration")
    st.info("Score bands define how input values are converted to credit scores")
    
    variables = manager.get_active_variables()
    
    if not variables:
        st.info("No active variables found. Add variables first.")
        return
    
    # Select variable to configure
    variable_options = [f"{v['display_name']} ({v['variable_id']})" for v in variables]
    selected_idx = st.selectbox("Select Variable to Configure:", range(len(variable_options)), format_func=lambda x: variable_options[x])
    
    if selected_idx is not None:
        selected_var = variables[selected_idx]
        
        st.markdown(f"### Configuring: {selected_var['display_name']}")
        st.markdown(f"**Category:** {selected_var['category']} | **Weight:** {selected_var['weight']}% | **Type:** {selected_var['data_type']}")
        
        # Show existing score bands
        score_bands = selected_var['score_bands']
        
        if score_bands:
            st.markdown("#### Current Score Bands")
            for band in score_bands:
                with st.expander(f"Band {band['band_order']}: {band['label']} (Score: {band['score']})"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Threshold:** {band['threshold_min']} - {band['threshold_max']}")
                        st.write(f"**Operator:** {band['operator']}")
                    with col2:
                        st.write(f"**Score:** {band['score']}")
                        st.write(f"**Description:** {band['description']}")
        else:
            st.info("No score bands configured for this variable")

def render_weight_distribution(manager):
    """Render weight distribution interface"""
    
    st.subheader("⚖️ Weight Distribution Analysis")
    
    variables = manager.get_active_variables()
    categories = manager.get_categories()
    
    if not variables:
        st.info("No active variables found.")
        return
    
    # Calculate current weights by category
    weight_by_category = {}
    total_weight = 0
    
    for var in variables:
        category = var['category']
        weight = var['weight']
        
        if category not in weight_by_category:
            weight_by_category[category] = 0
        weight_by_category[category] += weight
        total_weight += weight
    
    # Display weight distribution
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("#### Category Weight Distribution")
        
        for category in weight_by_category:
            category_weight = weight_by_category[category]
            percentage = (category_weight / total_weight * 100) if total_weight > 0 else 0
            
            # Find category color
            cat_info = next((cat for cat in categories if cat['category_name'] == category), None)
            color = cat_info['color_code'] if cat_info else '#666666'
            
            st.markdown(f"""
            <div style="padding: 10px; margin: 5px 0; background: {color}20; border-left: 4px solid {color}; border-radius: 4px;">
                <strong>{category}</strong><br>
                Weight: {category_weight:.1f}% | Expected: {cat_info['total_weight']:.1f}%
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("#### Weight Validation")
        
        if abs(total_weight - 100) > 0.1:
            st.error(f"Total weight is {total_weight:.1f}% (should be 100%)")
            st.warning("Please adjust variable weights to total exactly 100%")
        else:
            st.success(f"Total weight is {total_weight:.1f}% (Perfect!)")
        
        # Show variables by weight
        st.markdown("#### Variables by Weight")
        sorted_vars = sorted(variables, key=lambda x: x['weight'], reverse=True)
        
        for var in sorted_vars:
            percentage = (var['weight'] / total_weight * 100) if total_weight > 0 else 0
            st.write(f"**{var['display_name']}**: {var['weight']:.1f}% ({percentage:.1f}% of total)")

def render_category_management(manager):
    """Render category management interface"""
    
    st.subheader("📋 Category Management")
    
    categories = manager.get_categories()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### Current Categories")
        
        if categories:
            for cat in categories:
                with st.expander(f"{cat['icon']} {cat['category_name']} ({cat['total_weight']}%)"):
                    st.write(f"**Display Order:** {cat['display_order']}")
                    st.write(f"**Target Weight:** {cat['total_weight']}%")
                    st.write(f"**Color:** {cat['color_code']}")
                    
                    # Count variables in this category
                    variables = manager.get_active_variables()
                    var_count = len([v for v in variables if v['category'] == cat['category_name']])
                    st.write(f"**Variables:** {var_count}")
        else:
            st.info("No categories found.")
    
    with col2:
        st.markdown("### Add New Category")
        
        with st.form("add_category_form"):
            category_name = st.text_input("Category Name", placeholder="e.g., Risk Indicators")
            display_order = st.number_input("Display Order", min_value=1, value=len(categories) + 1)
            total_weight = st.number_input("Target Weight %", min_value=0.0, max_value=100.0, value=10.0)
            
            color_options = {
                "Red": "#e74c3c",
                "Blue": "#3498db", 
                "Green": "#27ae60",
                "Orange": "#e67e22",
                "Purple": "#9b59b6",
                "Brown": "#8b4513"
            }
            color_name = st.selectbox("Color", list(color_options.keys()))
            color_code = color_options[color_name]
            
            icon_options = ["📊", "🧠", "💼", "🏦", "💰", "🌍", "📈", "⚡", "🎯", "🔍"]
            icon = st.selectbox("Icon", icon_options)
            
            if st.form_submit_button("Add Category"):
                if category_name:
                    category_data = {
                        "category_name": category_name,
                        "display_order": display_order,
                        "total_weight": total_weight,
                        "color_code": color_code,
                        "icon": icon
                    }
                    
                    try:
                        manager.add_category(category_data)
                        st.success(f"Category '{category_name}' added successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error adding category: {str(e)}")
                else:
                    st.error("Category name is required")

# Function moved inline to tab5 to fix definition order

def render_variable_mapping_display(manager, icsm_weights):
    """Display variable mapping between Dynamic Scorecard and ICSM"""
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Dynamic Scorecard Variables")
        variables = manager.get_active_variables()
        if variables:
            # Group by category
            categories = {}
            for var in variables:
                cat = var['category']
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append(var)
            
            for category, cat_vars in categories.items():
                with st.expander(f"{category} ({len(cat_vars)} variables)"):
                    for var in cat_vars:
                        st.write(f"• **{var['display_name']}** ({var['weight']}%)")
        else:
            st.info("No Dynamic Scorecard variables found")
    
    with col2:
        st.markdown("#### ICSM Variables")
        if icsm_weights:
            # Sort by weight
            sorted_icsm = sorted(icsm_weights.items(), key=lambda x: x[1], reverse=True)
            
            # Group by estimated category based on variable name
            category_groups = {
                "Core Credit": ["credit_score", "income", "debt_ratio", "credit_history", "payment_history"],
                "Behavioral": ["spending_patterns", "transaction_frequency", "account_usage", "financial_behavior", "digital_footprint"],
                "Employment": ["employment", "job_tenure", "income_stability", "employer_type"],
                "Banking": ["account_history", "banking_relationship", "account_management", "overdraft_history"],
                "Exposure": ["existing_loans", "credit_utilization", "loan_purpose", "collateral_value"],
                "Geographic": ["location_risk", "social_indicators", "regional_factors", "demographic_data"]
            }
            
            for group_name, group_vars in category_groups.items():
                group_items = [(var, weight) for var, weight in sorted_icsm if var in group_vars]
                if group_items:
                    with st.expander(f"{group_name} ({len(group_items)} variables)"):
                        for var, weight in group_items:
                            percentage = weight * 100 if weight < 1 else weight
                            st.write(f"• **{var.replace('_', ' ').title()}** ({percentage:.1f}%)")
            
            # Show unmapped variables
            all_mapped = set()
            for group_vars in category_groups.values():
                all_mapped.update(group_vars)
            
            unmapped = [(var, weight) for var, weight in sorted_icsm if var not in all_mapped]
            if unmapped:
                with st.expander(f"Other Variables ({len(unmapped)} variables)"):
                    for var, weight in unmapped:
                        percentage = weight * 100 if weight < 1 else weight
                        st.write(f"• **{var.replace('_', ' ').title()}** ({percentage:.1f}%)")
        else:
            st.info("No ICSM variables found")

def render_icsm_category_structure(calibrator, icsm_weights):
    """Render ICSM with exact same category structure as Dynamic Scorecard"""
    
    st.markdown("""
    <div style="text-align: center; padding: 20px;">
        <h2>🎯 Institution-Calibrated Scoring Model (ICSM)</h2>
        <p style="color: #666;">Your institution's default scoring metrics - scientifically calibrated based on your business profile</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get category structure from calibrator
    categories = [
        {"name": "Core Credit Variables", "icon": "📊", "target": 35.0, "color": "#e74c3c"},
        {"name": "Behavioral Analytics", "icon": "🧠", "target": 20.0, "color": "#9b59b6"},
        {"name": "Employment Stability", "icon": "💼", "target": 15.0, "color": "#8b4513"},
        {"name": "Banking Behavior", "icon": "🏦", "target": 10.0, "color": "#3498db"},
        {"name": "Exposure & Intent", "icon": "💰", "target": 12.0, "color": "#e67e22"},
        {"name": "Geographic & Social", "icon": "🌍", "target": 8.0, "color": "#27ae60"}
    ]
    
    st.markdown("### Current Categories")
    
    # Calculate category totals from ICSM weights
    category_totals = {}
    for category_info in categories:
        category_name = category_info["name"]
        if category_name in calibrator.category_mapping:
            total_weight = 0.0
            for var in calibrator.category_mapping[category_name]["icsm_contributors"]:
                total_weight += icsm_weights.get(var, 0.0)
            category_totals[category_name] = total_weight * 100  # Convert to percentage
    
    # Render each category with expandable sections (identical to Category Management)
    for category_info in categories:
        category_name = category_info["name"]
        icon = category_info["icon"]
        target_weight = category_info["target"]
        actual_weight = category_totals.get(category_name, 0.0)
        
        # Create expandable section identical to Category Management
        with st.expander(f"{icon} {category_name} ({actual_weight:.1f}%)", expanded=False):
            
            # Show category details
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Target Weight:** {target_weight}%")
                st.write(f"**Current Weight:** {actual_weight:.1f}%")
                
                # Weight status indicator
                weight_diff = actual_weight - target_weight
                if abs(weight_diff) < 1.0:
                    st.success("✅ Weight on target")
                elif weight_diff > 0:
                    st.warning(f"⚠️ {weight_diff:.1f}% over target")
                else:
                    st.warning(f"⚠️ {abs(weight_diff):.1f}% under target")
            
            with col2:
                # Show contributing ICSM variables
                if category_name in calibrator.category_mapping:
                    icsm_contributors = calibrator.category_mapping[category_name]["icsm_contributors"]
                    primary_drivers = calibrator.category_mapping[category_name]["primary_drivers"]
                    
                    st.write(f"**ICSM Variables:** {len(icsm_contributors)}")
                    st.write(f"**Primary Drivers:** {len(primary_drivers)}")
            
            # Show individual ICSM variables in this category
            if category_name in calibrator.category_mapping:
                st.markdown("#### ICSM Variables in this Category")
                
                icsm_contributors = calibrator.category_mapping[category_name]["icsm_contributors"]
                primary_drivers = calibrator.category_mapping[category_name]["primary_drivers"]
                
                # Sort by weight (descending)
                category_vars = []
                for var in icsm_contributors:
                    if var in icsm_weights:
                        category_vars.append((var, icsm_weights[var]))
                
                category_vars.sort(key=lambda x: x[1], reverse=True)
                
                # Display variables with progress bars (like ICSM interface)
                for var_name, var_weight in category_vars:
                    var_percentage = var_weight * 100
                    
                    # Determine if primary driver
                    is_primary = var_name in primary_drivers
                    priority_label = "High" if is_primary else "Medium" if var_percentage > 5 else "Low"
                    priority_color = "#e74c3c" if is_primary else "#f39c12" if var_percentage > 5 else "#27ae60"
                    
                    # Create variable display identical to ICSM
                    var_col1, var_col2, var_col3 = st.columns([3, 2, 1])
                    
                    with var_col1:
                        st.write(f"**{var_name.replace('_', ' ').title()}**")
                    
                    with var_col2:
                        # Progress bar
                        progress_width = min(var_percentage * 4, 100)  # Scale for display
                        st.markdown(f"""
                        <div style="background-color: #f0f0f0; border-radius: 10px; height: 20px; margin: 5px 0;">
                            <div style="background-color: #3498db; height: 100%; width: {progress_width}%; border-radius: 10px; text-align: center; line-height: 20px; color: white; font-size: 12px;">
                                {var_percentage:.1f}%
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with var_col3:
                        st.markdown(f"<span style='color: {priority_color}'>● {priority_label}</span>", unsafe_allow_html=True)
                
                # Credit expertise note
                st.info(f"**Credit Expertise:** {calibrator.category_mapping[category_name]['credit_expertise']}")
    
    # Weight Distribution Summary (identical to ICSM)
    st.divider()
    st.markdown("### Weight Distribution Summary")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        core_weight = category_totals.get("Core Credit Variables", 0) + category_totals.get("Employment Stability", 0)
        st.metric("Core Variables", f"{core_weight:.1f}%", "Primary risk factors")
    
    with col2:
        behavioral_weight = category_totals.get("Behavioral Analytics", 0) + category_totals.get("Banking Behavior", 0)
        st.metric("Behavioral Data", f"{behavioral_weight:.1f}%", "Enhanced insights")
    
    with col3:
        total_weight = sum(category_totals.values())
        st.metric("Total Weight", f"{total_weight:.1f}%", "Should equal 100%")

def render_icsm_sync_controls(manager, calibrator):
    """Render synchronization controls"""
    
    st.markdown("## 🔄 ICSM Synchronization Controls")
    
    # Status overview
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Category Management Status")
        categories = manager.get_categories()
        variables = manager.get_active_variables()
        
        if categories and variables:
            for cat in categories:
                cat_vars = [v for v in variables if v['category'] == cat['category_name']]
                cat_weight = sum(v['weight'] for v in cat_vars)
                st.metric(f"{cat['category_name']}", f"{cat_weight:.1f}%", f"Target: {cat['total_weight']:.1f}%")
        else:
            st.warning("No categories configured in Dynamic Scorecard")
    
    with col2:
        st.markdown("### 🎯 ICSM Current Status")
        try:
            import json
            import os
            if os.path.exists("scoring_weights.json"):
                with open("scoring_weights.json", "r") as f:
                    icsm_weights = json.load(f)
                
                st.success(f"ICSM has {len(icsm_weights)} variables")
                total_icsm_weight = sum(icsm_weights.values())
                st.metric("Total ICSM Weight", f"{total_icsm_weight:.3f}", "Should be 1.000")
            else:
                st.error("ICSM weights file not found")
        except Exception as e:
            st.error(f"Error reading ICSM: {e}")
    
    st.divider()
    
    # Synchronization buttons
    st.markdown("### Synchronization Actions")
    
    sync_col1, sync_col2, sync_col3 = st.columns(3)
    
    with sync_col1:
        if st.button("📥 Import from ICSM", help="Import ICSM weights into Category Management", use_container_width=True):
            with st.spinner("Importing ICSM weights..."):
                if sync_weights_from_icsm():
                    st.success("Successfully imported from ICSM!")
                    st.rerun()
                else:
                    st.error("Failed to import from ICSM")
    
    with sync_col2:
        if st.button("📤 Export to ICSM", help="Export Category Management to ICSM", use_container_width=True):
            with st.spinner("Exporting to ICSM..."):
                if sync_weights_to_icsm():
                    st.success("Successfully exported to ICSM!")
                    st.rerun()
                else:
                    st.error("Failed to export to ICSM")
    
    with sync_col3:
        if st.button("🧪 Test ICSM", help="Test ICSM scoring", use_container_width=True):
            st.session_state.show_icsm_test = True
    
    # ICSM Testing
    if st.session_state.get('show_icsm_test', False):
        st.divider()
        st.markdown("### 🧪 ICSM Scoring Test")
        
        with st.expander("Test Application Data", expanded=True):
            test_col1, test_col2 = st.columns(2)
            
            with test_col1:
                credit_score = st.number_input("Credit Score", 300, 900, 720)
                monthly_income = st.number_input("Monthly Income", 10000, 200000, 50000)
                foir = st.slider("FOIR", 0.0, 1.0, 0.4, 0.01)
            
            with test_col2:
                dpd30plus = st.number_input("DPD 30+", 0, 50, 2)
                enquiry_count = st.number_input("Enquiry Count", 0, 30, 5)
            
            if st.button("Calculate ICSM Score", type="primary"):
                try:
                    with open("scoring_weights.json", "r") as f:
                        icsm_weights = json.load(f)
                    
                    test_data = {
                        'credit_score': credit_score,
                        'monthly_income': monthly_income,
                        'foir': foir,
                        'dpd30plus': dpd30plus,
                        'enquiry_count': enquiry_count
                    }
                    
                    result = calibrator.calculate_icsm_score(test_data, icsm_weights)
                    
                    # Display results
                    result_col1, result_col2, result_col3 = st.columns(3)
                    
                    with result_col1:
                        st.metric("Final Score", f"{result['final_score']:.1f}%")
                    
                    with result_col2:
                        st.metric("Risk Bucket", result['risk_bucket'])
                    
                    with result_col3:
                        st.metric("Decision", result['decision'])
                    
                    # Detailed breakdown
                    st.markdown("#### Score Breakdown")
                    for var, details in result['score_components'].items():
                        st.write(f"**{var}**: {details['weighted_score']:.2f} points (Weight: {details['weight']*100:.1f}%)")
                
                except Exception as e:
                    st.error(f"Error calculating score: {e}")

if __name__ == "__main__":
    main()