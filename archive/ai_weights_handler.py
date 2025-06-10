"""
AI Weights Handler - Clean implementation for applying AI-suggested weights
"""
import json
import streamlit as st
from typing import Dict, Any

class AIWeightsHandler:
    """Handles application of AI-suggested weights to the scoring system"""
    
    def __init__(self):
        self.weights_file = "scoring_weights.json"
    
    def apply_ai_weights(self, ai_weights: Dict[str, float]) -> bool:
        """Apply AI weights to the entire system"""
        try:
            # Step 1: Save weights to file
            self._save_weights_to_file(ai_weights)
            
            # Step 2: Clear session state completely
            self._clear_session_state()
            
            # Step 3: Force system reload
            self._reload_system_components()
            
            return True
            
        except Exception as e:
            st.error(f"Failed to apply AI weights: {str(e)}")
            return False
    
    def _save_weights_to_file(self, weights: Dict[str, float]):
        """Save weights to JSON file"""
        with open(self.weights_file, 'w') as f:
            json.dump(weights, f, indent=2)
    
    def _clear_session_state(self):
        """Clear all relevant session state variables"""
        keys_to_clear = [
            'config_manager',
            'scoring_engine',
            'weights_applied'
        ]
        
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
    
    def _reload_system_components(self):
        """Reload scoring engine and config manager"""
        # Import here to avoid circular imports
        from scoring_engine import LoanScoringEngine
        from scoring_config import ScoringWeightsConfig
        
        # Create fresh instances
        st.session_state.scoring_engine = LoanScoringEngine()
        st.session_state.config_manager = ScoringWeightsConfig()
        st.session_state.weights_applied = True

def apply_ai_weights_button(weights: Dict[str, float]):
    """Render button and handle AI weights application"""
    if st.button("✅ Apply AI-Suggested Weights", type="primary", key="apply_ai_weights"):
        handler = AIWeightsHandler()
        
        if handler.apply_ai_weights(weights):
            st.session_state.weights_updated = True
            st.success("AI-optimized weights applied successfully!")
            st.info("Navigate to 'Scoring Weights Configuration' to see the updated weights.")
            st.rerun()
        else:
            st.error("Failed to apply AI weights. Please try again.")