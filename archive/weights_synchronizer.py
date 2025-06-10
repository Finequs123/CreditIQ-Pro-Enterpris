"""
Weights Synchronizer - Links Scoring Weights Configuration with Dynamic Configuration
Ensures both systems share the same weight data and stay synchronized
"""
import json
import sqlite3
from typing import Dict, List, Any, Optional
import streamlit as st

class WeightsSynchronizer:
    """Synchronizes weights between different configuration systems"""
    
    def __init__(self, 
                 scorecard_db_path: str = "scorecard_config.db",
                 weights_json_path: str = "scoring_weights.json"):
        self.scorecard_db_path = scorecard_db_path
        self.weights_json_path = weights_json_path
        
    def get_unified_weights(self) -> Dict[str, float]:
        """Get weights from the most authoritative source (Dynamic Configuration first, then JSON)"""
        # Try Dynamic Configuration database first
        try:
            dynamic_weights = self._get_weights_from_dynamic_config()
            if dynamic_weights:
                return dynamic_weights
        except Exception:
            pass
            
        # Fall back to JSON file
        try:
            with open(self.weights_json_path, "r") as f:
                return json.load(f)
        except Exception:
            pass
            
        # Return scientific defaults if nothing found
        return self._get_scientific_defaults()
    
    def _get_weights_from_dynamic_config(self) -> Dict[str, float]:
        """Extract weights from Dynamic Configuration database"""
        conn = sqlite3.connect(self.scorecard_db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT variable_id, weight 
            FROM scorecard_variables 
            WHERE is_active = 1
        """)
        
        results = cursor.fetchall()
        conn.close()
        
        if not results:
            return {}
            
        # Convert to the format expected by scoring system
        weights = {}
        variable_mapping = self._get_variable_mapping()
        
        for variable_id, weight in results:
            # Convert dynamic config variable names to scoring system names
            scoring_key = variable_mapping.get(variable_id, variable_id)
            weights[scoring_key] = float(weight) / 100.0  # Convert percentage to decimal
            
        return weights
    
    def _get_variable_mapping(self) -> Dict[str, str]:
        """Map Dynamic Configuration variable names to Scoring System variable names"""
        # Both systems now use identical variable names - direct 1:1 mapping
        return {
            "credit_score": "credit_score",
            "foir": "foir", 
            "dpd30plus": "dpd30plus",
            "enquiry_count": "enquiry_count",
            "monthly_income": "monthly_income",
            "age": "age",
            "credit_vintage": "credit_vintage",
            "loan_mix_type": "loan_mix_type",
            "loan_completion_ratio": "loan_completion_ratio",
            "defaulted_loans": "defaulted_loans",
            "job_type": "job_type",
            "employment_tenure": "employment_tenure",
            "company_stability": "company_stability",
            "account_vintage": "account_vintage",
            "avg_monthly_balance": "avg_monthly_balance",
            "bounce_frequency": "bounce_frequency",
            "geographic_risk": "geographic_risk",
            "mobile_number_vintage": "mobile_number_vintage",
            "digital_engagement": "digital_engagement",
            "unsecured_loan_amount": "unsecured_loan_amount",
            "outstanding_amount_percent": "outstanding_amount_percent",
            "our_lender_exposure": "our_lender_exposure",
            "channel_type": "channel_type"
        }
    
    def save_weights_to_all_systems(self, weights: Dict[str, float]) -> bool:
        """Save weights to both JSON file and Dynamic Configuration database"""
        success = True
        
        # Save to JSON file (for backward compatibility)
        try:
            with open(self.weights_json_path, "w") as f:
                json.dump(weights, f, indent=2)
        except Exception as e:
            print(f"Error saving to JSON: {e}")
            success = False
        
        # Save to Dynamic Configuration database
        try:
            self._save_weights_to_dynamic_config(weights)
        except Exception as e:
            print(f"Error saving to Dynamic Config: {e}")
            success = False
            
        return success
    
    def _save_weights_to_dynamic_config(self, weights: Dict[str, float]):
        """Save weights to Dynamic Configuration database"""
        conn = sqlite3.connect(self.scorecard_db_path)
        cursor = conn.cursor()
        
        # Reverse mapping: scoring system names to dynamic config names
        reverse_mapping = {v: k for k, v in self._get_variable_mapping().items()}
        
        for scoring_key, weight in weights.items():
            dynamic_key = reverse_mapping.get(scoring_key, scoring_key)
            weight_percentage = float(weight) * 100.0  # Convert decimal to percentage
            
            cursor.execute("""
                UPDATE scorecard_variables 
                SET weight = ?, updated_at = datetime('now')
                WHERE variable_id = ?
            """, (weight_percentage, dynamic_key))
        
        conn.commit()
        conn.close()
    
    def sync_from_dynamic_to_sliders(self):
        """Sync weights from Dynamic Configuration to Sliders system"""
        dynamic_weights = self._get_weights_from_dynamic_config()
        if dynamic_weights:
            with open(self.weights_json_path, "w") as f:
                json.dump(dynamic_weights, f, indent=2)
            return True
        return False
    
    def sync_from_sliders_to_dynamic(self):
        """Sync weights from Sliders system to Dynamic Configuration"""
        try:
            with open(self.weights_json_path, "r") as f:
                slider_weights = json.load(f)
            self._save_weights_to_dynamic_config(slider_weights)
            return True
        except Exception:
            return False
    
    def _get_scientific_defaults(self) -> Dict[str, float]:
        """Get scientifically optimized default weights"""
        return {
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

def get_synchronized_weights() -> Dict[str, float]:
    """Get unified weights from synchronized systems"""
    synchronizer = WeightsSynchronizer()
    return synchronizer.get_unified_weights()

def save_synchronized_weights(weights: Dict[str, float]) -> bool:
    """Save weights to all synchronized systems"""
    synchronizer = WeightsSynchronizer()
    return synchronizer.save_weights_to_all_systems(weights)