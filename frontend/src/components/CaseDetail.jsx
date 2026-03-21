import React from 'react';
import GraphView from './GraphView';
import { downloadSTR } from '../api';

function CaseDetail({ alert }) {
  const getBadgeColor = (tier) => {
    switch(tier) {
      case 'CRITICAL': return 'bg-red-500 text-white';
      case 'HIGH': return 'bg-orange-500 text-white';
      case 'MEDIUM': return 'bg-yellow-500 text-gray-900';
      case 'LOW': return 'bg-gray-200 text-gray-800';
      default: return 'bg-gray-200';
    }
  };

  const handleDownloadSTR = () => {
    downloadSTR(alert.alert_id);
  };

  return (
    <div className="space-y-6">
      {/* Header Card */}
      <div className="bg-white p-6 rounded shadow-sm border border-gray-200 flex justify-between items-start">
        <div>
          <div className="flex items-center space-x-3 mb-2">
            <h2 className="text-2xl font-bold font-mono text-gray-800">{alert.alert_id}</h2>
            <span className={`px-3 py-1 rounded text-sm font-bold ${getBadgeColor(alert.risk_tier)}`}>
              {alert.risk_tier} RISK
            </span>
          </div>
          <p className="text-gray-600 mb-1">
            <strong>Account:</strong> <span className="text-blue-600 font-mono">{alert.account_id}</span>
          </p>
          <p className="text-gray-600">
            <strong>Action Required:</strong> <span className="font-semibold text-gray-900">{alert.recommended_action}</span>
          </p>
        </div>
        <div className="text-right">
          <div className="text-sm text-gray-500 font-medium">Composite Score</div>
          <div className="text-5xl font-black text-gray-800 mb-4">
            {(alert.composite_risk_score).toFixed(2)}
          </div>
          <button 
            onClick={handleDownloadSTR} 
            className="px-6 py-2 bg-blue-600 text-white font-medium rounded shadow hover:bg-blue-700 transition"
          >
            Download STR (PDF)
          </button>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-6">
        {/* Detector Scores */}
        <div className="bg-white p-6 rounded shadow-sm border border-gray-200">
          <h3 className="text-lg font-semibold border-b pb-2 mb-4">Detection Model Scores</h3>
          <div className="space-y-4">
            {Object.entries(alert.individual_scores || {
              "Graph Topology": 0.8,
              "Isolation Forest": 0.5,
              "Structuring": 0.1,
              "Dormant Activity": 0.0,
              "Profile Mismatch": 0.2
            }).map(([name, score]) => (
              <div key={name}>
                <div className="flex justify-between text-sm mb-1">
                  <span className="font-medium text-gray-700">{name.replace(/_/g, ' ').toUpperCase()}</span>
                  <span className="font-mono">{parseFloat(score).toFixed(2)}</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className={`h-2 rounded-full ${score > 0.7 ? 'bg-red-500' : score > 0.4 ? 'bg-orange-500' : 'bg-green-500'}`} 
                    style={{ width: `${Math.min(100, Math.max(0, score * 100))}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Triggered Reasons / Trail */}
        <div className="bg-white p-6 rounded shadow-sm border border-gray-200">
          <h3 className="text-lg font-semibold border-b pb-2 mb-4">Flagged Reasons</h3>
          <ul className="list-disc pl-5 space-y-2 text-gray-700 mb-6">
            {alert.reasons && alert.reasons.length > 0 ? (
              alert.reasons.map((reason, i) => <li key={i}>{reason}</li>)
            ) : (
              <li>No specific reasons provided.</li>
            )}
          </ul>

          <h3 className="text-lg font-semibold border-b pb-2 mb-4">Suspicious Fund Trail</h3>
          {alert.fund_trail && alert.fund_trail.length > 0 ? (
            <div className="flex items-center space-x-2 overflow-x-auto py-2 bg-gray-50 px-4 rounded border border-gray-100 font-mono text-sm">
              {alert.fund_trail.map((acc, i) => (
                <React.Fragment key={i}>
                  <span className={`px-2 py-1 rounded ${acc === alert.account_id ? 'bg-blue-100 text-blue-800 font-bold' : 'bg-gray-200'}`}>
                    {acc}
                  </span>
                  {i < alert.fund_trail.length - 1 && (
                    <span className="text-red-500 font-bold animate-pulse">&rarr;</span>
                  )}
                </React.Fragment>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 italic">No clear fund trail constructed.</p>
          )}
        </div>
      </div>

      {/* Graph Area */}
      <div>
        <h3 className="text-lg font-semibold mb-2">Network Graph Visualization</h3>
        <GraphView accountId={alert.account_id} />
      </div>
    </div>
  );
}

export default CaseDetail;
