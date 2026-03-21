import pandas as pd

class DormantDetector:
    def detect(self, txns_df, accs_df):
        print("Running Dormant Detector...")
        results = {}
        txns = txns_df.copy()
        accs = accs_df.copy()
        
        # Only care about large amounts > 10L
        large_txns = txns[txns['amount'] > 1000000]
        recent_in = large_txns.groupby('to_account')['amount'].max().to_dict()
        recent_out = large_txns.groupby('from_account')['amount'].max().to_dict()

        for _, row in accs.iterrows():
            acc = row['account_id']
            days = row['days_since_last_txn']
            
            if days > 180:
                max_amt = max(recent_in.get(acc, 0), recent_out.get(acc, 0))
                if max_amt > 1000000:
                    score = min(1.0, days/365.0) * min(1.0, max_amt/5000000.0)
                    results[acc] = {
                        'dormant_score': score,
                        'dormant_days': days
                    }
                else:
                    results[acc] = {'dormant_score': 0.0, 'dormant_days': days}
            else:
                results[acc] = {'dormant_score': 0.0, 'dormant_days': days}
                
        return results
