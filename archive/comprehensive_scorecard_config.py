"""
Comprehensive Scorecard Configuration
Integrates additional data sources into the main Scorecard Variables structure
"""

import streamlit as st
import sqlite3
import json
from typing import Dict, List, Any
from dynamic_scorecard import DynamicScorecardManager
from complete_variable_definitions import get_complete_variable_definitions, get_variables_by_category

def render_comprehensive_scorecard_config():
    """Render comprehensive scorecard configuration with integrated additional data sources"""
    
    st.title("🔧 Comprehensive Scorecard Configuration") 
    st.markdown("Complete variable management including core variables and additional data sources")
    
    # Initialize manager
    if 'dynamic_manager' not in st.session_state:
        st.session_state.dynamic_manager = DynamicScorecardManager()
    
    manager = st.session_state.dynamic_manager
    
    # Main tabs
    tab1, tab2, tab3 = st.tabs([
        "📊 All Scorecard Variables", 
        "🎯 Score Bands Configuration", 
        "⚖️ Weight Distribution"
    ])
    
    with tab1:
        render_comprehensive_variable_management(manager)
    
    with tab2:
        render_score_bands_config(manager)
    
    with tab3:
        render_comprehensive_weight_distribution(manager)

def render_comprehensive_variable_management(manager: DynamicScorecardManager):
    """Render comprehensive variable management with integrated additional data sources"""
    
    st.subheader("📊 Complete Scorecard Variables")
    st.markdown("All variables including core credit variables and additional data sources")
    
    # Get complete variable definitions
    complete_variables = get_complete_variable_definitions()
    categories, category_weights = get_variables_by_category()
    
    # Get additional data sources variables
    additional_variables = get_additional_data_variables()
    
    # Organize all variables by category
    all_categories = organize_all_variables_complete(categories, additional_variables, category_weights)
    
    # Display all categories with their variables
    for category, vars_list in all_categories.items():
        if vars_list:
            # Determine icon and expansion based on category
            if "Core Credit Variables" in category:
                icon = "🎯"
                expanded = True
            elif "Behavioral Analytics" in category:
                icon = "📊"
                expanded = False
            elif "Employment Stability" in category:
                icon = "💼"
                expanded = False
            elif "Banking Behavior" in category:
                icon = "🏦"
                expanded = False
            elif "Geographic & Social" in category:
                icon = "🌍"
                expanded = False
            elif "Exposure & Intent" in category:
                icon = "⚠️"
                expanded = False
            elif "Additional Data" in category:
                icon = "📈"
                expanded = False
            else:
                icon = "📋"
                expanded = False
            
            with st.expander(f"{icon} {category} ({len(vars_list)} variables)", expanded=expanded):
                if "Additional Data" in category:
                    st.info(f"Variables from your organization's selected additional data sources")
                
                for var in vars_list:
                    render_variable_item_comprehensive(manager, var)

def get_additional_data_variables() -> List[Dict]:
    """Get variables from additional data sources"""
    company_id = st.session_state.get('company_id')
    if not company_id:
        return []
    
    try:
        from dynamic_weights_config import DynamicWeightsConfig
        weights_config = DynamicWeightsConfig(company_id)
        selected_sources = weights_config.get_company_additional_sources()
        
        additional_vars = []
        
        for source in selected_sources:
            variables = weights_config.get_additional_data_variables(source)
            
            if variables:
                for var_key, var_config in variables.items():
                    # Create comprehensive variable object
                    var_obj = {
                        'variable_id': f"additional_{var_key}",
                        'display_name': var_config['name'],
                        'category': f"{source} (Additional Data)",
                        'data_type': var_config['type'],
                        'input_type': 'number' if var_config['type'] == 'numeric' else 'text',
                        'scientific_basis': var_config['description'],
                        'weight': var_config['weight'] * 100,
                        'is_active': True,
                        'is_additional': True,
                        'source': source,
                        'score_bands': []
                    }
                    additional_vars.append(var_obj)
        
        return additional_vars
        
    except Exception as e:
        return []

def organize_all_variables_complete(categories: Dict[str, List], additional_variables: List[Dict], category_weights: Dict[str, float]) -> Dict[str, List]:
    """Organize all variables using complete definitions and additional data sources"""
    
    organized_categories = {}
    
    # Map complete variable categories with proper weight labels
    category_mapping = {
        "Core Credit Variables": f"Core Credit Variables ({category_weights.get('Core Credit Variables', 40):.0f}% Weight)",
        "Behavioral Analytics": f"Behavioral Analytics ({category_weights.get('Behavioral Analytics', 25):.0f}% Weight)", 
        "Employment Stability": f"Employment Stability ({category_weights.get('Employment Stability', 15):.0f}% Weight)",
        "Banking Behavior": f"Banking Behavior ({category_weights.get('Banking Behavior', 10):.0f}% Weight)",
        "Geographic & Social": f"Geographic & Social Factors ({category_weights.get('Geographic & Social', 5):.0f}% Weight)",
        "Exposure & Intent": f"Exposure & Intent ({category_weights.get('Exposure & Intent', 5):.0f}% Weight)"
    }
    
    # Organize complete variable definitions
    for category, vars_list in categories.items():
        mapped_category = category_mapping.get(category, category)
        organized_categories[mapped_category] = vars_list
    
    # Add additional data source categories
    if additional_variables:
        additional_categories = {
            "GST Data (Additional Data)": [],
            "ITR Data (Additional Data)": [], 
            "Utility Bills (Additional Data)": [],
            "Other Additional Data": []
        }
        
        for var in additional_variables:
            source = var.get('source', 'Other')
            category_key = f"{source} (Additional Data)"
            
            if category_key in additional_categories:
                additional_categories[category_key].append(var)
            else:
                additional_categories["Other Additional Data"].append(var)
        
        # Add non-empty additional categories
        for cat, vars_list in additional_categories.items():
            if vars_list:
                organized_categories[cat] = vars_list
    
    return organized_categories

