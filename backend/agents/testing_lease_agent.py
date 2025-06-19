from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import ListSortOrder

project = AIProjectClient(
    credential=DefaultAzureCredential(),
    endpoint="https://team-paul-project-foundry.services.ai.azure.com/api/projects/PaulProjects")

agent = project.agents.get_agent("asst_BpZImzT6vacMJY6ENCOQROy5")

thread = project.agents.threads.get("thread_K2XbfvNFwEkU4GnDHPkphsi7")

message = project.agents.messages.create(
    thread_id=thread.id,
    role="user",
    content="what is the ROI on the AZ Lease?"
)

run = project.agents.runs.create_and_process(
    thread_id=thread.id,
    agent_id=agent.id)

if run.status == "failed":
    print(f"Run failed: {run.last_error}")
else:
    messages = project.agents.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)

    for message in messages:
        if message.text_messages:
            print(f"{message.role}: {message.text_messages[-1].text.value}")