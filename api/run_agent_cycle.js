// api/run_agent_cycle.js
// Proxy to Python agent API if available, otherwise mutate the local JS `stateStore`.
import { networkState, pushLog } from './stateStore';

const PYTHON_AGENT_URL = process.env.PYTHON_AGENT_URL || 'http://localhost:8001/api/run_agent_cycle';

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    res.status(405).json({ error: 'Method not allowed' });
    return;
  }

  // Try to proxy the request to the Python agent API
  try {
    const proxyResp = await fetch(PYTHON_AGENT_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(req.body || {}),
    });

    if (proxyResp.ok) {
      const data = await proxyResp.json();
      return res.status(200).json(data);
    }

    console.warn(`Python agent returned ${proxyResp.status}, falling back to local JS logic.`);
  } catch (err) {
    console.warn(`Could not reach Python agent at ${PYTHON_AGENT_URL}: ${err}`);
  }

  // Fallback: local JS agent logic (mirrors Python Agent.get_available_actions ordering)
  try {
    let actionTaken = null;

    // 1) Complete mission (in_progress)
    for (const m of networkState.missions) {
      if (m.status === 'in_progress') {
        m.status = 'completed';
        networkState.resources += m.reward || 0;
        actionTaken = `complete_mission:${m.id}`;
        pushLog(`Agent action: complete_mission - Mission '${m.title}' completed. Reward: ${m.reward}`);
        break;
      }
    }

    // 2) Accept mission (available and affordable)
    if (!actionTaken) {
      for (const m of networkState.missions) {
        if (m.status === 'available' && networkState.resources >= (m.cost || 0)) {
          m.status = 'in_progress';
          networkState.resources -= m.cost || 0;
          actionTaken = `accept_mission:${m.id}`;
          pushLog(`Agent action: accept_mission - Mission '${m.title}' accepted. Cost: ${m.cost}`);
          break;
        }
      }
    }

    // 3) Analyze data (not analyzed)
    if (!actionTaken) {
      for (const d of networkState.data_havens) {
        if (!d.analyzed) {
          d.analyzed = true;
          networkState.resources += d.value || 0;
          actionTaken = `analyze_data:${d.id}`;
          pushLog(`Agent action: analyze_data - Data '${d.name}' analyzed. Value: ${d.value}`);
          break;
        }
      }
    }

    if (!actionTaken) {
      pushLog('Agent action: idle - No available actions.');
    }

    return res.status(200).json(networkState);
  } catch (e) {
    console.error('Error in fallback JS agent cycle:', e);
    return res.status(500).json({ error: String(e) });
  }
}
