import json
from datetime import datetime

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
    try:
        with open("app_files/lease_analysis.json") as f:
            lease_data = json.load(f)
    except:
        lease_data = []

    try:
        with open("app_files/dependency_analysis.json") as f:
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

    return {
        "total_apps": total_apps,
        "migration_strategy": "ROI and risk weighted 3-phase migration",
        "waves": waves
    }

