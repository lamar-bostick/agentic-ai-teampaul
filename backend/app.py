from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import zipfile
import csv
import json
import traceback
from pathlib import Path

from agents.agent_lease import analyze_lease
from agents.agent_dependency import analyze_dependencies
from agents.agent_Lease_call import run_lease_agent
from agents.agent_dependency_call import run_dependency_agent
from agents.agent_migrationplan_call import run_migrationplan_agent
from agents.agent_migration import build_migration_plan

from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()

azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
agent_lease_id = os.getenv("AGENT_LEASE_ID")
agent_dependency_id = os.getenv("AGENT_DEPENDENCY_ID")
agent_migration_id = os.getenv("AGENT_MIGRATION_ID")

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = './uploads'
OUTPUT_FOLDER = './app_files'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def convert_csv_to_json(csv_path, output_dir):
    base_name = os.path.splitext(os.path.basename(csv_path))[0]
    json_path = os.path.join(output_dir, base_name + ".json")
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        rows = list(reader)
    with open(json_path, 'w', encoding='utf-8') as jsonfile:
        json.dump(rows, jsonfile, indent=4)
    return json_path

def process_zip(file):
    zip_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(zip_path)
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        extract_path = os.path.join(UPLOAD_FOLDER, os.path.splitext(file.filename)[0])
        zip_ref.extractall(extract_path)

    output_files = []
    for root, dirs, files in os.walk(extract_path):
        for f in files:
            full_path = os.path.join(root, f)
            if f.endswith('.csv'):
                json_path = convert_csv_to_json(full_path, OUTPUT_FOLDER)
                output_files.append(json_path)
            elif f.endswith('.pdf'):
                pdf_output = os.path.join(OUTPUT_FOLDER, f)
                with open(full_path, 'rb') as src_file:
                    with open(pdf_output, 'wb') as dest_file:
                        dest_file.write(src_file.read())
                output_files.append(pdf_output)
    return output_files

def extract_file_context(directory):
    file_context = []
    for file_path in Path(directory).rglob("*"):
        if file_path.suffix == ".json":
            try:
                with open(file_path, "r", encoding="utf-8") as jf:
                    data = json.load(jf)
                    file_context.append({file_path.name: data})
            except Exception:
                with open(file_path, "r", encoding="utf-8") as jf:
                    file_context.append({file_path.name: jf.read()[:3000]})
        elif file_path.suffix == ".csv":
            try:
                with open(file_path, "r", encoding="utf-8") as cf:
                    content = cf.read()
                    file_context.append({file_path.name: content[:3000]})
            except Exception:
                file_context.append({file_path.name: "[Could not read CSV]"})
        elif file_path.suffix == ".pdf":
            try:
                import fitz
                doc = fitz.open(file_path)
                text = "\n".join(page.get_text() for page in doc)
                doc.close()
                file_context.append({file_path.name: text[:3000]})
            except Exception as e:
                file_context.append({file_path.name: f"[Could not read PDF: {str(e)}]"})
    return file_context

@app.route('/upload', methods=['POST'])
def upload_zip():
    if 'files' not in request.files:
        return jsonify({"error": "No file part"}), 400

    uploaded_files = request.files.getlist("files")
    saved_outputs = []

    for file in uploaded_files:
        if file.filename.endswith(".zip"):
            saved_outputs.extend(process_zip(file))

    return jsonify({"message": "Files processed successfully", "output_files": saved_outputs})

@app.route('/analyze/lease', methods=['POST'])
def lease_route():
    data = request.get_json()
    prompt = data.get('prompt', 'Please provide important lease information for all leases')
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
    prompt = data.get('prompt', 'Please generate a cloud migration plan and double check your math')
    result = run_migrationplan_agent(prompt)
    return jsonify(result)

@app.route('/analyze/prompt', methods=['POST'])
def analyze_custom_prompt():
    data = request.get_json(silent=True) or {}
    user_prompt = data.get('prompt', 'No prompt provided.')

    uploaded_files = extract_file_context(OUTPUT_FOLDER)

    try:
        client = AzureOpenAI(
            api_key=azure_api_key,
            api_version="2024-03-01-preview",
            azure_endpoint=azure_endpoint
        )

        system_prompt = (
            "You are a helpful cloud migration assistant. "
            "The user has uploaded several files, including both structured JSON data and text extracted from PDF leases."
            "Use the summarized file contents below to answer the user's question with precision, prioritizing data from the files over assumptions.\n"
        )
        file_summary = json.dumps(uploaded_files, indent=2)[:4000]

        response = client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
            messages=[
                {"role": "system", "content": f"{system_prompt}\n\n{file_summary}"},
                {"role": "user", "content": user_prompt}
            ]
        )

        return jsonify({"result": response.choices[0].message.content})

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
