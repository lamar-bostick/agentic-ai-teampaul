import os
from dotenv import load_dotenv

load_dotenv()

AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AGENT_LEASE_ID = os.getenv("AGENT_LEASE_ID")
AGENT_DEPENDENCY_ID = os.getenv("AGENT_DEPENDENCY_ID")
AGENT_MIGRATION_ID = os.getenv("AGENT_MIGRATION_ID")

UPLOAD_FOLDER = "./uploads"
OUTPUT_FOLDER = "./app_files"
