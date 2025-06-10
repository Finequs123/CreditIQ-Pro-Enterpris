import streamlit as st
import pandas as pd
from dynamic_scorecard import DynamicScorecardManager
from typing import Dict, List, Any

def render_variable_item(manager: DynamicScorecardManager, var: dict):
    """Render individual variable item"""
    with st.container():
        col_a, col_b, col_c = st.columns([2, 1, 1])
        
        with col_a:
            st.write(f"**{var['display_name']}**")
            st.write(f"Type: {var['data_type']} ({var['input_type']})")
            if var['scientific_basis']:
                st.write(f"Basis: {var['scientific_basis'][:100]}...")
        
        with col_b:
            st.metric(
                label="AI Weight", 
                value=f"{var['weight']:.1f}%",
                help="Scientifically optimized weight"
            )
        
        with col_c:
            is_active = var.get('is_active', True)
            if st.button(
                "🔴 Deactivate" if is_active else "🟢 Activate",
                key=f"toggle_{var['variable_id']}",
                type="secondary" if is_active else "primary"
            ):
                if is_active:
                    manager.deactivate_variable(var['variable_id'])
                    st.success(f"Deactivated {var['display_name']}")
                else:
                    manager.reactivate_variable(var['variable_id'])
                    st.success(f"Activated {var['display_name']}")
                st.rerun()

def render_additional_data_sources_sections():
    """Render additional data sources sections based on company configuration"""
    company_id = st.session_state.get('company_id')
    if not company_id:
        return
    
    try:
        from dynamic_weights_config import DynamicWeightsConfig
        weights_config = DynamicWeightsConfig(company_id)
        selected_sources = weights_config.get_company_additional_sources()
        
        if selected_sources:
            st.markdown("---")
            st.markdown("### 📈 Additional Data Sources")
            st.write(f"Configure variables for your organization's {len(selected_sources)} additional data sources:")
            
            for source in selected_sources:
                variables = weights_config.get_additional_data_variables(source)
                
                if variables:
                    with st.expander(f"📊 {source}", expanded=False):
                        for var_key, var_config in variables.items():
                            with st.container():
                                col_a, col_b, col_c = st.columns([2, 1, 1])
                                
                                with col_a:
                                    st.write(f"**{var_config['name']}**")
                                    st.write(f"Type: {var_config['type']}")
                                    st.write(f"Description: {var_config['description']}")
                                
                                with col_b:
                                    st.metric(
                                        label="Default Weight", 
                                        value=f"{var_config['weight'] * 100:.1f}%",
                                        help="Configure in Scoring Weights Configuration"
                                    )
                                
                                with col_c:
                                    st.write("**Status:** Available")
                                    st.write("**Category:** Additional Data")
                
                st.write("")  # Add spacing
    
    except Exception as e:
        st.info("Additional data sources configuration available in company settings.")

def render_dynamic_scorecard_config():
    """Render the dynamic scorecard configuration interface"""
    
    st.title("🔧 Dynamic Scorecard Configuration") 
    st.markdown("Manage variables and score bands for your loan scoring model. Weights are AI-optimized and protected.")
    
    # Initialize manager
    if 'dynamic_manager' not in st.session_state:
        st.session_state.dynamic_manager = DynamicScorecardManager()
    
    manager = st.session_state.dynamic_manager
    
    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Variable Management", 
        "🎯 Score Bands Configuration", 
        "⚖️ Weight Distribution", 
        "📋 Category Management"
    ])
    
    with tab1:
        render_variable_management(manager)
    
    with tab2:
        render_score_bands_config(manager)
    
    with tab3:
        render_weight_distribution(manager)
    
    with tab4:
        render_category_management(manager)

