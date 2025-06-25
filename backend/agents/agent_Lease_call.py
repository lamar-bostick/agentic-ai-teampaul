from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import ListSortOrder
import os
import json

# Persistent thread file for lease agent
LEASE_THREAD_FILE = "lease_thread.json"

# === Azure Foundry project setup ===
project = AIProjectClient(
    credential=DefaultAzureCredential(),
    endpoint="https://team-paul-project-foundry.services.ai.azure.com/api/projects/PaulProjects"
)

# Load the lease agent
agent = project.agents.get_agent("asst_BpZImzT6vacMJY6ENCOQROy5")


# === Retrieve or create a thread for the lease agent ===
def get_or_create_lease_thread():
    try:
        if os.path.exists(LEASE_THREAD_FILE):
            with open(LEASE_THREAD_FILE, "r") as f:
                thread_id = json.load(f)["thread_id"]
                project.agents.threads.get(thread_id)  # Confirm it still exists
                return thread_id
    except Exception:
        print("⚠️ Lease thread not found or invalid. Creating a new one.")

    # Create a new thread if none exists
    new_thread = project.agents.threads.create()
    with open(LEASE_THREAD_FILE, "w") as f:
        json.dump({"thread_id": new_thread.id}, f)
    return new_thread.id


# === Main function to run lease agent ===
def run_lease_agent(user_prompt: str):
    thread_id = get_or_create_lease_thread()

    # Add user message
    project.agents.messages.create(
        thread_id=thread_id,
        role="user",
        content=user_prompt
    )

    # Run the agent
    run = project.agents.runs.create_and_process(
        thread_id=thread_id,
        agent_id=agent.id
    )

    if run.status == "failed":
        return {"error": f"Run failed", "details": run.last_error}

    # Get messages and return latest assistant reply
    messages = list(project.agents.messages.list(thread_id=thread_id, order=ListSortOrder.ASCENDING))
    for message in reversed(messages):
        if message.role == "assistant" and message.text_messages:
            return {"response": message.text_messages[-1].text.value}

    return {"response": "⚠️ No assistant reply found."}
