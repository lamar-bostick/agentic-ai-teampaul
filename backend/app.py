from flask import Flask, request, jsonify
from agents.agent_lease import analyze_lease
from agents.agent_dependency import analyze_dependencies
from agents.agent_migration import generate_plan

app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload_data():
    # Handle file upload here
    return jsonify({"status": "received"})

@app.route('/analyze/lease', methods=['POST'])
def analyze_lease_data():
    return analyze_lease(request.files)

@app.route('/analyze/dependencies', methods=['POST'])
def analyze_dependency_data():
    return analyze_dependencies(request.files)

@app.route('/generate-plan', methods=['POST'])
def generate_migration_plan():
    return generate_plan(request.json)

if __name__ == "__main__":
    app.run(debug=True)
