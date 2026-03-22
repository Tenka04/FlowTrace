import os
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from datetime import datetime

# Import detectors and engines
from data_generator import generate_data
from neo4j_loader import Neo4jLoader
from detectors.isolation_forest import IsolationAnomalyDetector
from detectors.structuring import StructuringDetector
from detectors.dormant import DormantDetector
from detectors.profile_mismatch import ProfileMismatchDetector
from detectors.graph_scorer import GraphScorer
from risk_engine import RiskEngine
from alert_engine import AlertEngine
from str_generator import STRGenerator

app = FastAPI(title="Flow Trace API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

alert_engine = AlertEngine()
str_gen = STRGenerator()
neo4j_loader = Neo4jLoader()

@app.on_event("startup")
def startup_event():
    # Load alerts on startup, if empty auto-run
    alerts = alert_engine.load_alerts()
    if not alerts:
        print("No existing alerts found. Running initial detection pipeline...")
        run_detection_pipeline()

@app.get("/api/alerts")
def get_alerts(limit: int = 100, offset: int = 0):
    alerts = alert_engine.alerts
    return alerts[offset : offset + limit]

@app.get("/api/alerts/{alert_id}")
def get_alert_detail(alert_id: str):
    for a in alert_engine.alerts:
        if a["alert_id"] == alert_id:
            return a
    raise HTTPException(status_code=404, detail="Alert not found")

@app.get("/api/graph/{account_id}")
def get_graph(account_id: str):
    data = neo4j_loader.get_account_subgraph(account_id)
    # The suspicious flag is already set by the neo4j loader for the fraud txns
    suspicious_nodes = set()
    for element in data:
        if 'source' in element['data'] and element['data'].get('suspicious'):
            suspicious_nodes.add(element['data']['source'])
            suspicious_nodes.add(element['data']['target'])
            
    for element in data:
        if 'source' not in element['data']:
            if element['data']['id'] in suspicious_nodes:
                element['data']['suspicious'] = True

    return data

@app.post("/api/run-detection")
def run_detection():
    stats = run_detection_pipeline()
    return stats

def run_detection_pipeline():
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    if not os.path.exists(os.path.join(data_dir, 'accounts.csv')):
        generate_data()
        
    accounts_path = os.path.join(data_dir, 'accounts.csv')
    txns_path = os.path.join(data_dir, 'transactions.csv')
    
    # Reload Neo4j
    neo4j_loader.load_data(accounts_path, txns_path)
    
    accs_df = pd.read_csv(accounts_path)
    txns_df = pd.read_csv(txns_path)
    
    # Detectors
    iso = IsolationAnomalyDetector()
    if not os.path.exists(iso.model_path):
        iso.train(txns_df, accs_df)
    iso_res = iso.predict(pd.merge(txns_df, accs_df, left_on='from_account', right_on='account_id'))
    
    # Map txn isolation scores back to accounts (max score)
    txns_df['iso_score'] = txns_df['txn_id'].map(iso_res)
    acc_iso_scores = txns_df.groupby('from_account')['iso_score'].max().to_dict()
    
    struct = StructuringDetector()
    struct_res = struct.detect(txns_df)
    
    dormant = DormantDetector()
    dormant_res = dormant.detect(txns_df, accs_df)
    
    profile = ProfileMismatchDetector()
    profile_res = profile.detect(txns_df, accs_df)
    
    graph = GraphScorer(neo4j_loader)
    graph_res = graph.detect()
    
    # Combine results
    all_scores = []
    for acc in accs_df['account_id']:
        row = {'account_id': acc}
        row['isolation_score'] = acc_iso_scores.get(acc, 0.0)
        
        sr = struct_res.get(acc, {})
        row['structuring_score'] = sr.get('structuring_score', 0.0)
        row['structuring_count'] = sr.get('count', 0)
        
        dr = dormant_res.get(acc, {})
        row['dormant_score'] = dr.get('dormant_score', 0.0)
        row['dormant_days'] = dr.get('dormant_days', 0)
        
        pr = profile_res.get(acc, {})
        row['mismatch_score'] = pr.get('mismatch_score', 0.0)
        row['mismatch_ratio'] = pr.get('mismatch_ratio', 0.0)
        
        gr = graph_res.get(acc, {})
        row['graph_score'] = gr.get('graph_score', 0.0)
        row['graph_reasons'] = gr.get('graph_reasons', [])
        
        all_scores.append(row)
        
    scores_df = pd.DataFrame(all_scores).set_index('account_id')
    
    # Risk Engine
    engine = RiskEngine()
    final_df = engine.assemble(scores_df)
    
    # Alert Engine
    alert_engine.generate_alerts(final_df, accs_df)
    
    return {
        "status": "success",
        "alerts_generated": len(alert_engine.alerts)
    }

@app.get("/api/str/{alert_id}")
def generate_str(alert_id: str):
    alert = None
    for a in alert_engine.alerts:
        if a["alert_id"] == alert_id:
            alert = a
            break
            
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
        
    pdf_path = str_gen.generate(alert)
    return FileResponse(pdf_path, media_type="application/pdf", filename=f"STR_{alert_id}.pdf")

@app.get("/api/stats")
def get_stats():
    alerts = alert_engine.alerts
    critical = sum(1 for a in alerts if a['risk_tier'] == 'CRITICAL')
    high = sum(1 for a in alerts if a['risk_tier'] == 'HIGH')
    return {
        "total_alerts": len(alerts),
        "critical_count": critical,
        "high_count": high,
        "accounts_monitored": 500,
        "last_run_time": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
