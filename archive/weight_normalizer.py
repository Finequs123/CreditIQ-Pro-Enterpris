"""
Weight Normalization System
Ensures all weights sum to exactly 100%
"""
import json
import sqlite3
from typing import Dict

def normalize_weights_to_100(weights: Dict[str, float]) -> Dict[str, float]:
    """Normalize weights to sum to exactly 100%"""
    current_total = sum(weights.values())
    
    if current_total == 0:
        # If all weights are 0, distribute equally
        equal_weight = 1.0 / len(weights)
        return {key: equal_weight for key in weights.keys()}
    
    # Scale all weights proportionally
    scaling_factor = 1.0 / current_total
    normalized = {key: value * scaling_factor for key, value in weights.items()}
    
    return normalized

def fix_weight_totals():
    """Fix weight totals in both JSON and database systems"""
    print("Fixing weight totals to sum to 100%...")
    
    # 1. Fix JSON weights
    try:
        with open("scoring_weights.json", "r") as f:
            json_weights = json.load(f)
        
        print(f"JSON weights total before: {sum(json_weights.values()):.3f}")
        
        normalized_json = normalize_weights_to_100(json_weights)
        
        with open("scoring_weights.json", "w") as f:
            json.dump(normalized_json, f, indent=2)
        
        print(f"JSON weights total after: {sum(normalized_json.values()):.3f}")
        
    except Exception as e:
        print(f"Error fixing JSON weights: {e}")
    
    # 2. Fix database weights
    try:
        conn = sqlite3.connect("scorecard_config.db")
        cursor = conn.cursor()
        
        # Get current weights
        cursor.execute("SELECT variable_id, weight FROM scorecard_variables WHERE is_active = 1")
        db_results = cursor.fetchall()
        
        # Convert to percentage format (database stores as percentages)
        db_weights = {var_id: weight/100.0 for var_id, weight in db_results}
        
        print(f"Database weights total before: {sum(db_weights.values()):.3f}")
        
        # Normalize
        normalized_db = normalize_weights_to_100(db_weights)
        
        # Update database with normalized weights (convert back to percentages)
        for var_id, normalized_weight in normalized_db.items():
            percentage_weight = normalized_weight * 100.0
            cursor.execute(
                "UPDATE scorecard_variables SET weight = ? WHERE variable_id = ?",
                (percentage_weight, var_id)
            )
        
        conn.commit()
        conn.close()
        
        print(f"Database weights total after: {sum(normalized_db.values()):.3f}")
        
    except Exception as e:
        print(f"Error fixing database weights: {e}")
    
    print("Weight normalization complete!")

if __name__ == "__main__":
    fix_weight_totals()