"""
Dynamic Additional Data Weight System
Creates a flexible weight for additional data sources based on company preferences
"""

import sqlite3
import json
from typing import Dict, Any, List

class DynamicAdditionalWeight:
    """Manages dynamic weighting for additional data sources"""
    
    def __init__(self, db_path: str = "user_management.db"):
        self.db_path = db_path
        
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
    
    def calculate_dynamic_weight(self, company_id: int) -> Dict[str, Any]:
        """Calculate dynamic weight based on company's additional data sources"""
        selected_sources = self.get_company_additional_sources(company_id)
        
        if not selected_sources:
            return {
                'has_additional_sources': False,
                'additional_weight': 0.0,
                'base_weight_adjustment': 1.0,
                'sources_count': 0,
                'selected_sources': []
            }
        
        # Dynamic weight calculation based on number of sources
        sources_count = len(selected_sources)
        
        # Weight allocation strategy:
        # 1 source: 5% additional weight
        # 2 sources: 8% additional weight  
        # 3 sources: 10% additional weight
        # 4+ sources: 12% additional weight
        
        if sources_count == 1:
            additional_weight = 5.0
        elif sources_count == 2:
            additional_weight = 8.0
        elif sources_count == 3:
            additional_weight = 10.0
        else:  # 4 or more sources
            additional_weight = 12.0
        
        # Adjust base weights to accommodate additional weight
        base_weight_adjustment = (100 - additional_weight) / 100
        
        return {
            'has_additional_sources': True,
            'additional_weight': additional_weight,
            'base_weight_adjustment': base_weight_adjustment,
            'sources_count': sources_count,
            'selected_sources': selected_sources
        }
    
    def get_additional_data_score(self, company_id: int, additional_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate score contribution from additional data sources"""
        weight_config = self.calculate_dynamic_weight(company_id)
        
        if not weight_config['has_additional_sources'] or not additional_data:
            return {
                'additional_score': 0.0,
                'additional_weight': 0.0,
                'breakdown': {}
            }
        
        # Simple scoring logic for demonstration
        # In practice, this would use sophisticated scoring algorithms
        total_fields = len(additional_data)
        if total_fields == 0:
            field_score = 0
        else:
            # Calculate average score based on filled fields
            field_scores = []
            for key, value in additional_data.items():
                if isinstance(value, (int, float)):
                    # Normalize numeric values to 0-100 scale
                    field_scores.append(min(100, max(0, float(value))))
                elif isinstance(value, str) and value:
                    # Simple categorical scoring
                    if value.lower() in ['excellent', 'good', 'high', 'strong']:
                        field_scores.append(90)
                    elif value.lower() in ['average', 'medium', 'satisfactory']:
                        field_scores.append(70)
                    elif value.lower() in ['below average', 'low', 'weak']:
                        field_scores.append(50)
                    else:
                        field_scores.append(60)  # Default score
                else:
                    field_scores.append(60)  # Default for other types
            
            field_score = sum(field_scores) / len(field_scores) if field_scores else 60
        
        # Convert to additional score based on weight
        additional_score = (field_score / 100) * weight_config['additional_weight']
        
        return {
            'additional_score': additional_score,
            'additional_weight': weight_config['additional_weight'],
            'breakdown': {
                'sources_count': weight_config['sources_count'],
                'selected_sources': weight_config['selected_sources'],
                'field_score': field_score,
                'fields_evaluated': total_fields
            }
        }