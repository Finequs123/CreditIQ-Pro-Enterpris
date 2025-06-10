#!/usr/bin/env python3
"""
Dynamic Weight Distribution Display - Shows actual earned scores based on inputs
"""

import streamlit as st
from typing import Dict, Any
import plotly.graph_objects as go
import plotly.express as px

def render_dynamic_weight_breakdown(form_data: Dict[str, Any], manager):
    """Render weight distribution showing actual earned vs possible scores"""
    
    if not form_data:
        st.info("Enter values in the scoring interface to see dynamic weight distribution")
        return
    
    # Define category mappings with slider ranges
    category_mappings = {
        'Core Credit Variables': {
            'weight': 35.0,
            'variables': {
                'credit_score': {'min': 0, 'max': 20, 'weight': 10.0},
                'foir': {'min': 0, 'max': 15, 'weight': 8.0},
                'dpd_30_plus': {'min': 0, 'max': 15, 'weight': 6.0},
                'enquiry_count': {'min': 0, 'max': 10, 'weight': 6.0},
                'age': {'min': 0, 'max': 8, 'weight': 3.0},
                'monthly_income': {'min': 0, 'max': 15, 'weight': 2.0}
            }
        },
        'Behavioral Analytics': {
            'weight': 20.0,
            'variables': {
                'credit_vintage_months': {'min': 0, 'max': 10, 'weight': 6.0},
                'loan_mix_type': {'min': 0, 'max': 8, 'weight': 4.0},
                'loan_completion_ratio': {'min': 0, 'max': 10, 'weight': 5.0},
                'defaulted_loans': {'min': 0, 'max': 10, 'weight': 5.0}
            }
        },
        'Employment Stability': {
            'weight': 15.0,
            'variables': {
                'job_type': {'min': 0, 'max': 10, 'weight': 5.0},
                'employment_tenure_months': {'min': 0, 'max': 10, 'weight': 5.0},
                'company_stability': {'min': 0, 'max': 10, 'weight': 5.0}
            }
        },
        'Banking Behavior': {
            'weight': 10.0,
            'variables': {
                'bank_account_vintage_months': {'min': 0, 'max': 8, 'weight': 3.0},
                'avg_monthly_balance': {'min': 0, 'max': 10, 'weight': 4.0},
                'bounce_frequency_per_year': {'min': 0, 'max': 8, 'weight': 3.0}
            }
        },
        'Exposure & Intent': {
            'weight': 12.0,
            'variables': {
                'unsecured_loan_amount': {'min': 0, 'max': 8, 'weight': 3.0},
                'outstanding_amount_percent': {'min': 0, 'max': 8, 'weight': 3.0},
                'our_lender_exposure': {'min': 0, 'max': 8, 'weight': 3.0},
                'channel_type': {'min': 0, 'max': 8, 'weight': 3.0}
            }
        },
        'Geographic & Social': {
            'weight': 8.0,
            'variables': {
                'geographic_risk': {'min': 0, 'max': 10, 'weight': 4.0},
                'mobile_vintage_months': {'min': 0, 'max': 8, 'weight': 2.0},
                'digital_engagement_score': {'min': 0, 'max': 8, 'weight': 2.0}
            }
        }
    }
    
    st.markdown("### 📊 Dynamic Weight Distribution")
    st.markdown("*Real-time earned vs possible scores based on your inputs*")
    
    # Calculate category scores
    category_results = {}
    total_earned = 0
    total_possible = 100
    
    for category_name, category_config in category_mappings.items():
        earned_in_category = 0
        possible_in_category = category_config['weight']
        
        for var_id, var_config in category_config['variables'].items():
            if var_id in form_data:
                slider_value = form_data[var_id]
                max_value = var_config['max']
                weight = var_config['weight']
                
                # Direct percentage calculation
                earned_percent = (slider_value / max_value) * weight
                earned_in_category += earned_percent
        
        category_results[category_name] = {
            'earned': earned_in_category,
            'possible': possible_in_category,
            'achievement': (earned_in_category / possible_in_category * 100) if possible_in_category > 0 else 0
        }
        
        total_earned += earned_in_category
    
    # Overall summary
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Earned", f"{total_earned:.2f}%", f"{total_earned - 50:.2f}% vs baseline")
    with col2:
        st.metric("Total Possible", f"{total_possible:.0f}%")
    with col3:
        overall_achievement = (total_earned / total_possible * 100) if total_possible > 0 else 0
        st.metric("Achievement", f"{overall_achievement:.1f}%")
    
    # Category breakdown with dynamic colors
    for category_name, results in category_results.items():
        achievement = results['achievement']
        
        # Dynamic color based on achievement
        if achievement >= 90:
            status = "🟢"
            color = "#27ae60"
        elif achievement >= 70:
            status = "🟡" 
            color = "#f39c12"
        elif achievement >= 50:
            status = "🟠"
            color = "#e67e22"
        else:
            status = "🔴"
            color = "#e74c3c"
        
        # Dynamic display showing earned vs possible
        st.markdown(f"""
        <div style="padding: 15px; margin: 10px 0; border-left: 4px solid {color}; background-color: {color}10;">
            <h4 style="margin: 0; color: {color};">
                {status} {category_name}
            </h4>
            <p style="margin: 5px 0 0 0; font-size: 16px;">
                <strong>Earned: {results['earned']:.2f}% of {results['possible']:.0f}% ({achievement:.1f}%)</strong>
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Progress bar showing actual achievement
        progress = results['earned'] / results['possible'] if results['possible'] > 0 else 0
        st.progress(min(progress, 1.0))
        
        # Variable details in expandable section
        with st.expander(f"Variable Details for {category_name}"):
            if category_name in category_mappings:
                for var_id, var_config in category_mappings[category_name]['variables'].items():
                    if var_id in form_data:
                        slider_value = form_data[var_id]
                        max_value = var_config['max']
                        weight = var_config['weight']
                        earned = (slider_value / max_value) * weight
                        
                        col_a, col_b, col_c, col_d = st.columns([2, 1, 1, 1])
                        
                        with col_a:
                            st.write(f"**{var_id.replace('_', ' ').title()}**")
                        with col_b:
                            st.metric("Slider", f"{slider_value}/{max_value}")
                        with col_c:
                            st.metric("Weight", f"{weight:.1f}%")
                        with col_d:
                            st.metric("Earned", f"{earned:.2f}%")
    
    # Visual chart
    st.markdown("### 📈 Category Performance Chart")
    
    # Create data for chart
    categories = list(category_results.keys())
    earned_values = [category_results[cat]['earned'] for cat in categories]
    possible_values = [category_results[cat]['possible'] for cat in categories]
    
    # Create grouped bar chart
    fig = go.Figure(data=[
        go.Bar(name='Earned %', x=categories, y=earned_values, marker_color='#3498db'),
        go.Bar(name='Possible %', x=categories, y=possible_values, marker_color='#ecf0f1', opacity=0.6)
    ])
    
    fig.update_layout(
        title='Earned vs Possible Scores by Category',
        xaxis_title='Categories',
        yaxis_title='Percentage Points',
        barmode='overlay',
        height=400,
        showlegend=True
    )
    
    st.plotly_chart(fig, use_container_width=True)

def calculate_slider_based_scores(slider_values: Dict[str, float]) -> Dict[str, float]:
    """Calculate scores based on slider values using the logic from the issue description"""
    
    # Core Credit Variables mapping from user's issue
    mappings = {
        'credit_score': {'max': 20, 'weight': 10.0},
        'foir': {'max': 15, 'weight': 8.0},
        'dpd_30_plus': {'max': 15, 'weight': 6.0},
        'enquiry_count': {'max': 10, 'weight': 6.0},
        'age': {'max': 8, 'weight': 3.0},
        'monthly_income': {'max': 15, 'weight': 2.0}
    }
    
    results = {}
    
    for var_id, config in mappings.items():
        if var_id in slider_values:
            slider_val = slider_values[var_id]
            max_val = config['max']
            weight = config['weight']
            
            # Direct calculation: (slider_value / max_value) × weight
            earned_percent = (slider_val / max_val) * weight
            results[var_id] = earned_percent
    
    return results