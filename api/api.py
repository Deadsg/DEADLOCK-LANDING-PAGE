from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import os
import random
import numpy as np
import onnxruntime as ort

# Import the Agent class from agent.py
from agents import Agent

app = FastAPI()

# Add CORS middleware to allow cross-origin requests
origins = [
    "*", # Allow all origins for now, consider restricting in production
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global agent instance
agent_instance: Agent = None

# Request models
class ChatRequest(BaseModel):
    prompt: str # Changed from 'message' to 'prompt'
    wallet: str = None # Added 'wallet'

class AgentCycleRequest(BaseModel):
    payload: dict # Assuming payload is a dictionary representing the state

# Response models
class ChatResponse(BaseModel):
    response: str
    session_id: str = "default_session"
    action: dict = None # To include the action chosen by the agent

class AgentCycleResponse(BaseModel):
    status: str
    result: dict = None # Assuming result can be a dictionary

@app.on_event("startup")
async def startup_event():
    global agent_instance
    print("Loading agent...")
    try:
        # Assuming the model path is relative to the project root or handled by Agent
        agent_instance = Agent() 
        print("Agent loaded successfully.")
    except Exception as e:
        print(f"Error loading agent: {e}. Agent will be None, potentially leading to errors.")
        agent_instance = None


@app.get("/")
async def read_root():
    return {"message": "Welcome to the Deadlock Landing Page API"}

# New endpoint for /api/state
@app.get("/api/state")
async def get_state():
    # This is a dummy state similar to what the frontend expects for initialization.
    # In a real application, this would come from a game state manager or database.
    dummy_state = {
        "resources": 10000,
        "log": ["System initialized.", "Waiting for commands."],
        "missions": [
            {"id": "m1", "title": "Corporate Espionage", "status": "available", "reward": 5000, "cost": 1000},
            {"id": "m2", "title": "Data Heist", "status": "in_progress", "reward": 2000, "cost": 500},
        ],
        "data_havens": [
            {"id": "d1", "name": "corp_intel_q3.zip", "analyzed": False, "value": 750},
            {"id": "d2", "name": "agent_profiles.db", "analyzed": True, "value": 1200},
        ],
        "agents": [
            {"id": "a1", "name": "Zero", "status": "available"},
            {"id": "a2", "name": "Ghost", "status": "deployed"}
        ]
    }
    return dummy_state


@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    if not agent_instance:
        raise HTTPException(status_code=500, detail="Agent not loaded.")
    
    print(f"Received chat prompt: {request.prompt} from wallet: {request.wallet}")
    
    # For chat, we need to convert the message into a state or use a default state.
    # This is a simplification. A real chat interaction might involve NLU to derive state.
    # For now, let's use a dummy state for demonstration with the agent's choose_action.
    example_state = {
        "missions": [
            {"id": "m1", "title": "Corporate Espionage", "status": "available", "cost": 1000},
            {"id": "m2", "title": "Data Heist", "status": "in_progress", "cost": 500},
        ],
        "data_havens": [
            {"id": "d1", "name": "corp_intel_q3.zip", "analyzed": False},
            {"id": "d2", "name": "agent_profiles.db", "analyzed": True},
        ],
        "agents": [
            {"id": "a1", "name": "Zero", "status": "available"}
        ],
        "resources": 10000
    }
    
    # Simulate agent thinking based on the message or current state
    chosen_action = agent_instance.choose_action(example_state)
    
    response_message = f"Acknowledged: '{request.prompt}'. Agent chose action: {chosen_action.get('action', 'unknown')}."
    
    return ChatResponse(response=response_message, session_id="default_session", action=chosen_action) # session_id remains default for now

@app.post("/api/run_agent_cycle", response_model=AgentCycleResponse)
async def run_agent_cycle_endpoint(request: AgentCycleRequest):
    if not agent_instance:
        raise HTTPException(status_code=500, detail="Agent not loaded.")
        
    print(f"Received agent cycle request with payload: {request.payload}")
    
    try:
        # The payload is expected to be the state for the agent to choose an action
        chosen_action = agent_instance.choose_action(request.payload)
        return AgentCycleResponse(status="success", result={"action": chosen_action})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during agent cycle: {e}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
