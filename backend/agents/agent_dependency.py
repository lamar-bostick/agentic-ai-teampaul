# backend/agents/agent_dependency.py

import os
import json
import networkx as nx

APP_FILES_DIR = "../app_files"

def load_json(filename):
    path = os.path.join(APP_FILES_DIR, filename)
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

    for app in applications:
        G.add_node(app["application_id"], label=app["application_name"], type="application")

    for dep in dependencies:
        G.add_edge(dep["source_application_id"], dep["target_application_id"], type="app_dep")

    for vm in vms:
        app_id = vm.get("application_id")
        if app_id:
            G.add_node(vm["vm_id"], label=vm["vm_name"], type="vm")
            G.add_edge(vm["vm_id"], app_id, type="vm_to_app")

    for server in servers:
        for vm_id in server.get("hosted_vms", []):
            G.add_node(server["server_id"], label=server["server_name"], type="server")
            G.add_edge(server["server_id"], vm_id, type="server_to_vm")

    return G

def analyze_dependencies():
    G = build_dependency_graph()

    summary = {
        "total_nodes": G.number_of_nodes(),
        "total_edges": G.number_of_edges(),
        "applications": [n for n, d in G.nodes(data=True) if d.get("type") == "application"],
        "dependencies": list(G.edges())
    }

    return summary
