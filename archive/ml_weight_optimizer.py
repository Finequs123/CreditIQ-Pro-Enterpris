"""
ML-driven Weight Optimization System
Automatically learns optimal scoring weights from actual loan performance data
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, r2_score
from scipy.optimize import minimize
import sqlite3
import json
import joblib
from datetime import datetime
from typing import Dict, Any, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

class MLWeightOptimizer:
    """ML system for automatic scoring weight optimization based on actual loan performance"""
    
    def __init__(self, db_path: str = "loan_scoring.db"):
        self.db_path = db_path
        self.model = None
        self.weight_model = None
        self.current_weights = {}
        self.performance_history = []
        self.variable_names = [
            'credit_score', 'foir', 'dpd30plus', 'enquiry_count', 'age', 'monthly_income',
            'credit_vintage', 'loan_mix_type', 'loan_completion_ratio', 'defaulted_loans',
            'job_type', 'employment_tenure', 'company_stability', 'account_vintage',
            'avg_monthly_balance', 'bounce_frequency', 'geographic_risk', 
            'mobile_number_vintage', 'digital_engagement', 'unsecured_loan_amount',
            'outstanding_amount_percent', 'our_lender_exposure', 'channel_type'
        ]
        self.init_database()
        
    def init_database(self):
        """Initialize database tables for ML learning"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create table for actual loan performance data
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS loan_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                pan TEXT,
                application_data TEXT,  -- JSON string of application data
                predicted_score REAL,
                predicted_bucket TEXT,
                actual_outcome TEXT,    -- 'good', 'bad', 'indeterminate'
                days_to_outcome INTEGER,
                amount_recovered REAL,
                total_exposure REAL,
                performance_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create table for weight optimization experiments
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS weight_experiments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                experiment_id TEXT UNIQUE,
                weights_config TEXT,    -- JSON string of weights
                performance_metrics TEXT, -- JSON string of metrics
                validation_score REAL,
                approval_rate REAL,
                default_rate REAL,
                experiment_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create table for ML model versions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ml_models (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_version TEXT UNIQUE,
                model_type TEXT,
                model_path TEXT,
                performance_metrics TEXT,
                is_active BOOLEAN DEFAULT FALSE,
                created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def load_performance_data(self) -> Optional[pd.DataFrame]:
        """Load actual loan performance data for ML training"""
        conn = sqlite3.connect(self.db_path)
        
        try:
            # Load performance data
            query = '''
                SELECT 
                    pan,
                    application_data,
                    predicted_score,
                    predicted_bucket,
                    actual_outcome,
                    days_to_outcome,
                    amount_recovered,
                    total_exposure,
                    performance_timestamp
                FROM loan_performance
                WHERE actual_outcome IS NOT NULL
                ORDER BY performance_timestamp DESC
            '''
            
            df = pd.read_sql_query(query, conn)
            
            if len(df) < 100:  # Need minimum data for reliable ML
                return None
                
            # Parse application data JSON
            application_data_list = df['application_data'].apply(json.loads).tolist()
            
            # Extract features from application data
            features_df = pd.json_normalize(application_data_list)
            
            # Combine with performance data
            result_df = pd.concat([df.drop('application_data', axis=1), features_df], axis=1)
            
            return result_df
            
        except Exception as e:
            print(f"Error loading performance data: {e}")
            return None
        finally:
            conn.close()
    
    def analyze_variable_performance(self, df: pd.DataFrame) -> Dict[str, float]:
        """Analyze how well each variable predicts actual loan performance"""
        variable_importance = {}
        
        # Create binary target: 1 for bad loans, 0 for good loans
        y = (df['actual_outcome'] == 'bad').astype(int)
        
        for var in self.variable_names:
            if var in df.columns:
                try:
                    # Handle categorical variables
                    if df[var].dtype == 'object':
                        # Convert to numeric using label encoding
                        var_encoded = pd.Categorical(df[var]).codes
                    else:
                        var_encoded = df[var].fillna(df[var].median())
                    
                    # Calculate correlation with actual outcome
                    correlation = np.corrcoef(var_encoded, y)[0, 1]
                    
                    # Use absolute correlation as importance
                    variable_importance[var] = abs(correlation) if not np.isnan(correlation) else 0.0
                    
                except Exception as e:
                    variable_importance[var] = 0.0
            else:
                variable_importance[var] = 0.0
        
        return variable_importance
    
    def optimize_weights_with_ml(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Use ML to find optimal weights based on actual loan performance"""
        
        # Analyze variable importance
        variable_importance = self.analyze_variable_performance(df)
        
        # Normalize importance scores to sum to 1.0
        total_importance = sum(variable_importance.values())
        if total_importance > 0:
            suggested_weights = {
                var: importance / total_importance 
                for var, importance in variable_importance.items()
            }
        else:
            # Fallback to equal weights
            num_vars = len(self.variable_names)
            suggested_weights = {var: 1.0/num_vars for var in self.variable_names}
        
        # Calculate performance metrics
        good_loans = len(df[df['actual_outcome'] == 'good'])
        bad_loans = len(df[df['actual_outcome'] == 'bad'])
        default_rate = bad_loans / (good_loans + bad_loans) if (good_loans + bad_loans) > 0 else 0
        
        # Simulate approval rate based on predicted buckets
        approved_buckets = ['A', 'B']
        approved_count = len(df[df['predicted_bucket'].isin(approved_buckets)])
        approval_rate = approved_count / len(df) if len(df) > 0 else 0
        
        # Calculate validation score (lower default rate + reasonable approval rate)
        validation_score = float((1 - default_rate) * 0.7 + (approval_rate * 0.3))
        
        return {
            'suggested_weights': suggested_weights,
            'variable_importance': variable_importance,
            'performance_metrics': {
                'total_loans': len(df),
                'good_loans': good_loans,
                'bad_loans': bad_loans,
                'default_rate': round(default_rate, 4),
                'approval_rate': round(approval_rate, 4),
                'validation_score': round(validation_score, 4)
            },
            'recommendation_confidence': min(len(df) / 1000, 1.0),  # Confidence based on data size
            'optimization_timestamp': datetime.now().isoformat()
        }
    
    def train_weight_prediction_model(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Train ML model to predict optimal weights for new scenarios"""
        
        if len(df) < 200:
            return {'status': 'insufficient_data', 'message': 'Need at least 200 performance records'}
        
        try:
            # Prepare features for weight prediction
            # Use loan characteristics to predict optimal variable weights
            
            # Extract application features
            feature_columns = []
            for var in self.variable_names:
                if var in df.columns:
                    if df[var].dtype == 'object':
                        # One-hot encode categorical variables
                        dummies = pd.get_dummies(df[var], prefix=var)
                        df = pd.concat([df, dummies], axis=1)
                        feature_columns.extend(dummies.columns.tolist())
                    else:
                        feature_columns.append(var)
            
            # Create target: success score for each loan
            y = np.where(df['actual_outcome'] == 'good', 1.0, 0.0)
            
            # Prepare feature matrix
            X = df[feature_columns].fillna(0)
            
            # Train Random Forest model
            self.weight_model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )
            
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            self.weight_model.fit(X_train, y_train)
            
            # Evaluate model
            train_score = self.weight_model.score(X_train, y_train)
            test_score = self.weight_model.score(X_test, y_test)
            
            # Get feature importance for weight suggestions
            feature_importance = dict(zip(feature_columns, self.weight_model.feature_importances_))
            
            # Save model
            model_version = f"weight_model_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            model_path = f"{model_version}.joblib"
            joblib.dump(self.weight_model, model_path)
            
            # Save to database
            self._save_model_version(model_version, "weight_predictor", model_path, {
                'train_score': train_score,
                'test_score': test_score,
                'feature_count': len(feature_columns)
            })
            
            return {
                'status': 'success',
                'model_version': model_version,
                'train_score': round(train_score, 3),
                'test_score': round(test_score, 3),
                'feature_importance': feature_importance,
                'training_records': len(df)
            }
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def suggest_weights_for_portfolio(self, portfolio_data: List[Dict]) -> Dict[str, Any]:
        """Suggest optimal weights for a new portfolio based on ML model"""
        
        if self.weight_model is None:
            # Fallback to performance-based analysis
            df = self.load_performance_data()
            if df is not None:
                return self.optimize_weights_with_ml(df)
            else:
                return self._get_default_weights()
        
        try:
            # Analyze portfolio characteristics
            portfolio_df = pd.DataFrame(portfolio_data)
            
            # Extract features similar to training
            feature_columns = []
            for var in self.variable_names:
                if var in portfolio_df.columns:
                    if portfolio_df[var].dtype == 'object':
                        dummies = pd.get_dummies(portfolio_df[var], prefix=var)
                        portfolio_df = pd.concat([portfolio_df, dummies], axis=1)
                        feature_columns.extend(dummies.columns.tolist())
                    else:
                        feature_columns.append(var)
            
            # Get available features that match training
            available_features = [col for col in feature_columns if col in portfolio_df.columns]
            X_portfolio = portfolio_df[available_features].fillna(0)
            
            # Predict success scores
            predicted_scores = self.weight_model.predict(X_portfolio)
            
            # Calculate variable importance for this portfolio
            if hasattr(self.weight_model, 'feature_importances_'):
                importance_dict = dict(zip(available_features, self.weight_model.feature_importances_))
                
                # Map back to original variables
                variable_weights = {}
                for var in self.variable_names:
                    var_importance = sum([imp for feat, imp in importance_dict.items() if feat.startswith(var)])
                    variable_weights[var] = var_importance
                
                # Normalize weights
                total_weight = sum(variable_weights.values())
                if total_weight > 0:
                    variable_weights = {var: weight/total_weight for var, weight in variable_weights.items()}
            
            return {
                'suggested_weights': variable_weights,
                'portfolio_risk_score': np.mean(predicted_scores),
                'confidence': min(len(portfolio_data) / 100, 1.0),
                'model_based': True
            }
            
        except Exception as e:
            # Fallback to default analysis
            return self._get_default_weights()
    
    def _save_model_version(self, version: str, model_type: str, path: str, metrics: Dict):
        """Save model version to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO ml_models 
            (model_version, model_type, model_path, performance_metrics, is_active)
            VALUES (?, ?, ?, ?, ?)
        ''', (version, model_type, path, json.dumps(metrics), True))
        
        conn.commit()
        conn.close()
    
    def save_performance_data(self, session_id: str, applications: List[Dict], outcomes: List[Dict]):
        """Save actual loan performance data for ML learning"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for app, outcome in zip(applications, outcomes):
            cursor.execute('''
                INSERT INTO loan_performance 
                (session_id, pan, application_data, predicted_score, predicted_bucket, 
                 actual_outcome, days_to_outcome, amount_recovered, total_exposure)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                session_id,
                app.get('pan', ''),
                json.dumps(app),
                outcome.get('predicted_score', 0),
                outcome.get('predicted_bucket', ''),
                outcome.get('actual_outcome', ''),
                outcome.get('days_to_outcome', 0),
                outcome.get('amount_recovered', 0),
                outcome.get('total_exposure', 0)
            ))
        
        conn.commit()
        conn.close()
    
    def _get_default_weights(self) -> Dict[str, Any]:
        """Get default weights when ML model is not available"""
        default_weights = {
            'credit_score': 0.12, 'foir': 0.06, 'dpd30plus': 0.06, 'enquiry_count': 0.05,
            'age': 0.03, 'monthly_income': 0.08, 'credit_vintage': 0.05, 'loan_mix_type': 0.05,
            'loan_completion_ratio': 0.06, 'defaulted_loans': 0.07, 'job_type': 0.05,
            'employment_tenure': 0.04, 'company_stability': 0.03, 'account_vintage': 0.03,
            'avg_monthly_balance': 0.04, 'bounce_frequency': 0.04, 'geographic_risk': 0.03,
            'mobile_number_vintage': 0.02, 'digital_engagement': 0.02, 'unsecured_loan_amount': 0.04,
            'outstanding_amount_percent': 0.04, 'our_lender_exposure': 0.02, 'channel_type': 0.03
        }
        
        return {
            'suggested_weights': default_weights,
            'model_based': False,
            'confidence': 0.5,
            'note': 'Using default weights - insufficient data for ML optimization'
        }
    
    def get_optimization_history(self) -> List[Dict]:
        """Get history of weight optimization experiments"""
        conn = sqlite3.connect(self.db_path)
        
        try:
            query = '''
                SELECT experiment_id, weights_config, performance_metrics, 
                       validation_score, approval_rate, default_rate, experiment_timestamp
                FROM weight_experiments
                ORDER BY experiment_timestamp DESC
                LIMIT 50
            '''
            
            df = pd.read_sql_query(query, conn)
            return df.to_dict('records')
            
        except:
            return []
        finally:
            conn.close()