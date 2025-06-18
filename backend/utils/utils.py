import os
import shutil
import zipfile
import pandas as pd
import json
import fitz  # PyMuPDF

UPLOAD_DIR = "temp_uploads"
OUTPUT_DIR = "app_files"

def clear_and_create_folder(path):
    if os.path.exists(path):
        shutil.rmtree(path)
    os.makedirs(path)

def list_app_files():
    try:
        return [f for f in os.listdir(OUTPUT_DIR) if os.path.isfile(os.path.join(OUTPUT_DIR, f))]
    except Exception as e:
        return [f"[Error listing files]: {e}"]


async def extract_and_convert_zip(file):
    clear_and_create_folder(UPLOAD_DIR)
    clear_and_create_folder(OUTPUT_DIR)

    with zipfile.ZipFile(file.file, "r") as zip_ref:
        zip_ref.extractall(UPLOAD_DIR)

    for root, _, files in os.walk(UPLOAD_DIR):
        for name in files:
            full_path = os.path.join(root, name)
            filename_no_ext, ext = os.path.splitext(name)

            # CSV → JSON
            if ext.lower() == ".csv":
                try:
                    df = pd.read_csv(full_path)
                    json_data = df.to_dict(orient="records")
                    with open(os.path.join(OUTPUT_DIR, f"{filename_no_ext}.json"), "w") as out:
                        json.dump(json_data, out, indent=2)
                except Exception as e:
                    print(f"Error converting {name} to JSON: {e}")

            # PDF → TXT
            elif ext.lower() == ".pdf":
                try:
                    doc = fitz.open(full_path)
                    text = "\n".join(page.get_text() for page in doc)
                    with open(os.path.join(OUTPUT_DIR, f"{filename_no_ext}.txt"), "w", encoding="utf-8") as out:
                        out.write(text)
                except Exception as e:
                    print(f"Error extracting text from {name}: {e}")

    return {"message": f"ZIP processed. Outputs saved to {OUTPUT_DIR}/"}
