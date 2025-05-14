from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
import os

app = FastAPI()

UPLOAD_DIR = "uploads"
MERGED_FILE = "merged_summary.md"

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_location = f"{UPLOAD_DIR}/{file.filename}"
    with open(file_location, "wb+") as f:
        f.write(await file.read())
    return {"filename": file.filename, "message": "File uploaded successfully"}

@app.get("/split")
async def split_file():
    files = os.listdir(UPLOAD_DIR)
    if not files:
        return {"error": "No file uploaded."}
    
    filepath = f"{UPLOAD_DIR}/{files[0]}"
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    transcripts = [block.strip() for block in content.split("\n\n") if block.strip()]

    parts_dir = f"{UPLOAD_DIR}/parts"
    if not os.path.exists(parts_dir):
        os.makedirs(parts_dir)

    for idx, transcript in enumerate(transcripts):
        with open(f"{parts_dir}/part_{idx+1}.md", "w", encoding="utf-8") as f:
            f.write(transcript)

    return {"parts_created": len(transcripts)}

@app.get("/merge")
async def merge_parts():
    parts_dir = f"{UPLOAD_DIR}/parts"
    if not os.path.exists(parts_dir):
        return {"error": "No parts to merge."}

    merged_content = ""
    files = sorted(os.listdir(parts_dir))
    for filename in files:
        with open(f"{parts_dir}/{filename}", "r", encoding="utf-8") as f:
            merged_content += f.read() + "\n\n---\n\n"

    merged_path = f"{UPLOAD_DIR}/{MERGED_FILE}"
    with open(merged_path, "w", encoding="utf-8") as f:
        f.write(merged_content)

    return {"message": "Files merged successfully", "download_url": f"/download/{MERGED_FILE}"}
