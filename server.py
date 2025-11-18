from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from agent import Agent

# --- App Setup ---
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Agent and Environment Setup ---
agent = Agent()
network_state = {
    "missions": [
        {"id": "m1", "title": "Corporate Espionage", "status": "available", "reward": 5000, "cost": 1000},
        {"id": "m2", "title": "Data Heist", "status": "available", "reward": 3500, "cost": 500},
        {"id": "m3", "title": "Asset Extraction", "status": "completed", "reward": 7000, "cost": 2000},
    ],
    "data_havens": [
        {"id": "d1", "name": "corp_intel_q3.zip", "analyzed": False, "value": 1200},
        {"id": "d2", "name": "agent_profiles.db", "analyzed": True, "value": 500},
        {"id": "d3", "name": "financial_records.csv", "analyzed": False, "value": 2800},
    ],
    "agents": [
        {"id": "a1", "name": "Zero", "status": "available"},
        {"id": "a2", "name": "Jynx", "status": "available"},
    ],
    "log": ["System initialized. Welcome, operator."],
    "resources": 10000,
}

# --- Webhook Endpoint ---
@app.post("/webhook")
async def receive_webhook(request: Request):
    """
    Accepts and logs incoming webhook payloads.
    """
    payload = await request.json()
    print("--- INCOMING WEBHOOK ---")
    print(payload)
    print("------------------------")
    return {"status": "success", "received_data": payload}

# --- Agent System API ---
@app.get("/api/state")
async def get_state():
    """Returns the current state of the DEADLOCK NETWORK."""
    return network_state

@app.post("/api/run_agent_cycle")
async def run_agent_cycle():
    """Runs one cycle of the agent's decision-making process."""
    global network_state
    try:
        # 1. Agent chooses an action based on the current state
        action = agent.choose_action(network_state)
        action_type = action.get("action")
        
        log_message = f"Agent action: {action_type}"
        
        # 2. Update state based on the chosen action
        if action_type == "accept_mission":
            mission_id = action.get("mission_id")
            for m in network_state["missions"]:
                if m["id"] == mission_id and m["status"] == "available":
                    if network_state["resources"] >= m["cost"]:
                        m["status"] = "in_progress"
                        network_state["resources"] -= m["cost"]
                        log_message += f" - Mission '{m['title']}' accepted. Cost: {m['cost']}"
                    else:
                        log_message += f" - Failed to accept '{m['title']}'. Insufficient resources."
                    break
        elif action_type == "complete_mission":
            mission_id = action.get("mission_id")
            for m in network_state["missions"]:
                if m["id"] == mission_id and m["status"] == "in_progress":
                    m["status"] = "completed"
                    network_state["resources"] += m["reward"]
                    log_message += f" - Mission '{m['title']}' completed. Reward: {m['reward']}"
                    break
        elif action_type == "analyze_data":
            data_id = action.get("data_id")
            for d in network_state["data_havens"]:
                if d["id"] == data_id and not d["analyzed"]:
                    d["analyzed"] = True
                    network_state["resources"] += d["value"]
                    log_message += f" - Data '{d['name']}' analyzed. Value: {d['value']}"
                    break
        else: # idle
            log_message = "Agent is idle. No available actions."

        network_state["log"].insert(0, log_message)
        if len(network_state["log"]) > 10: # Keep log from growing too large
            network_state["log"].pop()

        return network_state
    except Exception as e:
        import traceback
        traceback.print_exc() # Print full traceback to console
        # Return a 500 Internal Server Error
        from fastapi.responses import JSONResponse
        return JSONResponse(status_code=500, content={"detail": f"Internal server error in agent cycle: {e}"})


@app.get("/api/hello")
async def hello_world():
    """A simple test endpoint."""
    return {"message": "Hello, World!"}


# --- Static File Serving ---
# This will serve files from the 'static' directory at the '/static' URL.
app.mount("/static", StaticFiles(directory="static"), name="static")

# This will serve the 'index.html' file at the root URL.
@app.get("/")
async def read_index():
    return FileResponse('index.html')

# --- Server Entry Point ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)