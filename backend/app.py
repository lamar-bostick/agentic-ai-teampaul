from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import zipfile
import csv
import json

from agents.agent_lease import analyze_lease
from agents.agent_dependency import analyze_dependencies


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


@app.route('/analyze/lease', methods=['GET'])
def lease_route():
    results = analyze_lease()
    return jsonify(results)


@app.route('/analyze/dependencies', methods=['POST'])
def analyze_dependencies():
    # Placeholder for Dependency Analyzer (Agent B)
    return jsonify({"result": "Dependency analysis complete (stub)"})


@app.route('/generate-plan', methods=['POST'])
def generate_plan():
    # Placeholder for Migration Planner (Agent C)
    return jsonify({"result": "Migration plan created (stub)"})


if __name__ == '__main__':
    app.run(debug=True, port=5000)
