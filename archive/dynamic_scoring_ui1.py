import streamlit as st
from typing import Dict, List, Any
from dynamic_scorecard import DynamicScorecardManager

def render_dynamic_individual_scoring():
    """Render dynamic individual scoring interface based on configured variables"""
    
    # Initialize dynamic manager
    if 'dynamic_manager' not in st.session_state:
        st.session_state.dynamic_manager = DynamicScorecardManager()
    
    manager = st.session_state.dynamic_manager
    form_config = manager.generate_form_config()
    
    st.title("🎯 Individual Loan Application Scoring")
    st.markdown("Comprehensive risk assessment using your configured scorecard variables")
    
    # Check if scorecard is properly configured
    if form_config["total_weight"] == 0:
        st.error("No active variables found. Please configure your scorecard first.")
        if st.button("Go to Configuration"):
            st.session_state.page = "Dynamic Configuration"
            st.rerun()
        return
    
    # Weight validation warning
    if abs(form_config["total_weight"] - 100) > 0.1:
        st.warning(f"⚠️ Total variable weights = {form_config['total_weight']:.1f}% (should be 100%)")
    
    # Initialize form data
    if 'form_data' not in st.session_state:
        st.session_state.form_data = {}
    
    # Render form by categories
    tabs = []
    tab_labels = []
    
    for category in form_config["categories"]:
        if category["category_name"] in form_config["variables_by_category"]:
            tab_labels.append(f"{category['icon']} {category['category_name']}")
            tabs.append(category["category_name"])
    
    if tabs:
        tab_objects = st.tabs(tab_labels)
        
        for i, tab in enumerate(tab_objects):
            with tab:
                category_name = tabs[i]
                variables = form_config["variables_by_category"][category_name]
                render_category_form(variables, category_name, manager)
    
    # Scoring button and results
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("🚀 Calculate Risk Score", type="primary", use_container_width=True):
            results = calculate_dynamic_score(st.session_state.form_data, manager)
            if results:
                render_dynamic_scoring_results(results, st.session_state.form_data, manager)

def render_category_form(variables: List[Dict], category_name: str, manager: DynamicScorecardManager):
    """Render form inputs for a category"""
    
    st.subheader(f"📋 {category_name}")
    
    # Calculate category weight
    category_weight = sum(var["weight"] for var in variables)
    st.markdown(f"**Category Weight:** {category_weight:.1f}%")
    
    # Create form inputs
    cols = st.columns(2)
    
    for i, variable in enumerate(variables):
        col = cols[i % 2]
        
        with col:
            render_variable_input(variable, manager)

def render_variable_input(variable: Dict, manager: DynamicScorecardManager):
    """Render individual variable input"""
    
    var_id = variable["id"]
    label = variable["label"]
    help_text = variable.get("help_text", "")
    
    # Create label with weight info
    display_label = f"{label} ({variable['weight']:.1f}%)"
    
    if variable["type"] == "number":
        if variable["data_type"] == "integer":
            value = st.number_input(
                display_label,
                min_value=int(variable["min_value"]) if variable["min_value"] else None,
                max_value=int(variable["max_value"]) if variable["max_value"] else None,
                value=int(variable["default_value"]) if variable["default_value"] else 0,
                help=help_text,
                key=f"input_{var_id}"
            )
        else:  # float
            value = st.number_input(
                display_label,
                min_value=float(variable["min_value"]) if variable["min_value"] else None,
                max_value=float(variable["max_value"]) if variable["max_value"] else None,
                value=float(variable["default_value"]) if variable["default_value"] else 0.0,
                step=0.01,
                help=help_text,
                key=f"input_{var_id}"
            )
    
    elif variable["type"] == "selectbox":
        # Get options from score bands
        options = get_selectbox_options(var_id, manager)
        value = st.selectbox(
            display_label,
            options,
            help=help_text,
            key=f"input_{var_id}"
        )
    
    else:  # text_input
        value = st.text_input(
            display_label,
            value=variable["default_value"] if variable["default_value"] else "",
            help=help_text,
            key=f"input_{var_id}"
        )
    
    # Store value in session state
    st.session_state.form_data[var_id] = value
    
    # Show real-time score preview
    if value is not None and value != "":
        score_result = manager.get_variable_score(var_id, value)
        if "error" not in score_result:
            score_color = get_score_color(score_result["score"])
            st.markdown(f"""
            <div style="padding: 5px; margin: 5px 0; background: {score_color}20; border-left: 3px solid {score_color}; border-radius: 3px; font-size: 0.8rem;">
                Score: {score_result['score']:.2f} | {score_result['label']}
            </div>
            """, unsafe_allow_html=True)

def get_selectbox_options(var_id: str, manager: DynamicScorecardManager) -> List[str]:
    """Get selectbox options from score bands"""
    variables = manager.get_active_variables()
    variable = next((v for v in variables if v['variable_id'] == var_id), None)
    
    if variable and variable['score_bands']:
        return [band['label'] for band in variable['score_bands']]
    
    return ["Option 1", "Option 2", "Option 3"]  # Default options

