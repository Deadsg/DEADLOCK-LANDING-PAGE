# Project Setup and Commands

This project runs two kinds of servers in development:
- Python FastAPI servers for production-like APIs (`chat_server.py` and `server.py`).
- Optional JS API handlers in `api/` (Next-style) for lightweight local development or when running a Node/Next dev server.

You can run the Python servers directly (recommended if you want the real `Agent` and LLM integration), or run the JS handlers which will proxy to the Python servers when available.

## Running the Application (Python servers)

1.  **Start the Web Server (static files):**
    This serves `index.html` and `static/*` on port 5500.
    ```powershell
    python -m http.server 5500
    ```

2.  **Start the Chat API Server (Python + LLM):**
    - Requires `OPENAI_API_KEY` in your environment.
    ```powershell
    $Env:OPENAI_API_KEY = 'your_openai_key_here'
    uvicorn chat_server:app --reload --port 8000
    ```

3.  **Start the Agent API Server (Python):**
    - Optionally set `AGENT_MODEL_PATH` to point to your ONNX model. If not set, the agent will try the relative path `Q_Layered_Network/dqn_node_model.onnx`.
    ```powershell
    # Optional: point to a custom ONNX model
    $Env:AGENT_MODEL_PATH = 'C:\path\to\dqn_node_model.onnx'
    uvicorn server:app --reload --port 8001
    ```

## JS API handlers (optional)

The `api/` directory contains lightweight JS endpoints (`api/chat.js`, `api/state.js`, `api/run_agent_cycle.js`, `api/stateStore.js`) intended for Node/Next-style dev servers. These handlers:
- Proxy to the Python servers when reachable (configurable via `PYTHON_CHAT_URL` and `PYTHON_AGENT_URL`),
- Fall back to an in-memory JS implementation when the Python services are unreachable.

To run these handlers you need a Node/Next dev server (not included here). When running under such a server:

```powershell
# Optional: tell the JS handlers where the Python servers live
$Env:PYTHON_CHAT_URL = 'http://localhost:8000/api/chat'
$Env:PYTHON_AGENT_URL = 'http://localhost:8001/api/run_agent_cycle'

# Start your Next/Node dev server (example placeholder)
# npm run dev
```

Notes:
- The JS handlers use the global `fetch` API (Node 18+ or Next runtime). If your runtime lacks `fetch`, use a polyfill or swap to `node-fetch`.

## Frontend configuration

`static/script.js` contains two constants that the UI uses to contact APIs. The defaults are:

```javascript
const BASE_CHAT_API_URL = 'http://localhost:8000'; // Python chat server (port 8000)
const BASE_AGENT_API_URL = 'http://localhost:8001'; // Python agent/server API (port 8001)
```

If you run the JS `api/` handlers under a Node dev server on a different port (for example `http://localhost:3000`), update these constants or proxy accordingly.

## Exposing the Servers with ngrok

If you need public URLs (for webhooks, Vercel previews, etc.), run ngrok for each local port:

```powershell
ngrok http 5500   # frontend
ngrok http 8000   # chat API
ngrok http 8001   # agent API
```

Then update `static/script.js` or the environment variables (`PYTHON_CHAT_URL` / `PYTHON_AGENT_URL`) to point to the ngrok URLs.

## ONNX model and agent notes

- `agent.py` loads the ONNX model from the path provided by the `AGENT_MODEL_PATH` environment variable, or from `Q_Layered_Network/dqn_node_model.onnx` relative to the repo when unset.
- If the model file is missing or fails to load, the agent falls back to random action selection. Check console output for the resolved model path when debugging.

## Quick test commands (PowerShell)

```powershell
# Check the Python agent endpoint directly
curl -Method POST http://localhost:8001/api/run_agent_cycle

# Test chat (Python chat server)
$Env:OPENAI_API_KEY = 'your_key'
curl -Method POST -Body (@{ prompt='Hello' } | ConvertTo-Json) -ContentType 'application/json' http://localhost:8000/api/chat

# If using Node dev server hosting JS handlers on port 3000, call through it
curl -Method POST http://localhost:3000/api/run_agent_cycle
curl -Method POST -Body (@{ prompt='send 0.01 to DESTPUBKEY' } | ConvertTo-Json) -ContentType 'application/json' http://localhost:3000/api/chat
```

## Where to look when changing behavior
- `agent.py` — model loading, preprocessing, action-generation logic
- `server.py` — state shape, agent cycle flow, static file serving
- `chat_server.py` — LLM prompt structure, expected `tx` JSON format
- `static/script.js` — frontend integration, API endpoints, wallet flow
- `api/api.py` — an alternate Python API that demonstrates agent loading on FastAPI startup
