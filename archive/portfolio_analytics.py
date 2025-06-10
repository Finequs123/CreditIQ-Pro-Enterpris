"""
Advanced Portfolio Analytics and Predictive Risk Assessment
Provides cohort analysis, benchmarking, and portfolio risk trends
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import sqlite3
import json
from typing import Dict, Any, List, Optional, Tuple
from database import DatabaseManager
import warnings
warnings.filterwarnings('ignore')

class PortfolioAnalytics:
    """Advanced portfolio analytics and risk assessment"""
    
    def __init__(self, db_path: str = "loan_scoring.db"):
        self.db_path = db_path
        self.init_analytics_tables()
        self.db_manager = DatabaseManager()
    
    def init_analytics_tables(self):
        """Initialize analytics database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Portfolio cohorts tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS portfolio_cohorts (
                cohort_id TEXT PRIMARY KEY,
                cohort_name TEXT,
                cohort_date DATE,
                risk_bucket TEXT,
                score_range TEXT,
                application_count INTEGER,
                avg_score REAL,
                approval_rate REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Industry benchmarks
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS industry_benchmarks (
                benchmark_id TEXT PRIMARY KEY,
                industry_segment TEXT,
                metric_name TEXT,
                metric_value REAL,
                percentile_25 REAL,
                percentile_50 REAL,
                percentile_75 REAL,
                benchmark_date DATE,
                source TEXT
            )
        ''')
        
        # Risk trends tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS risk_trends (
                trend_id TEXT PRIMARY KEY,
                analysis_date DATE,
                portfolio_size INTEGER,
                high_risk_percentage REAL,
                medium_risk_percentage REAL,
                low_risk_percentage REAL,
                avg_portfolio_score REAL,
                approval_rate REAL,
                predicted_default_rate REAL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def analyze_portfolio_cohorts(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Analyze portfolio performance by cohorts"""
        conn = sqlite3.connect(self.db_path)
        
        try:
            # Get applications within date range
            query = '''
                SELECT DATE(timestamp) as application_date,
                       CASE 
                           WHEN total_score >= 600 THEN 'Low Risk'
                           WHEN total_score >= 400 THEN 'Medium Risk'
                           ELSE 'High Risk'
                       END as risk_bucket,
                       total_score,
                       decision,
                       COUNT(*) as application_count
                FROM individual_results 
                WHERE DATE(timestamp) BETWEEN ? AND ?
                GROUP BY application_date, risk_bucket
                ORDER BY application_date, risk_bucket
            '''
            
            cohort_df = pd.read_sql_query(query, conn, params=(
                start_date.strftime('%Y-%m-%d'), 
                end_date.strftime('%Y-%m-%d')
            ))
            
            if len(cohort_df) == 0:
                return {'error': 'No data found for the specified date range'}
            
            # Calculate cohort metrics
            cohort_analysis = {}
            
            for date in cohort_df['application_date'].unique():
                date_data = cohort_df[cohort_df['application_date'] == date]
                
                cohort_analysis[date] = {
                    'total_applications': date_data['application_count'].sum(),
                    'risk_distribution': {
                        'high_risk': date_data[date_data['risk_bucket'] == 'High Risk']['application_count'].sum(),
                        'medium_risk': date_data[date_data['risk_bucket'] == 'Medium Risk']['application_count'].sum(),
                        'low_risk': date_data[date_data['risk_bucket'] == 'Low Risk']['application_count'].sum()
                    },
                    'avg_score': self._get_avg_score_for_date(date, conn),
                    'approval_rate': self._get_approval_rate_for_date(date, conn)
                }
            
            return {
                'cohort_analysis': cohort_analysis,
                'summary': self._generate_cohort_summary(cohort_analysis),
                'trends': self._identify_portfolio_trends(cohort_analysis)
            }
            
        except Exception as e:
            return {'error': f'Error analyzing cohorts: {str(e)}'}
        finally:
            conn.close()
    
    def _get_avg_score_for_date(self, date: str, conn: sqlite3.Connection) -> float:
        """Get average score for specific date"""
        cursor = conn.cursor()
        cursor.execute('''
            SELECT AVG(total_score) FROM individual_results 
            WHERE DATE(timestamp) = ?
        ''', (date,))
        
        result = cursor.fetchone()
        return result[0] if result and result[0] else 0.0
    
    def _get_approval_rate_for_date(self, date: str, conn: sqlite3.Connection) -> float:
        """Get approval rate for specific date"""
        cursor = conn.cursor()
        cursor.execute('''
            SELECT 
                SUM(CASE WHEN decision = 'APPROVE' THEN 1 ELSE 0 END) * 1.0 / COUNT(*) as approval_rate
            FROM individual_results 
            WHERE DATE(timestamp) = ?
        ''', (date,))
        
        result = cursor.fetchone()
        return result[0] if result and result[0] else 0.0
    
    def _generate_cohort_summary(self, cohort_analysis: Dict) -> Dict[str, Any]:
        """Generate summary statistics for cohorts"""
        total_apps = sum([cohort['total_applications'] for cohort in cohort_analysis.values()])
        avg_scores = [cohort['avg_score'] for cohort in cohort_analysis.values()]
        approval_rates = [cohort['approval_rate'] for cohort in cohort_analysis.values()]
        
        return {
            'total_applications': total_apps,
            'avg_portfolio_score': np.mean(avg_scores) if avg_scores else 0,
            'avg_approval_rate': np.mean(approval_rates) if approval_rates else 0,
            'score_volatility': np.std(avg_scores) if len(avg_scores) > 1 else 0,
            'approval_volatility': np.std(approval_rates) if len(approval_rates) > 1 else 0
        }
    
    def _identify_portfolio_trends(self, cohort_analysis: Dict) -> Dict[str, str]:
        """Identify key trends in portfolio performance"""
        dates = sorted(cohort_analysis.keys())
        
        if len(dates) < 2:
            return {'trend': 'Insufficient data for trend analysis'}
        
        # Score trend
        scores = [cohort_analysis[date]['avg_score'] for date in dates]
        score_trend = "improving" if scores[-1] > scores[0] else "declining"
        
        # Approval rate trend
        approval_rates = [cohort_analysis[date]['approval_rate'] for date in dates]
        approval_trend = "increasing" if approval_rates[-1] > approval_rates[0] else "decreasing"
        
        # Risk distribution trend
        latest_risk = cohort_analysis[dates[-1]]['risk_distribution']
        earliest_risk = cohort_analysis[dates[0]]['risk_distribution']
        
        latest_total = sum(latest_risk.values())
        earliest_total = sum(earliest_risk.values())
        
        if latest_total > 0 and earliest_total > 0:
            latest_high_risk_pct = latest_risk['high_risk'] / latest_total
            earliest_high_risk_pct = earliest_risk['high_risk'] / earliest_total
            
            risk_trend = "improving" if latest_high_risk_pct < earliest_high_risk_pct else "deteriorating"
        else:
            risk_trend = "stable"
        
        return {
            'score_trend': score_trend,
            'approval_trend': approval_trend,
            'risk_trend': risk_trend,
            'overall_assessment': self._generate_overall_assessment(score_trend, approval_trend, risk_trend)
        }
    
    def _generate_overall_assessment(self, score_trend: str, approval_trend: str, risk_trend: str) -> str:
        """Generate overall portfolio assessment"""
        positive_indicators = sum([
            score_trend == "improving",
            approval_trend == "increasing", 
            risk_trend == "improving"
        ])
        
        if positive_indicators >= 2:
            return "Portfolio performance is showing positive trends"
        elif positive_indicators == 1:
            return "Portfolio performance shows mixed signals"
        else:
            return "Portfolio performance requires attention"
    
    def benchmark_against_industry(self, portfolio_metrics: Dict[str, float], 
                                 industry_segment: str = "Financial Services") -> Dict[str, Any]:
        """Benchmark portfolio against industry standards"""
        
        # Industry benchmark data (in real implementation, this would come from external sources)
        industry_benchmarks = {
            'Financial Services': {
                'approval_rate': {'p25': 0.65, 'p50': 0.75, 'p75': 0.85},
                'avg_credit_score': {'p25': 580, 'p50': 640, 'p75': 720},
                'high_risk_percentage': {'p25': 0.15, 'p50': 0.25, 'p75': 0.35},
                'default_rate': {'p25': 0.02, 'p50': 0.05, 'p75': 0.08}
            },
            'Fintech': {
                'approval_rate': {'p25': 0.55, 'p50': 0.68, 'p75': 0.78},
                'avg_credit_score': {'p25': 560, 'p50': 620, 'p75': 690},
                'high_risk_percentage': {'p25': 0.20, 'p50': 0.30, 'p75': 0.40},
                'default_rate': {'p25': 0.03, 'p50': 0.06, 'p75': 0.10}
            }
        }
        
        benchmarks = industry_benchmarks.get(industry_segment, industry_benchmarks['Financial Services'])
        
        benchmark_results = {}
        
        for metric, value in portfolio_metrics.items():
            if metric in benchmarks:
                benchmark_data = benchmarks[metric]
                
                # Determine percentile position
                if value <= benchmark_data['p25']:
                    percentile = "Below 25th percentile"
                    performance = "Below Average"
                elif value <= benchmark_data['p50']:
                    percentile = "25th-50th percentile"
                    performance = "Average"
                elif value <= benchmark_data['p75']:
                    percentile = "50th-75th percentile"
                    performance = "Above Average"
                else:
                    percentile = "Above 75th percentile"
                    performance = "Excellent"
                
                benchmark_results[metric] = {
                    'portfolio_value': value,
                    'industry_median': benchmark_data['p50'],
                    'percentile_position': percentile,
                    'performance_rating': performance,
                    'gap_to_median': value - benchmark_data['p50']
                }
        
        return {
            'industry_segment': industry_segment,
            'benchmark_results': benchmark_results,
            'overall_rating': self._calculate_overall_rating(benchmark_results)
        }
    
    def _calculate_overall_rating(self, benchmark_results: Dict) -> str:
        """Calculate overall portfolio rating"""
        performance_scores = {
            'Excellent': 4,
            'Above Average': 3,
            'Average': 2,
            'Below Average': 1
        }
        
        scores = [performance_scores.get(result['performance_rating'], 2) 
                 for result in benchmark_results.values()]
        
        avg_score = np.mean(scores)
        
        if avg_score >= 3.5:
            return "Excellent"
        elif avg_score >= 2.5:
            return "Above Average"
        elif avg_score >= 1.5:
            return "Average"
        else:
            return "Below Average"
    
    def predict_portfolio_risk_trends(self, historical_days: int = 90) -> Dict[str, Any]:
        """Predict future portfolio risk trends based on historical data"""
        conn = sqlite3.connect(self.db_path)
        
        try:
            cutoff_date = datetime.now() - timedelta(days=historical_days)
            
            query = '''
                SELECT DATE(timestamp) as date,
                       COUNT(*) as total_applications,
                       AVG(total_score) as avg_score,
                       SUM(CASE WHEN decision = 'APPROVE' THEN 1 ELSE 0 END) * 1.0 / COUNT(*) as approval_rate,
                       SUM(CASE WHEN total_score < 400 THEN 1 ELSE 0 END) * 1.0 / COUNT(*) as high_risk_rate
                FROM individual_results 
                WHERE timestamp >= ?
                GROUP BY DATE(timestamp)
                ORDER BY date
            '''
            
            df = pd.read_sql_query(query, conn, params=(cutoff_date,))
            
            if len(df) < 7:
                return {'error': 'Insufficient data for trend prediction (need at least 7 days)'}
            
            # Simple linear trend analysis
            days = np.arange(len(df))
            
            # Predict score trend
            score_trend = np.polyfit(days, df['avg_score'], 1)
            score_prediction = np.poly1d(score_trend)
            
            # Predict approval rate trend
            approval_trend = np.polyfit(days, df['approval_rate'], 1)
            approval_prediction = np.poly1d(approval_trend)
            
            # Predict high risk rate trend
            risk_trend = np.polyfit(days, df['high_risk_rate'], 1)
            risk_prediction = np.poly1d(risk_trend)
            
            # 30-day predictions
            future_days = np.arange(len(df), len(df) + 30)
            
            predictions = {
                'predicted_avg_score': score_prediction(future_days[-1]),
                'predicted_approval_rate': approval_prediction(future_days[-1]),
                'predicted_high_risk_rate': risk_prediction(future_days[-1]),
                'score_trend_direction': 'increasing' if score_trend[0] > 0 else 'decreasing',
                'approval_trend_direction': 'increasing' if approval_trend[0] > 0 else 'decreasing',
                'risk_trend_direction': 'increasing' if risk_trend[0] > 0 else 'decreasing'
            }
            
            # Generate alerts based on predictions
            alerts = []
            
            if predictions['predicted_high_risk_rate'] > 0.35:
                alerts.append("High risk applications predicted to exceed 35%")
            
            if predictions['predicted_approval_rate'] < 0.50:
                alerts.append("Approval rate predicted to fall below 50%")
            
            if predictions['predicted_avg_score'] < 500:
                alerts.append("Average portfolio score predicted to fall below 500")
            
            return {
                'historical_data': df.to_dict('records'),
                'predictions': predictions,
                'alerts': alerts,
                'confidence_level': self._calculate_prediction_confidence(df)
            }
            
        except Exception as e:
            return {'error': f'Error predicting trends: {str(e)}'}
        finally:
            conn.close()
    
    def _calculate_prediction_confidence(self, df: pd.DataFrame) -> str:
        """Calculate confidence level for predictions"""
        if len(df) >= 30:
            return "High"
        elif len(df) >= 14:
            return "Medium"
        else:
            return "Low"

def render_portfolio_analytics():
    """Render portfolio analytics dashboard"""
    st.header("📈 Portfolio Analytics & Risk Trends")
    st.write("Advanced analytics for portfolio performance and risk assessment")
    
    analytics = PortfolioAnalytics()
    
    tab1, tab2, tab3, tab4 = st.tabs(["Cohort Analysis", "Industry Benchmarks", "Risk Predictions", "Performance Summary"])
    
    with tab1:
        st.subheader("Portfolio Cohort Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            start_date = st.date_input("Start Date", value=datetime.now() - timedelta(days=30))
        
        with col2:
            end_date = st.date_input("End Date", value=datetime.now())
        
        if st.button("🔍 Analyze Cohorts"):
            cohort_results = analytics.analyze_portfolio_cohorts(
                datetime.combine(start_date, datetime.min.time()),
                datetime.combine(end_date, datetime.min.time())
            )
            
            if 'error' not in cohort_results:
                # Summary metrics
                summary = cohort_results['summary']
                trends = cohort_results['trends']
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Applications", f"{summary['total_applications']:,}")
                
                with col2:
                    st.metric("Avg Portfolio Score", f"{summary['avg_portfolio_score']:.0f}")
                
                with col3:
                    st.metric("Avg Approval Rate", f"{summary['avg_approval_rate']:.1%}")
                
                with col4:
                    st.metric("Score Volatility", f"{summary['score_volatility']:.1f}")
                
                # Trends analysis
                st.subheader("📊 Portfolio Trends")
                
                trend_color = {
                    'improving': 'success',
                    'increasing': 'success', 
                    'stable': 'info',
                    'declining': 'warning',
                    'decreasing': 'warning',
                    'deteriorating': 'error'
                }
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    color = trend_color.get(trends['score_trend'], 'info')
                    with getattr(st, color)():
                        st.write(f"**Score Trend:** {trends['score_trend'].title()}")
                
                with col2:
                    color = trend_color.get(trends['approval_trend'], 'info')
                    with getattr(st, color)():
                        st.write(f"**Approval Trend:** {trends['approval_trend'].title()}")
                
                with col3:
                    color = trend_color.get(trends['risk_trend'], 'info')
                    with getattr(st, color)():
                        st.write(f"**Risk Trend:** {trends['risk_trend'].title()}")
                
                # Overall assessment
                overall_color = 'success' if 'positive' in trends['overall_assessment'] else 'warning'
                with getattr(st, overall_color)():
                    st.write(f"**Overall Assessment:** {trends['overall_assessment']}")
                
                # Detailed cohort data
                st.subheader("📅 Daily Cohort Performance")
                
                cohort_data = []
                for date, data in cohort_results['cohort_analysis'].items():
                    cohort_data.append({
                        'Date': date,
                        'Total Applications': data['total_applications'],
                        'Avg Score': f"{data['avg_score']:.0f}",
                        'Approval Rate': f"{data['approval_rate']:.1%}",
                        'High Risk %': f"{data['risk_distribution']['high_risk'] / data['total_applications']:.1%}" if data['total_applications'] > 0 else "0%"
                    })
                
                st.dataframe(pd.DataFrame(cohort_data), use_container_width=True)
                
            else:
                st.error(cohort_results['error'])
    
    with tab2:
        st.subheader("Industry Benchmarking")
        
        industry_segment = st.selectbox(
            "Industry Segment",
            options=["Financial Services", "Fintech"],
            index=0
        )
        
        # Calculate current portfolio metrics (simulated for demo)
        portfolio_metrics = {
            'approval_rate': 0.72,
            'avg_credit_score': 650,
            'high_risk_percentage': 0.28,
            'default_rate': 0.045
        }
        
        benchmark_results = analytics.benchmark_against_industry(portfolio_metrics, industry_segment)
        
        st.write(f"**Benchmarking against:** {benchmark_results['industry_segment']}")
        st.write(f"**Overall Rating:** {benchmark_results['overall_rating']}")
        
        # Benchmark comparison table
        benchmark_data = []
        for metric, data in benchmark_results['benchmark_results'].items():
            benchmark_data.append({
                'Metric': metric.replace('_', ' ').title(),
                'Portfolio Value': f"{data['portfolio_value']:.3f}",
                'Industry Median': f"{data['industry_median']:.3f}",
                'Performance': data['performance_rating'],
                'Percentile': data['percentile_position']
            })
        
        st.dataframe(pd.DataFrame(benchmark_data), use_container_width=True)
        
        # Benchmark visualization
        fig = go.Figure()
        
        metrics = list(benchmark_results['benchmark_results'].keys())
        portfolio_values = [benchmark_results['benchmark_results'][m]['portfolio_value'] for m in metrics]
        industry_medians = [benchmark_results['benchmark_results'][m]['industry_median'] for m in metrics]
        
        fig.add_trace(go.Bar(
            name='Portfolio',
            x=metrics,
            y=portfolio_values,
            marker_color='blue'
        ))
        
        fig.add_trace(go.Bar(
            name='Industry Median',
            x=metrics,
            y=industry_medians,
            marker_color='orange'
        ))
        
        fig.update_layout(
            title="Portfolio vs Industry Benchmark",
            xaxis_title="Metrics",
            yaxis_title="Values",
            barmode='group'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.subheader("Risk Trend Predictions")
        
        historical_period = st.slider("Historical Period (days)", 30, 180, 90)
        
        if st.button("🔮 Generate Predictions"):
            predictions = analytics.predict_portfolio_risk_trends(historical_period)
            
            if 'error' not in predictions:
                # Prediction summary
                pred = predictions['predictions']
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        "Predicted Avg Score (30d)",
                        f"{pred['predicted_avg_score']:.0f}",
                        delta=f"{pred['score_trend_direction']}"
                    )
                
                with col2:
                    st.metric(
                        "Predicted Approval Rate (30d)",
                        f"{pred['predicted_approval_rate']:.1%}",
                        delta=f"{pred['approval_trend_direction']}"
                    )
                
                with col3:
                    st.metric(
                        "Predicted High Risk Rate (30d)",
                        f"{pred['predicted_high_risk_rate']:.1%}",
                        delta=f"{pred['risk_trend_direction']}"
                    )
                
                # Prediction confidence
                confidence_color = {
                    'High': 'success',
                    'Medium': 'warning',
                    'Low': 'error'
                }
                
                confidence = predictions['confidence_level']
                with getattr(st, confidence_color[confidence])():
                    st.write(f"**Prediction Confidence:** {confidence}")
                
                # Alerts
                if predictions['alerts']:
                    st.subheader("⚠️ Risk Alerts")
                    for alert in predictions['alerts']:
                        st.warning(alert)
                else:
                    st.success("No risk alerts for the predicted period")
                
                # Historical trend chart
                if predictions['historical_data']:
                    st.subheader("📈 Historical Trends")
                    
                    hist_df = pd.DataFrame(predictions['historical_data'])
                    
                    fig = go.Figure()
                    
                    fig.add_trace(go.Scatter(
                        x=hist_df['date'],
                        y=hist_df['avg_score'],
                        mode='lines+markers',
                        name='Average Score',
                        yaxis='y'
                    ))
                    
                    fig.add_trace(go.Scatter(
                        x=hist_df['date'],
                        y=hist_df['approval_rate'],
                        mode='lines+markers',
                        name='Approval Rate',
                        yaxis='y2'
                    ))
                    
                    fig.update_layout(
                        title="Historical Portfolio Trends",
                        xaxis_title="Date",
                        yaxis=dict(title="Average Score", side="left"),
                        yaxis2=dict(title="Approval Rate", side="right", overlaying="y")
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                
            else:
                st.error(predictions['error'])
    
    with tab4:
        st.subheader("Executive Summary")
        
        # High-level KPIs
        st.write("### Key Performance Indicators")
        
        # This would pull real data from the database
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Portfolio Size", "12,450", delta="5.2%")
        
        with col2:
            st.metric("Avg Credit Score", "647", delta="3 points")
        
        with col3:
            st.metric("Approval Rate", "72.3%", delta="1.5%")
        
        with col4:
            st.metric("Risk-Adjusted Return", "8.7%", delta="0.3%")
        
        # Portfolio composition
        st.write("### Portfolio Risk Composition")
        
        risk_data = {
            'Risk Category': ['Low Risk', 'Medium Risk', 'High Risk'],
            'Count': [4500, 5200, 2750],
            'Percentage': [36.1, 41.8, 22.1]
        }
        
        fig = px.pie(
            values=risk_data['Count'],
            names=risk_data['Risk Category'],
            title="Portfolio Risk Distribution"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Recent performance
        st.write("### Recent Performance Highlights")
        
        highlights = [
            "✅ Approval rate increased by 1.5% this month",
            "✅ Average credit score improved by 3 points", 
            "✅ High-risk applications reduced by 2.1%",
            "⚠️ Portfolio volatility slightly increased",
            "📈 Predicted continued improvement next quarter"
        ]
        
        for highlight in highlights:
            st.write(highlight)