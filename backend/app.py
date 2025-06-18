from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from utils import extract_and_convert_zip
from agents import run_agent_task
from utils import list_app_files

app = FastAPI()

# Enable CORS so frontend can connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload")
async def upload_zip(file: UploadFile = File(...)):
    """
    Accepts a ZIP file, extracts contents,
    converts CSVs to JSON and PDFs to text,
    and stores the output in app_files/.
    """
    result = await extract_and_convert_zip(file)
    return result

@app.post("/task")
async def run_task(task: str = Form(...)):
    """
    Handles task input from the frontend (prompt or button).
    Dispatches to correct agent and returns output.
    """
    output = run_agent_task(task)
    return {"output": output}



@app.get("/files")
def get_converted_files():
    return {"files": list_app_files()}
