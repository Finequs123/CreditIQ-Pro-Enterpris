"""
Comprehensive Testing for Modular Scoring Engine
Tests all components before deployment
"""

import pandas as pd
import json
from modular_scoring_engine import ModularScoringEngine
from field_mapping_manager import FieldMappingManager

def test_individual_scoring_functions():
    """Test individual scoring functions"""
    print("Testing Individual Scoring Functions...")
    
    engine = ModularScoringEngine()
    
    # Test credit score function
    assert engine.score_credit_score(750) == 1.0, "Credit score 750 should return 1.0"
    assert engine.score_credit_score(600) == 0.4, "Credit score 600 should return 0.4"
    assert engine.score_credit_score(None) == 0.0, "Missing credit score should return 0.0"
    
    # Test FOIR function
    assert engine.score_foir(25.0) == 1.0, "FOIR 25% should return 1.0"
    assert engine.score_foir(35.0) == 0.8, "FOIR 35% should return 0.8"
    assert engine.score_foir(None) == 0.0, "Missing FOIR should return 0.0"
    
    # Test employment tenure
    assert engine.score_employment_tenure(60) == 1.0, "60 months tenure should return 1.0"
    assert engine.score_employment_tenure(18) == 0.4, "18 months tenure should return 0.4"
    assert engine.score_employment_tenure(None) == 0.0, "Missing tenure should return 0.0"
    
    print("✓ Individual scoring functions working correctly")

def test_modular_application_scoring():
    """Test complete application scoring"""
    print("Testing Complete Application Scoring...")
    
    engine = ModularScoringEngine()
    
    # Complete application data
    complete_app = {
        "credit_score": 720,
        "foir": 30.0,
        "dpd30plus": 0,
        "enquiry_count": 2,
        "monthly_income": 75000,
        "employment_tenure": 36,
        "company_stability": "good",
        "account_vintage": 48,
        "avg_monthly_balance": 50000,
        "bounce_frequency": 1
    }
    
    result = engine.score_application_modular(complete_app)
    
    assert "final_score" in result, "Result should contain final_score"
    assert "bucket" in result, "Result should contain bucket"
    assert "decision" in result, "Result should contain decision"
    assert "variable_details" in result, "Result should contain variable_details"
    assert result["final_score"] > 0, "Final score should be positive"
    
    # Test with missing data
    incomplete_app = {
        "credit_score": 650,
        "monthly_income": 40000
        # Other fields missing
    }
    
    result_incomplete = engine.score_application_modular(incomplete_app)
    
    assert result_incomplete["final_score"] >= 0, "Score should be non-negative even with missing data"
    
    # Check that missing fields have appropriate reasons
    for var_name, details in result_incomplete["variable_details"].items():
        if var_name not in incomplete_app:
            assert details["reason"] == "Fallback applied", f"Missing {var_name} should use fallback"
        else:
            assert details["reason"] == "Scored", f"Present {var_name} should be scored"
    
    print("✓ Application scoring working correctly with complete and incomplete data")

def test_field_mapping():
    """Test field mapping functionality"""
    print("Testing Field Mapping...")
    
    # Create test mapping
    mapping_manager = FieldMappingManager()
    
    test_mapping = {
        "cibil_score": "credit_score",
        "monthly_sal": "monthly_income",
        "emp_months": "employment_tenure",
        "bank_balance": "avg_monthly_balance"
    }
    
    # Save mapping
    success = mapping_manager.save_mapping("TEST_DSA_001", "Test DSA Partner", test_mapping)
    assert success, "Mapping should save successfully"
    
    # Retrieve mapping
    retrieved_mapping = mapping_manager.get_mapping("TEST_DSA_001")
    assert retrieved_mapping == test_mapping, "Retrieved mapping should match saved mapping"
    
    # Test field mapping application
    engine = ModularScoringEngine()
    engine.set_field_mapping("TEST_DSA_001", test_mapping)
    
    # Create test DataFrame with DSA field names
    test_df = pd.DataFrame({
        "cibil_score": [720, 650, 580],
        "monthly_sal": [75000, 50000, 30000],
        "emp_months": [36, 24, 12],
        "bank_balance": [50000, 25000, 10000]
    })
    
    mapped_df = engine.apply_field_mapping(test_df, "TEST_DSA_001")
    
    expected_columns = ["credit_score", "monthly_income", "employment_tenure", "avg_monthly_balance"]
    for col in expected_columns:
        assert col in mapped_df.columns, f"Mapped DataFrame should contain {col}"
    
    print("✓ Field mapping working correctly")

