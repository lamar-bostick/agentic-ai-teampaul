from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import ListSortOrder

def run_lease_agent(user_prompt: str):
    project = AIProjectClient(
        credential=DefaultAzureCredential(),
        endpoint="https://team-paul-project-foundry.services.ai.azure.com/api/projects/PaulProjects"
    )

    agent = project.agents.get_agent("asst_BpZImzT6vacMJY6ENCOQROy5")
    thread = project.agents.threads.create()

    project.agents.messages.create(
        thread_id=thread.id,
        role="user",
        content=user_prompt  # ← use the user’s input here
    )

    run = project.agents.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)

    if run.status == "failed":
        return {"error": f"Run failed", "details": run.last_error}

    messages = list(project.agents.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING))
    for message in reversed(messages):
        if message.role == "assistant" and message.text_messages:
            return {"response": message.text_messages[-1].text.value}

    return {"response": "No assistant reply found."}

