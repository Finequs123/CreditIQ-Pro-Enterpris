"""
Modular Scoring Engine for CreditIQ Pro
Supports diverse DSA needs with modular scoring logic per variable,
fixed-weight fallback scoring, and flexible template mapping
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Callable
import json

class ModularScoringEngine:
    """Enhanced scoring engine with modular variable scoring functions"""
    
    def __init__(self):
        self.scoring_registry = self._initialize_scoring_registry()
        self.fallback_scores = self._initialize_fallback_scores()
        self.field_mappings = {}  # Store DSA-specific field mappings
    
    def _initialize_scoring_registry(self) -> Dict[str, Dict[str, Any]]:
        """Initialize the scoring registry with functions and weights"""
        return {
            # Core Credit Variables
            "credit_score": {"func": self.score_credit_score, "weight": 11},
            "foir": {"func": self.score_foir, "weight": 7},
            "dpd30plus": {"func": self.score_dpd30plus, "weight": 7},
            "enquiry_count": {"func": self.score_enquiry_count, "weight": 6},
            "monthly_income": {"func": self.score_monthly_income, "weight": 7},
            
            # Behavioral Analytics
            "credit_vintage": {"func": self.score_credit_vintage, "weight": 3},
            "loan_mix_type": {"func": self.score_loan_mix_type, "weight": 2},
            "loan_completion_ratio": {"func": self.score_loan_completion_ratio, "weight": 3},
            "defaulted_loans": {"func": self.score_defaulted_loans, "weight": 7},
            
            # Employment Stability
            "job_type": {"func": self.score_job_type, "weight": 2},
            "employment_tenure": {"func": self.score_employment_tenure, "weight": 4},
            "company_stability": {"func": self.score_company_stability, "weight": 1},
            
            # Banking Behavior
            "account_vintage": {"func": self.score_account_vintage, "weight": 3},
            "avg_monthly_balance": {"func": self.score_avg_monthly_balance, "weight": 6},
            "bounce_frequency": {"func": self.score_bounce_frequency, "weight": 4},
            
            # Geographic & Social
            "geographic_risk": {"func": self.score_geographic_risk, "weight": 1},
            "mobile_number_vintage": {"func": self.score_mobile_vintage, "weight": 3},
            "digital_engagement": {"func": self.score_digital_engagement, "weight": 3},
            
            # Exposure & Intent
            "unsecured_loan_amount": {"func": self.score_unsecured_loan_amount, "weight": 7},
            "outstanding_amount_percent": {"func": self.score_outstanding_amount_percent, "weight": 7},
            "our_lender_exposure": {"func": self.score_our_lender_exposure, "weight": 7},
            "channel_type": {"func": self.score_channel_type, "weight": 1}
        }
    
    def _initialize_fallback_scores(self) -> Dict[str, float]:
        """Initialize fallback scores for missing fields"""
        return {
            "credit_score": 0.3,
            "foir": 0.5,
            "dpd30plus": 0.8,  # Assume good if missing
            "enquiry_count": 0.7,  # Assume moderate if missing
            "monthly_income": 0.0,  # Critical field
            "credit_vintage": 0.5,
            "loan_mix_type": 0.5,
            "loan_completion_ratio": 0.5,
            "defaulted_loans": 0.8,  # Assume good if missing
            "job_type": 0.5,
            "employment_tenure": 0.5,
            "company_stability": 0.5,
            "account_vintage": 0.5,
            "avg_monthly_balance": 0.5,
            "bounce_frequency": 0.7,  # Assume good if missing
            "geographic_risk": 0.7,
            "mobile_number_vintage": 0.5,
            "digital_engagement": 0.5,
            "unsecured_loan_amount": 0.5,
            "outstanding_amount_percent": 0.5,
            "our_lender_exposure": 0.7,
            "channel_type": 0.5
        }
    
    # Individual scoring functions for each variable
    def score_credit_score(self, value: Any) -> float:
        """Score credit score variable"""
        if value is None or pd.isna(value):
            return 0.0
        try:
            score = float(value)
            if score >= 750: return 1.0
            elif score >= 700: return 0.8
            elif score >= 650: return 0.6
            elif score >= 600: return 0.4
            elif score >= 550: return 0.2
            else: return 0.0
        except (ValueError, TypeError):
            return 0.0
    
    def score_foir(self, value: Any) -> float:
        """Score Fixed Obligation to Income Ratio"""
        if value is None or pd.isna(value):
            return 0.0
        try:
            foir = float(value)
            if foir <= 30: return 1.0
            elif foir <= 40: return 0.8
            elif foir <= 50: return 0.6
            elif foir <= 60: return 0.4
            elif foir <= 70: return 0.2
            else: return 0.0
        except (ValueError, TypeError):
            return 0.0
    
    def score_dpd30plus(self, value: Any) -> float:
        """Score Days Past Due 30+ variable"""
        if value is None or pd.isna(value):
            return 0.0
        try:
            dpd = int(value)
            if dpd == 0: return 1.0
            elif dpd == 1: return 0.6
            elif dpd == 2: return 0.3
            else: return 0.0
        except (ValueError, TypeError):
            return 0.0
    
    def score_enquiry_count(self, value: Any) -> float:
        """Score credit enquiry count"""
        if value is None or pd.isna(value):
            return 0.0
        try:
            enquiries = int(value)
            if enquiries <= 2: return 1.0
            elif enquiries <= 4: return 0.8
            elif enquiries <= 6: return 0.6
            elif enquiries <= 8: return 0.4
            elif enquiries <= 10: return 0.2
            else: return 0.0
        except (ValueError, TypeError):
            return 0.0
    
    def score_monthly_income(self, value: Any) -> float:
        """Score monthly income"""
        if value is None or pd.isna(value):
            return 0.0
        try:
            income = float(value)
            if income >= 100000: return 1.0
            elif income >= 75000: return 0.8
            elif income >= 50000: return 0.6
            elif income >= 30000: return 0.4
            elif income >= 15000: return 0.2
            else: return 0.0
        except (ValueError, TypeError):
            return 0.0
    
    def score_credit_vintage(self, value: Any) -> float:
        """Score credit vintage in months"""
        if value is None or pd.isna(value):
            return 0.0
        try:
            vintage = int(value)
            if vintage >= 60: return 1.0
            elif vintage >= 36: return 0.8
            elif vintage >= 24: return 0.6
            elif vintage >= 12: return 0.4
            else: return 0.2
        except (ValueError, TypeError):
            return 0.0
    
    def score_loan_mix_type(self, value: Any) -> float:
        """Score loan mix type"""
        if value is None or pd.isna(value):
            return 0.0
        
        mix_type = str(value).lower().strip()
        if mix_type in ['secured_only', 'mixed_balanced']:
            return 1.0
        elif mix_type in ['mixed_secured_heavy', 'secured_dominant']:
            return 0.8
        elif mix_type in ['mixed_unsecured_heavy', 'balanced']:
            return 0.6
        elif mix_type in ['unsecured_only', 'unsecured_dominant']:
            return 0.4
        else:
            return 0.2
    
    def score_loan_completion_ratio(self, value: Any) -> float:
        """Score loan completion ratio"""
        if value is None or pd.isna(value):
            return 0.0
        try:
            ratio = float(value)
            if ratio >= 0.9: return 1.0
            elif ratio >= 0.8: return 0.8
            elif ratio >= 0.7: return 0.6
            elif ratio >= 0.6: return 0.4
            elif ratio >= 0.5: return 0.2
            else: return 0.0
        except (ValueError, TypeError):
            return 0.0
    
    def score_defaulted_loans(self, value: Any) -> float:
        """Score defaulted loans count"""
        if value is None or pd.isna(value):
            return 0.0
        try:
            defaults = int(value)
            if defaults == 0: return 1.0
            else: return 0.0  # Any default is critical
        except (ValueError, TypeError):
            return 0.0
    
    def score_job_type(self, value: Any) -> float:
        """Score job type stability"""
        if value is None or pd.isna(value):
            return 0.0
        
        job_type = str(value).lower().strip()
        if job_type in ['government', 'psu', 'mnc']:
            return 1.0
        elif job_type in ['large_corporate', 'established_company']:
            return 0.8
        elif job_type in ['mid_size_company', 'stable_private']:
            return 0.6
        elif job_type in ['small_company', 'startup']:
            return 0.4
        elif job_type in ['self_employed', 'freelance']:
            return 0.2
        else:
            return 0.3
    
    def score_employment_tenure(self, value: Any) -> float:
        """Score employment tenure in months"""
        if value is None or pd.isna(value):
            return 0.0
        try:
            tenure = int(value)
            if tenure >= 60: return 1.0
            elif tenure >= 36: return 0.8
            elif tenure >= 24: return 0.6
            elif tenure >= 12: return 0.4
            elif tenure >= 6: return 0.2
            else: return 0.0
        except (ValueError, TypeError):
            return 0.0
    
    def score_company_stability(self, value: Any) -> float:
        """Score company stability"""
        if value is None or pd.isna(value):
            return 0.0
        
        stability = str(value).lower().strip()
        if stability in ['excellent', 'very_stable']:
            return 1.0
        elif stability in ['good', 'stable']:
            return 0.8
        elif stability in ['average', 'moderate']:
            return 0.6
        elif stability in ['below_average', 'unstable']:
            return 0.4
        elif stability in ['poor', 'very_unstable']:
            return 0.2
        else:
            return 0.5
    
    def score_account_vintage(self, value: Any) -> float:
        """Score bank account vintage in months"""
        if value is None or pd.isna(value):
            return 0.0
        try:
            vintage = int(value)
            if vintage >= 60: return 1.0
            elif vintage >= 36: return 0.8
            elif vintage >= 24: return 0.6
            elif vintage >= 12: return 0.4
            else: return 0.2
        except (ValueError, TypeError):
            return 0.0
    
    def score_avg_monthly_balance(self, value: Any) -> float:
        """Score average monthly balance"""
        if value is None or pd.isna(value):
            return 0.0
        try:
            balance = float(value)
            if balance >= 100000: return 1.0
            elif balance >= 50000: return 0.8
            elif balance >= 25000: return 0.6
            elif balance >= 10000: return 0.4
            elif balance >= 5000: return 0.2
            else: return 0.0
        except (ValueError, TypeError):
            return 0.0
    
    def score_bounce_frequency(self, value: Any) -> float:
        """Score bounce frequency (lower is better)"""
        if value is None or pd.isna(value):
            return 0.0
        try:
            bounces = int(value)
            if bounces == 0: return 1.0
            elif bounces <= 2: return 0.8
            elif bounces <= 4: return 0.6
            elif bounces <= 6: return 0.4
            elif bounces <= 8: return 0.2
            else: return 0.0
        except (ValueError, TypeError):
            return 0.0
    
    def score_geographic_risk(self, value: Any) -> float:
        """Score geographic risk"""
        if value is None or pd.isna(value):
            return 0.0
        
        risk_level = str(value).lower().strip()
        if risk_level in ['low', 'very_low']:
            return 1.0
        elif risk_level in ['moderate_low', 'below_average']:
            return 0.8
        elif risk_level in ['moderate', 'average']:
            return 0.6
        elif risk_level in ['moderate_high', 'above_average']:
            return 0.4
        elif risk_level in ['high', 'very_high']:
            return 0.2
        else:
            return 0.5
    
    def score_mobile_vintage(self, value: Any) -> float:
        """Score mobile number vintage in months"""
        if value is None or pd.isna(value):
            return 0.0
        try:
            vintage = int(value)
            if vintage >= 60: return 1.0
            elif vintage >= 36: return 0.8
            elif vintage >= 24: return 0.6
            elif vintage >= 12: return 0.4
            else: return 0.2
        except (ValueError, TypeError):
            return 0.0
    
    def score_digital_engagement(self, value: Any) -> float:
        """Score digital engagement level"""
        if value is None or pd.isna(value):
            return 0.0
        try:
            engagement = float(value)
            if engagement >= 80: return 1.0
            elif engagement >= 60: return 0.8
            elif engagement >= 40: return 0.6
            elif engagement >= 20: return 0.4
            else: return 0.2
        except (ValueError, TypeError):
            return 0.0
    
    def score_unsecured_loan_amount(self, value: Any) -> float:
        """Score unsecured loan amount"""
        if value is None or pd.isna(value):
            return 0.0
        try:
            amount = float(value)
            if amount == 0: return 1.0
            elif amount <= 100000: return 0.8
            elif amount <= 300000: return 0.6
            elif amount <= 500000: return 0.4
            elif amount <= 1000000: return 0.2
            else: return 0.0
        except (ValueError, TypeError):
            return 0.0
    
    def score_outstanding_amount_percent(self, value: Any) -> float:
        """Score outstanding amount percentage"""
        if value is None or pd.isna(value):
            return 0.0
        try:
            percent = float(value)
            if percent <= 20: return 1.0
            elif percent <= 40: return 0.8
            elif percent <= 60: return 0.6
            elif percent <= 80: return 0.4
            elif percent <= 90: return 0.2
            else: return 0.0
        except (ValueError, TypeError):
            return 0.0
    
    def score_our_lender_exposure(self, value: Any) -> float:
        """Score exposure with our lender"""
        if value is None or pd.isna(value):
            return 0.0
        try:
            exposure = float(value)
            if exposure == 0: return 1.0
            elif exposure <= 50000: return 0.8
            elif exposure <= 100000: return 0.6
            elif exposure <= 200000: return 0.4
            elif exposure <= 500000: return 0.2
            else: return 0.0
        except (ValueError, TypeError):
            return 0.0
    
    def score_channel_type(self, value: Any) -> float:
        """Score channel type"""
        if value is None or pd.isna(value):
            return 0.0
        
        channel = str(value).lower().strip()
        if channel in ['direct', 'branch']:
            return 1.0
        elif channel in ['partner', 'dsa']:
            return 0.8
        elif channel in ['online', 'digital']:
            return 0.6
        elif channel in ['referral', 'agent']:
            return 0.4
        else:
            return 0.5
    
    def set_field_mapping(self, dsa_id: str, mapping: Dict[str, str]):
        """Set field mapping for a specific DSA"""
        self.field_mappings[dsa_id] = mapping
    
    def apply_field_mapping(self, df: pd.DataFrame, dsa_id: Optional[str]) -> pd.DataFrame:
        """Apply field mapping to transform DSA CSV format"""
        if dsa_id and dsa_id in self.field_mappings:
            mapping = self.field_mappings[dsa_id]
            df_mapped = df.rename(columns=mapping)
            return df_mapped
        return df
    
    def score_application_modular(self, applicant_data: Dict[str, Any], dsa_id: Optional[str] = None) -> Dict[str, Any]:
        """Score application using modular approach with transparent reasoning"""
        
        total_score = 0.0
        total_weight = 0
        variable_details = {}
        
        for var_name, config in self.scoring_registry.items():
            score_func = config["func"]
            weight = config["weight"]
            
            # Get value from applicant data
            value = applicant_data.get(var_name)
            
            if value is None or pd.isna(value):
                # Use fallback score
                score = self.fallback_scores.get(var_name, 0.0)
                reason = "Fallback applied"
            else:
                # Calculate actual score
                score = score_func(value)
                reason = "Scored"
            
            # Store detailed information
            variable_details[var_name] = {
                "value": value,
                "score": score,
                "weight": weight,
                "weighted_score": score * weight,
                "reason": reason
            }
            
            total_score += score * weight
            total_weight += weight
        
        # Calculate final score as percentage
        final_score = round((total_score / total_weight) * 100, 2) if total_weight > 0 else 0.0
        
        # Determine risk bucket
        if final_score >= 80:
            bucket = "A"
            decision = "Approve"
        elif final_score >= 65:
            bucket = "B" 
            decision = "Conditional Approve"
        elif final_score >= 50:
            bucket = "C"
            decision = "Review Required"
        else:
            bucket = "D"
            decision = "Decline"
        
        return {
            "final_score": final_score,
            "bucket": bucket,
            "decision": decision,
            "variable_details": variable_details,
            "total_weight": total_weight,
            "scoring_method": "modular"
        }
    
    def process_bulk_applications_modular(self, df: pd.DataFrame, dsa_id: Optional[str] = None) -> pd.DataFrame:
        """Process bulk applications using modular scoring"""
        
        # Apply field mapping if provided
        if dsa_id:
            df = self.apply_field_mapping(df, dsa_id)
        
        results = []
        
        for idx, row in df.iterrows():
            # Convert row to dictionary
            applicant_data = row.to_dict()
            
            # Score the application
            result = self.score_application_modular(applicant_data, dsa_id)
            
            # Create result row
            result_row = {
                "application_id": str(int(idx) + 1),
                "final_score": result["final_score"],
                "bucket": result["bucket"],
                "decision": result["decision"],
                "scoring_method": result["scoring_method"]
            }
            
            # Add individual variable scores and reasons
            for var_name, details in result["variable_details"].items():
                result_row[f"{var_name}_score"] = details["score"]
                result_row[f"{var_name}_reason"] = details["reason"]
                result_row[f"{var_name}_value"] = details["value"]
            
            results.append(result_row)
        
        return pd.DataFrame(results)
    
    def get_scoring_configuration(self) -> Dict[str, Any]:
        """Get current scoring configuration for display"""
        config = {
            "total_variables": len(self.scoring_registry),
            "total_weight": sum(config["weight"] for config in self.scoring_registry.values()),
            "variables": {}
        }
        
        for var_name, var_config in self.scoring_registry.items():
            config["variables"][var_name] = {
                "weight": var_config["weight"],
                "fallback_score": self.fallback_scores.get(var_name, 0.0),
                "function_name": var_config["func"].__name__
            }
        
        return config