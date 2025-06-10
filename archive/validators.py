import re
from typing import Dict, Any, List

def validate_individual_data(data: Dict[str, Any]) -> List[str]:
    """Validate individual application data"""
    errors = []
    
    # PAN validation
    pan = data.get('pan', '').strip()
    if not pan:
        errors.append("PAN number is required")
    elif not validate_pan_format(pan):
        errors.append("PAN number format is invalid (should be like ABCDE1234F)")
    
    # Age validation
    age = data.get('age', 0)
    if not isinstance(age, (int, float)) or age < 18 or age > 80:
        errors.append("Age must be between 18 and 80")
    
    # Monthly income validation
    income = data.get('monthly_income', 0)
    if not isinstance(income, (int, float)) or income < 0:
        errors.append("Monthly income must be a positive number")
    
    # Credit score validation
    credit_score = data.get('credit_score', 0)
    if not isinstance(credit_score, (int, float)) or credit_score < -1 or credit_score > 900:
        errors.append("Credit score must be between -1 and 900")
    
    # FOIR validation
    foir = data.get('foir', 0)
    if not isinstance(foir, (int, float)) or foir < 0 or foir > 2:
        errors.append("FOIR must be between 0 and 2")
    
    # DPD30Plus validation
    dpd = data.get('dpd30plus', 0)
    if not isinstance(dpd, (int, float)) or dpd < 0 or dpd > 50:
        errors.append("DPD30Plus must be between 0 and 50")
    
    # Enquiry count validation
    enquiry = data.get('enquiry_count', 0)
    if not isinstance(enquiry, (int, float)) or enquiry < 0 or enquiry > 100:
        errors.append("Enquiry count must be between 0 and 100")
    
    # Credit vintage validation
    vintage = data.get('credit_vintage', 0)
    if not isinstance(vintage, (int, float)) or vintage < 0 or vintage > 600:
        errors.append("Credit vintage must be between 0 and 600 months")
    
    # Loan mix type validation
    loan_mix = data.get('loan_mix_type', '')
    valid_loan_types = ["PL/HL/CC", "Gold + Consumer Durable", "Only Gold", "Agri/Other loans"]
    if loan_mix not in valid_loan_types:
        errors.append(f"Loan mix type must be one of: {', '.join(valid_loan_types)}")
    
    # Loan completion ratio validation
    completion = data.get('loan_completion_ratio', 0)
    if not isinstance(completion, (int, float)) or completion < 0 or completion > 1:
        errors.append("Loan completion ratio must be between 0 and 1")
    
    # Defaulted loans validation
    defaulted = data.get('defaulted_loans', 0)
    if not isinstance(defaulted, (int, float)) or defaulted < 0 or defaulted > 50:
        errors.append("Defaulted loans count must be between 0 and 50")
    
    # Unsecured loan amount validation
    unsecured = data.get('unsecured_loan_amount', 0)
    if not isinstance(unsecured, (int, float)) or unsecured < 0:
        errors.append("Unsecured loan amount must be a positive number")
    
    # Outstanding amount percent validation
    outstanding = data.get('outstanding_amount_percent', 0)
    if not isinstance(outstanding, (int, float)) or outstanding < 0 or outstanding > 1:
        errors.append("Outstanding amount percent must be between 0 and 1")
    
    # Our lender exposure validation
    exposure = data.get('our_lender_exposure', 0)
    if not isinstance(exposure, (int, float)) or exposure < 0:
        errors.append("Our lender exposure must be a positive number")
    
    # Channel type validation
    channel = data.get('channel_type', '')
    valid_channels = ["Merchant/Referral", "Digital/Other"]
    if channel not in valid_channels:
        errors.append(f"Channel type must be one of: {', '.join(valid_channels)}")
    
    # Write-off flag validation
    writeoff = data.get('writeoff_flag', False)
    if not isinstance(writeoff, bool):
        errors.append("Write-off flag must be true or false")
    
    return errors

def validate_pan_format(pan: str) -> bool:
    """Validate PAN number format"""
    if not pan or len(pan) != 10:
        return False
    
    # PAN format: 5 letters, 4 digits, 1 letter
    pattern = r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$'
    return bool(re.match(pattern, pan.upper()))

def validate_bulk_data_row(row: Dict[str, Any], row_index: int) -> Dict[str, Any]:
    """Validate a single row from bulk data"""
    errors = validate_individual_data(row)
    
    return {
        'row_index': row_index,
        'valid': len(errors) == 0,
        'errors': errors,
        'data': row
    }

def validate_bulk_data(df) -> Dict[str, Any]:
    """Validate entire bulk dataset"""
    validation_results = []
    total_rows = len(df)
    valid_rows = 0
    
    for idx, row in df.iterrows():
        row_dict = row.to_dict()
        validation_result = validate_bulk_data_row(row_dict, idx + 1)
        validation_results.append(validation_result)
        
        if validation_result['valid']:
            valid_rows += 1
    
    return {
        'total_rows': total_rows,
        'valid_rows': valid_rows,
        'invalid_rows': total_rows - valid_rows,
        'validation_results': validation_results,
        'overall_valid': valid_rows == total_rows
    }

def get_validation_summary(validation_results: List[Dict[str, Any]]) -> str:
    """Get a summary of validation results"""
    total = len(validation_results)
    valid = len([r for r in validation_results if r['valid']])
    invalid = total - valid
    
    summary = f"Validation Summary: {valid}/{total} rows passed validation"
    
    if invalid > 0:
        summary += f"\n{invalid} rows have validation errors"
        
        # Group errors by type
        error_counts = {}
        for result in validation_results:
            if not result['valid']:
                for error in result['errors']:
                    error_counts[error] = error_counts.get(error, 0) + 1
        
        summary += "\n\nCommon validation errors:"
        for error, count in sorted(error_counts.items(), key=lambda x: x[1], reverse=True):
            summary += f"\n• {error} ({count} rows)"
    
    return summary
