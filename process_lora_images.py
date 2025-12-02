#!/usr/bin/env python3
"""
LoRA Image Processor - Standalone Script
Processes images for Stable Diffusion LoRA training
"""

import os
import sys
import zipfile
import shutil
from pathlib import Path
from PIL import Image
import cv2
import numpy as np
from datetime import datetime

# Load face detection cascade
FACE_CASCADE = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

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
        print(f"  ✓ Face detected and centered")
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
        print(f"  ✓ Center cropped (no face detected)")
    
    return cropped

def upscale_image(image, target_width, target_height):
    """Upscale image to target size using Lanczos resampling"""
    return image.resize((target_width, target_height), Image.Resampling.LANCZOS)

def process_single_image(image_path, output_dir, filename):
    """Process a single image to create both 512x512 and 512x768 versions"""
    try:
        print(f"Processing: {filename}")
        
        # Open image
        img = Image.open(image_path).convert('RGB')
        print(f"  Original size: {img.size[0]}x{img.size[1]}")
        
        results = []
        
        # Process for 512x512 (close-up face)
        print(f"  Creating 512x512 version...")
        cropped_square = smart_crop_face(img, 512, 512)
        if cropped_square.size != (512, 512):
            cropped_square = upscale_image(cropped_square, 512, 512)
        
        # Save 512x512 version
        base_name = Path(filename).stem
        square_filename = f"{base_name}_512x512.png"
        square_path = output_dir / square_filename
        cropped_square.save(square_path, 'PNG', quality=95)
        results.append(square_filename)
        print(f"  ✓ Saved: {square_filename}")
        
        # Process for 512x768 (portrait)
        print(f"  Creating 512x768 version...")
        cropped_portrait = smart_crop_face(img, 512, 768)
        if cropped_portrait.size != (512, 768):
            cropped_portrait = upscale_image(cropped_portrait, 512, 768)
        
        # Save 512x768 version
        portrait_filename = f"{base_name}_512x768.png"
        portrait_path = output_dir / portrait_filename
        cropped_portrait.save(portrait_path, 'PNG', quality=95)
        results.append(portrait_filename)
        print(f"  ✓ Saved: {portrait_filename}")
        
        return results
    except Exception as e:
        print(f"  ✗ Error processing {filename}: {str(e)}")
        return []

def process_zip_file(zip_path, output_dir=None, make_public=False):
    """Process all images in a ZIP file"""
    zip_path = Path(zip_path)
    
    if not zip_path.exists():
        print(f"❌ Error: ZIP file not found: {zip_path}")
        return
    
    # Create output directory
    if output_dir is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if make_public:
            # Save to backend public downloads for web access
            output_dir = Path("/app/backend/public_downloads") / f"lora_processed_{timestamp}"
        else:
            output_dir = zip_path.parent / f"lora_processed_{timestamp}"
    else:
        output_dir = Path(output_dir)
    
    output_dir.mkdir(exist_ok=True)
    
    print(f"\n🎨 LoRA Image Processor")
    print(f"=" * 60)
    print(f"Input ZIP: {zip_path}")
    print(f"Output folder: {output_dir}")
    print(f"=" * 60)
    
    # Create temp extraction directory
    temp_dir = output_dir.parent / f"temp_extract_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    temp_dir.mkdir(exist_ok=True)
    
    try:
        # Extract ZIP
        print(f"\n📦 Extracting ZIP file...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        print(f"✓ Extraction complete")
        
        # Find all image files
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.webp'}
        image_files = []
        for ext in image_extensions:
            image_files.extend(temp_dir.rglob(f'*{ext}'))
            image_files.extend(temp_dir.rglob(f'*{ext.upper()}'))
        
        if not image_files:
            print(f"\n❌ No image files found in ZIP!")
            return
        
        print(f"\n📸 Found {len(image_files)} images")
        print(f"\n" + "=" * 60)
        
        # Process each image
        processed_count = 0
        for i, img_path in enumerate(image_files, 1):
            print(f"\n[{i}/{len(image_files)}]")
            results = process_single_image(img_path, output_dir, img_path.name)
            processed_count += len(results)
        
        print(f"\n" + "=" * 60)
        print(f"✅ Processing Complete!")
        print(f"=" * 60)
        print(f"Input images: {len(image_files)}")
        print(f"Output files: {processed_count}")
        print(f"Output location: {output_dir.absolute()}")
        print(f"\n💡 Each image was processed into:")
        print(f"   • 512×512 version (close-up faces)")
        print(f"   • 512×768 version (portrait shots)")
        
        # Create ZIP file for easy download
        print(f"\n📦 Creating ZIP file for download...")
        zip_output = output_dir.parent / f"{output_dir.name}.zip"
        with zipfile.ZipFile(zip_output, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in output_dir.iterdir():
                if file_path.is_file():
                    zipf.write(file_path, file_path.name)
        
        print(f"✅ ZIP created: {zip_output.absolute()}")
        print(f"\n" + "=" * 60)
        print(f"📥 DOWNLOAD YOUR IMAGES:")
        print(f"=" * 60)
        print(f"ZIP file: {zip_output.name}")
        print(f"Location: {zip_output.parent.absolute()}")
        
    finally:
        # Cleanup temp directory
        shutil.rmtree(temp_dir, ignore_errors=True)

def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python process_lora_images.py <input.zip> [output_folder]")
        print("\nExample:")
        print("  python process_lora_images.py my_photos.zip")
        print("  python process_lora_images.py my_photos.zip ./output")
        sys.exit(1)
    
    zip_file = sys.argv[1]
    output_folder = sys.argv[2] if len(sys.argv) > 2 else None
    
    process_zip_file(zip_file, output_folder)

if __name__ == "__main__":
    main()
