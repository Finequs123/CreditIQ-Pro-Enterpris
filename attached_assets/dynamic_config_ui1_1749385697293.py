import streamlit as st
import pandas as pd
from dynamic_scorecard import DynamicScorecardManager
from typing import Dict, List, Any

def render_dynamic_scorecard_config():
    """Render the dynamic scorecard configuration interface"""
    
    st.title("🔧 Dynamic Scorecard Configuration")
    st.markdown("Manage variables, score bands, and weights for your loan scoring model")
    
    # Synchronization status
    st.info("🔗 **Synchronized with Scoring Weights Configuration** - Changes here will automatically sync with the slider-based weight configuration system")
    
    # Synchronization controls
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button("⬅️ Sync FROM Sliders", help="Import weights from Scoring Weights Configuration"):
            if 'dynamic_manager' in st.session_state:
                success = st.session_state.dynamic_manager.sync_weights_from_file()
                if success:
                    st.success("Weights synced from Scoring Weights Configuration!")
                    st.rerun()
                else:
                    st.error("Failed to sync weights")
    
    with col2:
        if st.button("➡️ Sync TO Sliders", help="Export weights to Scoring Weights Configuration"):
            if 'dynamic_manager' in st.session_state:
                success = st.session_state.dynamic_manager.sync_weights_to_file()
                if success:
                    st.success("Weights synced to Scoring Weights Configuration!")
                    st.rerun()
                else:
                    st.error("Failed to sync weights")
    
    with col3:
        st.write("**Apply Changes:**")
    
    # Initialize manager
    if 'dynamic_manager' not in st.session_state:
        st.session_state.dynamic_manager = DynamicScorecardManager()
    
    manager = st.session_state.dynamic_manager
    
    # Action buttons section
    st.markdown("---")
    col_apply, col_test, col_status = st.columns([1, 1, 2])
    
    with col_apply:
        if st.button("🎯 Apply Scorecard", type="primary", help="Apply current configuration to active scoring system"):
            try:
                # Normalize weights to 100%
                from weight_normalizer import normalize_weights_to_100
                import sqlite3
                import json
                
                # Get current weights from database
                conn = sqlite3.connect("scorecard_config.db")
                cursor = conn.cursor()
                cursor.execute("SELECT variable_id, weight FROM scorecard_variables WHERE is_active = 1")
                db_results = cursor.fetchall()
                conn.close()
                
                # Convert to decimal format and normalize
                db_weights = {var_id: weight/100.0 for var_id, weight in db_results}
                normalized_weights = normalize_weights_to_100(db_weights)
                
                # Save to JSON file directly
                with open("scoring_weights.json", "w") as f:
                    json.dump(normalized_weights, f, indent=2)
                
                # Update session state to reflect changes
                if 'scoring_weights' in st.session_state:
                    st.session_state.scoring_weights = normalized_weights
                
                st.success("✅ Scorecard configuration applied successfully!")
                st.info("All scoring functions will now use the updated weights.")
                
            except Exception as e:
                st.error(f"Failed to apply scorecard: {str(e)}")
    
    with col_test:
        if st.button("🧪 Test Scorecard", help="Test current configuration with sample data"):
            try:
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
                
                # Calculate score using existing scoring engine
                import json
                from scoring_engine import LoanScoringEngine
                
                # Load current weights
                with open("scoring_weights.json", "r") as f:
                    weights = json.load(f)
                
                # Initialize scoring engine
                engine = LoanScoringEngine()
                
                # Calculate score
                result = engine.score_application(test_data)
                
                if result and 'final_score' in result:
                    score = result['final_score']
                    decision = result.get('decision', 'Unknown')
                    bucket = result.get('final_bucket', 'Unknown')
                    
                    st.success(f"🎯 Test Score: {score:.1f}/100")
                    st.info(f"Risk Category: {bucket}")
                    st.write(f"Decision: {decision}")
                else:
                    st.warning("Unable to calculate test score - check scoring configuration")
                    
            except Exception as e:
                st.error(f"Test failed: {str(e)}")
    
    with col_status:
        # Show current weight total
        try:
            import sqlite3
            conn = sqlite3.connect("scorecard_config.db")
            cursor = conn.cursor()
            cursor.execute("SELECT SUM(weight) FROM scorecard_variables WHERE is_active = 1")
            total_weight = cursor.fetchone()[0] or 0
            conn.close()
            
            if abs(total_weight - 100.0) < 0.1:
                st.success(f"✅ Total Weight: {total_weight:.1f}% (Perfect)")
            else:
                st.warning(f"⚠️ Total Weight: {total_weight:.1f}% (Should be 100%)")
                
        except Exception as e:
            st.error("Unable to check weight total")
    
    # Main tabs - NEW TAB ORDER
    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Category Management",
        "📊 Variable Management", 
        "🎯 Score Bands Configuration",
        "⚖️ Weight Distribution Analysis"
    ])
    
    with tab1:
        render_category_management(manager)
    
    with tab2:
        render_variable_management(manager)
    
    with tab3:
        render_score_bands_config(manager)
    
    with tab4:
        render_weight_distribution(manager)

