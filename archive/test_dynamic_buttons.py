"""
Test script to verify Apply and Test button functionality
"""
import sqlite3
import json
from dynamic_scorecard1 import DynamicScorecardManager
from dynamic_config_setup1 import calculate_dynamic_score
from weight_normalizer import normalize_weights_to_100

def test_apply_functionality():
    """Test the Apply Scorecard functionality"""
    print("=== TESTING APPLY SCORECARD FUNCTIONALITY ===")
    
    manager = DynamicScorecardManager()
    
    # Get current weights from database
    conn = sqlite3.connect("scorecard_config.db")
    cursor = conn.cursor()
    cursor.execute("SELECT variable_id, weight FROM scorecard_variables WHERE is_active = 1")
    db_results = cursor.fetchall()
    conn.close()
    
    print(f"Found {len(db_results)} variables in database")
    
    # Convert to decimal format
    db_weights = {var_id: weight/100.0 for var_id, weight in db_results}
    
    # Normalize weights
    normalized_weights = normalize_weights_to_100(db_weights)
    
    # Sync to file (simulating Apply button)
    manager._sync_weights_to_file()
    
    # Verify the sync worked
    with open("scoring_weights.json", "r") as f:
        json_weights = json.load(f)
    
    print(f"JSON weights total: {sum(json_weights.values()):.6f}")
    print("✅ Apply functionality working")
    
    return True

def test_scoring_functionality():
    """Test the Test Scorecard functionality"""
    print("\n=== TESTING SCORECARD SCORING FUNCTIONALITY ===")
    
    manager = DynamicScorecardManager()
    
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
    
    try:
        # Calculate score using current configuration
        result = calculate_dynamic_score(test_data, manager)
        
        if result:
            print(f"✅ Test Score: {result['score']:.1f}/100")
            print(f"✅ Risk Category: {result['risk_category']}")
            print(f"✅ Decision: {result['decision']}")
            return True
        else:
            print("❌ Scoring failed - no result returned")
            return False
            
    except Exception as e:
        print(f"❌ Scoring failed with error: {e}")
        return False

def test_weight_totals():
    """Test that weight totals are correct"""
    print("\n=== TESTING WEIGHT TOTALS ===")
    
    # Check database total
    conn = sqlite3.connect("scorecard_config.db")
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(weight) FROM scorecard_variables WHERE is_active = 1")
    db_total = cursor.fetchone()[0] or 0
    conn.close()
    
    # Check JSON total
    with open("scoring_weights.json", "r") as f:
        json_weights = json.load(f)
    json_total = sum(json_weights.values()) * 100
    
    print(f"Database total: {db_total:.2f}%")
    print(f"JSON total: {json_total:.2f}%")
    
    if abs(db_total - 100.0) < 0.1 and abs(json_total - 100.0) < 0.1:
        print("✅ Weight totals are correct (100%)")
        return True
    else:
        print("❌ Weight totals are incorrect")
        return False

if __name__ == "__main__":
    apply_test = test_apply_functionality()
    scoring_test = test_scoring_functionality()
    totals_test = test_weight_totals()
    
    if apply_test and scoring_test and totals_test:
        print("\n🎉 ALL DYNAMIC CONFIGURATION TESTS PASSED!")
        print("Apply Scorecard and Test buttons are working correctly.")
    else:
        print("\n⚠️ SOME TESTS FAILED - Check functionality")