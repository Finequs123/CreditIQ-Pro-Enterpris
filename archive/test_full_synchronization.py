"""
Comprehensive test to verify synchronization between Scoring Weights and Dynamic Configuration
"""
import sqlite3
import json
from weights_synchronizer import WeightsSynchronizer, save_synchronized_weights
from dynamic_scorecard1 import DynamicScorecardManager

def test_complete_synchronization():
    """Test complete synchronization workflow"""
    print("=== COMPREHENSIVE SYNCHRONIZATION TEST ===")
    
    # 1. Initialize systems
    print("\n1. Initializing systems...")
    synchronizer = WeightsSynchronizer()
    manager = DynamicScorecardManager()
    
    # 2. Check initial state
    print("\n2. Initial state check:")
    json_weights = synchronizer.get_unified_weights()
    print(f"JSON system has {len(json_weights)} variables")
    
    # Check database state
    conn = sqlite3.connect("scorecard_config.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM scorecard_variables WHERE is_active = 1")
    db_count = cursor.fetchone()[0]
    cursor.execute("SELECT variable_id, weight FROM scorecard_variables WHERE is_active = 1 LIMIT 5")
    db_sample = cursor.fetchall()
    conn.close()
    
    print(f"Database has {db_count} active variables")
    print("Sample database weights:")
    for var_id, weight in db_sample:
        print(f"  - {var_id}: {weight}%")
    
    # 3. Test sync from JSON to database
    print("\n3. Testing sync FROM JSON to database...")
    success = manager.sync_weights_from_file()
    print(f"Sync from JSON result: {success}")
    
    # 4. Verify sync worked
    print("\n4. Verifying sync results...")
    conn = sqlite3.connect("scorecard_config.db")
    cursor = conn.cursor()
    cursor.execute("SELECT variable_id, weight FROM scorecard_variables WHERE is_active = 1 LIMIT 5")
    updated_db_sample = cursor.fetchall()
    conn.close()
    
    print("Updated database weights:")
    for var_id, weight in updated_db_sample:
        print(f"  - {var_id}: {weight}%")
    
    # 5. Test sync from database to JSON
    print("\n5. Testing sync FROM database to JSON...")
    
    # First, modify a weight in database
    conn = sqlite3.connect("scorecard_config.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE scorecard_variables SET weight = 15.0 WHERE variable_id = 'credit_score'")
    conn.commit()
    conn.close()
    
    # Sync to JSON
    manager._sync_weights_to_file()
    
    # Verify JSON was updated
    with open("scoring_weights.json", "r") as f:
        updated_json = json.load(f)
    
    print(f"Updated JSON credit_score weight: {updated_json.get('credit_score', 'NOT FOUND')}")
    
    # 6. Test unified weights function
    print("\n6. Testing unified weights function...")
    unified = synchronizer.get_unified_weights()
    print(f"Unified weights credit_score: {unified.get('credit_score', 'NOT FOUND')}")
    
    print("\n=== TEST COMPLETE ===")
    
    # Check if weights match
    if abs(unified.get('credit_score', 0) - 0.15) < 0.001:
        print("✅ SYNCHRONIZATION WORKING CORRECTLY")
        return True
    else:
        print("❌ SYNCHRONIZATION ISSUE DETECTED")
        return False

def test_weight_mapping():
    """Test that all variables are properly mapped"""
    print("\n=== VARIABLE MAPPING TEST ===")
    
    synchronizer = WeightsSynchronizer()
    mapping = synchronizer._get_variable_mapping()
    
    # Get JSON variables
    try:
        with open("scoring_weights.json", "r") as f:
            json_vars = set(json.load(f).keys())
    except:
        json_vars = set()
    
    # Get database variables
    try:
        conn = sqlite3.connect("scorecard_config.db")
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT variable_id FROM scorecard_variables WHERE is_active = 1")
        db_vars = set(row[0] for row in cursor.fetchall())
        conn.close()
    except:
        db_vars = set()
    
    print(f"JSON variables: {len(json_vars)}")
    print(f"Database variables: {len(db_vars)}")
    print(f"Mapping entries: {len(mapping)}")
    
    # Check for unmapped variables
    json_only = json_vars - db_vars
    db_only = db_vars - json_vars
    
    if json_only:
        print(f"Variables only in JSON: {json_only}")
    
    if db_only:
        print(f"Variables only in Database: {db_only}")
    
    if not json_only and not db_only:
        print("✅ All variables properly mapped")
        return True
    else:
        print("❌ Variable mapping issues detected")
        return False

if __name__ == "__main__":
    sync_test = test_complete_synchronization()
    mapping_test = test_weight_mapping()
    
    if sync_test and mapping_test:
        print("\n🎉 ALL TESTS PASSED - SYNCHRONIZATION IS WORKING!")
    else:
        print("\n⚠️ SOME TESTS FAILED - SYNCHRONIZATION NEEDS ATTENTION")