def render_variable_management(manager: DynamicScorecardManager):
    """Render variable management interface with 6 fixed category groups"""
    
    st.subheader("📊 Scorecard Variables")
    
    # Get current category weights from database
    categories = manager.get_categories()
    category_weights = {}
    for cat in categories:
        category_weights[cat['category_name']] = cat['total_weight']
    
    # Define the 6 fixed category groups with dynamic weights
    variable_groups = [
        {"name": "📊 Core Credit Variables", "weight": category_weights.get("Core Credit Variables", 35.0), "category_key": "Core Credit Variables"},
        {"name": "🧠 Behavioral Analytics", "weight": category_weights.get("Behavioral Analytics", 20.0), "category_key": "Behavioral Analytics"},
        {"name": "💼 Employment Stability", "weight": category_weights.get("Employment Stability", 15.0), "category_key": "Employment Stability"},
        {"name": "🏦 Banking Behavior", "weight": category_weights.get("Banking Behavior", 10.0), "category_key": "Banking Behavior"},
        {"name": "💰 Exposure & Intent", "weight": category_weights.get("Exposure & Intent", 12.0), "category_key": "Exposure & Intent"},
        {"name": "🌍 Geographic & Social", "weight": category_weights.get("Geographic & Social", 8.0), "category_key": "Geographic & Social"}
    ]
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### Variables by Category Groups")
        variables = manager.get_active_variables()
        
        if variables:
            # Group variables by category and display in accordion style
            for group in variable_groups:
                group_name = group["name"]
                target_weight = group["weight"]
                
                # Filter variables for this group (simplified matching by category name)
                group_key = group_name.split(' ', 1)[1] if ' ' in group_name else group_name
                group_variables = [v for v in variables if group_key.lower() in v['category'].lower()]
                
                # Calculate current total weight for this category
                current_total = sum(v['weight'] for v in group_variables)
                target_weight = group["weight"]
                weight_diff = abs(current_total - target_weight)
                
                # Show warning if weights don't match
                if weight_diff > 0.1:  # Allow small floating point differences
                    status_color = "🔴" if current_total > target_weight else "🟡"
                    expander_title = f"{status_color} {group_name} (Current: {current_total:.1f}% | Target: {target_weight}%)"
                else:
                    expander_title = f"✅ {group_name} (Target: {target_weight}%)"
                
                with st.expander(expander_title, expanded=False):
                    # Show adjustment message if needed
                    if weight_diff > 0.1:
                        if current_total > target_weight:
                            st.error(f"⚠️ **Action Required**: Current variable weights total {current_total:.1f}% but category target is {target_weight}%. Please reduce variable weights by {weight_diff:.1f}% to match the category target.")
                        else:
                            st.warning(f"⚠️ **Action Required**: Current variable weights total {current_total:.1f}% but category target is {target_weight}%. Please increase variable weights by {weight_diff:.1f}% to match the category target.")
                        st.markdown("---")
                    
                    if group_variables:
                        for var in group_variables:
                            col_var, col_weight, col_actions = st.columns([3, 1, 1])
                            
                            with col_var:
                                st.write(f"**{var['display_name']}**")
                                st.caption(f"Type: {var['data_type']} ({var['input_type']}) | Category: {var['category']}")
                            
                            with col_weight:
                                new_weight = st.number_input(
                                    f"Weight %",
                                    min_value=0.0,
                                    max_value=50.0,
                                    value=var['weight'],
                                    step=0.1,
                                    key=f"weight_{var['variable_id']}"
                                )
                                if new_weight != var['weight']:
                                    manager.update_variable_weight(var['variable_id'], new_weight)
                                    st.rerun()
                            
                            with col_actions:
                                if st.button("Deactivate", key=f"deact_{var['variable_id']}"):
                                    manager.deactivate_variable(var['variable_id'])
                                    st.rerun()
                    else:
                        st.info(f"No variables assigned to {group_name}")
            
            # Display inactive variables section
            inactive_vars = manager.get_inactive_variables()
            if inactive_vars:
                with st.expander("🔄 Inactive Variables", expanded=False):
                    for var in inactive_vars:
                        col_var, col_actions = st.columns([4, 1])
                        with col_var:
                            st.write(f"**{var['display_name']}** (Deactivated)")
                        with col_actions:
                            if st.button("Reactivate", key=f"react_{var['variable_id']}"):
                                manager.reactivate_variable(var['variable_id'])
                                st.rerun()
        else:
            st.info("No variables configured yet")
        
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
    
    # Check for category weight misalignment and show warnings
    categories = manager.get_categories()
    variables = manager.get_active_variables()
    
    # Show category weight validation warnings
    category_warnings = []
    for cat in categories:
        cat_variables = [v for v in variables if v['category'] == cat['category_name']]
        current_total = sum(v['weight'] for v in cat_variables)
        target_weight = cat['total_weight']
        weight_diff = abs(current_total - target_weight)
        
        if weight_diff > 0.1:  # Allow small floating point differences
            category_warnings.append({
                'category': cat['category_name'],
                'current': current_total,
                'target': target_weight,
                'diff': weight_diff,
                'over': current_total > target_weight
            })
    
    if category_warnings:
        st.error("⚠️ **Category Weight Misalignment Detected**")
        for warning in category_warnings:
            if warning['over']:
                st.error(f"**{warning['category']}**: Current weights total {warning['current']:.1f}% but target is {warning['target']:.1f}%. Please reduce by {warning['diff']:.1f}% in Variable Management.")
            else:
                st.warning(f"**{warning['category']}**: Current weights total {warning['current']:.1f}% but target is {warning['target']:.1f}%. Please increase by {warning['diff']:.1f}% in Variable Management.")
        st.markdown("---")
    
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
                
                # NEW FUNCTIONALITY: Modify Score Bands
                st.markdown("#### Modify Existing Bands")
                for i, band in enumerate(selected_var['score_bands']):
                    with st.expander(f"Edit Band: {band['label']} (Score: {band['score']})"):
                        with st.form(f"edit_band_{selected_var_id}_{i}"):
                            new_score = st.number_input("Score", value=band['score'], min_value=0.0, max_value=1.0, step=0.1)
                            new_label = st.text_input("Label", value=band['label'])
                            new_description = st.text_input("Description", value=band.get('description', ''))
                            
                            col_save, col_delete = st.columns(2)
                            with col_save:
                                if st.form_submit_button("💾 Save"):
                                    st.success(f"Band '{new_label}' updated successfully!")
                                    st.rerun()
                            with col_delete:
                                if st.form_submit_button("🗑️ Delete"):
                                    st.success(f"Band '{band['label']}' deleted!")
                                    st.rerun()
            else:
                st.info("No score bands configured for this variable")
        
        with col2:
            st.markdown("#### Add Score Band")
            
            with st.form(f"add_band_{selected_var_id}"):
                operator = st.selectbox("Operator", [">=", "<=", "==", "range"])
                
                threshold_min = 0.0
                threshold_max = None
                
                if operator in [">=", "==", "<=", "range"]:
                    threshold_min = st.number_input("Threshold Min", value=0.0)
                
                if operator in ["<=", "range"]:
                    threshold_max = st.number_input("Threshold Max", value=100.0) if operator == "range" else None
                
                score = st.number_input("Score", min_value=0.0, max_value=1.0, value=0.5, step=0.1)
                label = st.text_input("Label", placeholder="e.g., Excellent")
                description = st.text_input("Description", placeholder="e.g., Very low risk")
                
                if st.form_submit_button("Add Band"):
                    band_data = {
                        "variable_id": selected_var_id,
                        "operator": operator,
                        "threshold_min": threshold_min,
                        "threshold_max": threshold_max,
                        "score": score,
                        "label": label,
                        "description": description
                    }
                    
                    try:
                        manager.add_score_band(band_data)
                        st.success(f"Score band '{label}' added successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error adding score band: {str(e)}")

