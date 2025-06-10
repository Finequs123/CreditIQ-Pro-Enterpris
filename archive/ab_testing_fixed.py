"""
Working A/B Testing Framework - Fixed Implementation
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import sqlite3
import json
import uuid
from datetime import datetime
from typing import Dict, Any, List

class SimpleABTestFramework:
    """Simple working A/B testing framework"""
    
    def __init__(self, db_path: str = "ab_testing.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize A/B testing database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tests table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ab_tests (
                test_id TEXT PRIMARY KEY,
                test_name TEXT,
                description TEXT,
                variant_a_config TEXT,
                variant_b_config TEXT,
                status TEXT DEFAULT 'ACTIVE',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ended_at TIMESTAMP,
                winner TEXT
            )
        ''')
        
        # Results table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ab_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                test_id TEXT,
                variant TEXT,
                credit_score INTEGER,
                final_score INTEGER,
                decision TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (test_id) REFERENCES ab_tests (test_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_test(self, test_name: str, description: str, 
                   variant_a_config: Dict, variant_b_config: Dict) -> str:
        """Create new A/B test"""
        test_id = str(uuid.uuid4())[:8]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO ab_tests (test_id, test_name, description, variant_a_config, variant_b_config)
            VALUES (?, ?, ?, ?, ?)
        ''', (test_id, test_name, description, 
              json.dumps(variant_a_config), json.dumps(variant_b_config)))
        
        conn.commit()
        conn.close()
        
        return test_id
    
    def simulate_test_data(self, test_id: str, num_samples: int = 100):
        """Generate simulated test data for demonstration"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get test configurations
        cursor.execute("SELECT variant_a_config, variant_b_config FROM ab_tests WHERE test_id = ?", (test_id,))
        result = cursor.fetchone()
        
        if not result:
            conn.close()
            return
        
        variant_a_config = json.loads(result[0])
        variant_b_config = json.loads(result[1])
        
        # Generate sample data for both variants
        for _ in range(num_samples):
            variant = 'A' if np.random.random() < 0.5 else 'B'
            config = variant_a_config if variant == 'A' else variant_b_config
            
            # Simulate credit scoring
            credit_score = np.random.randint(300, 850)
            
            # Calculate weighted score based on config
            base_score = 300
            credit_weight = config.get('credit_score', 25.0)
            income_weight = config.get('monthly_income', 20.0)
            
            # Simple scoring simulation
            score_factor = (credit_score - 300) / 550
            final_score = int(base_score + (score_factor * credit_weight * 10) + 
                            (np.random.random() * income_weight * 5))
            
            # Decision logic
            if final_score >= 750:
                decision = 'APPROVE'
            elif final_score >= 600:
                decision = 'REVIEW'
            else:
                decision = 'DECLINE'
            
            # Insert result
            cursor.execute('''
                INSERT INTO ab_results (test_id, variant, credit_score, final_score, decision)
                VALUES (?, ?, ?, ?, ?)
            ''', (test_id, variant, credit_score, final_score, decision))
        
        conn.commit()
        conn.close()
    
    def get_test_results(self, test_id: str) -> Dict[str, Any]:
        """Get results for a specific test"""
        conn = sqlite3.connect(self.db_path)
        
        query = '''
            SELECT variant, credit_score, final_score, decision, timestamp
            FROM ab_results 
            WHERE test_id = ?
        '''
        
        df = pd.read_sql_query(query, conn, params=(test_id,))
        conn.close()
        
        if df.empty:
            return {'error': 'No results found'}
        
        # Calculate metrics for each variant
        results = {}
        for variant in ['A', 'B']:
            variant_data = df[df['variant'] == variant]
            if len(variant_data) > 0:
                approve_rate = len(variant_data[variant_data['decision'] == 'APPROVE']) / len(variant_data) * 100
                avg_score = variant_data['final_score'].mean()
                total_count = len(variant_data)
                
                results[f'variant_{variant}'] = {
                    'total_applications': total_count,
                    'approval_rate': approve_rate,
                    'average_score': avg_score,
                    'approve_count': len(variant_data[variant_data['decision'] == 'APPROVE']),
                    'review_count': len(variant_data[variant_data['decision'] == 'REVIEW']),
                    'decline_count': len(variant_data[variant_data['decision'] == 'DECLINE'])
                }
        
        return {
            'test_id': test_id,
            'results': results,
            'raw_data': df
        }
    
    def get_active_tests(self) -> List[Dict]:
        """Get all active tests"""
        conn = sqlite3.connect(self.db_path)
        
        query = '''
            SELECT test_id, test_name, description, created_at
            FROM ab_tests 
            WHERE status = 'ACTIVE'
            ORDER BY created_at DESC
        '''
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        return df.to_dict('records')
    
    def end_test(self, test_id: str, winner: str = None):
        """End a test"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE ab_tests 
            SET status = 'ENDED', ended_at = CURRENT_TIMESTAMP, winner = ?
            WHERE test_id = ?
        ''', (winner, test_id))
        
        conn.commit()
        conn.close()

def render_working_ab_testing():
    """Render working A/B testing interface"""
    st.header("🧪 A/B Testing Framework")
    st.write("Test different scoring configurations to optimize performance")
    
    framework = SimpleABTestFramework()
    
    tab1, tab2, tab3 = st.tabs(["Create Test", "Monitor Tests", "View Results"])
    
    with tab1:
        st.subheader("Create New A/B Test")
        
        with st.form("create_ab_test"):
            test_name = st.text_input("Test Name", placeholder="e.g., Credit Weight Optimization")
            description = st.text_area("Description", placeholder="Describe what you're testing...")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Variant A Configuration**")
                a_credit = st.number_input("A: Credit Score Weight", value=25.0, step=1.0)
                a_income = st.number_input("A: Monthly Income Weight", value=20.0, step=1.0)
                a_foir = st.number_input("A: FOIR Weight", value=15.0, step=1.0)
                a_dpd = st.number_input("A: DPD30+ Weight", value=20.0, step=1.0)
            
            with col2:
                st.write("**Variant B Configuration**")
                b_credit = st.number_input("B: Credit Score Weight", value=30.0, step=1.0)
                b_income = st.number_input("B: Monthly Income Weight", value=25.0, step=1.0)
                b_foir = st.number_input("B: FOIR Weight", value=10.0, step=1.0)
                b_dpd = st.number_input("B: DPD30+ Weight", value=15.0, step=1.0)
            
            submitted = st.form_submit_button("Create A/B Test", type="primary")
            
            if submitted and test_name and description:
                variant_a = {
                    'credit_score': a_credit,
                    'monthly_income': a_income,
                    'foir': a_foir,
                    'dpd30plus': a_dpd
                }
                
                variant_b = {
                    'credit_score': b_credit,
                    'monthly_income': b_income,
                    'foir': b_foir,
                    'dpd30plus': b_dpd
                }
                
                test_id = framework.create_test(test_name, description, variant_a, variant_b)
                st.success(f"A/B Test created! Test ID: {test_id}")
                
                # Generate sample data for demonstration
                framework.simulate_test_data(test_id, 200)
                st.info("Sample data generated for demonstration")
    
    with tab2:
        st.subheader("Active Tests")
        
        active_tests = framework.get_active_tests()
        
        if active_tests:
            for test in active_tests:
                with st.expander(f"📊 {test['test_name']} (ID: {test['test_id']})"):
                    st.write(f"**Description:** {test['description']}")
                    st.write(f"**Created:** {test['created_at']}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"View Results", key=f"view_{test['test_id']}"):
                            st.session_state.selected_test = test['test_id']
                    
                    with col2:
                        if st.button(f"End Test", key=f"end_{test['test_id']}"):
                            framework.end_test(test['test_id'])
                            st.success("Test ended")
                            st.rerun()
        else:
            st.info("No active tests found")
    
    with tab3:
        st.subheader("Test Results")
        
        if 'selected_test' in st.session_state:
            test_id = st.session_state.selected_test
            results = framework.get_test_results(test_id)
            
            if 'error' not in results:
                st.write(f"**Test ID:** {test_id}")
                
                # Display metrics
                col1, col2 = st.columns(2)
                
                if 'variant_A' in results['results']:
                    with col1:
                        st.write("**Variant A Performance**")
                        a_results = results['results']['variant_A']
                        st.metric("Applications", a_results['total_applications'])
                        st.metric("Approval Rate", f"{a_results['approval_rate']:.1f}%")
                        st.metric("Average Score", f"{a_results['average_score']:.0f}")
                
                if 'variant_B' in results['results']:
                    with col2:
                        st.write("**Variant B Performance**")
                        b_results = results['results']['variant_B']
                        st.metric("Applications", b_results['total_applications'])
                        st.metric("Approval Rate", f"{b_results['approval_rate']:.1f}%")
                        st.metric("Average Score", f"{b_results['average_score']:.0f}")
                
                # Winner analysis
                if 'variant_A' in results['results'] and 'variant_B' in results['results']:
                    a_rate = results['results']['variant_A']['approval_rate']
                    b_rate = results['results']['variant_B']['approval_rate']
                    
                    if a_rate > b_rate:
                        st.success(f"🏆 Variant A is performing better with {a_rate - b_rate:.1f}% higher approval rate")
                    elif b_rate > a_rate:
                        st.success(f"🏆 Variant B is performing better with {b_rate - a_rate:.1f}% higher approval rate")
                    else:
                        st.info("Both variants are performing equally")
                
                # Chart
                if not results['raw_data'].empty:
                    df = results['raw_data']
                    
                    # Decision distribution chart
                    fig = go.Figure()
                    
                    for variant in ['A', 'B']:
                        variant_data = df[df['variant'] == variant]
                        decisions = variant_data['decision'].value_counts()
                        
                        fig.add_trace(go.Bar(
                            name=f'Variant {variant}',
                            x=decisions.index,
                            y=decisions.values,
                            text=decisions.values,
                            textposition='auto'
                        ))
                    
                    fig.update_layout(
                        title="Decision Distribution by Variant",
                        xaxis_title="Decision",
                        yaxis_title="Count",
                        barmode='group'
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.error(results['error'])
        else:
            st.info("Select a test from the Monitor Tests tab to view results")

if __name__ == "__main__":
    render_working_ab_testing()