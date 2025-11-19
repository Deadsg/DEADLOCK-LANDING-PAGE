# Copilot / AI Assistant Instructions for DEADLOCK-LANDING-PAGE

This file gives concise, actionable guidance for AI coding agents working on this repository. Focus on discoverable patterns, run/dev commands, integration points, and gotchas observed in the code.

1) Big-picture architecture
- Frontend: static site served from `index.html` + `static/*`. UI code is in `static/script.js` and expects two APIs: chat and agent APIs.
- Agent API / App server: `server.py` exposes `/api/state`, `/api/run_agent_cycle`, and serves `index.html` and `/static`.
- Chat API: `chat_server.py` offers `/api/chat` and relies on an LLM (via `langchain_openai.OpenAI`).
- Alternative API implementation: `api/api.py` is a FastAPI variant that also loads the `Agent` class on startup — it’s used as an alternate interface for `/api/*` endpoints.
- Agent logic & model: `agent.py` loads an ONNX Q-network from `Q_Layered_Network/dqn_node_model.onnx` and maps actions (order matters) to Q-network outputs.

2) How the pieces talk (data flows)
- Frontend -> Chat: POST to `/api/chat` with JSON `{ prompt, wallet, balance? }`. Chat may return `response` and optional `tx` JSON for transactions.
- Frontend -> Agent API: GET `/api/state` (initial state) and POST `/api/run_agent_cycle` which runs one agent decision cycle and returns the new state.
- Agent -> Model: `Agent.choose_action(state)` calls `get_available_actions(state)`; the order of the actions defines which Q-value index corresponds to which action.

3) Key developer workflows (run/dev commands)
- Start frontend web server (serves `index.html`):
  - `python -m http.server 5500` (README shows this; the front-end then expects API URLs to be reachable from the browser)
- Run Chat API (dev):
  - `uvicorn chat_server:app --reload --port 8000` (chat_server expects an OpenAI key; see below)
- Run Agent/API server (dev):
  - `uvicorn server:app --reload --port 8001` (the `server.py` FastAPI app runs agent cycles and serves static files)
- Notes: the codebase has inconsistent example ports (some files use 5500, 8000, 8001). Confirm which server maps to which port in your environment and update `static/script.js`'s `BASE_CHAT_API_URL` and `BASE_AGENT_API_URL` accordingly.

4) Environment & external dependencies
- LLM: `chat_server.py` uses `langchain_openai.OpenAI` and requires `OPENAI_API_KEY` in the environment.
- ONNX model: `agent.py` loads an ONNX file by default using an absolute path. If the model is missing, the `Agent` falls back to random actions. Check `Q_Layered_Network/dqn_node_model.onnx` and adjust `Agent(model_path=...)` as needed.
- Python packages: code references `fastapi`, `uvicorn`, `onnxruntime`, `numpy`, `pydantic`, and `langchain_openai`.

5) Project-specific conventions & gotchas
- Action ordering is significant: `Agent.get_available_actions()` constructs a list in a deterministic order; the ONNX Q-network output indices map to that list. When changing available actions or their ordering, also verify the model mapping.
- Two API implementations exist: `server.py` (serves site + agent cycles) and `api/api.py` (alternate FastAPI with startup agent loading). When modifying endpoints, update both if they are both used in your environment.
- Frontend expects `tx` field from chat responses to be present as a JSON object: example `{ "tx": { "to": "<pubkey>", "amount": 0.01 } }`. The frontend will prompt the user to confirm the transaction.
- `agent.py` default model path is absolute; prefer using a relative path or env var for portability.

6) Quick examples (copyable)
- Start the web server (serves `index.html` on 5500):
  - `python -m http.server 5500`
- Start chat server (dev):
  - `export OPENAI_API_KEY=...` (Windows PowerShell: `$Env:OPENAI_API_KEY = '...'`)
  - `uvicorn chat_server:app --reload --port 8000`
- Start agent API server (dev):
  - `uvicorn server:app --reload --port 8001`
- Update frontend API base URLs (if running locally): edit `static/script.js` and set:
  - `const BASE_CHAT_API_URL = 'http://localhost:8000'`
  - `const BASE_AGENT_API_URL = 'http://localhost:8001'`

7) Files to inspect first when changing behavior
- `agent.py` — model loading, preprocessing, action-generation logic
- `server.py` — state shape, agent cycle flow, static file serving
- `chat_server.py` — LLM prompt structure, expected `tx` JSON format
- `static/script.js` — frontend integration, API endpoints, wallet flow
- `api/api.py` — an alternate API that demonstrates agent loading on FastAPI startup

8) Suggested small improvements to make future AI edits easier (documented here so assistants can suggest them)
- Replace absolute model path in `agent.py` with a relative path or an env var.
- Centralize port constants (or read from env) and DRY the example ports across `README.md`, `static/script.js`, and server entrypoints.

If anything in this file is unclear or you want more detail about a specific file (for example, `Agent.preprocess_state` or the LLM prompt in `chat_server.py`), tell me which area to expand and I will update this document.
