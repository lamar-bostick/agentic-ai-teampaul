from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import ListSortOrder

def run_migrationplan_agent(user_prompt: str):
    project = AIProjectClient(
        credential=DefaultAzureCredential(),
        endpoint="https://team-paul-project-foundry.services.ai.azure.com/api/projects/PaulProjects"
    )

    agent = project.agents.get_agent("asst_6pgk9JBQmIeWqjn3UbnlZbmh")
    thread = project.agents.threads.create()

    project.agents.messages.create(
        thread_id=thread.id,
        role="user",
        content=user_prompt
    )

    run = project.agents.runs.create_and_process(
        thread_id=thread.id,
        agent_id=agent.id
    )

    if run.status == "failed":
        return {"error": "Run failed", "details": run.last_error}

    messages = project.agents.messages.list(
        thread_id=thread.id,
        order=ListSortOrder.ASCENDING
    )

    assistant_responses = []
    for message in messages:
        if message.role == "assistant" and message.text_messages:
            for text_msg in message.text_messages:
                assistant_responses.append(text_msg.text.value.strip())

    combined_response = "\n\n".join(assistant_responses)
    return {"response": combined_response if combined_response else "No assistant reply found."}
