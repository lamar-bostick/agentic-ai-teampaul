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

from agents.agent_lease import analyze_lease
from agents.agent_dependency import analyze_dependencies
from agents.agent_Lease_call import run_lease_agent
from agents.agent_dependency_call import run_dependency_agent
from agents.agent_migrationplan_call import run_migrationplan_agent
from agents.agent_migration import build_migration_plan
from agents.agent_chatbot import run_chatbot_agent

from dotenv import load_dotenv
load_dotenv()

agent_lease_id = os.getenv("AGENT_LEASE_ID")
agent_dependency_id = os.getenv("AGENT_DEPENDENCY_ID")
agent_migration_id = os.getenv("AGENT_MIGRATION_ID")

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = './uploads'
OUTPUT_FOLDER = './app_files'
SUMMARY_CACHE_FILE = os.path.join(tempfile.gettempdir(), "summary_cache.json")

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
                    summaries.append({
                        "filename": filename,
                        "type": ext,
                        "content": content[:max_chars]
                    })
                elif ext == "pdf":
                    doc = fitz.open(file_path)
                    text = "\n".join(page.get_text() for page in doc)
                    doc.close()
                    summaries.append({
                        "filename": filename,
                        "type": "pdf",
                        "content": text[:max_chars]
                    })
            except Exception as e:
                summaries.append({
                    "filename": filename,
                    "type": ext,
                    "content": f"[Error reading file: {str(e)}]"
                })
    return summaries

def process_zip_and_extract_summary(zip_file, extract_dir="./uploads", max_chars=2500):
    zip_path = os.path.join(UPLOAD_FOLDER, zip_file.filename)
    zip_file.save(zip_path)

    extract_path = os.path.join(UPLOAD_FOLDER, os.path.splitext(zip_file.filename)[0])
    os.makedirs(extract_path, exist_ok=True)

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)

    summaries = summarize_folder(extract_path, max_chars=max_chars)

    # Return full summaries for backend, and filenames only for frontend
    return summaries, [{"filename": s["filename"], "type": s["type"]} for s in summaries]

@app.route('/upload', methods=['POST'])
def upload_zip():
    if 'files' not in request.files:
        return jsonify({"error": "No file part"}), 400

    uploaded_files = request.files.getlist("files")
    all_full_summaries = []
    all_display_outputs = []

    for file in uploaded_files:
        if file.filename.endswith(".zip"):
            full_summaries, display_summaries = process_zip_and_extract_summary(file)
            all_full_summaries.extend(full_summaries)
            all_display_outputs.extend(display_summaries)

    # Save full summaries for chatbot
    with open(SUMMARY_CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(all_full_summaries, f, indent=2)

    return jsonify({"message": "Files processed successfully", "output_files": all_display_outputs})

@app.route('/analyze/lease', methods=['POST'])
def lease_route():
    data = request.get_json()
    prompt = data.get('prompt', 'Please provide important lease information and compute calculations for all leases')
    result = run_lease_agent(prompt)
    return jsonify(result)

@app.route('/analyze/dependencies', methods=['POST'])
def analyze_dependencies():
    data = request.get_json(silent=True) or {}
    prompt = data.get('prompt', 'Please provide a table of the dependencies and call out any circular dependencies.')
    result = run_dependency_agent(prompt)
    return jsonify(result)

@app.route('/generate-plan', methods=['POST'])
def generate_plan_route():
    data = request.get_json(silent=True) or {}
    prompt = data.get('prompt', 'Please generate a cloud migration plan')
    result = run_migrationplan_agent(prompt)
    return jsonify(result)

@app.route('/analyze/prompt', methods=['POST'])
def analyze_custom_prompt():
    user_prompt = (
    request.form.get("prompt")
    or (request.get_json(silent=True) or {}).get("prompt")
    or "What can you tell me about the uploaded data?"
)

    if not os.path.exists(SUMMARY_CACHE_FILE):
        return jsonify({"error": "No uploaded data found. Please upload a ZIP first."}), 400

    with open(SUMMARY_CACHE_FILE, "r", encoding="utf-8") as f:
        extracted_summaries = json.load(f)

    app_file_summaries = summarize_folder("./app_files")
    combined_summaries = extracted_summaries + app_file_summaries

    print("Summarized file contents being sent to chatbot agent:")
    print(json.dumps(combined_summaries, indent=2)[:4000])

    try:
        result = run_chatbot_agent(prompt=user_prompt, file_summaries=combined_summaries)
        return jsonify({"result": result})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
