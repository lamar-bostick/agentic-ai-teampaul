# backend/agents/agent_lease.py

import os
import fitz  # PyMuPDF
import json

APP_FILES_DIR = "../app_files"  # Relative path from backend

def extract_text_from_pdf(file_path):
    text = ""
    doc = fitz.open(file_path)
    for page in doc:
        text += page.get_text()
    doc.close()
    return text

def analyze_lease():
    lease_data = []

    for filename in os.listdir(APP_FILES_DIR):
        if filename.lower().endswith(".pdf"):
            file_path = os.path.join(APP_FILES_DIR, filename)
            raw_text = extract_text_from_pdf(file_path)

            # Simulated output (we'll replace with real Azure output later)
            lease_summary = {
                "filename": filename,
                "monthly_rent": "Unknown (placeholder)",
                "lease_term": "Unknown (placeholder)",
                "estimated_roi": "Unknown (placeholder)",
                "risks": ["Risk info not extracted yet"],
                "text_preview": raw_text[:300] + "..."  # Show first 300 chars
            }

            lease_data.append(lease_summary)

    return lease_data

