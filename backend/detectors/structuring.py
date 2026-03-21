import pandas as pd
from datetime import timedelta

class StructuringDetector:
    def __init__(self):
        self.threshold = 1000000

    def detect(self, txns_df):
        print("Running Structuring Detector...")
        df = txns_df.copy()
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df[(df['amount'] >= 850000) & (df['amount'] <= 995000)]
        df = df.sort_values(by=['from_account', 'timestamp'])
        
        results = {}
        for acc, group in df.groupby('from_account'):
            # rolling 7 day window
            group = group.set_index('timestamp')
            counts = group.rolling('7D')['amount'].count()
            max_count = counts.max()
            
            if max_count >= 3:
                results[acc] = {
                    'structuring_score': min(1.0, max_count / 5.0),
                    'count': int(max_count)
                }
            else:
                results[acc] = {'structuring_score': 0.0, 'count': 0}
                
        return results
