# backend/azure_agents.py

import requests
import json
from config import AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT

def call_foundry_agent(agent_id, input_data):
    url = f"{AZURE_OPENAI_ENDPOINT}/openai/assistants/{agent_id}/completions"
    
    headers = {
        "Content-Type": "application/json",
        "api-key": AZURE_OPENAI_API_KEY
    }

    payload = {
        "input": input_data
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}
