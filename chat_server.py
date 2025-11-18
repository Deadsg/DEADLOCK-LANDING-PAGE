from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_openai import OpenAI
import os
import json
import re
from fastapi import FastAPI, Request # Added Request here

# --- App Setup ---
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

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

# --- Network State (for context) ---
# This is a simplified copy for the chat server's context.
# In a real-world scenario, this might be shared via a database or Redis.
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

# --- AI/LLM Setup ---
# Note: This requires an OPENAI_API_KEY environment variable to be set.
try:
    llm = OpenAI(temperature=0.7)
except Exception as e:
    print(f"Could not initialize OpenAI LLM: {e}")
    llm = None

class Query(BaseModel):
    prompt: str
    wallet: str = None
    balance: float = None

@app.post("/api/chat")
async def chat(query: Query):
    try:
        if not llm:
            return {"response": "LLM not configured. Please set the OPENAI_API_KEY.", "tx": None, "balance": query.balance}

        wallet_info = (
            f"Connected wallet: {query.wallet}" if query.wallet
            else "No wallet connected."
        )

        balance_info = (
            f"Wallet balance: {query.balance} SOL" if query.balance is not None
            else "Wallet balance unknown."
        )

        full_prompt = f"""
        You are the central command AI for the DEADLOCK NETWORK. Your primary function is to communicate with the operator, provide information about the network's state, and report on the status and activities of the agents. You can also interpret commands related to agent operations, missions, and data analysis.

        Current Network State:
        - Resources: {network_state.get("resources")}
        - Missions: {json.dumps(network_state.get("missions"))}
        - Data Havens: {json.dumps(network_state.get("data_havens"))}
        - Agents: {json.dumps(network_state.get("agents"))}
        - Recent Log: {json.dumps(network_state.get("log"))}

        User query: {query.prompt}

        {wallet_info}
        {balance_info}

        If the user wants to send SOL, include a JSON object like:
        {{ "tx": {{ "to": "<recipient_pubkey>", "amount": 0.01 }} }}

        Only include the transaction JSON if the user asks for a transfer.
        Respond normally otherwise.
        """

        response = llm.invoke(full_prompt)

        tx_match = re.search(r'({.*"tx".*})', response)
        tx_data = None

        if tx_match:
            try:
                tx_data = json.loads(tx_match.group(1))
            except:
                tx_data = None

        return {
            "response": response,
            "tx": tx_data,
            "balance": query.balance
        }
    except Exception as e:
        import traceback
        traceback.print_exc() # Print full traceback to console
        return {"response": f"Internal server error in chat: {e}", "tx": None, "balance": query.balance, "status_code": 500}

# --- Server Entry Point ---
if __name__ == "__main__":
    import uvicorn
    print("Starting Chat Server on port 8000")
    uvicorn.run(app, host="127.0.0.1", port=5500)
