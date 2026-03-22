import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api', // Use env var for Render
});

export const getAlerts = async (limit = 100, offset = 0) => {
  const response = await api.get(`/alerts?limit=${limit}&offset=${offset}`);
  return response.data;
};

export const getAlertDetail = async (id) => {
  const response = await api.get(`/alerts/${id}`);
  return response.data;
};

export const getGraphData = async (accountId) => {
  const response = await api.get(`/graph/${accountId}`);
  return response.data;
};

export const runDetection = async () => {
  const response = await api.post('/run-detection');
  return response.data;
};

export const downloadSTR = (alertId) => {
  window.open(`http://localhost:8000/api/str/${alertId}`, '_blank');
};

export const getStats = async () => {
  const response = await api.get('/stats');
  return response.data;
};
