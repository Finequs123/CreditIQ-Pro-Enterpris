"""
DSA Field Mapping UI - Shows only mapped fields with custom names
"""

import streamlit as st
import json
from field_mapping_manager import FieldMappingManager, get_dsa_mapping_options

def render_dsa_scoring_form():
    """Render scoring form with only DSA mapped fields"""
    st.header("🎯 DSA Partner Scoring")
    
    # Initialize mapping manager
    mapping_manager = FieldMappingManager()
    
    # DSA Selection
    dsa_options = get_dsa_mapping_options()
    if not dsa_options:
        st.warning("No DSA mappings configured. Configure DSA mappings first.")
        return
    
    selected_dsa = st.selectbox("Select DSA Partner", options=list(dsa_options.keys()))
    dsa_id = dsa_options.get(selected_dsa)
    
    if not dsa_id:
        st.error("Invalid DSA selection")
        return
    
    # Get the field mapping
    mapping_data = mapping_manager.get_mapping(dsa_id)
    if not mapping_data:
        st.error(f"No field mapping found for {selected_dsa}")
        return
    
    field_mapping = mapping_data.get('mapping', {})
    if not field_mapping:
        st.error("No field mappings configured for this DSA")
        return
    
    st.success(f"✓ Loaded {len(field_mapping)} custom fields for {selected_dsa}")
    
    # Create form with ONLY the mapped fields
    st.subheader("Application Data")
    
    form_data = {}
    
    # Display each mapped field with its custom name  
    for custom_name, standard_field in field_mapping.items():
        if standard_field == "credit_score":
            form_data[standard_field] = st.number_input(
                custom_name, min_value=300, max_value=900, value=650
            )
        elif standard_field == "monthly_income":
            form_data[standard_field] = st.number_input(
                custom_name, min_value=0, value=50000
            )
        elif "enquiry" in standard_field.lower():
            form_data[standard_field] = st.number_input(
                custom_name, min_value=0, max_value=20, value=3
            )
        elif "dsr" in standard_field.lower() or "foir" in custom_name.lower():
            form_data[standard_field] = st.number_input(
                custom_name, min_value=0.0, max_value=100.0, value=35.0
            )
        elif "loan" in custom_name.lower() and ("type" in custom_name.lower() or "loan_mix" in standard_field.lower()):
            form_data[standard_field] = st.selectbox(
                custom_name, ["personal", "business", "home", "auto", "education"]
            )
        elif "completion" in custom_name.lower() or "ratio" in custom_name.lower():
            form_data[standard_field] = st.number_input(
                custom_name, min_value=0.0, max_value=1.0, value=0.8
            )
        elif "defaulted" in custom_name.lower() or "dpd" in standard_field.lower():
            form_data[standard_field] = st.number_input(
                custom_name, min_value=0, max_value=10, value=0
            )
        elif "job" in custom_name.lower() or "occupation" in custom_name.lower():
            form_data[standard_field] = st.selectbox(
                custom_name, ["government", "private", "self_employed", "business"]
            )
        elif "experience" in custom_name.lower() or "stability" in custom_name.lower():
            form_data[standard_field] = st.selectbox(
                custom_name, ["excellent", "good", "average", "below_average", "poor"]
            )
        elif "account" in custom_name.lower() and "vintage" in custom_name.lower():
            form_data[standard_field] = st.number_input(
                custom_name, min_value=0, value=36
            )
        elif "balance" in custom_name.lower():
            form_data[standard_field] = st.number_input(
                custom_name, min_value=0, value=25000
            )
        elif "outstanding" in custom_name.lower():
            form_data[standard_field] = st.number_input(
                custom_name, min_value=0.0, max_value=100.0, value=65.0
            )
        elif "unsecured" in custom_name.lower():
            form_data[standard_field] = st.number_input(
                custom_name, min_value=0, value=200000
            )
        else:
            # Default text input for unmapped field types
            form_data[standard_field] = st.text_input(custom_name, value="")
    
    # Score button
    if st.button("🎯 Calculate Score", type="primary"):
        st.success("Form submitted with DSA custom field names!")
        
        # Show submitted data
        st.subheader("Submitted Data")
        for standard_field, value in form_data.items():
            # Find the custom name by looking up the standard field in the mapping
            custom_name = None
            for custom, standard in field_mapping.items():
                if standard == standard_field:
                    custom_name = custom
                    break
            if not custom_name:
                custom_name = standard_field
            st.write(f"**{custom_name}:** {value}")
        
        return form_data
    
    return None