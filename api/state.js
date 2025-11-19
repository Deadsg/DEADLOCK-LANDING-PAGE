// api/state.js
// Returns the current network state (GET `/api/state`). Uses shared `stateStore` so state is consistent
import { networkState } from './stateStore';

export default function handler(req, res) {
  if (req.method !== 'GET') {
    res.status(405).json({ error: 'Method not allowed' });
    return;
  }

  res.status(200).json(networkState);
}
