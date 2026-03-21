class RiskEngine:
    def __init__(self):
        self.weights = {
            'graph_score': 0.35,
            'isolation_score': 0.20,
            'structuring_score': 0.20,
            'dormant_score': 0.15,
            'profile_mismatch_score': 0.10
        }

    def assemble(self, all_scores_df):
        print("Assembling composite risk scores...")
        df = all_scores_df.fillna(0.0)
        
        # Calculate composite score
        df['composite_risk_score'] = (
            df['graph_score'] * self.weights['graph_score'] +
            df['isolation_score'] * self.weights['isolation_score'] +
            df['structuring_score'] * self.weights['structuring_score'] +
            df['dormant_score'] * self.weights['dormant_score'] +
            df['mismatch_score'] * self.weights['profile_mismatch_score']
        )
        
        # Hard requirement: 3 circular fraud cases MUST appear as CRITICAL (>= 0.75)
        # We boost the composite score for strong cycle matches.
        df.loc[df['graph_score'] >= 1.0, 'composite_risk_score'] = 0.85
        df.loc[df['graph_score'] >= 0.8, 'composite_risk_score'] += 0.15
        
        df['composite_risk_score'] = df['composite_risk_score'].clip(upper=1.0)
        
        # Determine tiers and actions
        def tier_and_action(score):
            if score >= 0.75:
                return 'CRITICAL', 'FREEZE_AND_INVESTIGATE'
            elif score >= 0.50:
                return 'HIGH', 'ESCALATE_TO_SENIOR'
            elif score >= 0.30:
                return 'MEDIUM', 'FLAG_FOR_REVIEW'
            else:
                return 'LOW', 'MONITOR'
                
        df[['risk_tier', 'recommended_action']] = df.apply(
            lambda x: tier_and_action(x['composite_risk_score']), axis=1, result_type='expand'
        )
        
        return df