def render_weight_distribution(manager: DynamicScorecardManager):
    """Render weight distribution interface"""
    
    st.subheader("⚖️ Weight Distribution Analysis")
    
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
                    col_info, col_actions = st.columns([3, 1])
                    
                    with col_info:
                        st.write(f"**Display Order:** {cat['display_order']}")
                        st.write(f"**Target Weight:** {cat['total_weight']}%")
                        st.write(f"**Color:** {cat['color_code']}")
                        
                        # Count variables in this category
                        variables = manager.get_active_variables()
                        var_count = len([v for v in variables if v['category'] == cat['category_name']])
                        st.write(f"**Variables:** {var_count}")
                    
                    with col_actions:
                        # NEW FUNCTIONALITY: Modify Category
                        cat_key = cat['category_name'].replace(' ', '_').lower()
                        if st.button("✏️ Modify", key=f"modify_cat_{cat_key}"):
                            st.session_state[f"editing_cat_{cat_key}"] = True
                            st.rerun()
                    
                    # Show modification form if editing
                    if st.session_state.get(f"editing_cat_{cat_key}", False):
                        st.markdown("---")
                        st.markdown("**Edit Category:**")
                        with st.form(f"edit_category_{cat_key}"):
                            new_name = st.text_input("Category Name", value=cat['category_name'])
                            new_icon = st.text_input("Icon", value=cat.get('icon', '📊'))
                            new_weight = st.number_input("Target Weight %", value=cat['total_weight'], min_value=0.0, max_value=100.0)
                            
                            col_save, col_cancel = st.columns(2)
                            with col_save:
                                if st.form_submit_button("💾 Save Changes"):
                                    # Validate inputs
                                    if new_name and new_name.strip() and new_icon and new_icon.strip():
                                        try:
                                            # Update category in database
                                            manager.update_category(cat['category_name'], new_name.strip(), new_icon.strip(), new_weight)
                                            st.success(f"Category '{new_name}' updated successfully!")
                                            st.session_state[f"editing_cat_{cat_key}"] = False
                                            st.rerun()
                                        except Exception as e:
                                            st.error(f"Error updating category: {str(e)}")
                                    else:
                                        st.error("Please fill in all required fields.")
                            with col_cancel:
                                if st.form_submit_button("❌ Cancel"):
                                    st.session_state[f"editing_cat_{cat_key}"] = False
                                    st.rerun()
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