def get_score_color(score: float) -> str:
    """Get color based on score value"""
    if score >= 0.8:
        return "#27ae60"  # Green
    elif score >= 0.6:
        return "#f39c12"  # Orange
    elif score >= 0.4:
        return "#e67e22"  # Dark Orange
    else:
        return "#e74c3c"  # Red

def calculate_dynamic_score(form_data: Dict, manager: DynamicScorecardManager) -> Dict[str, Any]:
    """Calculate overall score using slider-based percentage mapping"""
    
    # Define slider mappings for direct percentage calculation
    slider_mappings = {
        # Core Credit Variables (35% total)
        'credit_score': {'min': 0, 'max': 20, 'weight': 10.0, 'category': 'Core Credit Variables'},
        'foir': {'min': 0, 'max': 15, 'weight': 8.0, 'category': 'Core Credit Variables'},
        'dpd_30_plus': {'min': 0, 'max': 15, 'weight': 6.0, 'category': 'Core Credit Variables'},
        'enquiry_count': {'min': 0, 'max': 10, 'weight': 6.0, 'category': 'Core Credit Variables'},
        'age': {'min': 0, 'max': 8, 'weight': 3.0, 'category': 'Core Credit Variables'},
        'monthly_income': {'min': 0, 'max': 15, 'weight': 2.0, 'category': 'Core Credit Variables'},
        
        # Behavioral Analytics (20% total)
        'credit_vintage_months': {'min': 0, 'max': 10, 'weight': 6.0, 'category': 'Behavioral Analytics'},
        'loan_mix_type': {'min': 0, 'max': 8, 'weight': 4.0, 'category': 'Behavioral Analytics'},
        'loan_completion_ratio': {'min': 0, 'max': 10, 'weight': 5.0, 'category': 'Behavioral Analytics'},
        'defaulted_loans': {'min': 0, 'max': 10, 'weight': 5.0, 'category': 'Behavioral Analytics'},
        
        # Employment Stability (15% total)
        'job_type': {'min': 0, 'max': 10, 'weight': 5.0, 'category': 'Employment Stability'},
        'employment_tenure_months': {'min': 0, 'max': 10, 'weight': 5.0, 'category': 'Employment Stability'},
        'company_stability': {'min': 0, 'max': 10, 'weight': 5.0, 'category': 'Employment Stability'},
        
        # Banking Behavior (10% total)
        'bank_account_vintage_months': {'min': 0, 'max': 8, 'weight': 3.0, 'category': 'Banking Behavior'},
        'avg_monthly_balance': {'min': 0, 'max': 10, 'weight': 4.0, 'category': 'Banking Behavior'},
        'bounce_frequency_per_year': {'min': 0, 'max': 8, 'weight': 3.0, 'category': 'Banking Behavior'},
        
        # Exposure & Intent (12% total)
        'unsecured_loan_amount': {'min': 0, 'max': 8, 'weight': 3.0, 'category': 'Exposure & Intent'},
        'outstanding_amount_percent': {'min': 0, 'max': 8, 'weight': 3.0, 'category': 'Exposure & Intent'},
        'our_lender_exposure': {'min': 0, 'max': 8, 'weight': 3.0, 'category': 'Exposure & Intent'},
        'channel_type': {'min': 0, 'max': 8, 'weight': 3.0, 'category': 'Exposure & Intent'},
        
        # Geographic & Social (8% total)
        'geographic_risk': {'min': 0, 'max': 10, 'weight': 4.0, 'category': 'Geographic & Social'},
        'mobile_vintage_months': {'min': 0, 'max': 8, 'weight': 2.0, 'category': 'Geographic & Social'},
        'digital_engagement_score': {'min': 0, 'max': 8, 'weight': 2.0, 'category': 'Geographic & Social'}
    }
    
    total_score = 0
    variable_scores = {}
    
    for var_id, config in slider_mappings.items():
        if var_id in form_data:
            slider_value = form_data[var_id]
            max_value = config['max']
            weight = config['weight']
            
            # Direct percentage calculation: (slider_value / max_value) × weight
            earned_percent = (slider_value / max_value) * weight
            total_score += earned_percent
            
            variable_scores[var_id] = {
                "variable_name": var_id.replace('_', ' ').title(),
                "value": slider_value,
                "raw_score": slider_value / max_value,
                "weight": weight,
                "weighted_score": earned_percent / 100,  # Convert to decimal for consistency
                "label": f"{slider_value}/{max_value}",
                "category": config['category']
            }
    
    # Final score is the sum of earned percentages
    final_score = total_score
    
    # Determine risk bucket (using same logic as original)
    if final_score >= 80:
        bucket = "A"
        decision = "Auto-approve"
        risk_level = "Low Risk (<3%)"
    elif final_score >= 65:
        bucket = "B" 
        decision = "Recommend"
        risk_level = "Moderate Risk (3-8%)"
    elif final_score >= 50:
        bucket = "C"
        decision = "Refer for Manual Review"
        risk_level = "High Risk (8-15%)"
    else:
        bucket = "D"
        decision = "Decline"
        risk_level = "Very High Risk (>15%)"
    
    return {
        "final_score": final_score,
        "risk_bucket": bucket,
        "decision": decision,
        "risk_level": risk_level,
        "variable_scores": variable_scores,
        "total_variables": len(slider_mappings),
        "scored_variables": len(variable_scores)
    }

