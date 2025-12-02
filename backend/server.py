from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/downloads", StaticFiles(directory="/app/backend/public_downloads"), name="downloads")

@app.get("/")
async def root():
    return {
        "message": "LoRA Image Processor Download Server", 
        "status": "ready",
        "file": "lora_image_processor_v1.3.0.zip",
        "download_url": "/api/files/download/lora_image_processor_v1.3.0.zip"
    }

@app.get("/api/files/download/{filename}")
async def download_file(filename: str):
    file_path = f"/app/backend/public_downloads/{filename}"
    print(f"[DOWNLOAD REQUEST] Attempting to serve: {file_path}")
    print(f"[FILE CHECK] File exists: {os.path.exists(file_path)}")
    print(f"[FILE CHECK] File size: {os.path.getsize(file_path) if os.path.exists(file_path) else 'N/A'} bytes")
    
    if os.path.exists(file_path):
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type='application/zip',
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Cache-Control": "no-cache"
            }
        )
    
    print(f"[ERROR] File not found: {file_path}")
    return {"detail": "File not found", "path": file_path, "filename": filename}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
