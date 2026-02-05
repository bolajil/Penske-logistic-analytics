"""
Customer Acquisition & Retention Module for Penske Logistics
Lead scoring, churn prediction, and customer segmentation
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report
)
try:
    import xgboost as xgb
    HAS_XGBOOST = True
except ImportError:
    HAS_XGBOOST = False
    xgb = None
import joblib
from pathlib import Path
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class LeadScorer:
    """Score and prioritize sales leads for customer acquisition"""
    
    def __init__(self):
        self.model = None
        self.scaler = None
        self.feature_columns = []
        self.label_encoders = {}
        
    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare features for lead scoring model"""
        
        df = df.copy()
        
        df['num_services_interested'] = df['services_interested'].str.count(',') + 1
        df['has_decision_maker'] = df['decision_maker_contact'].astype(int)
        df['has_budget'] = df['budget_confirmed'].astype(int)
        
        df['engagement_per_day'] = df['num_interactions'] / (df['days_in_pipeline'] + 1)
        
        df['log_revenue'] = np.log1p(df['estimated_annual_revenue'])
        
        categorical_cols = ['industry', 'company_size', 'region', 'lead_source', 'current_logistics_provider']
        for col in categorical_cols:
            if col in df.columns:
                df = pd.get_dummies(df, columns=[col], prefix=col, drop_first=True)
        
        return df
    
    def train(self, df: pd.DataFrame, target_col: str = 'converted') -> Dict:
        """
        Train lead scoring model
        
        Args:
            df: Leads dataframe with conversion outcome
            target_col: Target variable column
        """
        
        df_prepared = self.prepare_features(df)
        
        exclude_cols = ['lead_id', 'company_name', 'services_interested', target_col,
                       'contract_value_if_converted', 'decision_maker_contact', 'budget_confirmed']
        feature_cols = [c for c in df_prepared.columns if c not in exclude_cols]
        self.feature_columns = df_prepared[feature_cols].select_dtypes(include=[np.number]).columns.tolist()
        
        X = df_prepared[self.feature_columns]
        y = df_prepared[target_col].astype(int)
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
        
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        if HAS_XGBOOST:
            self.model = xgb.XGBClassifier(
                n_estimators=150,
                max_depth=5,
                learning_rate=0.1,
                subsample=0.8,
                colsample_bytree=0.8,
                scale_pos_weight=len(y_train[y_train==0]) / len(y_train[y_train==1]),
                random_state=42,
                use_label_encoder=False,
                eval_metric='logloss'
            )
        else:
            logger.warning("XGBoost not installed, using GradientBoosting instead")
            self.model = GradientBoostingClassifier(
                n_estimators=150,
                max_depth=5,
                learning_rate=0.1,
                subsample=0.8,
                random_state=42
            )
        
        self.model.fit(X_train_scaled, y_train)
        
        y_pred = self.model.predict(X_test_scaled)
        y_pred_proba = self.model.predict_proba(X_test_scaled)[:, 1]
        
        metrics = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred),
            'recall': recall_score(y_test, y_pred),
            'f1': f1_score(y_test, y_pred),
            'auc_roc': roc_auc_score(y_test, y_pred_proba)
        }
        
        cv_scores = cross_val_score(self.model, X_train_scaled, y_train, cv=5, scoring='roc_auc')
        metrics['cv_auc_mean'] = cv_scores.mean()
        metrics['cv_auc_std'] = cv_scores.std()
        
        importance = dict(zip(self.feature_columns, self.model.feature_importances_))
        self.feature_importance = dict(sorted(importance.items(), key=lambda x: x[1], reverse=True)[:15])
        
        logger.info(f"Lead scoring model trained: AUC={metrics['auc_roc']:.3f}")
        
        return {
            'metrics': metrics,
            'feature_importance': self.feature_importance,
            'confusion_matrix': confusion_matrix(y_test, y_pred).tolist()
        }
    
    def score_leads(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Score new leads
        
        Args:
            df: Leads to score
            
        Returns:
            DataFrame with lead scores and priority
        """
        
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")
        
        df_prepared = self.prepare_features(df)
        
        missing_cols = set(self.feature_columns) - set(df_prepared.columns)
        for col in missing_cols:
            df_prepared[col] = 0
        
        X = df_prepared[self.feature_columns]
        X_scaled = self.scaler.transform(X)
        
        scores = self.model.predict_proba(X_scaled)[:, 1]
        
        result = df[['lead_id', 'company_name', 'industry', 'region', 'company_size']].copy()
        result['conversion_probability'] = scores
        result['lead_score'] = (scores * 100).round(1)
        
        result['priority'] = pd.cut(
            result['lead_score'],
            bins=[0, 25, 50, 75, 100],
            labels=['Low', 'Medium', 'High', 'Hot']
        )
        
        return result.sort_values('lead_score', ascending=False)
    
    def get_lead_insights(self, lead_id: str, df: pd.DataFrame) -> Dict:
        """Get detailed insights for a specific lead"""
        
        lead = df[df['lead_id'] == lead_id].iloc[0]
        
        scored = self.score_leads(df[df['lead_id'] == lead_id])
        score = scored['lead_score'].iloc[0]
        
        insights = {
            'lead_id': lead_id,
            'company': lead['company_name'],
            'score': score,
            'priority': scored['priority'].iloc[0],
            'strengths': [],
            'weaknesses': [],
            'recommended_actions': []
        }
        
        if lead.get('decision_maker_contact', False):
            insights['strengths'].append('Has decision maker contact')
        else:
            insights['weaknesses'].append('No decision maker contact')
            insights['recommended_actions'].append('Identify and connect with decision maker')
        
        if lead.get('budget_confirmed', False):
            insights['strengths'].append('Budget confirmed')
        else:
            insights['weaknesses'].append('Budget not confirmed')
            insights['recommended_actions'].append('Discuss budget and timeline')
        
        if lead.get('engagement_score', 0) > 50:
            insights['strengths'].append(f"High engagement ({lead.get('engagement_score', 0):.0f})")
        else:
            insights['weaknesses'].append('Low engagement')
            insights['recommended_actions'].append('Increase touchpoints and provide value content')
        
        if lead.get('company_size') in ['Large', 'Enterprise']:
            insights['strengths'].append(f"High-value prospect ({lead.get('company_size')})")
        
        return insights


class ChurnPredictor:
    """Predict customer churn risk"""
    
    def __init__(self):
        self.model = None
        self.scaler = None
        self.feature_columns = []
        
    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare features for churn prediction"""
        
        df = df.copy()
        
        df['tenure_years'] = df['tenure_months'] / 12
        df['revenue_per_service'] = df['contract_value'] / df['num_services'].replace(0, 1)
        df['value_score'] = (df['contract_value'] / df['contract_value'].max()) * 100
        
        df['sat_below_avg'] = (df['satisfaction_score'] < df['satisfaction_score'].mean()).astype(int)
        
        df['payment_risk'] = (df['payment_reliability'] < 80).astype(int)
        
        categorical_cols = ['industry', 'region', 'shipment_frequency', 'growth_potential']
        for col in categorical_cols:
            if col in df.columns:
                df = pd.get_dummies(df, columns=[col], prefix=col, drop_first=True)
        
        return df
    
    def train(self, df: pd.DataFrame) -> Dict:
        """Train churn prediction model"""
        
        df_prepared = self.prepare_features(df)
        
        target_col = 'is_active'
        df_prepared['churned'] = (~df_prepared[target_col]).astype(int)
        
        exclude_cols = ['customer_id', 'company_name', 'services_used', 'is_active', 'churned']
        feature_cols = [c for c in df_prepared.columns if c not in exclude_cols]
        self.feature_columns = df_prepared[feature_cols].select_dtypes(include=[np.number]).columns.tolist()
        
        X = df_prepared[self.feature_columns]
        y = df_prepared['churned']
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
        
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        self.model = GradientBoostingClassifier(
            n_estimators=100,
            max_depth=4,
            learning_rate=0.1,
            random_state=42
        )
        
        self.model.fit(X_train_scaled, y_train)
        
        y_pred = self.model.predict(X_test_scaled)
        y_pred_proba = self.model.predict_proba(X_test_scaled)[:, 1]
        
        metrics = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred),
            'recall': recall_score(y_test, y_pred),
            'f1': f1_score(y_test, y_pred),
            'auc_roc': roc_auc_score(y_test, y_pred_proba)
        }
        
        importance = dict(zip(self.feature_columns, self.model.feature_importances_))
        self.feature_importance = dict(sorted(importance.items(), key=lambda x: x[1], reverse=True)[:10])
        
        logger.info(f"Churn model trained: AUC={metrics['auc_roc']:.3f}")
        
        return {'metrics': metrics, 'feature_importance': self.feature_importance}
    
    def predict_churn_risk(self, df: pd.DataFrame) -> pd.DataFrame:
        """Predict churn risk for customers"""
        
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")
        
        df_prepared = self.prepare_features(df)
        
        missing_cols = set(self.feature_columns) - set(df_prepared.columns)
        for col in missing_cols:
            df_prepared[col] = 0
        
        X = df_prepared[self.feature_columns]
        X_scaled = self.scaler.transform(X)
        
        churn_prob = self.model.predict_proba(X_scaled)[:, 1]
        
        result = df[['customer_id', 'company_name', 'contract_value', 'tenure_months', 'satisfaction_score']].copy()
        result['churn_probability'] = churn_prob
        result['churn_risk_score'] = (churn_prob * 100).round(1)
        
        result['risk_level'] = pd.cut(
            result['churn_risk_score'],
            bins=[0, 20, 40, 60, 100],
            labels=['Low', 'Moderate', 'High', 'Critical']
        )
        
        result['revenue_at_risk'] = result['contract_value'] * result['churn_probability']
        
        return result.sort_values('churn_risk_score', ascending=False)


