import os
import random
import numpy as np
import onnxruntime as ort

class Agent:
    """
    An agent for the DEADLOCK NETWORK that uses an ONNX Q-network model to make decisions.
    """
    def __init__(self, model_path=None):
        """
        Initializes the Agent and loads the ONNX Q-network model.
        Model path is taken from the `model_path` argument or the `AGENT_MODEL_PATH`
        environment variable. If neither is provided, falls back to the relative
        path `Q_Layered_Network/dqn_node_model.onnx` inside the repo.
        """
        self.q_network = None
        self.input_name = None
        self.output_name = None
        self.state_size = 128  # Based on analysis of the training script

        # Resolve model path: explicit arg -> env var -> default relative path
        if model_path is None:
            model_path = ('C:/Users/deads/OneDrive/Documents/AGI/DEADLOCK-LANDING-PAGE/Q_Layered_Network/dqn_node_model.onnx')

        # Expand user and make absolute if relative
        model_path = os.path.expanduser(model_path)
        if not os.path.isabs(model_path):
            repo_root = os.path.dirname(__file__)
            model_path = os.path.join(repo_root, model_path)

        try:
            print(f"Attempting to load ONNX Q-network from: {model_path}")
            self.q_network = ort.InferenceSession(model_path)
            self.input_name = self.q_network.get_inputs()[0].name
            self.output_name = self.q_network.get_outputs()[0].name
            print(f"Agent initialized with ONNX Q-network from {model_path}.")
        except FileNotFoundError:
            print(f"Model file not found at {model_path}. Agent will use random action selection.")
        except Exception as e:
            print(f"Error loading ONNX Q-network: {e}. Agent will use random action selection.")

    def choose_action(self, state):
        """
        Chooses an action based on the current state of the network using the ONNX model.
        """
        available_actions = self.get_available_actions(state)
        
        if not available_actions:
            return {"action": "idle", "details": "No actions available."}

        # If the model isn't loaded, fall back to random action selection
        if not self.q_network:
            return random.choice(available_actions)

        # --- Q-Network Logic ---
        # 1. Pre-process state
        processed_state = self.preprocess_state(state)
        
        # 2. Get Q-values from the ONNX model
        q_values = self.q_network.run([self.output_name], {self.input_name: processed_state})[0][0]
        
        # 3. Choose the best available action based on Q-values
        # We map the available actions to the first N q-values.
        best_action = None
        max_q_value = -np.inf
        
        for i, action in enumerate(available_actions):
            if i < len(q_values) and q_values[i] > max_q_value:
                max_q_value = q_values[i]
                best_action = action
        
        return best_action if best_action else random.choice(available_actions)


    def preprocess_state(self, state):
        """
        Converts the state dictionary into a NumPy array for the ONNX model.
        The model expects a 1D array of size 128.
        """
        # Create a numerical representation of the state
        # This is a simplified representation. A more complex one could include more features.
        text_representation = ""
        
        # Add mission titles
        for mission in state.get("missions", []):
            if mission["status"] == "available" or mission["status"] == "in_progress":
                text_representation += mission["title"] + " "

        # Add data haven names
        for data in state.get("data_havens", []):
            if not data["analyzed"]:
                text_representation += data["name"] + " "

        # Convert text to ordinal values
        ord_values = [ord(char) for char in text_representation]
        
        # Pad or truncate to the required state size
        padded_values = np.zeros(self.state_size, dtype=np.float32)
        length = min(len(ord_values), self.state_size)
        padded_values[:length] = ord_values[:length]
        
        return padded_values.reshape(1, -1)


    def get_available_actions(self, state):
        """
        Determines the list of possible actions based on the current state.
        The order of actions here is important as it maps to the Q-network output.
        """
        actions = []

        # Action: Complete a mission
        for mission in state.get("missions", []):
            if mission.get("status") == "in_progress":
                actions.append({"action": "complete_mission", "mission_id": mission["id"]})

        # Action: Accept a mission
        for mission in state.get("missions", []):
            if mission.get("status") == "available" and state.get("resources", 0) >= mission.get("cost", 0):
                actions.append({"action": "accept_mission", "mission_id": mission["id"]})

        # Action: Analyze data
        for data_file in state.get("data_havens", []):
            if not data_file.get("analyzed"):
                actions.append({"action": "analyze_data", "data_id": data_file["id"]})
        
        return actions

# To test the agent independently:
if __name__ == "__main__":
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

    agent = Agent()
    if agent.q_network:
        action = agent.choose_action(example_state)
        
        print("\n--- Agent Test ---")
        print(f"Current state: {example_state}")
        print(f"Chosen action: {action}")
        print("--------------------")