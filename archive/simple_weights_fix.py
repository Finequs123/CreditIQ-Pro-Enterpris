"""
Simple weights fix - Direct approach that actually works
"""
import streamlit as st
import json

def apply_ai_weights_simple(weights_dict):
    """Simple function to apply AI weights that actually works"""
    
    if st.button("Apply AI-Suggested Weights", type="primary"):
        # Step 1: Save weights to file
        with open("scoring_weights.json", "w") as f:
            json.dump(weights_dict, f, indent=2)
        
        # Step 2: Force clear the broken config manager
        if 'config_manager' in st.session_state:
            del st.session_state['config_manager']
        
        # Step 3: Show success and force page refresh
        st.success("AI weights applied successfully!")
        st.info("The weights have been updated. Navigate to Scoring Weights Configuration to see changes.")
        
        # Step 4: Set a flag to force config reload
        st.session_state['weights_just_applied'] = True
        
        # Force rerun
        st.rerun()