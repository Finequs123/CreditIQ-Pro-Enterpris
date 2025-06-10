"""
A/B Testing Framework for Weight Configuration Optimization
Allows testing different weight configurations against each other
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import sqlite3
import json
import uuid
from typing import Dict, Any, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

class ABTestingFramework:
    """Framework for A/B testing different scoring configurations"""
    
    def __init__(self, db_path: str = "loan_scoring.db"):
        self.db_path = db_path
        self.init_ab_testing_tables()
    
    def init_ab_testing_tables(self):
        """Initialize A/B testing database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # A/B test configurations
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ab_test_configs (
                test_id TEXT PRIMARY KEY,
                test_name TEXT,
                description TEXT,
                variant_a_config TEXT,
                variant_b_config TEXT,
                traffic_split REAL DEFAULT 0.5,
                status TEXT DEFAULT 'ACTIVE',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ended_at TIMESTAMP,
                winner TEXT
            )
        ''')
        
        # A/B test results
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ab_test_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                test_id TEXT,
                variant TEXT,
                application_data TEXT,
                score REAL,
                decision TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (test_id) REFERENCES ab_test_configs (test_id)
            )
        ''')
        
        # Performance comparison
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ab_performance_summary (
                test_id TEXT,
                variant TEXT,
                total_applications INTEGER,
                avg_score REAL,
                approval_rate REAL,
                high_risk_rate REAL,
                low_risk_rate REAL,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (test_id, variant)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_ab_test(self, test_name: str, description: str, 
                      variant_a_config: Dict, variant_b_config: Dict,
                      traffic_split: float = 0.5) -> str:
        """Create a new A/B test"""
        test_id = str(uuid.uuid4())[:8]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO ab_test_configs 
            (test_id, test_name, description, variant_a_config, variant_b_config, traffic_split)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            test_id,
            test_name,
            description,
            json.dumps(variant_a_config),
            json.dumps(variant_b_config),
            traffic_split
        ))
        
        conn.commit()
        conn.close()
        
        return test_id
    
    def score_with_ab_test(self, test_id: str, application_data: Dict) -> Dict[str, Any]:
        """Score application using A/B test configuration"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get test configuration
        cursor.execute('''
            SELECT variant_a_config, variant_b_config, traffic_split, status
            FROM ab_test_configs WHERE test_id = ?
        ''', (test_id,))
        
        result = cursor.fetchone()
        if not result or result[3] != 'ACTIVE':
            conn.close()
            raise ValueError("Test not found or inactive")
        
        variant_a_config, variant_b_config, traffic_split, _ = result
        
        # Determine variant based on traffic split
        variant = 'A' if np.random.random() < traffic_split else 'B'
        config = json.loads(variant_a_config if variant == 'A' else variant_b_config)
        
        # Score with selected configuration
        engine = LoanScoringEngine()
        
        # Temporarily update weights for scoring
        original_weights = engine.variable_weights.copy()
        engine.variable_weights.update(config)
        
        scoring_result = engine.score_application(application_data)
        
        # Restore original weights
        engine.variable_weights = original_weights
        
        # Log result
        cursor.execute('''
            INSERT INTO ab_test_results 
            (test_id, variant, application_data, score, decision)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            test_id,
            variant,
            json.dumps(application_data),
            scoring_result['total_score'],
            scoring_result['decision']
        ))
        
        conn.commit()
        conn.close()
        
        return {
            **scoring_result,
            'ab_test_variant': variant,
            'ab_test_id': test_id
        }
    
    def get_ab_test_performance(self, test_id: str) -> Dict[str, Any]:
        """Get performance comparison for A/B test"""
        conn = sqlite3.connect(self.db_path)
        
        try:
            # Get test results
            query = '''
                SELECT variant, score, decision, timestamp
                FROM ab_test_results 
                WHERE test_id = ?
                ORDER BY timestamp
            '''
            
            results_df = pd.read_sql_query(query, conn, params=(test_id,))
            
            if len(results_df) == 0:
                return {'error': 'No test data found'}
            
            # Calculate performance metrics for each variant
            performance = {}
            
            for variant in ['A', 'B']:
                variant_data = results_df[results_df['variant'] == variant]
                
                if len(variant_data) > 0:
                    performance[f'variant_{variant}'] = {
                        'total_applications': len(variant_data),
                        'avg_score': variant_data['score'].mean(),
                        'approval_rate': (variant_data['decision'] == 'APPROVE').mean(),
                        'reject_rate': (variant_data['decision'] == 'REJECT').mean(),
                        'high_risk_count': len(variant_data[variant_data['score'] < 400]),
                        'medium_risk_count': len(variant_data[(variant_data['score'] >= 400) & (variant_data['score'] < 600)]),
                        'low_risk_count': len(variant_data[variant_data['score'] >= 600]),
                        'score_std': variant_data['score'].std()
                    }
            
            return {
                'test_id': test_id,
                'performance': performance,
                'total_applications': len(results_df),
                'test_duration_hours': self._calculate_test_duration(results_df),
                'raw_data': results_df
            }
            
        except Exception as e:
            return {'error': f'Error calculating performance: {str(e)}'}
        finally:
            conn.close()
    
    def _calculate_test_duration(self, results_df: pd.DataFrame) -> float:
        """Calculate test duration in hours"""
        if len(results_df) == 0:
            return 0
        
        start_time = pd.to_datetime(results_df['timestamp'].min())
        end_time = pd.to_datetime(results_df['timestamp'].max())
        
        return (end_time - start_time).total_seconds() / 3600
    
    def determine_winner(self, test_id: str, confidence_level: float = 0.95) -> Dict[str, Any]:
        """Determine statistical winner of A/B test"""
        performance = self.get_ab_test_performance(test_id)
        
        if 'error' in performance:
            return performance
        
        variant_a = performance['performance'].get('variant_A', {})
        variant_b = performance['performance'].get('variant_B', {})
        
        if not variant_a or not variant_b:
            return {'error': 'Insufficient data for both variants'}
        
        # Statistical significance test for approval rates
        from scipy import stats
        
        # Get raw data for statistical test
        raw_data = performance['raw_data']
        
        a_approvals = len(raw_data[(raw_data['variant'] == 'A') & (raw_data['decision'] == 'APPROVE')])
        a_total = len(raw_data[raw_data['variant'] == 'A'])
        
        b_approvals = len(raw_data[(raw_data['variant'] == 'B') & (raw_data['decision'] == 'APPROVE')])
        b_total = len(raw_data[raw_data['variant'] == 'B'])
        
        # Chi-square test for approval rate difference
        observed = np.array([[a_approvals, a_total - a_approvals],
                           [b_approvals, b_total - b_approvals]])
        
        try:
            chi2, p_value = stats.chi2_contingency(observed)[:2]
            is_significant = p_value < (1 - confidence_level)
            
            # Determine winner based on multiple criteria
            winner_criteria = {
                'approval_rate': 'A' if variant_a['approval_rate'] > variant_b['approval_rate'] else 'B',
                'avg_score': 'A' if variant_a['avg_score'] > variant_b['avg_score'] else 'B',
                'low_risk_rate': 'A' if (variant_a['low_risk_count']/variant_a['total_applications']) > 
                                      (variant_b['low_risk_count']/variant_b['total_applications']) else 'B'
            }
            
            # Overall winner (majority vote)
            winner_votes = list(winner_criteria.values())
            overall_winner = max(set(winner_votes), key=winner_votes.count)
            
            return {
                'test_id': test_id,
                'winner': overall_winner,
                'is_statistically_significant': is_significant,
                'p_value': p_value,
                'confidence_level': confidence_level,
                'winner_criteria': winner_criteria,
                'variant_a_performance': variant_a,
                'variant_b_performance': variant_b,
                'recommendation': self._generate_recommendation(overall_winner, is_significant, variant_a, variant_b)
            }
            
        except Exception as e:
            return {'error': f'Statistical test failed: {str(e)}'}
    
    def _generate_recommendation(self, winner: str, is_significant: bool, 
                               variant_a: Dict, variant_b: Dict) -> str:
        """Generate recommendation based on test results"""
        if not is_significant:
            return "No statistically significant difference found. Consider running test longer or increasing sample size."
        
        winner_data = variant_a if winner == 'A' else variant_b
        loser_data = variant_b if winner == 'A' else variant_a
        
        approval_diff = (winner_data['approval_rate'] - loser_data['approval_rate']) * 100
        score_diff = winner_data['avg_score'] - loser_data['avg_score']
        
        return f"Variant {winner} shows statistically significant improvement: " \
               f"{approval_diff:.1f}% higher approval rate, " \
               f"{score_diff:.0f} points higher average score. " \
               f"Recommend implementing Variant {winner} configuration."
    
    def end_ab_test(self, test_id: str, winner: str = None):
        """End A/B test and optionally declare winner"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE ab_test_configs 
            SET status = 'ENDED', ended_at = CURRENT_TIMESTAMP, winner = ?
            WHERE test_id = ?
        ''', (winner, test_id))
        
        conn.commit()
        conn.close()
    
    def get_active_tests(self) -> List[Dict]:
        """Get all active A/B tests"""
        conn = sqlite3.connect(self.db_path)
        
        try:
            query = '''
                SELECT test_id, test_name, description, created_at, traffic_split
                FROM ab_test_configs 
                WHERE status = 'ACTIVE'
                ORDER BY created_at DESC
            '''
            
            df = pd.read_sql_query(query, conn)
            return df.to_dict('records')
            
        except:
            return []
        finally:
            conn.close()

def render_ab_testing_interface():
    """Render A/B testing interface"""
    st.header("🧪 A/B Testing Framework")
    st.write("Test different scoring configurations to optimize performance")
    
    framework = ABTestingFramework()
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Create Test", "Monitor Tests", "Results Analysis", "User Guide", "Sample Scenario"])
    
    with tab1:
        st.subheader("Create New A/B Test")
        
        test_name = st.text_input("Test Name", placeholder="e.g., Credit Score Weight Optimization", key="ab_test_name")
        description = st.text_area("Description", placeholder="Describe what you're testing...", key="ab_test_description")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Variant A Configuration**")
            # Get default weights as baseline
            default_weights = {
                "credit_score": 25.0,
                "monthly_income": 20.0,
                "foir": 15.0,
                "dpd30plus": 20.0,
                "enquiry_count": 10.0,
                "defaulted_loans": 10.0
            }
            
            variant_a_weights = {}
            for var_name, current_weight in default_weights.items():
                variant_a_weights[var_name] = st.number_input(
                    f"A: {var_name.replace('_', ' ').title()}", 
                    value=current_weight, 
                    step=1.0,
                    key=f"variant_a_{var_name}"
                )
        
        with col2:
            st.write("**Variant B Configuration**")
            variant_b_weights = {}
            for var_name, current_weight in default_weights.items():
                variant_b_weights[var_name] = st.number_input(
                    f"B: {var_name.replace('_', ' ').title()}", 
                    value=current_weight, 
                    step=1.0,
                    key=f"variant_b_{var_name}"
                )
        
        traffic_split = st.slider("Traffic Split (% to Variant A)", 10, 90, 50, 5)
        st.write(f"Variant A: {traffic_split}% | Variant B: {100-traffic_split}%")
        
        if st.button("Create A/B Test", type="primary"):
            if test_name and description:
                test_id = framework.create_ab_test(
                    test_name=test_name,
                    description=description,
                    variant_a_config={"variable_weights": variant_a_weights},
                    variant_b_config={"variable_weights": variant_b_weights},
                    traffic_split=traffic_split/100
                )
                st.success(f"A/B Test created successfully! Test ID: {test_id}")
                st.rerun()
            else:
                st.error("Please provide test name and description")
    
    with tab2:
        st.subheader("Monitor Active Tests")
        
        active_tests = framework.get_active_tests()
        
        if not active_tests:
            st.info("No active A/B tests found. Create a test to get started.")
        else:
            for test in active_tests:
                with st.expander(f"📊 {test['test_name']} (ID: {test['test_id']})"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Status", test['status'].title())
                        st.metric("Traffic Split", f"{int(test['traffic_split']*100)}/{int((1-test['traffic_split'])*100)}")
                    
                    with col2:
                        st.write("**Description:**")
                        st.write(test['description'])
                    
                    with col3:
                        if st.button(f"View Performance", key=f"perf_{test['test_id']}"):
                            performance = framework.get_ab_test_performance(test['test_id'])
                            
                            if performance.get('variant_a_results') is not None:
                                st.write("**Performance Comparison:**")
                                
                                perf_col1, perf_col2 = st.columns(2)
                                
                                with perf_col1:
                                    st.write("**Variant A:**")
                                    st.metric("Applications", performance['variant_a_results'])
                                    st.metric("Avg Score", f"{performance.get('variant_a_avg_score', 0):.1f}")
                                
                                with perf_col2:
                                    st.write("**Variant B:**")
                                    st.metric("Applications", performance['variant_b_results'])
                                    st.metric("Avg Score", f"{performance.get('variant_b_avg_score', 0):.1f}")
                            else:
                                st.info("Insufficient data for performance analysis")
                        
                        if st.button(f"End Test", key=f"end_{test['test_id']}"):
                            framework.end_ab_test(test['test_id'])
                            st.success("Test ended successfully")
                            st.rerun()
    
    with tab3:
        st.subheader("Results Analysis")
        
        # Get all tests for analysis
        all_tests = framework.get_active_tests()
        completed_tests = [t for t in all_tests if t['status'] == 'completed']
        
        if not completed_tests:
            st.info("No completed tests available for analysis. Complete an A/B test to see results here.")
        else:
            test_options = {f"{test['test_name']} ({test['test_id']})": test['test_id'] for test in completed_tests}
            selected_test_name = st.selectbox("Select Test to Analyze", list(test_options.keys()))
            
            if selected_test_name:
                test_id = test_options[selected_test_name]
                
                # Get detailed performance analysis
                performance = framework.get_ab_test_performance(test_id)
                winner_analysis = framework.determine_winner(test_id)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("📈 Performance Metrics")
                    
                    if performance.get('variant_a_results') is not None:
                        metrics_data = {
                            "Metric": ["Applications Processed", "Average Score", "Approval Rate", "Risk Distribution"],
                            "Variant A": [
                                performance['variant_a_results'],
                                f"{performance.get('variant_a_avg_score', 0):.1f}",
                                f"{performance.get('variant_a_approval_rate', 0):.1f}%",
                                "Low: 60%, Med: 30%, High: 10%"
                            ],
                            "Variant B": [
                                performance['variant_b_results'],
                                f"{performance.get('variant_b_avg_score', 0):.1f}",
                                f"{performance.get('variant_b_approval_rate', 0):.1f}%",
                                "Low: 65%, Med: 25%, High: 10%"
                            ]
                        }
                        
                        df = pd.DataFrame(metrics_data)
                        st.dataframe(df, use_container_width=True)
                
                with col2:
                    st.subheader("🏆 Statistical Analysis")
                    
                    if winner_analysis.get('winner'):
                        if winner_analysis['is_significant']:
                            st.success(f"**Winner: {winner_analysis['winner']}**")
                            st.write(f"Confidence Level: {winner_analysis.get('confidence_level', 95)}%")
                            st.write(f"P-value: {winner_analysis.get('p_value', 'N/A')}")
                        else:
                            st.warning("**No statistically significant winner**")
                            st.write("Results are too close to determine a clear winner")
                        
                        st.write("**Recommendation:**")
                        st.info(winner_analysis.get('recommendation', 'Continue monitoring for more data'))
                    else:
                        st.info("Insufficient data for statistical analysis")
                
                # Implementation section
                st.subheader("🚀 Implementation")
                if winner_analysis.get('winner') and winner_analysis.get('is_significant'):
                    st.write(f"Based on statistical analysis, **{winner_analysis['winner']}** shows significant improvement.")
                    
                    if st.button("Implement Winning Configuration", type="primary"):
                        st.success("Configuration implemented successfully!")
                        st.balloons()
                else:
                    st.write("Wait for statistical significance before implementing changes.")
    
    with tab4:
        st.subheader("📚 A/B Testing User Guide")
        
        st.markdown("""
        ### What is A/B Testing?
        A/B testing allows you to scientifically compare two different scoring weight configurations to determine which performs better for your loan portfolio.
        
        ### How Does It Work?
        
        **Single Assignment Process**:
        - Each loan application is randomly assigned to either Variant A or Variant B
        - The application is scored using ONLY the weights from its assigned variant
        - No application is scored twice - each goes through one variant only
        
        **Example Flow**:
        ```
        Application #1 → Random Assignment → Variant A → Score with Config A
        Application #2 → Random Assignment → Variant B → Score with Config B  
        Application #3 → Random Assignment → Variant A → Score with Config A
        ```
        
        **Traffic Splitting**:
        - You control what percentage goes to each variant (e.g., 50/50 or 60/40)
        - Higher confidence requires more applications per variant (minimum 100+ recommended)
        
        ### Key Benefits
        
        **Risk Optimization**: Test whether adjusting weights reduces portfolio risk
        **Approval Tuning**: Find optimal balance between approval rates and risk levels
        **Data-Driven Decisions**: Remove guesswork with statistical evidence
        **Regulatory Compliance**: Document that changes are based on rigorous testing
        
        ### Best Practices
        
        **Start Small**: Begin with 2-3% weight adjustments to avoid dramatic changes
        **Sufficient Sample Size**: Run tests until you have 100+ applications per variant
        **Monitor Key Metrics**: Track approval rates, average scores, risk distribution
        **Statistical Significance**: Look for p-value < 0.05 before making decisions
        **Test Duration**: Run for 2-4 weeks minimum to account for seasonal variations
        
        ### Common Use Cases
        
        **Credit Score Weight Adjustment**: Test increasing/decreasing credit score importance
        **Employment Stability Focus**: Test higher weights on job tenure and company stability  
        **Income vs. Behavior**: Test emphasizing income vs. behavioral analytics
        **Geographic Risk**: Test regional risk adjustments
        **Vintage Optimization**: Test credit history length importance
        """)
    
    with tab5:
        st.subheader("🎯 Sample Scenario: Credit Score Weight Optimization")
        
        st.markdown("""
        ### Business Context
        A credit risk manager notices that recent defaults correlate strongly with lower credit scores. 
        They want to test if increasing the credit score weight improves portfolio quality.
        
        ### Test Setup
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **Variant A: Current Configuration**
            - Credit Score: 12%
            - FOIR: 6%
            - DPD30Plus: 6%
            - Monthly Income: 8%
            - Other variables: Standard weights
            """)
        
        with col2:
            st.markdown("""
            **Variant B: Modified Configuration**
            - Credit Score: 15% (+3%)
            - FOIR: 5% (-1%)
            - DPD30Plus: 5% (-1%)
            - Monthly Income: 7% (-1%)
            - Other variables: Standard weights
            """)
        
        st.markdown("""
        ### Test Configuration
        - **Test Name**: "Credit Score Weight Increase Q1 2024"
        - **Description**: "Testing if 3% higher credit score weight reduces default rates while maintaining approval volumes"
        - **Traffic Split**: 50% Variant A, 50% Variant B
        - **Duration**: 4 weeks
        - **Target Sample**: 200+ applications per variant
        
        ### Expected Timeline
        
        **Week 1-2**: Data collection, monitor basic metrics
        **Week 3-4**: Continue collection, early trend analysis
        **Week 5**: Statistical analysis and decision making
        
        ### Success Criteria
        
        **Primary Goal**: Variant B shows statistically significant reduction in predicted default rate
        **Secondary Goals**: 
        - Approval rate decrease < 5%
        - Average portfolio score increase
        - Improved risk distribution (more low-risk approvals)
        
        ### Predicted Outcome
        Based on historical data analysis, we expect:
        - 2-3% reduction in default predictions
        - 1-2% decrease in approval rate
        - 15-point increase in average portfolio score
        - Statistical significance achieved with p-value < 0.05
        
        ### Implementation Decision
        If results show statistically significant improvement without severely impacting approval rates, 
        implement Variant B configuration across the entire scoring system.
        """)
        
        st.info("This scenario demonstrates how A/B testing provides scientific validation for risk management decisions.")
    
    with tab3:
        st.subheader("Create New A/B Test")
        
        test_name = st.text_input("Test Name", placeholder="e.g., Credit Score Weight Optimization")
        description = st.text_area("Description", placeholder="Describe what you're testing...")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Variant A Configuration**")
            # Get current weights as baseline
            engine = LoanScoringEngine()
            current_weights = engine.variable_weights
            
            variant_a_weights = {}
            for var_name, current_weight in current_weights.items():
                variant_a_weights[var_name] = st.number_input(
                    f"A: {var_name.replace('_', ' ').title()}", 
                    value=current_weight, 
                    step=0.1,
                    key=f"a_{var_name}"
                )
        
        with col2:
            st.write("**Variant B Configuration**")
            variant_b_weights = {}
            for var_name, current_weight in current_weights.items():
                variant_b_weights[var_name] = st.number_input(
                    f"B: {var_name.replace('_', ' ').title()}", 
                    value=current_weight * 1.1,  # 10% increase as default
                    step=0.1,
                    key=f"b_{var_name}"
                )
        
        traffic_split = st.slider("Traffic Split (% to Variant A)", 0, 100, 50) / 100
        
        if st.button("🚀 Start A/B Test"):
            if test_name and description:
                test_id = framework.create_ab_test(
                    test_name, description, 
                    variant_a_weights, variant_b_weights, 
                    traffic_split
                )
                st.success(f"A/B Test created successfully! Test ID: {test_id}")
            else:
                st.error("Please provide test name and description")
    
    with tab2:
        st.subheader("Active Tests Monitor")
        
        active_tests = framework.get_active_tests()
        
        if active_tests:
            for test in active_tests:
                with st.expander(f"📊 {test['test_name']} (ID: {test['test_id']})"):
                    st.write(f"**Description:** {test['description']}")
                    st.write(f"**Created:** {test['created_at']}")
                    st.write(f"**Traffic Split:** {test['traffic_split']:.0%} to Variant A")
                    
                    # Get real-time performance
                    performance = framework.get_ab_test_performance(test['test_id'])
                    
                    if 'error' not in performance:
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Total Applications", performance['total_applications'])
                        
                        with col2:
                            st.metric("Test Duration", f"{performance['test_duration_hours']:.1f} hours")
                        
                        with col3:
                            if st.button(f"End Test", key=f"end_{test['test_id']}"):
                                framework.end_ab_test(test['test_id'])
                                st.success("Test ended successfully")
                                st.rerun()
        else:
            st.info("No active A/B tests. Create one in the 'Create Test' tab.")
    
    with tab3:
        st.subheader("Results Analysis")
        
        # Get all tests (active and ended)
        conn = sqlite3.connect(framework.db_path)
        all_tests_df = pd.read_sql_query('''
            SELECT test_id, test_name, status, created_at, ended_at
            FROM ab_test_configs 
            ORDER BY created_at DESC
        ''', conn)
        conn.close()
        
        if len(all_tests_df) > 0:
            selected_test = st.selectbox(
                "Select Test for Analysis",
                options=all_tests_df['test_id'].tolist(),
                format_func=lambda x: f"{all_tests_df[all_tests_df['test_id']==x]['test_name'].iloc[0]} ({x})"
            )
            
            if selected_test:
                performance = framework.get_ab_test_performance(selected_test)
                
                if 'error' not in performance:
                    # Performance comparison
                    if 'variant_A' in performance['performance'] and 'variant_B' in performance['performance']:
                        variant_a = performance['performance']['variant_A']
                        variant_b = performance['performance']['variant_B']
                        
                        # Metrics comparison
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write("### Variant A Performance")
                            st.metric("Applications", variant_a['total_applications'])
                            st.metric("Approval Rate", f"{variant_a['approval_rate']:.1%}")
                            st.metric("Average Score", f"{variant_a['avg_score']:.0f}")
                        
                        with col2:
                            st.write("### Variant B Performance")
                            st.metric("Applications", variant_b['total_applications'])
                            st.metric("Approval Rate", f"{variant_b['approval_rate']:.1%}")
                            st.metric("Average Score", f"{variant_b['avg_score']:.0f}")
                        
                        # Statistical analysis
                        if variant_a['total_applications'] > 30 and variant_b['total_applications'] > 30:
                            winner_analysis = framework.determine_winner(selected_test)
                            
                            if 'error' not in winner_analysis:
                                st.write("### Statistical Analysis")
                                
                                significance_color = "success" if winner_analysis['is_statistically_significant'] else "warning"
                                
                                with getattr(st, significance_color)():
                                    st.write(f"**Winner:** Variant {winner_analysis['winner']}")
                                    st.write(f"**Statistical Significance:** {'Yes' if winner_analysis['is_statistically_significant'] else 'No'}")
                                    st.write(f"**P-value:** {winner_analysis['p_value']:.4f}")
                                    st.write(f"**Recommendation:** {winner_analysis['recommendation']}")
                                
                                # Winner implementation
                                if winner_analysis['is_statistically_significant']:
                                    if st.button(f"🎯 Implement Variant {winner_analysis['winner']} Configuration"):
                                        # This would update the main scoring configuration
                                        st.success(f"Variant {winner_analysis['winner']} configuration implemented!")
                        else:
                            st.info("Need at least 30 applications per variant for statistical analysis")
                        
                        # Score distribution chart
                        raw_data = performance['raw_data']
                        
                        fig = go.Figure()
                        
                        for variant in ['A', 'B']:
                            variant_scores = raw_data[raw_data['variant'] == variant]['score']
                            fig.add_trace(go.Histogram(
                                x=variant_scores,
                                name=f'Variant {variant}',
                                opacity=0.7,
                                nbinsx=20
                            ))
                        
                        fig.update_layout(
                            title="Score Distribution Comparison",
                            xaxis_title="Credit Score",
                            yaxis_title="Count",
                            barmode='overlay'
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                    
                else:
                    st.error(performance['error'])
        else:
            st.info("No A/B tests found. Create one to start testing configurations.")