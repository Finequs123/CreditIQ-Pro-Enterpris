"""
API Integration Module for CreditIQ Pro
Provides REST API endpoints and webhook capabilities
"""

import streamlit as st
import pandas as pd
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from scoring_engine import LoanScoringEngine
from database import DatabaseManager
from ml_weight_optimizer import MLWeightOptimizer
import uuid
import sqlite3
import warnings
warnings.filterwarnings('ignore')

class APIIntegration:
    """Handles API endpoints and external integrations"""
    
    def __init__(self, db_path: str = "loan_scoring.db"):
        self.db_path = db_path
        self.init_api_tables()
        self.scoring_engine = LoanScoringEngine()
        self.db_manager = DatabaseManager()
    
    def init_api_tables(self):
        """Initialize API-related database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # API keys management
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS api_keys (
                key_id TEXT PRIMARY KEY,
                key_name TEXT,
                api_key TEXT UNIQUE,
                permissions TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_used TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        # API request logs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS api_request_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                api_key TEXT,
                endpoint TEXT,
                method TEXT,
                request_data TEXT,
                response_data TEXT,
                status_code INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Webhook configurations
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS webhook_configs (
                webhook_id TEXT PRIMARY KEY,
                name TEXT,
                url TEXT,
                events TEXT,
                secret TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Webhook delivery logs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS webhook_deliveries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                webhook_id TEXT,
                event_type TEXT,
                payload TEXT,
                response_status INTEGER,
                delivery_attempts INTEGER DEFAULT 1,
                delivered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (webhook_id) REFERENCES webhook_configs (webhook_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def generate_api_key(self, key_name: str, permissions: List[str]) -> str:
        """Generate new API key"""
        key_id = str(uuid.uuid4())[:8]
        api_key = f"ck_{''.join([str(uuid.uuid4()).replace('-', '') for _ in range(2)][:32])}"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO api_keys (key_id, key_name, api_key, permissions)
            VALUES (?, ?, ?, ?)
        ''', (key_id, key_name, api_key, json.dumps(permissions)))
        
        conn.commit()
        conn.close()
        
        return api_key
    
    def validate_api_key(self, api_key: str, required_permission: str = None) -> bool:
        """Validate API key and permissions"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT permissions, is_active FROM api_keys 
            WHERE api_key = ?
        ''', (api_key,))
        
        result = cursor.fetchone()
        
        if not result or not result[1]:  # Key not found or inactive
            conn.close()
            return False
        
        permissions = json.loads(result[0])
        
        # Update last used timestamp
        cursor.execute('''
            UPDATE api_keys SET last_used = CURRENT_TIMESTAMP 
            WHERE api_key = ?
        ''', (api_key,))
        
        conn.commit()
        conn.close()
        
        if required_permission and required_permission not in permissions:
            return False
        
        return True
    
    def score_application_api(self, api_key: str, application_data: Dict[str, Any]) -> Dict[str, Any]:
        """API endpoint for scoring individual applications"""
        if not self.validate_api_key(api_key, 'score_applications'):
            return {
                'error': 'Invalid API key or insufficient permissions',
                'status': 401
            }
        
        try:
            # Score the application
            result = self.scoring_engine.score_application(application_data)
            
            # Save to database
            self.db_manager.save_individual_result(application_data, result)
            
            # Log API request
            self._log_api_request(api_key, '/api/score', 'POST', application_data, result, 200)
            
            return {
                'status': 200,
                'data': result,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            error_response = {'error': str(e), 'status': 500}
            self._log_api_request(api_key, '/api/score', 'POST', application_data, error_response, 500)
            return error_response
    
    def bulk_score_api(self, api_key: str, applications: List[Dict[str, Any]]) -> Dict[str, Any]:
        """API endpoint for bulk scoring"""
        if not self.validate_api_key(api_key, 'bulk_score'):
            return {
                'error': 'Invalid API key or insufficient permissions',
                'status': 401
            }
        
        try:
            results = []
            session_id = str(uuid.uuid4())
            
            for app_data in applications:
                result = self.scoring_engine.score_application(app_data)
                results.append({
                    'application_id': app_data.get('application_id', str(uuid.uuid4())[:8]),
                    'score': result['total_score'],
                    'decision': result['decision'],
                    'risk_bucket': result['risk_bucket']
                })
            
            # Save bulk results
            self.db_manager.save_bulk_results(results)
            
            # Trigger webhook if configured
            self._trigger_webhook('bulk_processing_complete', {
                'session_id': session_id,
                'total_applications': len(applications),
                'results_summary': {
                    'approved': len([r for r in results if r['decision'] == 'APPROVE']),
                    'rejected': len([r for r in results if r['decision'] == 'REJECT']),
                    'average_score': sum([r['score'] for r in results]) / len(results)
                }
            })
            
            response = {
                'status': 200,
                'session_id': session_id,
                'total_processed': len(results),
                'results': results,
                'timestamp': datetime.now().isoformat()
            }
            
            self._log_api_request(api_key, '/api/bulk-score', 'POST', 
                                {'application_count': len(applications)}, response, 200)
            
            return response
            
        except Exception as e:
            error_response = {'error': str(e), 'status': 500}
            self._log_api_request(api_key, '/api/bulk-score', 'POST', 
                                {'application_count': len(applications)}, error_response, 500)
            return error_response
    
    def get_scoring_config_api(self, api_key: str) -> Dict[str, Any]:
        """API endpoint to retrieve current scoring configuration"""
        if not self.validate_api_key(api_key, 'read_config'):
            return {
                'error': 'Invalid API key or insufficient permissions',
                'status': 401
            }
        
        try:
            config = {
                'weights': self.scoring_engine.variable_weights,
                'score_bands': {
                    'high_risk': '< 400',
                    'medium_risk': '400 - 599',
                    'low_risk': '>= 600'
                },
                'clearance_rules': {
                    'auto_reject_foir': '> 65%',
                    'auto_reject_dpd': '> 5',
                    'auto_reject_enquiries': '> 8'
                }
            }
            
            response = {
                'status': 200,
                'configuration': config,
                'timestamp': datetime.now().isoformat()
            }
            
            self._log_api_request(api_key, '/api/config', 'GET', {}, response, 200)
            return response
            
        except Exception as e:
            error_response = {'error': str(e), 'status': 500}
            self._log_api_request(api_key, '/api/config', 'GET', {}, error_response, 500)
            return error_response
    
    def _log_api_request(self, api_key: str, endpoint: str, method: str, 
                        request_data: Dict, response_data: Dict, status_code: int):
        """Log API request for monitoring"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO api_request_logs 
            (api_key, endpoint, method, request_data, response_data, status_code)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (api_key, endpoint, method, 
              json.dumps(request_data), json.dumps(response_data), status_code))
        
        conn.commit()
        conn.close()
    
    def add_webhook(self, name: str, url: str, events: List[str], secret: str = None) -> str:
        """Add webhook configuration"""
        webhook_id = str(uuid.uuid4())[:8]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO webhook_configs (webhook_id, name, url, events, secret)
            VALUES (?, ?, ?, ?, ?)
        ''', (webhook_id, name, url, json.dumps(events), secret or ''))
        
        conn.commit()
        conn.close()
        
        return webhook_id
    
    def _trigger_webhook(self, event_type: str, payload: Dict[str, Any]):
        """Trigger webhook for specific event"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT webhook_id, url, secret FROM webhook_configs 
            WHERE is_active = 1 AND events LIKE ?
        ''', (f'%{event_type}%',))
        
        webhooks = cursor.fetchall()
        
        for webhook_id, url, secret in webhooks:
            try:
                # In a real implementation, this would make HTTP requests
                # For now, we'll log the webhook delivery
                cursor.execute('''
                    INSERT INTO webhook_deliveries 
                    (webhook_id, event_type, payload, response_status)
                    VALUES (?, ?, ?, ?)
                ''', (webhook_id, event_type, json.dumps(payload), 200))
                
            except Exception as e:
                cursor.execute('''
                    INSERT INTO webhook_deliveries 
                    (webhook_id, event_type, payload, response_status)
                    VALUES (?, ?, ?, ?)
                ''', (webhook_id, event_type, json.dumps(payload), 500))
        
        conn.commit()
        conn.close()
    
    def get_api_usage_stats(self, days: int = 30) -> Dict[str, Any]:
        """Get API usage statistics"""
        conn = sqlite3.connect(self.db_path)
        
        cutoff_date = datetime.now().timestamp() - (days * 24 * 3600)
        
        try:
            # Request volume by endpoint
            cursor = conn.cursor()
            cursor.execute('''
                SELECT endpoint, COUNT(*) as request_count, 
                       AVG(CASE WHEN status_code = 200 THEN 1 ELSE 0 END) as success_rate
                FROM api_request_logs 
                WHERE timestamp >= datetime(?, 'unixepoch')
                GROUP BY endpoint
            ''', (cutoff_date,))
            
            endpoint_stats = cursor.fetchall()
            
            # API key usage
            cursor.execute('''
                SELECT api_key, COUNT(*) as request_count
                FROM api_request_logs 
                WHERE timestamp >= datetime(?, 'unixepoch')
                GROUP BY api_key
                ORDER BY request_count DESC
            ''', (cutoff_date,))
            
            key_usage = cursor.fetchall()
            
            return {
                'period_days': days,
                'endpoint_statistics': [
                    {
                        'endpoint': endpoint,
                        'request_count': count,
                        'success_rate': f"{success_rate:.1%}"
                    }
                    for endpoint, count, success_rate in endpoint_stats
                ],
                'top_api_keys': [
                    {
                        'api_key': key[:8] + '...',  # Mask the key
                        'request_count': count
                    }
                    for key, count in key_usage[:10]
                ]
            }
            
        except Exception as e:
            return {'error': f'Failed to get usage stats: {str(e)}'}
        finally:
            conn.close()

def render_api_management():
    """Render API management interface"""
    st.header("🔌 API Integration & Management")
    st.write("Manage API keys, webhooks, and external integrations")
    
    api_integration = APIIntegration()
    
    tab1, tab2, tab3, tab4 = st.tabs(["API Keys", "Webhooks", "Usage Stats", "API Docs"])
    
    with tab1:
        st.subheader("API Key Management")
        
        # Create new API key
        with st.expander("Create New API Key"):
            key_name = st.text_input("API Key Name", placeholder="e.g., Production Integration")
            
            permissions = st.multiselect(
                "Permissions",
                options=['score_applications', 'bulk_score', 'read_config', 'webhook_manage'],
                default=['score_applications']
            )
            
            if st.button("Generate API Key"):
                if key_name and permissions:
                    new_key = api_integration.generate_api_key(key_name, permissions)
                    st.success("API Key generated successfully!")
                    st.code(new_key, language='text')
                    st.warning("⚠️ Save this key securely. It won't be shown again.")
                else:
                    st.error("Please provide key name and select permissions")
        
        # Show existing API keys
        st.subheader("Active API Keys")
        
        conn = sqlite3.connect(api_integration.db_path)
        keys_df = pd.read_sql_query('''
            SELECT key_name, api_key, permissions, created_at, last_used, is_active
            FROM api_keys 
            ORDER BY created_at DESC
        ''', conn)
        conn.close()
        
        if len(keys_df) > 0:
            # Mask API keys for display
            keys_df['masked_key'] = keys_df['api_key'].apply(lambda x: x[:8] + '...' + x[-4:])
            display_df = keys_df[['key_name', 'masked_key', 'permissions', 'created_at', 'last_used', 'is_active']].copy()
            
            st.dataframe(display_df, use_container_width=True)
        else:
            st.info("No API keys created yet")
    
    with tab2:
        st.subheader("Webhook Configuration")
        
        # Add new webhook
        with st.expander("Add New Webhook"):
            webhook_name = st.text_input("Webhook Name", placeholder="e.g., Results Notification")
            webhook_url = st.text_input("Webhook URL", placeholder="https://your-system.com/webhook")
            
            webhook_events = st.multiselect(
                "Events to Subscribe",
                options=['bulk_processing_complete', 'scoring_config_updated', 'performance_alert'],
                default=['bulk_processing_complete']
            )
            
            webhook_secret = st.text_input("Secret (optional)", type="password")
            
            if st.button("Add Webhook"):
                if webhook_name and webhook_url and webhook_events:
                    webhook_id = api_integration.add_webhook(
                        webhook_name, webhook_url, webhook_events, webhook_secret
                    )
                    st.success(f"Webhook added successfully! ID: {webhook_id}")
                else:
                    st.error("Please provide all required fields")
        
        # Show existing webhooks
        st.subheader("Active Webhooks")
        
        conn = sqlite3.connect(api_integration.db_path)
        webhooks_df = pd.read_sql_query('''
            SELECT webhook_id, name, url, events, created_at, is_active
            FROM webhook_configs 
            ORDER BY created_at DESC
        ''', conn)
        conn.close()
        
        if len(webhooks_df) > 0:
            st.dataframe(webhooks_df, use_container_width=True)
        else:
            st.info("No webhooks configured yet")
    
    with tab3:
        st.subheader("API Usage Statistics")
        
        period = st.selectbox("Period", [7, 14, 30, 60], index=2)
        
        usage_stats = api_integration.get_api_usage_stats(period)
        
        if 'error' not in usage_stats:
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Endpoint Usage**")
                if usage_stats['endpoint_statistics']:
                    for stat in usage_stats['endpoint_statistics']:
                        st.metric(
                            stat['endpoint'],
                            stat['request_count'],
                            f"{stat['success_rate']} success"
                        )
                else:
                    st.info("No API usage in selected period")
            
            with col2:
                st.write("**Top API Keys**")
                if usage_stats['top_api_keys']:
                    for key_stat in usage_stats['top_api_keys']:
                        st.metric(
                            key_stat['api_key'],
                            f"{key_stat['request_count']} requests"
                        )
                else:
                    st.info("No API key usage in selected period")
        else:
            st.error(usage_stats['error'])
    
    with tab4:
        st.subheader("API Documentation")
        
        st.markdown("""
        ### CreditIQ Pro API Endpoints
        
        #### Authentication
        Include your API key in the `Authorization` header:
        ```
        Authorization: Bearer your_api_key_here
        ```
        
        #### Endpoints
        
        **1. Score Individual Application**
        ```
        POST /api/score
        Content-Type: application/json
        
        {
            "credit_score": 720,
            "foir": 0.45,
            "dpd30plus": 1,
            "enquiry_count": 3,
            "monthly_income": 75000,
            "age": 35,
            "credit_vintage": 60,
            "loan_mix": "Mixed",
            "completion_ratio": 0.85,
            "defaulted_loans": 0,
            "unsecured_amount": 150000,
            "outstanding_amount_percent": 0.3,
            "our_lender_exposure": 0.15,
            "channel": "Direct",
            "job_type": "Salaried",
            "employment_tenure": 48,
            "company_stability": "Large Corporate",
            "account_vintage": 72,
            "avg_monthly_balance": 45000,
            "bounce_frequency": 2,
            "geographic_risk": "Metro",
            "mobile_vintage": 84,
            "digital_engagement": 0.75
        }
        ```
        
        **2. Bulk Score Applications**
        ```
        POST /api/bulk-score
        Content-Type: application/json
        
        {
            "applications": [
                { /* application data */ },
                { /* application data */ }
            ]
        }
        ```
        
        **3. Get Scoring Configuration**
        ```
        GET /api/config
        ```
        
        #### Response Format
        ```json
        {
            "status": 200,
            "data": {
                "total_score": 650,
                "decision": "APPROVE",
                "risk_bucket": "Medium Risk",
                "variable_scores": { /* detailed scores */ }
            },
            "timestamp": "2024-01-15T10:30:00Z"
        }
        ```
        
        #### Webhooks
        Configure webhooks to receive notifications for:
        - `bulk_processing_complete`: When bulk scoring is finished
        - `scoring_config_updated`: When scoring weights are modified
        - `performance_alert`: When model performance alerts are triggered
        """)