def render_variable_management(manager: DynamicScorecardManager):
    """Render variable management interface"""
    
    st.subheader("📊 Scorecard Variables")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### Current Variables")
        variables = manager.get_active_variables()
        
        if variables:
            # Organize variables by category
            categories = {}
            for var in variables:
                cat = var['category']
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append(var)
            
            # Display Core Credit Variables
            if 'Core Credit Variables' in categories:
                with st.expander("🎯 Core Credit Variables", expanded=True):
                    for var in categories['Core Credit Variables']:
                        render_variable_item(manager, var)
            
            # Display Behavioral Analytics
            if 'Behavioral Analytics' in categories:
                with st.expander("📊 Behavioral Analytics", expanded=False):
                    for var in categories['Behavioral Analytics']:
                        render_variable_item(manager, var)
            
            # Display Employment Stability
            if 'Employment Stability' in categories:
                with st.expander("💼 Employment Stability", expanded=False):
                    for var in categories['Employment Stability']:
                        render_variable_item(manager, var)
            
            # Display Banking Behavior
            if 'Banking Behavior' in categories:
                with st.expander("🏦 Banking Behavior", expanded=False):
                    for var in categories['Banking Behavior']:
                        render_variable_item(manager, var)
            
            # Display Geographic & Social
            if 'Geographic & Social' in categories:
                with st.expander("🌍 Geographic & Social", expanded=False):
                    for var in categories['Geographic & Social']:
                        render_variable_item(manager, var)
            
            # Display Exposure & Intent
            if 'Exposure & Intent' in categories:
                with st.expander("⚠️ Exposure & Intent", expanded=False):
                    for var in categories['Exposure & Intent']:
                        render_variable_item(manager, var)
            
            # Integrate additional data sources into existing categories
            render_integrated_additional_data_sources()
            
            # Display any other categories
            core_categories = ['Core Credit Variables', 'Behavioral Analytics', 'Employment Stability', 
                             'Banking Behavior', 'Geographic & Social', 'Exposure & Intent']
            for cat, vars_list in categories.items():
                if cat not in core_categories:
                    with st.expander(f"📈 {cat}", expanded=False):
                        for var in vars_list:
                            render_variable_item(manager, var)
        else:
            st.info("No active variables found. Add some variables to get started.")
        
        # Show inactive variables section
        st.markdown("### Inactive Variables")
        inactive_variables = manager.get_inactive_variables()
        
        if inactive_variables:
            st.warning(f"Found {len(inactive_variables)} deactivated variables")
            
            for var in inactive_variables:
                with st.expander(f"🔍 {var['display_name']} (DEACTIVATED - {var['weight']}% weight)"):
                    col_a, col_b = st.columns([3, 1])
                    
                    with col_a:
                        st.write(f"**Category:** {var['category']}")
                        st.write(f"**Type:** {var['data_type']} ({var['input_type']})")
                        st.write(f"**Scientific Basis:** {var['scientific_basis']}")
                        st.write(f"**Score Bands:** {len(var['score_bands'])}")
                        st.write(f"**Deactivated:** {var['updated_at'][:10]}")
                    
                    with col_b:
                        if st.button(f"🔄 Reactivate", key=f"reactivate_{var['variable_id']}"):
                            manager.reactivate_variable(var['variable_id'])
                            st.success(f"Variable {var['display_name']} reactivated!")
                            st.rerun()
        else:
            st.info("No inactive variables found.")
    
    with col2:
        st.markdown("### Add New Variable")
        
        with st.form("add_variable_form"):
            var_id = st.text_input("Variable ID", placeholder="e.g., debt_to_income")
            display_name = st.text_input("Display Name", placeholder="e.g., Debt to Income Ratio")
            
            categories = [cat['category_name'] for cat in manager.get_categories()]
            category = st.selectbox("Category", categories)
            
            col_type1, col_type2 = st.columns(2)
            with col_type1:
                data_type = st.selectbox("Data Type", ["integer", "float", "text"])
            with col_type2:
                input_type = st.selectbox("Input Type", ["number", "selectbox", "text_input"])
            
            weight = st.number_input("Weight %", min_value=0.0, max_value=50.0, value=1.0, step=0.5)
            
            col_range1, col_range2 = st.columns(2)
            with col_range1:
                min_value = st.number_input("Min Value", value=0.0) if data_type != "text" else None
            with col_range2:
                max_value = st.number_input("Max Value", value=100.0) if data_type != "text" else None
            
            default_value = st.text_input("Default Value", placeholder="Default input value")
            help_text = st.text_area("Help Text", placeholder="User guidance for this field")
            scientific_basis = st.text_area("Scientific Basis", placeholder="Why this variable matters for credit risk")
            
            is_required = st.checkbox("Required Field", value=True)
            
            if st.form_submit_button("Add Variable"):
                if var_id and display_name:
                    variable_data = {
                        "variable_id": var_id,
                        "display_name": display_name,
                        "category": category,
                        "weight": weight,
                        "data_type": data_type,
                        "input_type": input_type,
                        "min_value": min_value,
                        "max_value": max_value,
                        "default_value": default_value,
                        "help_text": help_text,
                        "scientific_basis": scientific_basis,
                        "is_required": is_required
                    }
                    
                    try:
                        manager.add_variable(variable_data)
                        st.success(f"Variable '{display_name}' added successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error adding variable: {str(e)}")
                else:
                    st.error("Variable ID and Display Name are required")

