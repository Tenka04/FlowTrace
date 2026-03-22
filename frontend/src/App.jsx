import React, { useState, useEffect } from 'react';
import AlertQueue from './components/AlertQueue';
import CaseDetail from './components/CaseDetail';

function App() {
  const [selectedAlert, setSelectedAlert] = useState(null);

  return (
    <div className="flex h-screen bg-gray-100 font-sans">
      {/* Sidebar */}
      <div className="w-64 bg-[#1a2744] text-white flex flex-col">
        <div className="p-6 border-b border-gray-700">
          <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-red-500 to-orange-400">Flow Trace</h1>
          <p className="text-sm text-gray-400">IDEA 2.0 Hackathon | PS3</p>
        </div>
        <nav className="flex-1 p-4 space-y-2">
          <button className="w-full text-left px-4 py-2 bg-blue-900/30 text-white rounded font-medium border-l-4 border-[#EC2026]">
            Alerts Dashboard
          </button>
          <button className="w-full text-left px-4 py-2 text-gray-400 hover:bg-blue-900/20 rounded font-medium">
            Risk Models
          </button>
          <button className="w-full text-left px-4 py-2 text-gray-400 hover:bg-blue-900/20 rounded font-medium">
            Settings
          </button>
        </nav>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="bg-white px-6 py-4 shadow-sm z-10 flex justify-between items-center">
          <h2 className="text-xl font-semibold text-gray-800">
            {selectedAlert ? 'Case Investigation' : 'Fund Flow Tracking & Fraud Detection'}
          </h2>
          {selectedAlert && (
            <button 
              onClick={() => setSelectedAlert(null)}
              className="px-4 py-2 text-sm bg-gray-200 hover:bg-gray-300 rounded text-gray-800 font-medium transition-colors"
            >
              &larr; Back to Queue
            </button>
          )}
        </header>

        {/* Dynamic View */}
        <main className="flex-1 overflow-auto p-6">
          {selectedAlert ? (
            <CaseDetail alert={selectedAlert} />
          ) : (
            <AlertQueue onSelectAlert={setSelectedAlert} />
          )}
        </main>
      </div>
    </div>
  );
}

export default App;
