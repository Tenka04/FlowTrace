import pandas as pd

class ProfileMismatchDetector:
    def detect(self, txns_df, accs_df):
        print("Running Profile Mismatch Detector...")
        results = {}
        df = txns_df.copy()
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Consider last 30 days
        last_date = df['timestamp'].max()
        thirty_days_ago = last_date - pd.Timedelta(days=30)
        recent_df = df[df['timestamp'] >= thirty_days_ago]
        
        monthly_flow = recent_df.groupby('from_account')['amount'].sum().to_dict()
        
        for _, row in accs_df.iterrows():
            acc = row['account_id']
            flow = monthly_flow.get(acc, 0)
            declared_annual = row['declared_annual_income']
            monthly_income = declared_annual / 12.0
            
            mismatch_ratio = flow / (monthly_income + 1)
            score = min(1.0, mismatch_ratio / 20.0)
            
            if score > 0.1:
                results[acc] = {
                    'mismatch_score': score,
                    'mismatch_ratio': mismatch_ratio
                }
            else:
                results[acc] = {'mismatch_score': 0.0, 'mismatch_ratio': mismatch_ratio}
                
        return results

