from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "LoRA Image Processor Download Server", "status": "ready"}

@app.get("/api/files/download/{filename}")
async def download_file(filename: str):
    file_path = f"/app/backend/public_downloads/{filename}"
    print(f"Attempting to download: {file_path}")
    print(f"File exists: {os.path.exists(file_path)}")
    
    if os.path.exists(file_path):
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type='application/zip',
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    return {"error": "File not found", "path": file_path}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
