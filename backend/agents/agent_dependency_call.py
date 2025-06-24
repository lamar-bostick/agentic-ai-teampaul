from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import ListSortOrder
import pandas as pd
from io import StringIO

def run_dependency_agent(user_prompt: str):
    project = AIProjectClient(
        credential=DefaultAzureCredential(),
        endpoint="https://team-paul-project-foundry.services.ai.azure.com/api/projects/PaulProjects"
    )

    agent = project.agents.get_agent("asst_0dU7Cr89h80iyShw36xwbZHJ")
    thread = project.agents.threads.create()

    project.agents.messages.create(
        thread_id=thread.id,
        role="user",
        content=user_prompt
    )

    run = project.agents.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)

    if run.status == "failed":
        return {"error": f"Run failed", "details": run.last_error}

    messages = list(project.agents.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING))

    for message in reversed(messages):
        if message.role == "assistant" and message.text_messages:
            response_text = message.text_messages[-1].text.value

            # Try to parse markdown-style table
            if "| App_ID" in response_text and "|---" in response_text:
                try:
                    lines = response_text.splitlines()
                    table_start = next(i for i, line in enumerate(lines) if "| App_ID" in line)
                    table_lines = []
                    for line in lines[table_start:]:
                        if line.strip().startswith("|"):
                            table_lines.append(line)
                        else:
                            break

                    csv_data = "\n".join(
                        line.strip().strip("|").replace(" | ", ",") 
                        for line in table_lines 
                        if "---" not in line
                    )
                    df = pd.read_csv(StringIO(csv_data))
                    html_table = df.to_html(classes="table table-bordered table-striped", index=False, escape=False)
                    return {
                        "html_table": html_table,
                        "raw_text": response_text
                    }
                except Exception as e:
                    return {"response": response_text, "error": f"Failed to parse table: {str(e)}"}

            return {"response": response_text}

    return {"response": "No assistant reply found."}