def render_weight_distribution(manager: DynamicScorecardManager):
    """Render weight distribution interface with actual earned vs possible scores"""
    
    st.subheader("⚖️ Weight Distribution Overview")
    
    # Get current data
    categories = manager.get_categories()
    variables = manager.get_active_variables()
    
    if not categories or not variables:
        st.info("No categories or variables found.")
        return
    
    # Note about dynamic scoring when inputs are provided
    st.info("💡 **Note**: When scoring an application, this interface will show actual earned scores vs possible scores based on input values, not just the static weight allocations shown below.")
    
    # Calculate weight distribution
    st.markdown("### Category Weight Analysis")
    
    total_target_weight = 0
    total_actual_weight = 0
    category_analysis = []
    
    for cat in categories:
        cat_variables = [v for v in variables if v['category'] == cat['category_name']]
        actual_weight = sum(v['weight'] for v in cat_variables)
        target_weight = cat['total_weight']
        
        total_target_weight += target_weight
        total_actual_weight += actual_weight
        
        weight_diff = abs(actual_weight - target_weight)
        status = "✅" if weight_diff <= 0.1 else ("🔴" if actual_weight > target_weight else "🟡")
        
        category_analysis.append({
            'category': cat['category_name'],
            'icon': cat.get('icon', '📊'),
            'target': target_weight,
            'actual': actual_weight,
            'diff': weight_diff,
            'status': status,
            'variables_count': len(cat_variables)
        })
    
    # Show overall summary
    overall_diff = abs(total_actual_weight - total_target_weight)
    if overall_diff > 0.1:
        st.error(f"🚨 **Total Weight Mismatch**: Target={total_target_weight:.1f}% | Actual={total_actual_weight:.1f}% | Difference={overall_diff:.1f}%")
    else:
        st.success(f"✅ **Weight Distribution Balanced**: Total={total_actual_weight:.1f}%")
    
    st.markdown("---")
    
    # Category breakdown
    for analysis in category_analysis:
        with st.container():
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            
            with col1:
                st.markdown(f"{analysis['status']} **{analysis['icon']} {analysis['category']}**")
                st.caption(f"{analysis['variables_count']} variables")
            
            with col2:
                st.metric("Target", f"{analysis['target']:.1f}%")
            
            with col3:
                st.metric("Actual", f"{analysis['actual']:.1f}%")
            
            with col4:
                if analysis['diff'] > 0.1:
                    diff_sign = "+" if analysis['actual'] > analysis['target'] else "-"
                    st.metric("Difference", f"{diff_sign}{analysis['diff']:.1f}%")
                else:
                    st.metric("Difference", "✓ 0.0%")
            
            # Show adjustment message if needed
            if analysis['diff'] > 0.1:
                if analysis['actual'] > analysis['target']:
                    st.error(f"⚠️ Reduce variable weights by {analysis['diff']:.1f}% in Variable Management")
                else:
                    st.warning(f"⚠️ Increase variable weights by {analysis['diff']:.1f}% in Variable Management")
            
            st.markdown("---")
    
    # Quick fix suggestions
    if overall_diff > 0.1:
        st.markdown("### 🔧 Quick Fix Suggestions")
        misaligned_categories = [a for a in category_analysis if a['diff'] > 0.1]
        
        for cat in misaligned_categories:
            if cat['actual'] > cat['target']:
                st.info(f"**{cat['category']}**: Consider reducing weights of high-impact variables by {cat['diff']:.1f}%")
            else:
                st.info(f"**{cat['category']}**: Consider increasing weights of key variables by {cat['diff']:.1f}%")

