#!/usr/bin/env python3
"""
Dynamic Configuration Setup - Complete integration package
Copy this file along with the core module files to your new Replit project
"""

import streamlit as st
from dynamic_config_ui1 import render_dynamic_scorecard_config
from dynamic_scoring_ui1 import render_dynamic_individual_scoring, calculate_dynamic_score
from dynamic_scorecard1 import DynamicScorecardManager
from dynamic_weight_display1 import render_dynamic_weight_breakdown

class DynamicConfigIntegration:
    """
    Complete integration class for Dynamic Configuration functionality
    Use this to easily add dynamic configuration to any Streamlit app
    """
    
    def __init__(self, db_path: str = "scorecard_config.db"):
        """
        Initialize the dynamic configuration system
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.manager = None
        self._initialize_manager()
    
    def _initialize_manager(self):
        """Initialize the scorecard manager and database"""
        if 'scorecard_manager' not in st.session_state:
            st.session_state.scorecard_manager = DynamicScorecardManager(self.db_path)
            st.session_state.scorecard_manager.init_database()
        
        self.manager = st.session_state.scorecard_manager
    
    def render_configuration_page(self):
        """
        Render the complete configuration interface
        Call this from your main app navigation
        """
        st.title("🔧 Dynamic Scorecard Configuration")
        st.markdown("Configure variables, weights, and score bands for your scoring system")
        
        render_dynamic_scorecard_config()
    
    def render_scoring_page(self):
        """
        Render the dynamic scoring interface
        Call this for individual application scoring
        """
        st.title("🎯 Dynamic Scoring Interface")
        st.markdown("Score individual applications using your configured scorecard")
        
        render_dynamic_individual_scoring()
    
    def render_weight_analysis(self, form_data: dict = None):
        """
        Render weight distribution analysis
        
        Args:
            form_data: Form input data for real-time analysis
        """
        st.title("📊 Weight Distribution Analysis")
        
        if form_data:
            render_dynamic_weight_breakdown(form_data, self.manager)
        else:
            st.info("Enter values in the scoring interface to see dynamic weight distribution")
    
    def get_manager(self):
        """Get the scorecard manager instance"""
        return self.manager
    
    def calculate_score(self, form_data: dict):
        """
        Calculate score using dynamic configuration
        
        Args:
            form_data: Dictionary with applicant data
            
        Returns:
            Dictionary with scoring results
        """
        return calculate_dynamic_score(form_data, self.manager)
    
    def get_active_variables(self):
        """Get list of active variables"""
        return self.manager.get_active_variables()
    
    def get_categories(self):
        """Get list of active categories"""
        return self.manager.get_categories()

# Simplified integration functions for direct use
def setup_dynamic_config(db_path: str = "scorecard_config.db"):
    """
    Simple setup function - call this once in your main app
    
    Returns:
        DynamicConfigIntegration: Integration instance
    """
    return DynamicConfigIntegration(db_path)

def add_config_to_sidebar(integration_instance):
    """
    Add configuration navigation to sidebar
    
    Args:
        integration_instance: DynamicConfigIntegration instance
    """
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔧 Dynamic Configuration")
    
    if st.sidebar.button("Variable Management"):
        st.session_state.current_page = "config_variables"
    
    if st.sidebar.button("Weight Distribution"):
        st.session_state.current_page = "config_weights"
    
    if st.sidebar.button("Score Bands"):
        st.session_state.current_page = "config_bands"

# Example usage in main app
def example_main_app():
    """
    Example of how to integrate into your main Streamlit app
    """
    
    # 1. Setup (call once at app start)
    config_system = setup_dynamic_config()
    
    # 2. Navigation
    page = st.sidebar.selectbox("Choose Page", [
        "Home",
        "Individual Scoring", 
        "Dynamic Configuration",
        "Weight Analysis"
    ])
    
    # 3. Page routing
    if page == "Individual Scoring":
        config_system.render_scoring_page()
    
    elif page == "Dynamic Configuration":
        config_system.render_configuration_page()
    
    elif page == "Weight Analysis":
        # Get form data from scoring page if available
        form_data = st.session_state.get('current_form_data', {})
        config_system.render_weight_analysis(form_data)
    
    else:  # Home page
        st.title("Welcome to Your Loan Scoring Application")
        st.markdown("Navigate to different sections using the sidebar")
        
        # Display current configuration summary
        st.subheader("Current Configuration")
        
        variables = config_system.get_active_variables()
        categories = config_system.get_categories()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Active Variables", len(variables))
        with col2:
            st.metric("Categories", len(categories))

if __name__ == "__main__":
    example_main_app()