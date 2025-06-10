#!/usr/bin/env python3

from scoring_engine import LoanScoringEngine

def test_scoring_engine():
    """Test the scoring engine with sample data"""
    
    # Initialize scoring engine
    engine = LoanScoringEngine()
    
    # Test case 1: Good applicant profile
    good_applicant = {
        'pan': 'ABCDE1234F',
        'age': 30,
        'monthly_income': 35000,
        'credit_score': 750,
        'foir': 0.3,
        'dpd30plus': 0,
        'enquiry_count': 1,
        'credit_vintage': 48,
        'loan_mix_type': 'PL/HL/CC',
        'loan_completion_ratio': 0.8,
        'defaulted_loans': 0,
        'unsecured_loan_amount': 75000,
        'outstanding_amount_percent': 0.25,
        'our_lender_exposure': 10000,
        'channel_type': 'Merchant/Referral',
        'writeoff_flag': False
    }
    
    print("Testing Good Applicant Profile:")
    print("-" * 40)
    result = engine.score_application(good_applicant)
    
    print(f"Final Score: {result['final_score']:.2f}")
    print(f"Initial Bucket: {result['initial_bucket']}")
    print(f"Final Bucket: {result['final_bucket']}")
    print(f"Decision: {result['decision']}")
    print(f"Clearance Passed: {result['clearance_passed']}")
    
    if result['variable_scores']:
        print("\nVariable Score Breakdown:")
        for var, score_info in result['variable_scores'].items():
            print(f"  {var}: {score_info['weighted_score']:.4f} (band: {score_info['band_score']}, weight: {score_info['weight']:.1%})")
    
    print("\n" + "="*50 + "\n")
    
    # Test case 2: Poor applicant profile
    poor_applicant = {
        'pan': 'XYZTE5678Z',
        'age': 25,
        'monthly_income': 18000,
        'credit_score': 550,
        'foir': 0.6,
        'dpd30plus': 1,
        'enquiry_count': 5,
        'credit_vintage': 10,
        'loan_mix_type': 'Only Gold',
        'loan_completion_ratio': 0.3,
        'defaulted_loans': 0,
        'unsecured_loan_amount': 150000,
        'outstanding_amount_percent': 0.7,
        'our_lender_exposure': 0,
        'channel_type': 'Digital/Other',
        'writeoff_flag': False
    }
    
    print("Testing Poor Applicant Profile:")
    print("-" * 40)
    result2 = engine.score_application(poor_applicant)
    
    print(f"Final Score: {result2['final_score']:.2f}")
    print(f"Initial Bucket: {result2['initial_bucket']}")
    print(f"Final Bucket: {result2['final_bucket']}")
    print(f"Decision: {result2['decision']}")
    print(f"Clearance Passed: {result2['clearance_passed']}")
    
    if result2['variable_scores']:
        print("\nVariable Score Breakdown:")
        for var, score_info in result2['variable_scores'].items():
            print(f"  {var}: {score_info['weighted_score']:.4f} (band: {score_info['band_score']}, weight: {score_info['weight']:.1%})")

if __name__ == "__main__":
    test_scoring_engine()