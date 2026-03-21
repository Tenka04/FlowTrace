import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
import pickle
import os
from datetime import datetime

class IsolationAnomalyDetector:
    def __init__(self):
        self.model = IsolationForest(contamination=0.01, n_estimators=200, random_state=42)
        self.model_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'isolation_forest.pkl')

    def _engineer_features(self, txns_df, accs_df):
        if 'days_since_last_txn' not in txns_df.columns:
            df = pd.merge(txns_df, accs_df[['account_id', 'days_since_last_txn']], left_on='from_account', right_on='account_id', how='left')
        else:
            df = txns_df.copy()
            
        df['timestamp_dt'] = pd.to_datetime(df['timestamp'])
        df['hour_of_day'] = df['timestamp_dt'].dt.hour
        df['day_of_week'] = df['timestamp_dt'].dt.dayofweek
        
        avg_amt = df.groupby('from_account')['amount'].transform('mean')
        df['amount_to_avg_ratio'] = df['amount'] / (avg_amt + 1)
        
        df['date'] = df['timestamp_dt'].dt.date
        daily_ct = df.groupby(['from_account', 'date']).size().reset_index(name='daily_txn_count')
        df = pd.merge(df, daily_ct, on=['from_account', 'date'], how='left')
        
        df['month'] = df['timestamp_dt'].dt.to_period('M')
        monthly_ct = df.groupby(['from_account', 'month']).size().reset_index(name='monthly_txn_count')
        df = pd.merge(df, monthly_ct, on=['from_account', 'month'], how='left')
        
        return df

    def train(self, txns_df, accs_df):
        print("Training Isolation Forest model...")
        df = self._engineer_features(txns_df, accs_df)
        
        features = ['amount', 'hour_of_day', 'day_of_week', 'days_since_last_txn', 'amount_to_avg_ratio', 'daily_txn_count', 'monthly_txn_count']
        X = df[features].fillna(0)
        
        self.model.fit(X)
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        with open(self.model_path, 'wb') as f:
            pickle.dump(self.model, f)
        print(f"Saved model to {self.model_path}")

    def predict(self, features_df):
        with open(self.model_path, 'rb') as f:
            self.model = pickle.load(f)
            
        df = self._engineer_features(features_df, pd.DataFrame(columns=['account_id', 'days_since_last_txn']))
        
        features = ['amount', 'hour_of_day', 'day_of_week', 'days_since_last_txn', 'amount_to_avg_ratio', 'daily_txn_count', 'monthly_txn_count']
        X = df[features].fillna(0)
        scores = self.model.decision_function(X)
        
        # normalize to 0-1
        norm_scores = (scores.max() - scores) / (scores.max() - scores.min())
        
        # return dict mapping txn_id to score
        return dict(zip(features_df['txn_id'], norm_scores))
