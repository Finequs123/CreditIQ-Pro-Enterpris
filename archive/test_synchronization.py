"""
Test script to check synchronization between Scoring Weights and Dynamic Configuration
"""
import sqlite3
import json
from weights_synchronizer import WeightsSynchronizer

def test_current_state():
    """Test the current state of both systems"""
    print("=== TESTING SYNCHRONIZATION STATE ===")
    
    # Check JSON weights file
    print("\n1. JSON Weights File:")
    try:
        with open("scoring_weights.json", "r") as f:
            json_weights = json.load(f)
        print(f"Found {len(json_weights)} variables in JSON:")
        for key, value in list(json_weights.items())[:5]:
            print(f"  - {key}: {value}")
    except Exception as e:
        print(f"Error reading JSON: {e}")
        json_weights = {}
    
    # Check Dynamic Configuration database
    print("\n2. Dynamic Configuration Database:")
    try:
        conn = sqlite3.connect("scorecard_config.db")
        cursor = conn.cursor()
        cursor.execute("SELECT variable_id, weight FROM scorecard_variables WHERE is_active = 1")
        db_results = cursor.fetchall()
        conn.close()
        
        print(f"Found {len(db_results)} variables in database:")
        for variable_id, weight in db_results[:5]:
            print(f"  - {variable_id}: {weight}%")
    except Exception as e:
        print(f"Error reading database: {e}")
        db_results = []
    
    # Test synchronizer
    print("\n3. Synchronizer Test:")
    try:
        synchronizer = WeightsSynchronizer()
        unified_weights = synchronizer.get_unified_weights()
        print(f"Synchronizer returned {len(unified_weights)} variables:")
        for key, value in list(unified_weights.items())[:5]:
            print(f"  - {key}: {value}")
    except Exception as e:
        print(f"Synchronizer error: {e}")
    
    # Check variable mapping
    print("\n4. Variable Mapping Test:")
    try:
        synchronizer = WeightsSynchronizer()
        mapping = synchronizer._get_variable_mapping()
        print(f"Mapping has {len(mapping)} entries:")
        for db_key, json_key in list(mapping.items())[:5]:
            print(f"  - {db_key} -> {json_key}")
    except Exception as e:
        print(f"Mapping error: {e}")

if __name__ == "__main__":
    test_current_state()