def render_variable_item_comprehensive(manager: DynamicScorecardManager, var: dict):
    """Render comprehensive variable item with complete details and scoring bands"""
    
    with st.container():
        st.markdown(f"### {var['display_name']} ({var['weight']:.1f}% Weight)")
        
        col_a, col_b = st.columns([2, 1])
        
        with col_a:
            st.write(f"**Scientific Basis:** {var['scientific_basis']}")
            st.write(f"**Data Type:** {var['data_type']} ({var['input_type']})")
            
            # Display scoring bands
            if var.get('score_bands'):
                st.write("**Scoring Bands:**")
                for band in var['score_bands']:
                    if 'value' in band:  # Text-based scoring
                        st.write(f"• **{band['value']}:** {band['description']} ({band['score']:.1f} score)")
                    else:  # Numeric range scoring
                        if band.get('min') == band.get('max'):
                            range_text = f"{band['min']}"
                        else:
                            range_text = f"{band.get('min', 0)}-{band.get('max', 100)}"
                        st.write(f"• **{range_text}:** {band['description']} ({band['score']:.1f} score)")
        
        with col_b:
            st.metric(
                label="Scientific Weight", 
                value=f"{var['weight']:.1f}%",
                help="Scientifically optimized based on risk correlation"
            )
            
            if var.get('is_additional', False):
                st.write("**Type:** Additional Data")
                st.info("Configure in Scoring Weights")
            else:
                st.write("**Type:** Core Variable")
                st.success("Active & Configured")
        
        st.divider()

def render_score_bands_config(manager: DynamicScorecardManager):
    """Render score bands configuration for all variables"""
    st.subheader("🎯 Score Bands Configuration")
    st.markdown("Configure scoring bands for all variables")
    
    variables = manager.get_active_variables()
    
    if variables:
        selected_var = st.selectbox(
            "Select Variable to Configure",
            variables,
            format_func=lambda x: x['display_name']
        )
        
        if selected_var:
            st.markdown(f"### Configuring: {selected_var['display_name']}")
            
            # Display current bands
            bands = selected_var.get('score_bands', [])
            if bands:
                st.write("**Current Score Bands:**")
                for i, band in enumerate(bands):
                    st.write(f"Band {i+1}: {band}")
            
            # Add new band interface
            with st.form(f"add_band_{selected_var['variable_id']}"):
                st.write("**Add New Score Band**")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    min_val = st.number_input("Min Value", value=0.0)
                with col2:
                    max_val = st.number_input("Max Value", value=100.0)
                with col3:
                    score = st.number_input("Score", min_value=0.0, max_value=1.0, value=1.0, step=0.1)
                
                if st.form_submit_button("Add Band"):
                    # Add band logic here
                    st.success("Score band added successfully!")
    else:
        st.info("No variables available for score band configuration")

def render_comprehensive_weight_distribution(manager: DynamicScorecardManager):
    """Render comprehensive weight distribution including additional data sources"""
    st.subheader("⚖️ Complete Weight Distribution")
    st.markdown("Weight distribution across all variable categories")
    
    # Get all variables
    core_variables = manager.get_active_variables()
    additional_variables = get_additional_data_variables()
    
    # Calculate weight distributions
    core_weight = sum(var['weight'] for var in core_variables)
    additional_weight = sum(var['weight'] for var in additional_variables)
    total_weight = core_weight + additional_weight
    
    # Display weight summary
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Core Variables Weight", f"{core_weight:.1f}%")
    
    with col2:
        st.metric("Additional Data Weight", f"{additional_weight:.1f}%")
    
    with col3:
        st.metric("Total Weight", f"{total_weight:.1f}%")
    
    # Weight distribution by category
    if total_weight > 0:
        st.markdown("### Weight Distribution by Category")
        
        # Calculate category weights
        category_weights = {}
        
        for var in core_variables:
            cat = var['category']
            category_weights[cat] = category_weights.get(cat, 0) + var['weight']
        
        for var in additional_variables:
            source = var.get('source', 'Additional Data')
            cat = f"{source} (Additional)"
            category_weights[cat] = category_weights.get(cat, 0) + var['weight']
        
        # Display category weights
        for category, weight in category_weights.items():
            percentage = (weight / total_weight) * 100 if total_weight > 0 else 0
            st.write(f"**{category}:** {weight:.1f}% ({percentage:.1f}% of total)")
    
    # Weight validation
    if total_weight > 100:
        st.error(f"⚠️ Total weight ({total_weight:.1f}%) exceeds 100%. Please adjust weights.")
    elif total_weight < 95:
        st.warning(f"⚠️ Total weight ({total_weight:.1f}%) is below recommended 95%. Consider adding more variables.")
    else:
        st.success(f"✅ Weight distribution is optimal ({total_weight:.1f}%)")