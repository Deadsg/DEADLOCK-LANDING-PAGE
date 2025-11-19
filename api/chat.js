// api/chat.js
// Proxy to Python chat server if available, otherwise reply locally.
const PYTHON_CHAT_URL = process.env.PYTHON_CHAT_URL || 'http://localhost:8000/api/chat';

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    res.status(405).json({ error: 'Method not allowed' });
    return;
  }

  const { prompt = '', wallet = null, balance = null } = req.body || {};

  // Try proxying to Python chat server
  try {
    const proxyResp = await fetch(PYTHON_CHAT_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt, wallet, balance }),
    });

    if (proxyResp.ok) {
      const data = await proxyResp.json();
      // Ensure we return the same shape: { response, tx, balance }
      return res.status(200).json(data);
    }

    console.warn(`Python chat returned ${proxyResp.status}, falling back to local response.`);
  } catch (err) {
    console.warn(`Could not reach Python chat at ${PYTHON_CHAT_URL}: ${err}`);
  }

  // Fallback local behavior (echo + simple tx detection)
  const sendMatch = typeof prompt === 'string' && prompt.match(/send\s+([0-9]*\.?[0-9]+)\s+to\s+([A-Za-z0-9_\-]+)/i);
  let tx = null;
  if (sendMatch) {
    tx = { to: sendMatch[2], amount: Number(sendMatch[1]) };
  }

  const response = `Echo: ${prompt}`;
  return res.status(200).json({ response, tx, balance });
}