def test_bulk_processing():
    """Test bulk application processing"""
    print("Testing Bulk Processing...")
    
    engine = ModularScoringEngine()
    
    # Create test dataset
    test_data = pd.DataFrame({
        "credit_score": [750, 680, 620, 580, 720],
        "monthly_income": [80000, 60000, 45000, 35000, 70000],
        "foir": [25.0, 35.0, 45.0, 55.0, 30.0],
        "employment_tenure": [48, 36, 24, 12, 60],
        "dpd30plus": [0, 0, 1, 2, 0],
        "enquiry_count": [1, 3, 5, 8, 2]
    })
    
    # Process bulk applications
    results_df = engine.process_bulk_applications_modular(test_data)
    
    assert len(results_df) == len(test_data), "Results should match input count"
    assert "final_score" in results_df.columns, "Results should contain final_score"
    assert "bucket" in results_df.columns, "Results should contain bucket"
    assert "decision" in results_df.columns, "Results should contain decision"
    
    # Check that all scores are reasonable
    assert results_df["final_score"].min() >= 0, "All scores should be non-negative"
    assert results_df["final_score"].max() <= 100, "All scores should be <= 100"
    
    # Check that higher credit scores generally get better results
    high_credit_apps = results_df[results_df["credit_score_value"] >= 700]
    low_credit_apps = results_df[results_df["credit_score_value"] < 600]
    
    if len(high_credit_apps) > 0 and len(low_credit_apps) > 0:
        avg_high_score = high_credit_apps["final_score"].mean()
        avg_low_score = low_credit_apps["final_score"].mean()
        assert avg_high_score > avg_low_score, "Higher credit scores should generally get better results"
    
    print("✓ Bulk processing working correctly")

def test_scoring_transparency():
    """Test scoring transparency and reasons"""
    print("Testing Scoring Transparency...")
    
    engine = ModularScoringEngine()
    
    # Test application with mixed data availability
    test_app = {
        "credit_score": 700,  # Present
        "monthly_income": 60000,  # Present
        # foir missing
        "employment_tenure": 30,  # Present
        # Other fields missing
    }
    
    result = engine.score_application_modular(test_app)
    
    # Check transparency
    details = result["variable_details"]
    
    # Present fields should be "Scored"
    assert details["credit_score"]["reason"] == "Scored", "Present credit_score should be 'Scored'"
    assert details["monthly_income"]["reason"] == "Scored", "Present monthly_income should be 'Scored'"
    assert details["employment_tenure"]["reason"] == "Scored", "Present employment_tenure should be 'Scored'"
    
    # Missing fields should be "Fallback applied"
    assert details["foir"]["reason"] == "Fallback applied", "Missing foir should be 'Fallback applied'"
    assert details["account_vintage"]["reason"] == "Fallback applied", "Missing account_vintage should be 'Fallback applied'"
    
    # Check that fallback scores are used correctly
    for var_name, var_details in details.items():
        if var_details["reason"] == "Fallback applied":
            expected_fallback = engine.fallback_scores.get(var_name, 0.0)
            assert var_details["score"] == expected_fallback, f"Fallback score for {var_name} should match expected"
    
    print("✓ Scoring transparency working correctly")

def test_weight_system():
    """Test fixed weight system"""
    print("Testing Fixed Weight System...")
    
    engine = ModularScoringEngine()
    
    # Get total weights
    total_weight = sum(config["weight"] for config in engine.scoring_registry.values())
    
    # Test application
    test_app = {var: 50000 if "amount" in var or "income" in var else 1.0 
                for var in engine.scoring_registry.keys()}
    
    result = engine.score_application_modular(test_app)
    
    # Verify weight calculation
    calculated_total = sum(details["weighted_score"] for details in result["variable_details"].values())
    expected_final_score = (calculated_total / total_weight) * 100
    
    assert abs(result["final_score"] - expected_final_score) < 0.01, "Final score calculation should be correct"
    assert result["total_weight"] == total_weight, "Total weight should match registry"
    
    print("✓ Fixed weight system working correctly")

def run_all_tests():
    """Run comprehensive test suite"""
    print("Starting Comprehensive Testing of Modular Scoring Engine")
    print("=" * 60)
    
    try:
        test_individual_scoring_functions()
        test_modular_application_scoring()
        test_field_mapping()
        test_bulk_processing()
        test_scoring_transparency()
        test_weight_system()
        
        print("\n" + "=" * 60)
        print("🎉 ALL TESTS PASSED - Modular Scoring Engine is ready for deployment!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        print("=" * 60)
        return False

if __name__ == "__main__":
    run_all_tests()