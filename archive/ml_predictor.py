import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score
import joblib
import sqlite3
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

class LoanMLPredictor:
    """Machine Learning predictor for loan default probability"""
    
    def __init__(self, db_path: str = "loan_scoring.db"):
        self.db_path = db_path
        self.model = None
        self.feature_columns = [
            'credit_score', 'foir', 'dpd30plus', 'enquiry_count', 'monthly_income',
            'age', 'credit_vintage_months', 'loan_completion_ratio', 'defaulted_loans',
            'unsecured_loan_amount', 'outstanding_amount_percent', 'our_lender_exposure',
            'employment_tenure_months', 'bank_account_vintage_months', 
            'avg_monthly_balance', 'bounce_frequency_per_year', 'mobile_vintage_months',
            'digital_engagement_score'
        ]
        self.categorical_mappings = {
            'loan_mix_type': {'Only Secured': 0, 'Only Unsecured': 1, 'Mixed': 2},
            'channel_type': {'Online': 0, 'Branch': 1, 'Partner': 2},
            'job_type': {'Salaried': 0, 'Self-employed': 1, 'Business': 2},
            'company_stability': {'Stable MNC': 0, 'Government': 1, 'Startup': 2, 'Mid-size': 3},
            'geographic_location_risk': {'Low Risk': 0, 'Medium Risk': 1, 'High Risk': 2}
        }
        
    def load_historical_data(self) -> pd.DataFrame:
        """Load historical data from database"""
        conn = sqlite3.connect(self.db_path)
        
        query = '''
        SELECT applicant_data, scoring_result, final_bucket, decision
        FROM individual_applications
        WHERE timestamp >= date('now', '-12 months')
        '''
        
        historical_data = []
        cursor = conn.execute(query)
        
        for row in cursor.fetchall():
            try:
                import json
                applicant_data = json.loads(row[0])
                scoring_result = json.loads(row[1])
                
                # Create feature vector
                features = self._extract_features(applicant_data)
                features['final_bucket'] = row[2]
                features['decision'] = row[3]
                features['default_risk'] = 1 if row[2] in ['C', 'D'] else 0  # Target variable
                
                historical_data.append(features)
            except:
                continue
                
        conn.close()
        
        if len(historical_data) < 50:  # Need minimum data for training
            return None
            
        return pd.DataFrame(historical_data)
    
    def _extract_features(self, applicant_data: Dict[str, Any]) -> Dict[str, float]:
        """Extract numerical features from applicant data"""
        features = {}
        
        # Numerical features
        for col in self.feature_columns:
            features[col] = float(applicant_data.get(col, 0))
        
        # Categorical features (encoded)
        for cat_col, mapping in self.categorical_mappings.items():
            value = applicant_data.get(cat_col, list(mapping.keys())[0])
            features[f'{cat_col}_encoded'] = mapping.get(value, 0)
            
        return features
    
    def train_model(self) -> Dict[str, Any]:
        """Train the ML model on historical data"""
        df = self.load_historical_data()
        
        if df is None:
            return {
                'status': 'insufficient_data',
                'message': 'Need at least 50 historical records to train model',
                'records_needed': 50
            }
        
        # Prepare features and target
        feature_cols = self.feature_columns + [f'{cat}_encoded' for cat in self.categorical_mappings.keys()]
        X = df[feature_cols].fillna(0)
        y = df['default_risk']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Train Gradient Boosting model
        self.model = GradientBoostingClassifier(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=42
        )
        
        self.model.fit(X_train, y_train)
        
        # Evaluate model
        train_score = self.model.score(X_train, y_train)
        test_score = self.model.score(X_test, y_test)
        
        # Get feature importance
        feature_importance = dict(zip(feature_cols, self.model.feature_importances_))
        top_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Predictions for AUC
        y_pred_proba = self.model.predict_proba(X_test)[:, 1]
        auc_score = roc_auc_score(y_test, y_pred_proba)
        
        # Save model
        model_path = f"loan_ml_model_{datetime.now().strftime('%Y%m%d_%H%M%S')}.joblib"
        joblib.dump(self.model, model_path)
        
        return {
            'status': 'success',
            'training_records': len(df),
            'train_accuracy': round(train_score, 3),
            'test_accuracy': round(test_score, 3),
            'auc_score': round(auc_score, 3),
            'top_features': top_features[:5],
            'model_path': model_path,
            'trained_at': datetime.now().isoformat()
        }
    
    def predict_default_probability(self, applicant_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict default probability for new applicant"""
        if self.model is None:
            return {
                'status': 'no_model',
                'message': 'Model not trained yet. Please train the model first.'
            }
        
        # Extract features
        features = self._extract_features(applicant_data)
        feature_cols = self.feature_columns + [f'{cat}_encoded' for cat in self.categorical_mappings.keys()]
        
        # Create feature vector
        X = pd.DataFrame([features])[feature_cols].fillna(0)
        
        # Predict
        default_probability = self.model.predict_proba(X)[0][1]
        risk_prediction = self.model.predict(X)[0]
        
        # Get feature contributions (simplified)
        feature_importance = dict(zip(feature_cols, self.model.feature_importances_))
        
        return {
            'status': 'success',
            'default_probability': round(float(default_probability), 4),
            'risk_level': 'High Risk' if risk_prediction == 1 else 'Low Risk',
            'confidence': round(max(self.model.predict_proba(X)[0]), 3),
            'top_risk_factors': self._get_top_risk_factors(features, feature_importance)
        }
    
    def _get_top_risk_factors(self, features: Dict[str, float], importance: Dict[str, float]) -> List[Dict[str, Any]]:
        """Get top risk factors for the applicant"""
        risk_factors = []
        
        for feature, imp in sorted(importance.items(), key=lambda x: x[1], reverse=True)[:5]:
            if feature in features:
                risk_factors.append({
                    'factor': feature.replace('_', ' ').title(),
                    'value': features[feature],
                    'importance': round(imp, 3)
                })
        
        return risk_factors
    
    def load_model(self, model_path: str) -> bool:
        """Load a pre-trained model"""
        try:
            self.model = joblib.load(model_path)
            return True
        except:
            return False
    
    def get_model_performance(self) -> Dict[str, Any]:
        """Get comprehensive model performance metrics"""
        df = self.load_historical_data()
        
        if df is None or self.model is None:
            return {'status': 'no_data_or_model'}
        
        feature_cols = self.feature_columns + [f'{cat}_encoded' for cat in self.categorical_mappings.keys()]
        X = df[feature_cols].fillna(0)
        y = df['default_risk']
        
        # Predictions
        y_pred = self.model.predict(X)
        y_pred_proba = self.model.predict_proba(X)[:, 1]
        
        # Performance metrics
        from sklearn.metrics import confusion_matrix, precision_recall_fscore_support
        
        cm = confusion_matrix(y, y_pred)
        precision, recall, f1, _ = precision_recall_fscore_support(y, y_pred, average='binary')
        
        return {
            'status': 'success',
            'total_records': len(df),
            'accuracy': round(self.model.score(X, y), 3),
            'precision': round(precision, 3),
            'recall': round(recall, 3),
            'f1_score': round(f1, 3),
            'auc_score': round(roc_auc_score(y, y_pred_proba), 3),
            'confusion_matrix': cm.tolist(),
            'default_rate': round(y.mean(), 3),
            'feature_importance': dict(zip(feature_cols, self.model.feature_importances_))
        }