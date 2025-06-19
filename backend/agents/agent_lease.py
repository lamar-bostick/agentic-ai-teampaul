import os
import fitz  # PyMuPDF
import json
import requests
from config import AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, AGENT_LEASE_ID

# Correct path to app_files
APP_FILES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app_files"))

def extract_text_from_pdf(file_path):
    text = ""
    doc = fitz.open(file_path)
    for page in doc:
        text += page.get_text()
    doc.close()
    return text

def analyze_lease():
    #import pdb; pdb.set_trace()
    lease_data = []

    # Ensure the app_files directory exists
    if not os.path.exists(APP_FILES_DIR):
        return {"error": f"Lease folder not found at {APP_FILES_DIR}"}

    for filename in os.listdir(APP_FILES_DIR):
        if filename.lower().endswith(".pdf"):
            file_path = os.path.join(APP_FILES_DIR, filename)
            raw_text = extract_text_from_pdf(file_path)

            # Send extracted text to Azure Agent
            try:
                headers = {
                    "Content-Type": "application/json",
                    "api-key": os.getenv("AZURE_OPENAI_API_KEY")
                }
                payload = {
                    "inputs": [
                        {
                            "input": raw_text
                        }
                    ]
                }
                url = f"{AZURE_OPENAI_ENDPOINT}/openai/assistants/{AGENT_LEASE_ID}/invoke?api-version=2024-12-01-preview"
                response = requests.post(url, headers=headers, json=payload)

                if response.status_code == 200:
                    result = response.json()
                    lease_summary = {
                        "filename": filename,
                        "summary": result,
                        "text_preview": raw_text[:300] + "..."
                    }
                else:
                    lease_summary = {
                        "filename": filename,
                        "error": f"Agent error: {response.status_code}",
                        "text_preview": raw_text[:300] + "..."
                    }

            except Exception as e:
                lease_summary = {
                    "filename": filename,
                    "error": str(e),
                    "text_preview": raw_text[:300] + "..."
                }

            lease_data.append(lease_summary)

    return lease_data