class CustomerSegmenter:
    """Segment customers for targeted strategies"""
    
    def __init__(self, n_segments: int = 5):
        self.n_segments = n_segments
        self.model = None
        self.scaler = None
        self.segment_profiles = {}
        
    def prepare_features(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
        """Prepare features for segmentation"""
        
        df = df.copy()
        
        segmentation_features = [
            'contract_value',
            'tenure_months',
            'num_services',
            'satisfaction_score',
            'payment_reliability',
            'avg_shipment_value'
        ]
        
        available_features = [f for f in segmentation_features if f in df.columns]
        
        df_features = df[available_features].copy()
        df_features = df_features.fillna(df_features.median())
        
        return df_features, available_features
    
    def fit_segments(self, df: pd.DataFrame) -> Dict:
        """Fit customer segmentation model"""
        
        df_features, feature_cols = self.prepare_features(df)
        
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(df_features)
        
        self.model = KMeans(n_clusters=self.n_segments, random_state=42, n_init=10)
        segments = self.model.fit_predict(X_scaled)
        
        df_result = df.copy()
        df_result['segment'] = segments
        
        segment_names = {
            0: 'Premium Partners',
            1: 'Growth Accounts',
            2: 'Stable Core',
            3: 'New Prospects',
            4: 'At-Risk Accounts'
        }
        
        for seg in range(self.n_segments):
            seg_data = df_result[df_result['segment'] == seg]
            
            self.segment_profiles[seg] = {
                'name': segment_names.get(seg, f'Segment {seg}'),
                'count': len(seg_data),
                'pct_of_total': len(seg_data) / len(df) * 100,
                'avg_contract_value': seg_data['contract_value'].mean(),
                'avg_tenure': seg_data['tenure_months'].mean(),
                'avg_satisfaction': seg_data['satisfaction_score'].mean(),
                'total_revenue': seg_data['contract_value'].sum(),
                'characteristics': self._describe_segment(seg_data, df)
            }
        
        return {
            'n_segments': self.n_segments,
            'segment_profiles': self.segment_profiles,
            'feature_columns': feature_cols
        }
    
    def _describe_segment(self, seg_data: pd.DataFrame, full_data: pd.DataFrame) -> List[str]:
        """Generate descriptive characteristics for a segment"""
        
        chars = []
        
        if seg_data['contract_value'].mean() > full_data['contract_value'].quantile(0.75):
            chars.append('High-value contracts')
        elif seg_data['contract_value'].mean() < full_data['contract_value'].quantile(0.25):
            chars.append('Lower contract values')
        
        if seg_data['tenure_months'].mean() > full_data['tenure_months'].mean():
            chars.append('Long-term relationships')
        else:
            chars.append('Newer customers')
        
        if seg_data['satisfaction_score'].mean() > 8:
            chars.append('Highly satisfied')
        elif seg_data['satisfaction_score'].mean() < 6:
            chars.append('Satisfaction concerns')
        
        if seg_data['num_services'].mean() > 2:
            chars.append('Multi-service users')
        
        return chars
    
    def assign_segments(self, df: pd.DataFrame) -> pd.DataFrame:
        """Assign segments to customers"""
        
        if self.model is None:
            raise ValueError("Model not fitted. Call fit_segments() first.")
        
        df_features, _ = self.prepare_features(df)
        X_scaled = self.scaler.transform(df_features)
        
        segments = self.model.predict(X_scaled)
        
        result = df.copy()
        result['segment_id'] = segments
        result['segment_name'] = result['segment_id'].map(
            {k: v['name'] for k, v in self.segment_profiles.items()}
        )
        
        return result
    
    def get_segment_strategies(self) -> Dict[str, Dict]:
        """Get recommended strategies for each segment"""
        
        strategies = {
            'Premium Partners': {
                'focus': 'Retention and expansion',
                'actions': [
                    'Assign dedicated account manager',
                    'Quarterly business reviews',
                    'Early access to new services',
                    'Custom SLA arrangements'
                ],
                'upsell_potential': 'High - explore additional services'
            },
            'Growth Accounts': {
                'focus': 'Accelerate growth',
                'actions': [
                    'Increase service adoption',
                    'Volume-based incentives',
                    'Technology integration support',
                    'Regular check-ins'
                ],
                'upsell_potential': 'Very High - prime for expansion'
            },
            'Stable Core': {
                'focus': 'Maintain and optimize',
                'actions': [
                    'Efficiency improvements',
                    'Automation opportunities',
                    'Annual reviews',
                    'Loyalty recognition'
                ],
                'upsell_potential': 'Moderate - focus on optimization'
            },
            'New Prospects': {
                'focus': 'Onboarding and engagement',
                'actions': [
                    'Structured onboarding program',
                    'Quick wins demonstration',
                    'Regular communication',
                    'Training and support'
                ],
                'upsell_potential': 'Growing - build relationship first'
            },
            'At-Risk Accounts': {
                'focus': 'Retention intervention',
                'actions': [
                    'Immediate satisfaction survey',
                    'Executive escalation',
                    'Service recovery plan',
                    'Competitive pricing review'
                ],
                'upsell_potential': 'Low - focus on retention'
            }
        }
        
        return strategies


if __name__ == '__main__':
    from src.data_prep import DataLoader
    
    loader = DataLoader(use_dummy=True)
    datasets = loader.load_all()
    
    print("\n=== Lead Scoring ===")
    scorer = LeadScorer()
    results = scorer.train(datasets['sales_leads'])
    print(f"AUC-ROC: {results['metrics']['auc_roc']:.3f}")
    print(f"Precision: {results['metrics']['precision']:.3f}")
    print(f"Recall: {results['metrics']['recall']:.3f}")
    
    scored_leads = scorer.score_leads(datasets['sales_leads'].head(10))
    print("\nTop Scored Leads:")
    print(scored_leads[['company_name', 'lead_score', 'priority']].head())
    
    print("\n=== Churn Prediction ===")
    churn_predictor = ChurnPredictor()
    results = churn_predictor.train(datasets['customer_data'])
    print(f"AUC-ROC: {results['metrics']['auc_roc']:.3f}")
    
    churn_risks = churn_predictor.predict_churn_risk(datasets['customer_data'])
    print("\nHighest Churn Risk:")
    print(churn_risks[['company_name', 'churn_risk_score', 'risk_level', 'revenue_at_risk']].head())
    
    print("\n=== Customer Segmentation ===")
    segmenter = CustomerSegmenter(n_segments=5)
    results = segmenter.fit_segments(datasets['customer_data'])
    
    print("\nSegment Profiles:")
    for seg_id, profile in results['segment_profiles'].items():
        print(f"\n{profile['name']}:")
        print(f"  Count: {profile['count']} ({profile['pct_of_total']:.1f}%)")
        print(f"  Avg Contract: ${profile['avg_contract_value']:,.0f}")
        print(f"  Characteristics: {', '.join(profile['characteristics'])}")
