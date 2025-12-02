from fastapi import FastAPI, APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone
import zipfile
import io
import shutil
from PIL import Image
import cv2
import numpy as np


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create temporary directories for image processing
UPLOAD_DIR = ROOT_DIR / 'uploads'
PROCESSED_DIR = ROOT_DIR / 'processed'
UPLOAD_DIR.mkdir(exist_ok=True)
PROCESSED_DIR.mkdir(exist_ok=True)

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Load face detection cascade
FACE_CASCADE = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')


# Define Models
class StatusCheck(BaseModel):
    model_config = ConfigDict(extra="ignore")  # Ignore MongoDB's _id field
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StatusCheckCreate(BaseModel):
    client_name: str

class ProcessingStatus(BaseModel):
    status: str
    progress: int
    total_images: int
    message: str

# Image Processing Functions
def detect_face(image_np):
    """Detect face in image and return coordinates"""
    gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
    faces = FACE_CASCADE.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    
    if len(faces) > 0:
        # Return largest face
        largest_face = max(faces, key=lambda f: f[2] * f[3])
        return largest_face
    return None

def smart_crop_face(image, target_width, target_height):
    """Crop image focusing on detected face or center"""
    img_array = np.array(image)
    height, width = img_array.shape[:2]
    
    # Detect face
    face = detect_face(img_array)
    
    if face is not None:
        x, y, w, h = face
        # Calculate center of face
        face_center_x = x + w // 2
        face_center_y = y + h // 2
        
        # Calculate crop area with face in center, with some padding
        padding_factor = 1.8 if target_height > target_width else 1.5
        crop_width = int(w * padding_factor)
        crop_height = int(h * padding_factor)
        
        # Adjust to target aspect ratio
        aspect_ratio = target_width / target_height
        if crop_width / crop_height > aspect_ratio:
            crop_height = int(crop_width / aspect_ratio)
        else:
            crop_width = int(crop_height * aspect_ratio)
        
        # Calculate crop boundaries
        left = max(0, face_center_x - crop_width // 2)
        top = max(0, face_center_y - crop_height // 2)
        right = min(width, left + crop_width)
        bottom = min(height, top + crop_height)
        
        # Adjust if crop goes out of bounds
        if right - left < crop_width:
            if left == 0:
                right = min(width, crop_width)
            else:
                left = max(0, width - crop_width)
        
        if bottom - top < crop_height:
            if top == 0:
                bottom = min(height, crop_height)
            else:
                top = max(0, height - crop_height)
        
        cropped = image.crop((left, top, right, bottom))
    else:
        # No face detected, do center crop
        aspect_ratio = target_width / target_height
        current_ratio = width / height
        
        if current_ratio > aspect_ratio:
            # Image is wider, crop width
            new_width = int(height * aspect_ratio)
            left = (width - new_width) // 2
            cropped = image.crop((left, 0, left + new_width, height))
        else:
            # Image is taller, crop height
            new_height = int(width / aspect_ratio)
            top = (height - new_height) // 2
            cropped = image.crop((0, top, width, top + new_height))
    
    return cropped

def upscale_image(image, target_width, target_height):
    """Upscale image to target size using Lanczos resampling"""
    return image.resize((target_width, target_height), Image.Resampling.LANCZOS)

def process_single_image(image_path, output_dir, filename):
    """Process a single image to create both 512x512 and 512x768 versions"""
    try:
        # Open image
        img = Image.open(image_path).convert('RGB')
        
        results = []
        
        # Process for 512x512 (close-up face)
        cropped_square = smart_crop_face(img, 512, 512)
        if cropped_square.size != (512, 512):
            cropped_square = upscale_image(cropped_square, 512, 512)
        
        # Save 512x512 version
        base_name = Path(filename).stem
        square_filename = f"{base_name}_512x512.png"
        square_path = output_dir / square_filename
        cropped_square.save(square_path, 'PNG', quality=95)
        results.append(square_filename)
        
        # Process for 512x768 (portrait)
        cropped_portrait = smart_crop_face(img, 512, 768)
        if cropped_portrait.size != (512, 768):
            cropped_portrait = upscale_image(cropped_portrait, 512, 768)
        
        # Save 512x768 version
        portrait_filename = f"{base_name}_512x768.png"
        portrait_path = output_dir / portrait_filename
        cropped_portrait.save(portrait_path, 'PNG', quality=95)
        results.append(portrait_filename)
        
        return results
    except Exception as e:
        logger.error(f"Error processing {filename}: {str(e)}")
        return []

# Add your routes to the router instead of directly to app
@api_router.get("/")
async def root():
    return {"message": "LoRA Image Processor API"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.model_dump()
    status_obj = StatusCheck(**status_dict)
    
    # Convert to dict and serialize datetime to ISO string for MongoDB
    doc = status_obj.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    
    _ = await db.status_checks.insert_one(doc)
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    # Exclude MongoDB's _id field from the query results
    status_checks = await db.status_checks.find({}, {"_id": 0}).to_list(1000)
    
    # Convert ISO string timestamps back to datetime objects
    for check in status_checks:
        if isinstance(check['timestamp'], str):
            check['timestamp'] = datetime.fromisoformat(check['timestamp'])
    
    return status_checks

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()