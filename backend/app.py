from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import zipfile
import csv
import json
import traceback
from pathlib import Path
import fitz  # PyMuPDF
import tempfile
from dotenv import load_dotenv

# === Local Imports ===
from agents.agent_lease import analyze_lease
from agents.agent_dependency import analyze_dependencies
from agents.agent_Lease_call import run_lease_agent
from agents.agent_dependency_call import run_dependency_agent
from agents.agent_migrationplan_call import run_migrationplan_agent
from agents.agent_migration import build_migration_plan
from agents.agent_chatbot import run_chatbot_agent
from agents.roi_formatter import get_html_output  # <-- Make sure this exists and is imported

load_dotenv()

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = './uploads'
OUTPUT_FOLDER = './app_files'
SUMMARY_CACHE_FILE = os.path.join(tempfile.gettempdir(), "summary_cache.json")
LEASE_JSON_PATH = os.path.join(tempfile.gettempdir(), "lease_output.json")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def summarize_folder(directory, max_chars=2500):
    summaries = []
    for root, dirs, files in os.walk(directory):
        for filename in files:
            file_path = os.path.join(root, filename)
            ext = filename.lower().split(".")[-1]
            try:
                if ext in ["csv", "json"]:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    summaries.append({"filename": filename, "type": ext, "content": content[:max_chars]})
                elif ext == "pdf":
                    doc = fitz.open(file_path)
                    text = "\n".join(page.get_text() for page in doc)
                    doc.close()
                    summaries.append({"filename": filename, "type": "pdf", "content": text[:max_chars]})
            except Exception as e:
                summaries.append({"filename": filename, "type": ext, "content": f"[Error reading file: {str(e)}]"})
    return summaries

def process_zip_and_extract_summary(zip_file, extract_dir="./uploads", max_chars=2500):
    zip_path = os.path.join(UPLOAD_FOLDER, zip_file.filename)
    zip_file.save(zip_path)
    extract_path = os.path.join(UPLOAD_FOLDER, os.path.splitext(zip_file.filename)[0])
    os.makedirs(extract_path, exist_ok=True)

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)

    summaries = summarize_folder(extract_path, max_chars=max_chars)
    return summaries, [{"filename": s["filename"], "type": s["type"]} for s in summaries]

@app.route('/upload', methods=['POST'])
def upload_zip():
    if 'files' not in request.files:
        return jsonify({"error": "No file part"}), 400

    uploaded_files = request.files.getlist("files")
    all_full_summaries, all_display_outputs = [], []

    for file in uploaded_files:
        if file.filename.endswith(".zip"):
            full_summaries, display_summaries = process_zip_and_extract_summary(file)
            all_full_summaries.extend(full_summaries)
            all_display_outputs.extend(display_summaries)

    with open(SUMMARY_CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(all_full_summaries, f, indent=2)

    return jsonify({"message": "Files processed successfully", "output_files": all_display_outputs})

@app.route('/analyze/lease', methods=['POST'])
def lease_route():
    data = request.get_json()
    prompt = data.get('prompt', """You are a data extraction assistant. Your goal is to parse the provided PDF and JSON files and return a single valid JSON object where each key is a site name (\\"VA\\", \\"AZ\\", or \\"CO\\") and the value is a dictionary with the following fields:

Required fields for each site:
- site (str): Name of the site
- Monthly Rent (int)
- termination_fee_clause (str): Text describing early termination penalties from the lease PDF
- under_occupancy (str): Text describing any under-occupancy clause or penalty
- lease_end_date (str): Lease expiration date in YYYY-MM-DD format (best effort)
- total_GB (float): Total Used_Cap_GB from storage_volumes.json, for servers that are not fully powered off
- number_of_applications (int): Count of App_IDs in applications.json that start with the site prefix (\\"VA\\", \\"AZ\\", \\"CO\\")
- DL380_count (int): Count of active HP ProLiant DL380 servers (based on physical_servers.json and virtual_machines.json)
- R740_R750_count (int): Count of active Dell R740 or R750 servers
- SR650_count (int): Count of active Lenovo SR650 servers
- sum_of_bandwidth (float): Total Bandwidth_Gbps from network_links.json where Link_ID starts with the site code

Instructions for extracting values:

1. **Lease PDFs** (e.g., \\"VA Lease.pdf\\"):
   - termination_fee_clause: Extract from sections about “Termination,” “Early Exit,” or “Penalty”
   - under_occupancy: Extract from sections about “Occupancy,” “Utilization,” or “Under-occupancy”
   - lease_end_date: Extract any explicit date marking end of lease term; format as YYYY-MM-DD

2. **physical_servers.json**:
   - Filter out servers where Host_Server_ID is fully powered off (see virtual_machines.json)
   - For remaining active servers, count:
     - DL380_count: If Model contains “DL380”
     - R740_R750_count: If Model contains “R740” or “R750”
     - SR650_count: If Model contains “SR650”

3. **virtual_machines.json**:
   - For each Host_Server_ID, exclude if **all** associated VMs have "Power_State": "Off"

4. **storage_volumes.json**:
   - Sum Used_Cap_GB by site
   - Only include volumes attached to active servers (as defined above)

5. **applications.json**:
   - Count the number of App_IDs where App_ID starts with the site prefix (\\"VA\\", \\"AZ\\", \\"CO\\")

6. **network_links.json**:
   - For each site, sum Bandwidth_Gbps where Link_ID starts with that site prefix (e.g., \\"VA\\", \\"AZ\\", \\"CO\\")

Rules:
- Return a single valid JSON object only.
- Use numeric types (int or float) where appropriate.
- Use "" or 0 if a field is missing.
- Do not include any explanation, headers, or extra formatting—only the JSON.
""")

    try:
        # 1. Run lease agent
        result = run_lease_agent(prompt)
        if not result or not isinstance(result, dict):
            return jsonify({"error": "Invalid JSON returned by agent"}), 500

        # 2. Save output
        with open(LEASE_JSON_PATH, "w") as f:
            json.dump(result, f, indent=2)

        # 3. Collect CSVs
        csvs = {
            "applications": os.path.join(OUTPUT_FOLDER, "applications.csv"),
            "servers": os.path.join(OUTPUT_FOLDER, "physical_servers.csv"),
            "vms": os.path.join(OUTPUT_FOLDER, "virtual_machines.csv"),
            "storage": os.path.join(OUTPUT_FOLDER, "storage_volumes.csv"),
            "network": os.path.join(OUTPUT_FOLDER, "network_links.csv")
        }

        # 4. Format and return
        html_output = get_html_output(LEASE_JSON_PATH)
        return html_output  # instead of jsonify({"html_table": html_output})

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"Lease analysis failed: {str(e)}"}), 500

