import json
import os
from datetime import datetime
import requests
from config import AGENT_MIGRATION_ID, AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, OUTPUT_FOLDER

def rank_applications_by_roi_and_urgency(lease_data, dependency_data):
    ranked_apps = []
    for lease in lease_data:
        risk = 2 if "high" in str(lease.get("risks", [])).lower() else 1
        roi = lease.get("estimated_roi", 0)
        try:
            roi = float(roi) if isinstance(roi, str) else roi
        except:
            roi = 0
        score = roi - risk * 10
        ranked_apps.append((lease.get("filename", "unknown"), score))

    ranked_apps.sort(key=lambda x: x[1], reverse=True)
    return [app for app, score in ranked_apps]

def build_migration_plan():
    lease_data_path = os.path.join(OUTPUT_FOLDER, "lease_analysis.json")
    dependency_data_path = os.path.join(OUTPUT_FOLDER, "dependency_analysis.json")

    try:
        with open(lease_data_path) as f:
            lease_data = json.load(f)
    except:
        lease_data = []

    try:
        with open(dependency_data_path) as f:
            dependency_data = json.load(f)
    except:
        dependency_data = {}

    ordered_apps = rank_applications_by_roi_and_urgency(lease_data, dependency_data)
    total_apps = len(ordered_apps)

    waves = [
        {
            "wave": i + 1,
            "apps": ordered_apps[i::3],
            "migration_window": f"{datetime.now().year + i}-Q1"
        }
        for i in range(3)
    ]

    plan = {
        "total_apps": total_apps,
        "migration_strategy": "ROI and risk weighted 3-phase migration",
        "waves": waves
    }

    try:
        headers = {
            "Content-Type": "application/json",
            "api-key": AZURE_OPENAI_API_KEY
        }
        payload = {
            "inputs": [
                {
                    "input": json.dumps(plan)
                }
            ]
        }
        url = f"{AZURE_OPENAI_ENDPOINT}/openai/assistants/{AGENT_MIGRATION_ID}/invoke"
        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 200:
            return {
                "agent_response": response.json(),
                "plan": plan
            }
        else:
            return {
                "error": f"Agent error: {response.status_code}",
                "plan": plan
            }

    except Exception as e:
        return {
            "error": str(e),
            "plan": plan
        }
