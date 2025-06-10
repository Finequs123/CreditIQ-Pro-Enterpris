"""
Additional Data Sources Scoring Module
Dynamically extends scoring based on company's selected additional data sources
"""

import json
import sqlite3
from typing import Dict, List, Any, Optional

class AdditionalDataScoring:
    """Handles dynamic scorecard expansion based on additional data sources"""
    
    def __init__(self, db_path: str = "user_management.db"):
        self.db_path = db_path
        self.additional_variables = self._define_additional_variables()
    
    def _define_additional_variables(self) -> Dict[str, Dict]:
        """Define comprehensive variables for each additional data source"""
        return {
            "ITR Data": {
                "variables": {
                    "annual_income_itr": {
                        "name": "Annual Income (ITR)",
                        "weight": 8.0,
                        "type": "numeric",
                        "min_value": 0,
                        "max_value": 10000000,
                        "scoring_bands": [
                            {"min": 0, "max": 300000, "score": 20},
                            {"min": 300001, "max": 600000, "score": 40},
                            {"min": 600001, "max": 1200000, "score": 60},
                            {"min": 1200001, "max": 2400000, "score": 80},
                            {"min": 2400001, "max": 999999999, "score": 100}
                        ]
                    },
                    "income_consistency": {
                        "name": "Income Consistency (3-year)",
                        "weight": 6.0,
                        "type": "numeric",
                        "min_value": 0,
                        "max_value": 100,
                        "scoring_bands": [
                            {"min": 0, "max": 20, "score": 20},
                            {"min": 21, "max": 40, "score": 40},
                            {"min": 41, "max": 60, "score": 60},
                            {"min": 61, "max": 80, "score": 80},
                            {"min": 81, "max": 100, "score": 100}
                        ]
                    },
                    "tax_payment_regularity": {
                        "name": "Tax Payment Regularity",
                        "weight": 5.0,
                        "type": "categorical",
                        "options": ["Always On Time", "Mostly On Time", "Occasional Delays", "Frequent Delays", "Poor"],
                        "scoring_map": {
                            "Always On Time": 100,
                            "Mostly On Time": 80,
                            "Occasional Delays": 60,
                            "Frequent Delays": 40,
                            "Poor": 20
                        }
                    },
                    "income_growth_rate": {
                        "name": "Income Growth Rate (%)",
                        "weight": 4.0,
                        "type": "numeric",
                        "min_value": -50,
                        "max_value": 200,
                        "scoring_bands": [
                            {"min": -50, "max": -10, "score": 20},
                            {"min": -9, "max": 0, "score": 40},
                            {"min": 1, "max": 10, "score": 60},
                            {"min": 11, "max": 25, "score": 80},
                            {"min": 26, "max": 200, "score": 100}
                        ]
                    },
                    "tax_compliance_score": {
                        "name": "Tax Compliance Score",
                        "weight": 5.0,
                        "type": "numeric",
                        "min_value": 0,
                        "max_value": 100,
                        "scoring_bands": [
                            {"min": 0, "max": 40, "score": 20},
                            {"min": 41, "max": 60, "score": 40},
                            {"min": 61, "max": 75, "score": 60},
                            {"min": 76, "max": 90, "score": 80},
                            {"min": 91, "max": 100, "score": 100}
                        ]
                    },
                    "declared_assets_value": {
                        "name": "Declared Assets Value",
                        "weight": 4.0,
                        "type": "numeric",
                        "min_value": 0,
                        "max_value": 50000000,
                        "scoring_bands": [
                            {"min": 0, "max": 500000, "score": 20},
                            {"min": 500001, "max": 1500000, "score": 40},
                            {"min": 1500001, "max": 3000000, "score": 60},
                            {"min": 3000001, "max": 7500000, "score": 80},
                            {"min": 7500001, "max": 50000000, "score": 100}
                        ]
                    }
                },
                "total_weight": 32.0
            },
            
            "GST Data": {
                "variables": {
                    "monthly_gst_turnover": {
                        "name": "Monthly GST Turnover",
                        "weight": 8.0,
                        "type": "numeric",
                        "min_value": 0,
                        "max_value": 10000000,
                        "scoring_bands": [
                            {"min": 0, "max": 200000, "score": 20},
                            {"min": 200001, "max": 500000, "score": 40},
                            {"min": 500001, "max": 1000000, "score": 60},
                            {"min": 1000001, "max": 2500000, "score": 80},
                            {"min": 2500001, "max": 10000000, "score": 100}
                        ]
                    },
                    "gst_payment_consistency": {
                        "name": "GST Payment Consistency",
                        "weight": 6.0,
                        "type": "numeric",
                        "min_value": 0,
                        "max_value": 100,
                        "scoring_bands": [
                            {"min": 0, "max": 60, "score": 20},
                            {"min": 61, "max": 70, "score": 40},
                            {"min": 71, "max": 80, "score": 60},
                            {"min": 81, "max": 90, "score": 80},
                            {"min": 91, "max": 100, "score": 100}
                        ]
                    },
                    "business_stability_score": {
                        "name": "Business Stability Score",
                        "weight": 5.0,
                        "type": "numeric",
                        "min_value": 0,
                        "max_value": 100,
                        "scoring_bands": [
                            {"min": 0, "max": 40, "score": 20},
                            {"min": 41, "max": 60, "score": 40},
                            {"min": 61, "max": 75, "score": 60},
                            {"min": 76, "max": 90, "score": 80},
                            {"min": 91, "max": 100, "score": 100}
                        ]
                    },
                    "revenue_growth_trend": {
                        "name": "Revenue Growth Trend (%)",
                        "weight": 5.0,
                        "type": "numeric",
                        "min_value": -50,
                        "max_value": 200,
                        "scoring_bands": [
                            {"min": -50, "max": -10, "score": 20},
                            {"min": -9, "max": 0, "score": 40},
                            {"min": 1, "max": 15, "score": 60},
                            {"min": 16, "max": 30, "score": 80},
                            {"min": 31, "max": 200, "score": 100}
                        ]
                    },
                    "gst_compliance_rating": {
                        "name": "GST Compliance Rating",
                        "weight": 4.0,
                        "type": "categorical",
                        "options": ["Excellent", "Good", "Average", "Below Average", "Poor"],
                        "scoring_map": {
                            "Excellent": 100,
                            "Good": 80,
                            "Average": 60,
                            "Below Average": 40,
                            "Poor": 20
                        }
                    }
                },
                "total_weight": 28.0
            },
            
            "Utility Bills": {
                "variables": {
                    "payment_consistency_score": {
                        "name": "Utility Payment Consistency",
                        "weight": 6.0,
                        "type": "numeric",
                        "min_value": 0,
                        "max_value": 100,
                        "scoring_bands": [
                            {"min": 0, "max": 60, "score": 20},
                            {"min": 61, "max": 70, "score": 40},
                            {"min": 71, "max": 80, "score": 60},
                            {"min": 81, "max": 90, "score": 80},
                            {"min": 91, "max": 100, "score": 100}
                        ]
                    },
                    "average_monthly_consumption": {
                        "name": "Average Monthly Bill Amount",
                        "weight": 4.0,
                        "type": "numeric",
                        "min_value": 0,
                        "max_value": 50000,
                        "scoring_bands": [
                            {"min": 0, "max": 2000, "score": 40},
                            {"min": 2001, "max": 5000, "score": 60},
                            {"min": 5001, "max": 10000, "score": 80},
                            {"min": 10001, "max": 20000, "score": 100},
                            {"min": 20001, "max": 50000, "score": 80}
                        ]
                    },
                    "payment_delay_frequency": {
                        "name": "Payment Delay Frequency",
                        "weight": 5.0,
                        "type": "categorical",
                        "options": ["Never", "Rarely", "Sometimes", "Often", "Always"],
                        "scoring_map": {
                            "Never": 100,
                            "Rarely": 80,
                            "Sometimes": 60,
                            "Often": 40,
                            "Always": 20
                        }
                    },
                    "address_stability": {
                        "name": "Address Stability (Months)",
                        "weight": 4.0,
                        "type": "numeric",
                        "min_value": 0,
                        "max_value": 240,
                        "scoring_bands": [
                            {"min": 0, "max": 6, "score": 20},
                            {"min": 7, "max": 12, "score": 40},
                            {"min": 13, "max": 24, "score": 60},
                            {"min": 25, "max": 60, "score": 80},
                            {"min": 61, "max": 240, "score": 100}
                        ]
                    },
                    "lifestyle_spending_indicator": {
                        "name": "Lifestyle Spending Indicator",
                        "weight": 3.0,
                        "type": "categorical",
                        "options": ["Conservative", "Moderate", "High", "Luxurious", "Extravagant"],
                        "scoring_map": {
                            "Conservative": 100,
                            "Moderate": 80,
                            "High": 60,
                            "Luxurious": 40,
                            "Extravagant": 20
                        }
                    }
                },
                "total_weight": 22.0
            },
            
            "Telecom Data": {
                "variables": {
                    "bill_payment_regularity": {
                        "name": "Telecom Payment Regularity",
                        "weight": 5.0,
                        "type": "numeric",
                        "min_value": 0,
                        "max_value": 100,
                        "scoring_bands": [
                            {"min": 0, "max": 60, "score": 20},
                            {"min": 61, "max": 70, "score": 40},
                            {"min": 71, "max": 80, "score": 60},
                            {"min": 81, "max": 90, "score": 80},
                            {"min": 91, "max": 100, "score": 100}
                        ]
                    },
                    "usage_pattern_consistency": {
                        "name": "Usage Pattern Consistency",
                        "weight": 4.0,
                        "type": "numeric",
                        "min_value": 0,
                        "max_value": 100,
                        "scoring_bands": [
                            {"min": 0, "max": 40, "score": 40},
                            {"min": 41, "max": 60, "score": 60},
                            {"min": 61, "max": 80, "score": 80},
                            {"min": 81, "max": 100, "score": 100}
                        ]
                    },
                    "location_consistency": {
                        "name": "Location Consistency Score",
                        "weight": 4.0,
                        "type": "numeric",
                        "min_value": 0,
                        "max_value": 100,
                        "scoring_bands": [
                            {"min": 0, "max": 50, "score": 40},
                            {"min": 51, "max": 70, "score": 60},
                            {"min": 71, "max": 85, "score": 80},
                            {"min": 86, "max": 100, "score": 100}
                        ]
                    },
                    "plan_stability": {
                        "name": "Plan Stability",
                        "weight": 3.0,
                        "type": "categorical",
                        "options": ["Very Stable", "Stable", "Moderate", "Frequent Changes", "Very Unstable"],
                        "scoring_map": {
                            "Very Stable": 100,
                            "Stable": 80,
                            "Moderate": 60,
                            "Frequent Changes": 40,
                            "Very Unstable": 20
                        }
                    }
                },
                "total_weight": 16.0
            },
            
            "Social Media": {
                "variables": {
                    "digital_footprint_maturity": {
                        "name": "Digital Footprint Maturity",
                        "weight": 4.0,
                        "type": "numeric",
                        "min_value": 0,
                        "max_value": 100,
                        "scoring_bands": [
                            {"min": 0, "max": 30, "score": 40},
                            {"min": 31, "max": 50, "score": 60},
                            {"min": 51, "max": 75, "score": 80},
                            {"min": 76, "max": 100, "score": 100}
                        ]
                    },
                    "social_network_stability": {
                        "name": "Social Network Stability",
                        "weight": 3.0,
                        "type": "numeric",
                        "min_value": 0,
                        "max_value": 100,
                        "scoring_bands": [
                            {"min": 0, "max": 40, "score": 40},
                            {"min": 41, "max": 60, "score": 60},
                            {"min": 61, "max": 80, "score": 80},
                            {"min": 81, "max": 100, "score": 100}
                        ]
                    },
                    "professional_network_quality": {
                        "name": "Professional Network Quality",
                        "weight": 4.0,
                        "type": "categorical",
                        "options": ["Excellent", "Good", "Average", "Below Average", "Poor"],
                        "scoring_map": {
                            "Excellent": 100,
                            "Good": 80,
                            "Average": 60,
                            "Below Average": 40,
                            "Poor": 20
                        }
                    },
                    "lifestyle_consistency": {
                        "name": "Lifestyle Consistency Score",
                        "weight": 3.0,
                        "type": "numeric",
                        "min_value": 0,
                        "max_value": 100,
                        "scoring_bands": [
                            {"min": 0, "max": 40, "score": 40},
                            {"min": 41, "max": 60, "score": 60},
                            {"min": 61, "max": 80, "score": 80},
                            {"min": 81, "max": 100, "score": 100}
                        ]
                    }
                },
                "total_weight": 14.0
            },
            
            "App Usage": {
                "variables": {
                    "financial_app_engagement": {
                        "name": "Financial App Engagement",
                        "weight": 4.0,
                        "type": "numeric",
                        "min_value": 0,
                        "max_value": 100,
                        "scoring_bands": [
                            {"min": 0, "max": 20, "score": 20},
                            {"min": 21, "max": 40, "score": 40},
                            {"min": 41, "max": 60, "score": 60},
                            {"min": 61, "max": 80, "score": 80},
                            {"min": 81, "max": 100, "score": 100}
                        ]
                    },
                    "digital_literacy_score": {
                        "name": "Digital Literacy Score",
                        "weight": 3.0,
                        "type": "numeric",
                        "min_value": 0,
                        "max_value": 100,
                        "scoring_bands": [
                            {"min": 0, "max": 30, "score": 40},
                            {"min": 31, "max": 50, "score": 60},
                            {"min": 51, "max": 75, "score": 80},
                            {"min": 76, "max": 100, "score": 100}
                        ]
                    },
                    "payment_app_usage": {
                        "name": "Payment App Usage Frequency",
                        "weight": 3.0,
                        "type": "categorical",
                        "options": ["Daily", "Weekly", "Monthly", "Rarely", "Never"],
                        "scoring_map": {
                            "Daily": 100,
                            "Weekly": 80,
                            "Monthly": 60,
                            "Rarely": 40,
                            "Never": 20
                        }
                    },
                    "digital_transaction_behavior": {
                        "name": "Digital Transaction Behavior",
                        "weight": 3.0,
                        "type": "categorical",
                        "options": ["Excellent", "Good", "Average", "Below Average", "Poor"],
                        "scoring_map": {
                            "Excellent": 100,
                            "Good": 80,
                            "Average": 60,
                            "Below Average": 40,
                            "Poor": 20
                        }
                    }
                },
                "total_weight": 13.0
            }
        }
    
    def get_company_additional_sources(self, company_id: int) -> List[str]:
        """Get selected additional data sources for a company"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT user_preferences FROM companies WHERE id = ?", (company_id,))
            result = cursor.fetchone()
            conn.close()
            
            if result and result[0]:
                prefs = json.loads(result[0])
                return prefs.get('additional_data', [])
            return []
        except Exception as e:
            print(f"Error getting additional sources: {e}")
            return []
    
    def get_additional_variables_for_company(self, company_id: int) -> Dict[str, Any]:
        """Get all additional variables that should be included for a company"""
        selected_sources = self.get_company_additional_sources(company_id)
        
        additional_vars = {}
        total_additional_weight = 0
        
        for source in selected_sources:
            if source in self.additional_variables:
                source_data = self.additional_variables[source]
                additional_vars[source] = source_data
                total_additional_weight += source_data['total_weight']
        
        return {
            'variables': additional_vars,
            'total_additional_weight': total_additional_weight,
            'selected_sources': selected_sources
        }
    
    def calculate_additional_score(self, form_data: Dict[str, Any], company_id: int) -> Dict[str, Any]:
        """Calculate score contribution from additional data sources"""
        additional_config = self.get_additional_variables_for_company(company_id)
        
        if not additional_config['variables']:
            return {
                'additional_score': 0,
                'additional_weight': 0,
                'source_scores': {},
                'missing_fields': []
            }
        
        total_score = 0
        total_weight = 0
        source_scores = {}
        missing_fields = []
        
        for source_name, source_config in additional_config['variables'].items():
            source_score = 0
            source_weight = 0
            
            for var_key, var_config in source_config['variables'].items():
                if var_key in form_data and form_data[var_key] is not None:
                    field_score = self._calculate_field_score(form_data[var_key], var_config)
                    weighted_score = field_score * var_config['weight']
                    source_score += weighted_score
                    source_weight += var_config['weight']
                else:
                    missing_fields.append(var_config['name'])
                    # Use fallback score of 50 for missing fields
                    fallback_score = 50 * var_config['weight']
                    source_score += fallback_score
                    source_weight += var_config['weight']
            
            source_scores[source_name] = {
                'score': source_score / source_weight if source_weight > 0 else 0,
                'weight': source_weight
            }
            
            total_score += source_score
            total_weight += source_weight
        
        return {
            'additional_score': total_score / total_weight if total_weight > 0 else 0,
            'additional_weight': total_weight,
            'source_scores': source_scores,
            'missing_fields': missing_fields
        }
    
    def _calculate_field_score(self, value: Any, field_config: Dict[str, Any]) -> float:
        """Calculate score for individual field based on its configuration"""
        if field_config['type'] == 'numeric':
            return self._score_numeric_field(value, field_config)
        elif field_config['type'] == 'categorical':
            return self._score_categorical_field(value, field_config)
        else:
            return 50  # Default score
    
    def _score_numeric_field(self, value: float, field_config: Dict[str, Any]) -> float:
        """Score numeric field using scoring bands"""
        try:
            value = float(value)
            for band in field_config['scoring_bands']:
                if band['min'] <= value <= band['max']:
                    return band['score']
            return 50  # Default if no band matches
        except (ValueError, TypeError):
            return 50
    
    def _score_categorical_field(self, value: str, field_config: Dict[str, Any]) -> float:
        """Score categorical field using scoring map"""
        scoring_map = field_config.get('scoring_map', {})
        return scoring_map.get(value, 50)  # Default score if value not found
    
    def get_dynamic_weights(self, company_id: int, base_weights: Dict[str, float]) -> Dict[str, float]:
        """Adjust base weights to accommodate additional data sources"""
        additional_config = self.get_additional_variables_for_company(company_id)
        additional_weight = additional_config['total_additional_weight']
        
        if additional_weight == 0:
            return base_weights
        
        # Calculate adjustment factor to maintain total weight around 100%
        base_total_weight = sum(base_weights.values())
        target_base_weight = 100 - additional_weight
        adjustment_factor = target_base_weight / base_total_weight if base_total_weight > 0 else 1
        
        # Adjust base weights
        adjusted_weights = {}
        for field, weight in base_weights.items():
            adjusted_weights[field] = weight * adjustment_factor
        
        return adjusted_weights