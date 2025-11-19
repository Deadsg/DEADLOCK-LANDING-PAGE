// api/stateStore.js
// Shared in-memory state used by the example JS API endpoints.
export const networkState = {
  missions: [
    { id: 'm1', title: 'Corporate Espionage', status: 'available', reward: 5000, cost: 1000 },
    { id: 'm2', title: 'Data Heist', status: 'available', reward: 3500, cost: 500 },
    { id: 'm3', title: 'Asset Extraction', status: 'completed', reward: 7000, cost: 2000 },
  ],
  data_havens: [
    { id: 'd1', name: 'corp_intel_q3.zip', analyzed: false, value: 1200 },
    { id: 'd2', name: 'agent_profiles.db', analyzed: true, value: 500 },
    { id: 'd3', name: 'financial_records.csv', analyzed: false, value: 2800 },
  ],
  agents: [
    { id: 'a1', name: 'Zero', status: 'available' },
    { id: 'a2', name: 'Jynx', status: 'available' },
  ],
  log: ['System initialized. Welcome, operator.'],
  resources: 10000,
};

export function pushLog(message) {
  networkState.log.unshift(message);
  if (networkState.log.length > 10) networkState.log.pop();
}
