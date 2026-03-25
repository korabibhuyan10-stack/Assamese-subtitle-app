from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os, shutil, uuid

from gemini import transcribe_assamese
from subtitle import to_srt, to_vtt

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("uploads", exist_ok=True)
os.makedirs("outputs", exist_ok=True)

@app.get("/", response_class=HTMLResponse)
def home():
    with open("index.html", encoding="utf-8") as f:
        return f.read()

@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    allowed = ["mp4", "mov", "webm", "mkv", "avi", "mp3", "wav", "m4a"]
    ext = file.filename.split(".")[-1].lower()
    if ext not in allowed:
        raise HTTPException(status_code=400, detail=f"File type .{ext} not supported")

    job_id = str(uuid.uuid4())[:8]
    save_path = f"uploads/{job_id}.{ext}"

    with open(save_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        segments = transcribe_assamese(save_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(save_path):
            os.remove(save_path)

    if not segments:
        raise HTTPException(status_code=422, detail="No Assamese speech detected")

    return JSONResponse({"job_id": job_id, "segments": segments})

@app.post("/export")
async def export(request: Request):
    data = await request.json()
    segments = data.get("segments", [])
    fmt = data.get("format", "srt")
    job_id = data.get("job_id", "subtitle")

    if not segments:
        raise HTTPException(status_code=400, detail="No segments to export")

    if fmt == "srt":
        content = to_srt(segments)
        filename = f"{job_id}.srt"
    else:
        content = to_vtt(segments)
        filename = f"{job_id}.vtt"

    out_path = f"outputs/{filename}"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(content)

    return FileResponse(
        out_path,
        media_type="text/plain",
        filename=filename
    )

@app.get("/health")
def health():
    return {"status": "ok"}
