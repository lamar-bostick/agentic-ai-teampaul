from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import ListSortOrder
import os
import json

# Thread ID persistence file
THREAD_FILE = "chatbot_thread.json"

# === Azure Foundry project setup ===
project = AIProjectClient(
    credential=DefaultAzureCredential(),
    endpoint="https://team-paul-project-foundry.services.ai.azure.com/api/projects/PaulProjects"
)

# Set your chatbot agent ID (from environment or hardcoded)
agent = project.agents.get_agent("asst_i1CbduhlHlvRxhYnjIJ75YSJ")


# === Retrieve or create a thread ===
def get_or_create_thread():
    try:
        if os.path.exists(THREAD_FILE):
            with open(THREAD_FILE, "r") as f:
                thread_id = json.load(f)["thread_id"]
                # Confirm thread still exists
                project.agents.threads.get(thread_id)
                return thread_id
    except Exception:
        print("⚠️ Thread not found or invalid. Creating a new one.")

    # Create new thread
    new_thread = project.agents.threads.create()
    with open(THREAD_FILE, "w") as f:
        json.dump({"thread_id": new_thread.id}, f)
    return new_thread.id


# === Main entry point from app.py ===
def run_chatbot_agent(prompt, file_summaries=None):
    thread_id = get_or_create_thread()

    # Append summaries to prompt if provided
    if file_summaries:
        prompt += "\n\nHere is a summary of the uploaded files:\n"
        for f in file_summaries:
            prompt += f"\n--- {f['filename']} ({f['type']}) ---\n{f['content']}\n"

    # Add user message to thread
    project.agents.messages.create(
        thread_id=thread_id,
        role="user",
        content=prompt
    )

    # Run the assistant
    run = project.agents.runs.create_and_process(
        thread_id=thread_id,
        agent_id=agent.id
    )

    if run.status == "failed":
        raise RuntimeError(f"❌ Agent run failed: {run.last_error}")

    # List all messages in thread and return latest assistant reply
    messages = list(project.agents.messages.list(
        thread_id=thread_id,
        order=ListSortOrder.ASCENDING
    ))

    for msg in reversed(messages):
        if msg.role == "assistant" and msg.text_messages:
            return msg.text_messages[-1].text.value

    return "⚠️ No response from assistant."