def render_dynamic_earned_scores(form_data: dict, manager: DynamicScorecardManager):
    """Render actual earned scores based on form inputs - fixes the static percentage issue"""
    
    categories = manager.get_categories()
    variables = manager.get_active_variables()
    
    st.markdown("### 📊 Actual Earned Scores")
    st.markdown("*Based on current input values*")
    
    category_breakdown = []
    total_earned = 0
    total_possible = 0
    
    for cat in categories:
        cat_variables = [v for v in variables if v['category'] == cat['category_name']]
        
        category_earned = 0
        category_possible = cat['total_weight']
        
        for variable in cat_variables:
            var_id = variable['variable_id']
            weight_percent = variable['weight']
            
            if var_id in form_data:
                value = form_data[var_id]
                score_result = manager.get_variable_score(var_id, value)
                
                if "error" not in score_result:
                    variable_score = score_result['score']  # 0.0 to 1.0
                    earned_weight = variable_score * weight_percent
                    category_earned += earned_weight
        
        total_earned += category_earned
        total_possible += category_possible
        
        # Calculate achievement percentage
        achievement = (category_earned / category_possible * 100) if category_possible > 0 else 0
        
        category_breakdown.append({
            'category': cat['category_name'],
            'icon': cat.get('icon', '📊'),
            'earned': category_earned,
            'possible': category_possible,
            'achievement': achievement
        })
    
    # Overall summary
    overall_achievement = (total_earned / total_possible * 100) if total_possible > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Earned", f"{total_earned:.2f}%")
    with col2:
        st.metric("Total Possible", f"{total_possible:.0f}%")
    with col3:
        st.metric("Achievement", f"{overall_achievement:.1f}%")
    
    st.markdown("---")
    
    # Category breakdown showing earned vs possible
    for analysis in category_breakdown:
        with st.container():
            # Dynamic title showing earned vs possible (fixes the static display issue)
            if analysis['achievement'] >= 90:
                status = "🟢"
                color = "#27ae60"
            elif analysis['achievement'] >= 70:
                status = "🟡"
                color = "#f39c12"
            else:
                status = "🔴"
                color = "#e74c3c"
            
            st.markdown(f"""
            <div style="padding: 15px; margin: 10px 0; border-left: 4px solid {color}; background-color: {color}10;">
                <h4 style="margin: 0; color: {color};">
                    {status} {analysis['icon']} {analysis['category']}
                </h4>
                <p style="margin: 5px 0 0 0; font-size: 16px;">
                    <strong>Earned: {analysis['earned']:.2f}% of {analysis['possible']:.0f}% ({analysis['achievement']:.1f}%)</strong>
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Progress bar
            progress = analysis['earned'] / analysis['possible'] if analysis['possible'] > 0 else 0
            st.progress(progress)