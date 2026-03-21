import json
import os
from datetime import datetime

class AlertEngine:
    def __init__(self):
        self.alerts_file = os.path.join(os.path.dirname(__file__), 'data', 'alerts.json')
        self.alerts = []

    def generate_alerts(self, risk_df, accounts_df):
        print("Generating alerts...")
        self.alerts = []
        
        # Merge account level info
        df = risk_df.merge(accounts_df[['account_id', 'customer_id']], left_index=True, right_on='account_id')
        
        # Only alert for >= 0.30
        alert_df = df[df['composite_risk_score'] >= 0.30].sort_values(by='composite_risk_score', ascending=False)
        date_str = datetime.now().strftime("%Y%m%d")
        
        for idx, row in alert_df.iterrows():
            seq = len(self.alerts) + 1
            
            detectors = []
            reasons = []
            
            if row.get('graph_score', 0) > 0.1:
                detectors.append('Graph Scorer')
                if isinstance(row.get('graph_reasons'), list):
                    reasons.extend(row.get('graph_reasons'))
                elif isinstance(row.get('graph_reasons'), str) and row.get('graph_reasons'):
                    reasons.append(row.get('graph_reasons'))

            if row.get('isolation_score', 0) > 0.5:
                detectors.append('Isolation Forest')
                reasons.append(f'Unusual transaction behavior detected (IF score: {row["isolation_score"]:.2f})')
                
            if row.get('structuring_score', 0) > 0.1:
                detectors.append('Structuring Detector')
                reasons.append(f'Structuring cluster identified: {int(row.get("structuring_count", 0))} transactions near reporting threshold')
                
            if row.get('dormant_score', 0) > 0.1:
                detectors.append('Dormant Activation')
                reasons.append(f'Sudden high-value activity after {int(row.get("dormant_days", 0))} days of inactivity')
                
            if row.get('mismatch_score', 0) > 0.1:
                detectors.append('Profile Mismatch')
                reasons.append(f'Monthly transaction volume is {row.get("mismatch_ratio", 0):.1f}x declared income')

            alert = {
                'alert_id': f"ALT_{date_str}_{str(seq).zfill(4)}",
                'timestamp': datetime.now().isoformat(),
                'account_id': row['account_id'],
                'customer_id': row['customer_id'],
                'composite_risk_score': round(row['composite_risk_score'], 2),
                'risk_tier': row['risk_tier'],
                'triggered_detectors': detectors,
                'reasons': reasons,
                'individual_scores': {
                    'Graph Topology': row.get('graph_score', 0),
                    'Isolation Forest': row.get('isolation_score', 0),
                    'Structuring': row.get('structuring_score', 0),
                    'Dormant Activity': row.get('dormant_score', 0),
                    'Profile Mismatch': row.get('mismatch_score', 0)
                },
                'fund_trail': [], # Can be populated via Neo4j if desired later
                'recommended_action': row['recommended_action'],
                'str_auto_drafted': False
            }
            self.alerts.append(alert)
            
        # Save to disk
        os.makedirs(os.path.dirname(self.alerts_file), exist_ok=True)
        with open(self.alerts_file, 'w') as f:
            json.dump(self.alerts, f, indent=2)
            
        print(f"Generated {len(self.alerts)} alerts.")

    def load_alerts(self):
        if os.path.exists(self.alerts_file):
            with open(self.alerts_file, 'r') as f:
                self.alerts = json.load(f)
        return self.alerts