def render_score_bands_config(manager: DynamicScorecardManager):
    """Render score bands configuration interface"""
    
    st.subheader("🎯 Score Bands Configuration")
    
    variables = manager.get_active_variables()
    
    if not variables:
        st.info("No active variables found. Please add variables first.")
        return
    
    # Select variable to configure
    var_names = [f"{var['display_name']} ({var['variable_id']})" for var in variables]
    selected_var_display = st.selectbox("Select Variable to Configure", var_names)
    
    if selected_var_display:
        # Extract variable ID
        selected_var_id = selected_var_display.split('(')[1].split(')')[0]
        selected_var = next(var for var in variables if var['variable_id'] == selected_var_id)
        
        st.markdown(f"### Configuring: {selected_var['display_name']}")
        st.markdown(f"**Scientific Basis:** {selected_var['scientific_basis']}")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("#### Current Score Bands")
            
            if selected_var['score_bands']:
                bands_data = []
                for band in selected_var['score_bands']:
                    threshold_text = ""
                    if band['operator'] == '>=':
                        threshold_text = f">= {band['threshold_min']}"
                    elif band['operator'] == '<=':
                        threshold_text = f"<= {band['threshold_max']}"
                    elif band['operator'] == '==':
                        threshold_text = f"= {band['threshold_min']}"
                    elif band['operator'] == 'range':
                        if band['threshold_max']:
                            threshold_text = f"{band['threshold_min']} - {band['threshold_max']}"
                        else:
                            threshold_text = f">= {band['threshold_min']}"
                    
                    bands_data.append({
                        "Threshold": threshold_text,
                        "Score": band['score'],
                        "Label": band['label'],
                        "Description": band['description']
                    })
                
                df_bands = pd.DataFrame(bands_data)
                st.dataframe(df_bands, use_container_width=True)
            else:
                st.info("No score bands configured for this variable")
        
        with col2:
            st.markdown("#### Add Score Band")
            
            with st.form(f"add_band_{selected_var_id}"):
                operator = st.selectbox("Operator", [">=", "<=", "==", "range"])
                
                if operator in [">=", "==", "<=", "range"]:
                    threshold_min = st.number_input("Threshold Min", value=0.0)
                
                if operator in ["<=", "range"]:
                    threshold_max = st.number_input("Threshold Max", value=100.0) if operator == "range" else None
                else:
                    threshold_max = None
                
                score = st.number_input("Score", min_value=0.0, max_value=1.0, value=0.5, step=0.1)
                label = st.text_input("Label", placeholder="e.g., Excellent")
                description = st.text_input("Description", placeholder="e.g., Very low risk")
                
                if st.form_submit_button("Add Band"):
                    band_data = {
                        "variable_id": selected_var_id,
                        "band_order": len(selected_var['score_bands']),
                        "threshold_min": threshold_min if operator in [">=", "==", "range"] else None,
                        "threshold_max": threshold_max,
                        "operator": operator,
                        "score": score,
                        "label": label,
                        "description": description
                    }
                    
                    try:
                        manager.add_score_band(band_data)
                        st.success("Score band added successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error adding score band: {str(e)}")

