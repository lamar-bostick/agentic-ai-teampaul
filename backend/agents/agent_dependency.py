import os
import json
import networkx as nx
import requests
from config import AGENT_DEPENDENCY_ID, AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, OUTPUT_FOLDER

def load_json(filename):
    path = os.path.join(OUTPUT_FOLDER, filename)
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def build_dependency_graph():
    applications = load_json("applications.json")
    dependencies = load_json("application_dependencies.json")
    vms = load_json("virtual_machines.json")
    servers = load_json("physical_servers.json")

    G = nx.DiGraph()

    # Add application nodes
    for app in applications:
        app_id = app.get("application_id") or app.get("App_ID")  # fallback if format changed
        app_name = app.get("application_name") or app.get("App_Name", "Unnamed App")
        if app_id:
            G.add_node(app_id, label=app_name, type="application")

    # Add dependency edges using the JSON keys you provided
    for dep in dependencies:
        source = dep.get("App_ID")
        target = dep.get("Depends_On_App_ID")
        dtype = dep.get("Dependency_Type", "depends_on")
        if source and target:
            G.add_edge(source, target, type="app_dep", label=dtype)

    # Add VM nodes and edges
    for vm in vms:
        app_id = vm.get("application_id")
        if app_id:
            vm_id = vm.get("vm_id")
            vm_name = vm.get("vm_name", vm_id)
            G.add_node(vm_id, label=vm_name, type="vm")
            G.add_edge(vm_id, app_id, type="vm_to_app")

    # Add server nodes and edges
    for server in servers:
        for vm_id in server.get("hosted_vms", []):
            server_id = server.get("server_id")
            server_name = server.get("server_name", server_id)
            G.add_node(server_id, label=server_name, type="server")
            G.add_edge(server_id, vm_id, type="server_to_vm")

    return G


def analyze_dependencies():
    G = build_dependency_graph()

    summary = {
        "total_nodes": G.number_of_nodes(),
        "total_edges": G.number_of_edges(),
        "applications": [n for n, d in G.nodes(data=True) if d.get("type") == "application"],
        "dependencies": list(G.edges())
    }

    try:
        headers = {
            "Content-Type": "application/json",
            "api-key": AZURE_OPENAI_API_KEY
        }
        payload = {
            "inputs": [
                {
                    "input": json.dumps(summary)
                }
            ]
        }
        url = f"{AZURE_OPENAI_ENDPOINT}/openai/assistants/{AGENT_DEPENDENCY_ID}/invoke?api-version=2024-12-01-preview"
        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 200:
            return {
                "agent_response": response.json(),
                "graph_summary": summary
            }
        else:
            return {
                "error": f"Agent error: {response.status_code}",
                "graph_summary": summary
            }

    except Exception as e:
        return {
            "error": str(e),
            "graph_summary": summary
        }