@app.route('/analyze/dependencies', methods=['POST'])
def dependency_route():
    data = request.get_json(silent=True) or {}
    prompt = data.get('prompt', 'Please provide a table of the dependencies and call out any circular dependencies.')
    result = run_dependency_agent(prompt)
    return jsonify(result)

@app.route('/generate-plan', methods=['POST'])
def generate_plan_route():
    data = request.get_json(silent=True) or {}
    prompt = data.get('prompt', f"""
You are a cloud migration planning Agent that focuses on analysis of dependencies in an organization's data infrastructure
You have already ingested the client’s infrastructure CSVs and network flow data. Using that information:

1. **Generate a detailed dependency analysis report** that unearths how applications, VMs, and physical servers interact.

2. **Structure your response exactly with these headings** (in Markdown):

## 1. Dependency Graph Summary  
- Total number of applications, VMs, and servers analyzed  
- Overall data flow volume (e.g. “1.2 TB/day”)  
- Key business priority levels represented

## 2. Application Clusters  
| Cluster ID | Apps Included            | Total Data Flow | VM/Server Count | Priority Level |  
|------------|--------------------------|---------------:|----------------:|---------------:|  
| 1          | AppA, AppB, AppC         |  500 GB/day    |             3   | High           |  
| 2          | AppD, AppE               |  120 GB/day    |             2   | Medium         |

## 3. Risk Flags & Co-location Issues  
- **Co-located Dependencies:** list clusters where >2 high-traffic apps share one server  
- **Duplicate Dependencies:** highlight apps calling the same service through multiple paths  
- **Cross-Site Flows:** identify flows between data centers that may incur egress charges

## 4. Recommendations for Migration Grouping  
- Clusters recommended to migrate together (by ID)  
- Rationale for co-migration (e.g. “>8 GB/day traffic between AppA & AppB”)  
- Suggested split-points where decoupling is safe

3. **Formatting rules:**  
- Use tables where indicated.  
- Keep bullet lists to no more than 5 items per section.  
- Use consistent units (GB/day) and terminology (“cluster,” “node,” “edge”).  
- Return only valid Markdown as specified.  
 
        """)
    result = run_migrationplan_agent(prompt)
    return jsonify(result)

@app.route('/analyze/prompt', methods=['POST'])
def analyze_custom_prompt():
    user_prompt = request.form.get("prompt") or (request.get_json(silent=True) or {}).get("prompt") or "What can you tell me about the uploaded data?"

    if not os.path.exists(SUMMARY_CACHE_FILE):
        return jsonify({"error": "No uploaded data found. Please upload a ZIP first."}), 400

    with open(SUMMARY_CACHE_FILE, "r", encoding="utf-8") as f:
        extracted_summaries = json.load(f)

    app_file_summaries = summarize_folder("./app_files")
    combined_summaries = extracted_summaries + app_file_summaries

    try:
        result = run_chatbot_agent(prompt=user_prompt, file_summaries=combined_summaries)
        return jsonify({"result": result})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