def render_dynamic_scoring_results(results: Dict[str, Any], form_data: Dict, manager: DynamicScorecardManager):
    """Render dynamic scoring results"""
    
    st.markdown("---")
    st.subheader("📊 Scoring Results")
    
    # Main result display
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        score_color = get_bucket_color(results["risk_bucket"])
        st.markdown(f"""
        <div style="padding: 20px; background: {score_color}20; border: 2px solid {score_color}; border-radius: 10px; text-align: center;">
            <h2 style="color: {score_color}; margin: 0;">{results['final_score']:.1f}</h2>
            <p style="margin: 5px 0 0 0;"><strong>Final Score</strong></p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="padding: 20px; background: {score_color}20; border: 2px solid {score_color}; border-radius: 10px; text-align: center;">
            <h2 style="color: {score_color}; margin: 0;">{results['risk_bucket']}</h2>
            <p style="margin: 5px 0 0 0;"><strong>Risk Bucket</strong></p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style="padding: 20px; background: {score_color}20; border: 2px solid {score_color}; border-radius: 10px; text-align: center;">
            <h3 style="color: {score_color}; margin: 0; font-size: 1rem;">{results['decision']}</h3>
            <p style="margin: 5px 0 0 0;"><strong>Decision</strong></p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div style="padding: 20px; background: {score_color}20; border: 2px solid {score_color}; border-radius: 10px; text-align: center;">
            <h3 style="color: {score_color}; margin: 0; font-size: 1rem;">{results['risk_level']}</h3>
            <p style="margin: 5px 0 0 0;"><strong>Risk Level</strong></p>
        </div>
        """, unsafe_allow_html=True)
    
    # Dynamic weight breakdown showing earned vs possible scores
    st.markdown("### 📈 Dynamic Score Breakdown by Category")
    st.markdown("*Showing actual earned scores based on your input values*")
    
    categories = manager.get_categories()
    
    for category in categories:
        category_vars = [v for v in results["variable_scores"].values() 
                        if v["category"] == category["category_name"]]
        
        if category_vars:
            # Calculate earned vs possible for this category
            category_earned_score = sum(v["weighted_score"] for v in category_vars)
            category_possible_score = category["total_weight"] / 100  # Convert percentage to decimal
            category_achievement = (category_earned_score / category_possible_score * 100) if category_possible_score > 0 else 0
            
            # Color coding based on achievement
            if category_achievement >= 90:
                status = "🟢"
                color = "#27ae60"
            elif category_achievement >= 70:
                status = "🟡" 
                color = "#f39c12"
            else:
                status = "🔴"
                color = "#e74c3c"
            
            # Fixed display showing earned vs possible (addresses the static percentage issue)
            expander_title = f"{status} {category['icon']} {category['category_name']}: {category_earned_score*100:.2f}% of {category['total_weight']:.0f}% ({category_achievement:.1f}%)"
            
            with st.expander(expander_title):
                
                st.markdown(f"""
                <div style="padding: 10px; border-left: 4px solid {color}; background-color: {color}10; margin-bottom: 15px;">
                    <strong>Category Performance:</strong><br>
                    Earned: {category_earned_score*100:.2f}% | Possible: {category['total_weight']:.0f}% | Achievement: {category_achievement:.1f}%
                </div>
                """, unsafe_allow_html=True)
                
                # Progress bar for visual representation
                progress = category_earned_score / category_possible_score if category_possible_score > 0 else 0
                st.progress(min(progress, 1.0))
                
                for var_id, var_data in results["variable_scores"].items():
                    if var_data["category"] == category["category_name"]:
                        col_a, col_b, col_c, col_d = st.columns([2, 1, 1, 1])
                        
                        with col_a:
                            st.write(f"**{var_data['variable_name']}**")
                            st.write(f"Value: {var_data['value']}")
                        
                        with col_b:
                            st.write(f"Score: {var_data['raw_score']:.2f}")
                            st.write(f"Label: {var_data['label']}")
                        
                        with col_c:
                            st.write(f"Weight: {var_data['weight']:.1f}%")
                        
                        with col_d:
                            st.write(f"Contribution: {var_data['weighted_score']:.3f}")

def get_bucket_color(bucket: str) -> str:
    """Get color for risk bucket"""
    colors = {
        "A": "#27ae60",  # Green
        "B": "#f39c12",  # Orange  
        "C": "#e67e22",  # Dark Orange
        "D": "#e74c3c"   # Red
    }
    return colors.get(bucket, "#666666")