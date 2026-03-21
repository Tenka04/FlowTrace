import React, { useState, useEffect } from 'react';
import { getAlerts, runDetection, getStats } from '../api';

function AlertQueue({ onSelectAlert }) {
  const [alerts, setAlerts] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    setLoading(true);
    try {
      const statsData = await getStats();
      setStats(statsData);
      
      const alertsData = await getAlerts(100, 0);
      setAlerts(alertsData);
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleRunDetection = async () => {
    setLoading(true);
    try {
      await runDetection();
      await fetchData();
    } catch (e) {
      console.error(e);
      setLoading(false);
    }
  };

  const getTierColor = (tier) => {
    switch(tier) {
      case 'CRITICAL': return 'bg-red-50 dark:bg-red-900/20';
      case 'HIGH': return 'bg-orange-50 dark:bg-orange-900/20';
      case 'MEDIUM': return 'bg-yellow-50 dark:bg-yellow-900/20';
      case 'LOW': return 'bg-white dark:bg-gray-800';
      default: return 'bg-white';
    }
  };

  const getBadgeColor = (tier) => {
    switch(tier) {
      case 'CRITICAL': return 'bg-red-500 text-white';
      case 'HIGH': return 'bg-orange-500 text-white';
      case 'MEDIUM': return 'bg-yellow-500 text-gray-900';
      case 'LOW': return 'bg-gray-200 text-gray-800';
      default: return 'bg-gray-200';
    }
  };

  return (
    <div className="space-y-6">
      {/* Stats Bar */}
      <div className="grid grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded shadow-sm border border-gray-100 flex flex-col items-center">
          <p className="text-sm text-gray-500 font-medium">Total Alerts</p>
          <p className="text-2xl font-bold">{stats?.total_alerts || 0}</p>
        </div>
        <div className="bg-white p-4 rounded shadow-sm border border-gray-100 flex flex-col items-center">
          <p className="text-sm text-gray-500 font-medium">Critical</p>
          <p className="text-2xl font-bold text-red-600">{stats?.critical_count || 0}</p>
        </div>
        <div className="bg-white p-4 rounded shadow-sm border border-gray-100 flex flex-col items-center">
          <p className="text-sm text-gray-500 font-medium">High</p>
          <p className="text-2xl font-bold text-orange-600">{stats?.high_count || 0}</p>
        </div>
        <div className="bg-white p-4 rounded shadow-sm border border-gray-100 flex flex-col items-center">
          <p className="text-sm text-gray-500 font-medium">Accounts Monitored</p>
          <p className="text-2xl font-bold text-blue-600">{stats?.accounts_monitored || 0}</p>
        </div>
      </div>

      {/* Main Table Area */}
      <div className="bg-white rounded shadow-sm border border-gray-200 overflow-hidden flex flex-col">
        <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center bg-gray-50">
          <h3 className="text-lg font-semibold text-gray-800">Alert Detection Queue</h3>
          <button 
            onClick={handleRunDetection}
            disabled={loading}
            className="px-4 py-2 bg-[#EC2026] text-white font-medium rounded hover:bg-red-700 transition-colors shadow-sm disabled:opacity-50"
          >
            {loading ? 'Running...' : 'Run Detection Pipeline'}
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm whitespace-nowrap">
            <thead className="bg-gray-100 text-gray-600 font-medium">
              <tr>
                <th className="px-6 py-3">Alert ID</th>
                <th className="px-6 py-3">Account</th>
                <th className="px-6 py-3">Risk Score</th>
                <th className="px-6 py-3">Tier</th>
                <th className="px-6 py-3">Top Detectors</th>
                <th className="px-6 py-3">Action</th>
                <th className="px-6 py-3">Time</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {alerts.length === 0 ? (
                <tr>
                  <td colSpan="7" className="px-6 py-8 text-center text-gray-500">
                    {loading ? 'Loading...' : 'No alerts found. Run detection to analyze data.'}
                  </td>
                </tr>
              ) : (
                alerts.map(alert => (
                  <tr 
                    key={alert.alert_id} 
                    onClick={() => onSelectAlert(alert)}
                    className={`${getTierColor(alert.risk_tier)} hover:bg-gray-100 cursor-pointer transition-colors`}
                  >
                    <td className="px-6 py-4 font-mono text-xs">{alert.alert_id}</td>
                    <td className="px-6 py-4 font-mono text-sm text-blue-600">{alert.account_id}</td>
                    <td className="px-6 py-4">
                      <div className="w-16 h-2 bg-gray-200 rounded-full overflow-hidden inline-block mr-2 align-middle">
                        <div 
                          className={`h-full ${alert.composite_risk_score > 0.7 ? 'bg-red-500' : alert.composite_risk_score > 0.4 ? 'bg-orange-500' : 'bg-yellow-500'}`} 
                          style={{ width: `${alert.composite_risk_score * 100}%` }}
                        ></div>
                      </div>
                      <span className="font-medium">{(alert.composite_risk_score).toFixed(2)}</span>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`px-2 py-1 rounded text-xs font-bold ${getBadgeColor(alert.risk_tier)}`}>
                        {alert.risk_tier}
                      </span>
                    </td>
                    <td className="px-6 py-4 max-w-[200px] truncate">
                      {alert.triggered_detectors.join(', ')}
                    </td>
                    <td className="px-6 py-4 text-xs font-semibold">{alert.recommended_action}</td>
                    <td className="px-6 py-4 text-gray-500">{new Date(alert.timestamp).toLocaleTimeString()}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default AlertQueue;
