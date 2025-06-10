"""
Test script to verify synchronization between Dynamic Configuration and Scoring Weights Configuration
"""
import json
import sqlite3
from dynamic_scorecard1 import DynamicScorecardManager

def test_sync_functionality():
    """Test the sync buttons functionality"""
    print("Testing Sync Functionality...")
    
    # Initialize manager
    manager = DynamicScorecardManager()
    
    # Read current JSON weights
    print("\n1. Current JSON weights:")
    try:
        with open("scoring_weights.json", "r") as f:
            json_weights = json.load(f)
        for key, value in list(json_weights.items())[:5]:
            print(f"   {key}: {value}")
        print(f"   ... (total {len(json_weights)} variables)")
    except Exception as e:
        print(f"   Error reading JSON: {e}")
        return
    
    # Read current database weights
    print("\n2. Current database weights:")
    try:
        conn = sqlite3.connect("scorecard_config.db")
        cursor = conn.cursor()
        cursor.execute("SELECT variable_id, weight FROM scorecard_variables WHERE is_active = 1 LIMIT 5")
        db_weights = cursor.fetchall()
        conn.close()
        
        for variable_id, weight in db_weights:
            print(f"   {variable_id}: {weight}%")
        print(f"   ... (showing first 5)")
    except Exception as e:
        print(f"   Error reading database: {e}")
        return
    
    # Test sync FROM sliders (JSON to Database)
    print("\n3. Testing 'Sync FROM Sliders' (JSON → Database):")
    try:
        success = manager.sync_weights_from_file()
        if success:
            print("   ✓ Sync FROM Sliders completed successfully")
            
            # Verify the sync worked
            conn = sqlite3.connect("scorecard_config.db")
            cursor = conn.cursor()
            cursor.execute("SELECT variable_id, weight FROM scorecard_variables WHERE is_active = 1 LIMIT 3")
            new_db_weights = cursor.fetchall()
            conn.close()
            
            print("   Updated database weights:")
            for variable_id, weight in new_db_weights:
                expected_weight = json_weights.get(variable_id, 0) * 100
                print(f"   {variable_id}: {weight}% (expected: {expected_weight}%)")
        else:
            print("   ✗ Sync FROM Sliders failed")
    except Exception as e:
        print(f"   Error during sync FROM sliders: {e}")
    
    # Test sync TO sliders (Database to JSON)
    print("\n4. Testing 'Sync TO Sliders' (Database → JSON):")
    try:
        success = manager.sync_weights_to_file()
        if success:
            print("   ✓ Sync TO Sliders completed successfully")
            
            # Verify the sync worked
            with open("scoring_weights.json", "r") as f:
                updated_json_weights = json.load(f)
            
            print("   Updated JSON weights:")
            for key, value in list(updated_json_weights.items())[:3]:
                print(f"   {key}: {value}")
        else:
            print("   ✗ Sync TO Sliders failed")
    except Exception as e:
        print(f"   Error during sync TO sliders: {e}")
    
    print("\n5. Sync functionality test completed!")

if __name__ == "__main__":
    test_sync_functionality()