def render_weight_distribution(manager: DynamicScorecardManager):
    """Render weight distribution interface"""
    
    st.subheader("⚖️ AI-Optimized Weight Distribution")
    st.info("These weights are scientifically optimized from actual loan performance data and cannot be modified.")
    
    variables = manager.get_active_variables()
    categories = manager.get_categories()
    
    if not variables:
        st.info("No active variables found.")
        return
    
    # Calculate current weights by category
    weight_by_category = {}
    total_weight = 0
    
    for var in variables:
        category = var['category']
        weight = var['weight']
        
        if category not in weight_by_category:
            weight_by_category[category] = 0
        weight_by_category[category] += weight
        total_weight += weight
    
    # Display weight distribution
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("#### Category Weight Distribution")
        
        for category in weight_by_category:
            category_weight = weight_by_category[category]
            percentage = (category_weight / total_weight * 100) if total_weight > 0 else 0
            
            # Find category color
            cat_info = next((cat for cat in categories if cat['category_name'] == category), None)
            color = cat_info['color_code'] if cat_info else '#666666'
            
            st.markdown(f"""
            <div style="padding: 10px; margin: 5px 0; background: {color}20; border-left: 4px solid {color}; border-radius: 4px;">
                <strong>{category}</strong><br>
                Weight: {category_weight:.1f}% | Expected: {cat_info['total_weight']:.1f}%
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("#### Weight Validation")
        
        if abs(total_weight - 100) > 0.1:
            st.error(f"⚠️ Total weight is {total_weight:.1f}% (should be 100%)")
            st.warning("Please adjust variable weights to total exactly 100%")
        else:
            st.success(f"✅ Total weight is {total_weight:.1f}% (Perfect!)")
        
        # Show variables by weight
        st.markdown("#### Variables by Weight")
        sorted_vars = sorted(variables, key=lambda x: x['weight'], reverse=True)
        
        for var in sorted_vars:
            percentage = (var['weight'] / total_weight * 100) if total_weight > 0 else 0
            st.write(f"**{var['display_name']}**: {var['weight']:.1f}% ({percentage:.1f}% of total)")

def render_category_management(manager: DynamicScorecardManager):
    """Render category management interface"""
    
    st.subheader("📋 Category Management")
    
    categories = manager.get_categories()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### Current Categories")
        
        if categories:
            for cat in categories:
                with st.expander(f"{cat['icon']} {cat['category_name']} ({cat['total_weight']}%)"):
                    st.write(f"**Display Order:** {cat['display_order']}")
                    st.write(f"**Target Weight:** {cat['total_weight']}%")
                    st.write(f"**Color:** {cat['color_code']}")
                    
                    # Count variables in this category
                    variables = manager.get_active_variables()
                    var_count = len([v for v in variables if v['category'] == cat['category_name']])
                    st.write(f"**Variables:** {var_count}")
        else:
            st.info("No categories found.")
    
    with col2:
        st.markdown("### Add New Category")
        
        with st.form("add_category_form"):
            category_name = st.text_input("Category Name", placeholder="e.g., Risk Indicators")
            display_order = st.number_input("Display Order", min_value=1, value=len(categories) + 1)
            total_weight = st.number_input("Target Weight %", min_value=0.0, max_value=100.0, value=10.0)
            
            color_options = {
                "Red": "#e74c3c",
                "Blue": "#3498db", 
                "Green": "#27ae60",
                "Orange": "#e67e22",
                "Purple": "#9b59b6",
                "Brown": "#8b4513"
            }
            color_name = st.selectbox("Color", list(color_options.keys()))
            color_code = color_options[color_name]
            
            icon_options = ["📊", "🧠", "💼", "🏦", "💰", "🌍", "📈", "⚡", "🎯", "🔍"]
            icon = st.selectbox("Icon", icon_options)
            
            if st.form_submit_button("Add Category"):
                if category_name:
                    category_data = {
                        "category_name": category_name,
                        "display_order": display_order,
                        "total_weight": total_weight,
                        "color_code": color_code,
                        "icon": icon
                    }
                    
                    try:
                        manager.add_category(category_data)
                        st.success(f"Category '{category_name}' added successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error adding category: {str(e)}")
                else:
                    st.error("Category name is required")

def render_variable_item(manager: DynamicScorecardManager, var: dict):
    """Render individual variable item"""
    with st.container():
        col_a, col_b, col_c = st.columns([2, 1, 1])
        
        with col_a:
            st.write(f"**{var['display_name']}**")
            st.write(f"Type: {var['data_type']} ({var['input_type']})")
            if var['scientific_basis']:
                st.write(f"Basis: {var['scientific_basis'][:100]}...")
        
        with col_b:
            st.metric(
                label="AI Weight", 
                value=f"{var['weight']:.1f}%",
                help="Scientifically optimized weight"
            )
        
        with col_c:
            is_active = var.get('is_active', True)
            if st.button(
                "🔴 Deactivate" if is_active else "🟢 Activate",
                key=f"toggle_{var['variable_id']}",
                type="secondary" if is_active else "primary"
            ):
                if is_active:
                    manager.deactivate_variable(var['variable_id'])
                    st.success(f"Deactivated {var['display_name']}")
                else:
                    manager.reactivate_variable(var['variable_id'])
                    st.success(f"Activated {var['display_name']}")
                st.rerun()

def render_additional_data_sources_sections():
    """Render additional data sources sections based on company configuration"""
    company_id = st.session_state.get('company_id')
    if not company_id:
        return
    
    try:
        from dynamic_weights_config import DynamicWeightsConfig
        weights_config = DynamicWeightsConfig(company_id)
        selected_sources = weights_config.get_company_additional_sources()
        
        if selected_sources:
            st.markdown("---")
            st.markdown("### 📈 Additional Data Sources")
            st.write(f"Configure variables for your organization's {len(selected_sources)} additional data sources:")
            
            for source in selected_sources:
                variables = weights_config.get_additional_data_variables(source)
                
                if variables:
                    with st.expander(f"📊 {source}", expanded=False):
                        for var_key, var_config in variables.items():
                            with st.container():
                                col_a, col_b, col_c = st.columns([2, 1, 1])
                                
                                with col_a:
                                    st.write(f"**{var_config['name']}**")
                                    st.write(f"Type: {var_config['type']}")
                                    st.write(f"Description: {var_config['description']}")
                                
                                with col_b:
                                    st.metric(
                                        label="Default Weight", 
                                        value=f"{var_config['weight'] * 100:.1f}%",
                                        help="Configure in Scoring Weights Configuration"
                                    )
                                
                                with col_c:
                                    st.write("**Status:** Available")
                                    st.write("**Category:** Additional Data")
                
                st.write("")  # Add spacing
    
    except Exception as e:
        st.info("Additional data sources configuration available in company settings.")