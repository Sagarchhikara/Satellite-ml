import os
import tempfile
import uuid
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from utils import validate_tif
from ndvi import compute_ndvi

app = FastAPI(title="Satellite NDVI Microservice")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok", "service": "satellite-ndvi"}

@app.post("/analyze")
async def analyze_endpoint(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename missing")
    
    filename = file.filename.lower()
    if not (filename.endswith(".tif") or filename.endswith(".tiff")):
        raise HTTPException(status_code=400, detail="Only .tif or .tiff allowed")
        
    temp_filepath = os.path.join(tempfile.gettempdir(), f"{uuid.uuid4()}_{file.filename}")
    
    try:
        content = await file.read()
        with open(temp_filepath, "wb") as f:
            f.write(content)
                  
        ndvi_stats = compute_ndvi(temp_filepath)
        ndvi_stats["filename"] = file.filename
        return ndvi_stats
        
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
    finally:
        if os.path.exists(temp_filepath):
            try:
                os.remove(temp_filepath)
            except OSError:
                pass
