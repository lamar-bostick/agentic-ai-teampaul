import os
import json
from dotenv import load_dotenv
import openai

# Load credentials from .env file
load_dotenv()
openai.api_type = "azure"
openai.api_key = os.getenv("OPENAI_API_KEY")
openai.api_base = os.getenv("OPENAI_API_BASE")
openai.api_version = os.getenv("OPENAI_API_VERSION")
deployment_name = os.getenv("OPENAI_DEPLOYMENT_NAME")

APP_FILES_DIR = "app_files"

def load_json_file(filename):
    path = os.path.join(APP_FILES_DIR, filename)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def load_text_file(filename):
    path = os.path.join(APP_FILES_DIR, filename)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return ""

def call_openai(prompt):
    try:
        response = openai.ChatCompletion.create(
            engine=deployment_name,
            messages=[
                {"role": "system", "content": "You are a cloud infrastructure and migration planning expert."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message["content"]
    except Exception as e:
        return f"[Error calling OpenAI]: {str(e)}"

def run_agent_task(task):
    task = task.lower()

    if "dependency" in task:
        data = load_json_file("application_dependencies.json")
        if not data:
            return "No dependency data found."
        prompt = f"""Here is a list of application dependencies:\n{json.dumps(data, indent=2)}\n
        Analyze the critical dependencies and suggest how to group applications for migration."""
        return call_openai(prompt)

    elif "lease" in task:
        text = load_text_file("lease_info.txt")
        if not text:
            return "No lease information found."
        prompt = f"""Given this lease contract text:\n{text}\n
        Identify key financial terms, renewal risks, and any opportunities to reduce costs."""
        return call_openai(prompt)

    elif "migration plan" in task or "build" in task:
        dependencies = load_json_file("application_dependencies.json")
        lease_text = load_text_file("lease_info.txt")
        servers = load_json_file("physical_servers.json")
        apps = load_json_file("applications.json")

        prompt = f"""
You are a highly skilled cloud migration strategist. You will use the following structured data to build a professional-grade 3-year cloud migration plan:

### DATA:
- Application Dependencies: {json.dumps(dependencies or {}, indent=2)}
- Server Info: {json.dumps(servers or {}, indent=2)}
- Lease Terms: {lease_text}
- Application Metadata: {json.dumps(apps or {}, indent=2)}

### TASK:
Using the data above, create a structured cloud migration plan that:
1. Prioritizes **cost efficiency** and minimizes risk.
2. Aligns with the following business goals:
   - Reduce costs
   - Enable scalability
   - Improve customer satisfaction
   - Foster innovation
3. Includes specific **security measures** (encryption, access control, etc.).
4. Describes **backup & recovery strategies** during the transition.
5. Minimizes downtime during migration by staging deployments.
6. Recommends appropriate technologies (e.g., Kubernetes, serverless, VMs).

### FORMAT:
Structure your response using these 3 sections:

#### 1. Executive Summary
- Brief overview of the plan and rationale.
- Summary of cloud platform recommendation.

#### 2. Migration Phases
- Use a table to define each migration wave. Include:
  - Wave Number
  - Timeline
  - Applications/Services
  - Migration Method (lift & shift, re-platform, etc.)
  - Recommended Cloud Option (Kubernetes, VM, etc.)
  - Risks
  - Risk Mitigation Strategy

#### 3. Alignment with Business Goals
- Explain **how** each element of the plan supports the business goals above.
- Bullet points or short paragraphs are okay.

Please return the response as clear markdown-formatted text or HTML.
        """

        return call_openai(prompt)


    # Default fallback: use freeform user prompt
    prompt = f"Answer this task or question about cloud migration: {task}"
    return call_openai(prompt)
 