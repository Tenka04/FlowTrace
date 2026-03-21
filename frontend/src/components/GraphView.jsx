import React, { useEffect, useRef } from 'react';
import cytoscape from 'cytoscape';
import { getGraphData } from '../api';

const GraphView = ({ accountId }) => {
  const containerRef = useRef(null);
  const cyRef = useRef(null);

  useEffect(() => {
    let unmounted = false;

    const initGraph = async () => {
      try {
        const data = await getGraphData(accountId);
        if (unmounted) return;

        const cy = cytoscape({
          container: containerRef.current,
          elements: data,
          style: [
            {
              selector: 'node',
              style: {
                'label': 'data(id)',
                'font-size': '10px',
                'text-valign': 'center',
                'text-halign': 'center',
                'color': '#fff',
                'text-outline-width': 1,
                'text-outline-color': '#555',
                'background-color': '#999',
                'width': 40,
                'height': 40
              }
            },
            {
              selector: 'node[type="hub"]',
              style: {
                'background-color': 'orange',
                'width': 60,
                'height': 60
              }
            },
            {
              selector: `node[id="${accountId}"]`, // Source account
              style: {
                'background-color': '#3b82f6',
                'width': 70,
                'height': 70,
                'text-outline-color': '#1e40af'
              }
            },
            {
              selector: 'node[suspicious=true]', // Suspicious path
              style: {
                'background-color': '#EC2026',
                'width': 55,
                'height': 55,
                'border-width': 2,
                'border-color': '#7f1d1d'
              }
            },
            {
              selector: 'edge',
              style: {
                'width': 1.5,
                'line-color': '#ccc',
                'target-arrow-color': '#ccc',
                'target-arrow-shape': 'triangle',
                'curve-style': 'bezier',
                'label': 'data(formatted_amount)',
                'font-size': '9px',
                'text-rotation': 'autorotate',
                'text-margin-y': -10,
                'color': '#666',
                'arrow-scale': 1.2
              }
            },
            {
              selector: 'edge[suspicious=true]',
              style: {
                'width': 3,
                'line-color': '#EC2026',
                'target-arrow-color': '#EC2026',
                'line-style': 'dashed',
                'color': '#EC2026',
                'font-weight': 'bold',
                'font-size': '11px',
                'text-outline-width': 2,
                'text-outline-color': '#fff'
              }
            }
          ],
          layout: {
            name: 'concentric',
            concentric: function(node){
              if(node.id() === accountId) return 100;
              if(node.data('suspicious')) return 50;
              return 10;
            },
            levelWidth: function(nodes){
              return 10;
            },
            padding: 50
          }
        });

        // Add some animation to suspicious edges
        let offset = 0;
        const animateEdges = () => {
          if(!cy || cy.destroyed()) return;
          offset += 2;
          cy.edges('[suspicious=true]').style('line-dash-offset', -offset);
          requestAnimationFrame(animateEdges);
        };
        animateEdges();

        cyRef.current = cy;
        
        cy.on('tap', 'node', function(evt){
          const node = evt.target;
          alert(`Account: ${node.id()}\nBalance: ₹${node.data('balance')} Lakhs\nKYC: ${node.data('kyc_tier')}`);
        });

      } catch (err) {
        console.error('Failed to load graph data', err);
      }
    };

    initGraph();

    return () => {
      unmounted = true;
      if(cyRef.current) {
        cyRef.current.destroy();
      }
    };
  }, [accountId]);

  return (
    <div className="flex flex-col h-full bg-white rounded shadow-sm border border-gray-200 p-2 relative">
      <div className="absolute top-4 left-4 z-10 space-x-2">
        <button 
          onClick={() => cyRef.current && cyRef.current.fit()}
          className="px-3 py-1 bg-white border border-gray-300 rounded shadow text-sm hover:bg-gray-50"
        >
          Fit to Screen
        </button>
      </div>
      <div ref={containerRef} className="w-full h-96 min-h-[400px]"></div>
    </div>
  );
};

export default GraphView;
