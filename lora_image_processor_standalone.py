#!/usr/bin/env python3
"""
LoRA Image Processor - Standalone Script
For Stable Diffusion LoRA Training

Copyright (c) 2025 LoRA Image Processor
Licensed under MIT License (see LICENSE file)

Author: AI Assistant
Version: 1.0.0
License: MIT (Free and Open Source)
Repository: github.com/yourusername/lora-image-processor

This is FREE SOFTWARE released under the MIT License.
You are free to use, modify, and distribute this software.
See LICENSE file for full terms

This script processes images for LoRA training by:
- Detecting faces automatically
- Cropping intelligently with face centering
- Creating 512x512 (close-up) and 512x768 (portrait) versions
- Upscaling with high-quality Lanczos resampling
"""

import os
import sys
import zipfile
import shutil
from pathlib import Path
from datetime import datetime
import argparse
import random

try:
    from PIL import Image, ImageStat
    import cv2
    import numpy as np
except ImportError as e:
    print("ERROR: Missing required library!")
    print("\nPlease install dependencies:")
    print("  pip install pillow opencv-python numpy")
    print("\nOr use:")
    print("  pip install -r requirements.txt")
    sys.exit(1)

# Quality thresholds
BLUR_THRESHOLD = 100.0  # Laplacian variance threshold
MIN_BRIGHTNESS = 30     # Minimum average brightness
MAX_BRIGHTNESS = 225    # Maximum average brightness
MIN_CONTRAST = 30       # Minimum contrast

# Version
__version__ = "1.0.0"

# Load face detection cascade
try:
    FACE_CASCADE = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
except Exception as e:
    print(f"Warning: Could not load face detection cascade: {e}")
    print("Face detection will be disabled, using center crop only.")
    FACE_CASCADE = None

def detect_facial_features(image_np):
    """Detect individual facial features (eyes, nose, mouth) when full face detection fails"""
    gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
    height, width = gray.shape
    
    features_found = []
    
    # Try to detect eyes
    try:
        eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        eyes = eye_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(20, 20))
        if len(eyes) >= 2:  # Need at least 2 eyes for a valid face region
            features_found.extend(eyes)
    except:
        pass
    
    # Try to detect nose
    try:
        # Use profile cascade which sometimes works for nose detection
        nose_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_profileface.xml')
        noses = nose_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=3, minSize=(30, 30))
        if len(noses) > 0:
            features_found.extend(noses)
    except:
        pass
    
    # Try to detect mouth/smile
    try:
        smile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_smile.xml')
        mouths = smile_cascade.detectMultiScale(gray, scaleFactor=1.8, minNeighbors=20, minSize=(25, 25))
        if len(mouths) > 0:
            features_found.extend(mouths)
    except:
        pass
    
    if len(features_found) >= 2:  # Need at least 2 features to consider it a face region
        # Calculate bounding box around all detected features
        min_x = min([x for x, y, w, h in features_found])
        min_y = min([y for x, y, w, h in features_found])
        max_x = max([x + w for x, y, w, h in features_found])
        max_y = max([y + h for x, y, w, h in features_found])
        
        # Create a synthetic face box around the features
        face_x = min_x
        face_y = min_y
        face_w = max_x - min_x
        face_h = max_y - min_y
        
        # Add padding (features are usually in the middle of face)
        padding = 0.5  # 50% padding around detected features
        face_x = max(0, int(face_x - face_w * padding))
        face_y = max(0, int(face_y - face_h * padding))
        face_w = int(face_w * (1 + padding * 2))
        face_h = int(face_h * (1 + padding * 2))
        
        # Ensure within image bounds
        face_w = min(face_w, width - face_x)
        face_h = min(face_h, height - face_y)
        
        return {
            'box': (face_x, face_y, face_w, face_h),
            'angle': 'frontal',
            'confidence': 'features_based'
        }
    
    return None

def detect_face(image_np):
    """Detect face in image with multiple attempts and better accuracy"""
    if FACE_CASCADE is None:
        return None
        
    gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
    
    # Try multiple detection parameters for better results
    detection_params = [
        {'scaleFactor': 1.05, 'minNeighbors': 3, 'minSize': (40, 40)},  # More sensitive
        {'scaleFactor': 1.1, 'minNeighbors': 5, 'minSize': (30, 30)},   # Default
        {'scaleFactor': 1.2, 'minNeighbors': 4, 'minSize': (20, 20)},   # Even more sensitive
    ]
    
    all_faces = []
    for params in detection_params:
        faces = FACE_CASCADE.detectMultiScale(gray, **params)
        if len(faces) > 0:
            all_faces.extend(faces)
    
    if len(all_faces) > 0:
        # Remove duplicate detections (overlapping boxes)
        unique_faces = []
        for face in all_faces:
            x, y, w, h = face
            is_duplicate = False
            for uf in unique_faces:
                ux, uy, uw, uh = uf
                # Check if faces overlap significantly
                overlap_x = max(0, min(x + w, ux + uw) - max(x, ux))
                overlap_y = max(0, min(y + h, uy + uh) - max(y, uy))
                overlap_area = overlap_x * overlap_y
                if overlap_area > (w * h * 0.5):  # 50% overlap
                    is_duplicate = True
                    break
            if not is_duplicate:
                unique_faces.append(face)
        
        # Return largest face
        largest_face = max(unique_faces, key=lambda f: f[2] * f[3])
        x, y, w, h = largest_face
        
        # Estimate face angle by aspect ratio
        aspect = w / h
        if aspect > 1.2:
            angle = 'profile'
        elif aspect < 0.9:
            angle = 'tilted'
        else:
            angle = 'frontal'
        
        return {'box': largest_face, 'angle': angle}
    
    return None

def check_image_quality(image):
    """Check if image meets quality standards for LoRA training"""
    img_array = np.array(image.convert('L'))  # Convert to grayscale for analysis
    quality_issues = []
    
    # 1. Check sharpness (blur detection)
    laplacian_var = cv2.Laplacian(img_array, cv2.CV_64F).var()
    if laplacian_var < BLUR_THRESHOLD:
        quality_issues.append(f"blurry (sharpness: {laplacian_var:.1f})")
    
    # 2. Check brightness
    stat = ImageStat.Stat(image.convert('L'))
    brightness = stat.mean[0]
    if brightness < MIN_BRIGHTNESS:
        quality_issues.append(f"too dark (brightness: {brightness:.1f})")
    elif brightness > MAX_BRIGHTNESS:
        quality_issues.append(f"overexposed (brightness: {brightness:.1f})")
    
    # 3. Check contrast
    contrast = stat.stddev[0]
    if contrast < MIN_CONTRAST:
        quality_issues.append(f"low contrast ({contrast:.1f})")
    
    return {
        'passed': len(quality_issues) == 0,
        'issues': quality_issues,
        'sharpness': laplacian_var,
        'brightness': brightness,
        'contrast': contrast
    }

def analyze_facial_expression(image, face_data):
    """
    ADVANCED facial expression analysis with MAXIMUM detail for LoRA training.
    Detects nuanced expressions, gaze direction, head position, and more.
    """
    if not face_data:
        return 'neutral', []
    
    img_array = np.array(image)
    gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    face_box = face_data['box']
    face_x, face_y, face_w, face_h = face_box
    
    # Extract face region
    face_region = gray[face_y:face_y+face_h, face_x:face_x+face_w]
    if face_region.size == 0:
        return 'neutral', []
    
    expression_signals = {}
    additional_descriptors = []
    
    # === 1. ADVANCED SMILE/LAUGH DETECTION ===
    try:
        smile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_smile.xml')
        mouth_region = face_region[int(face_h*0.4):, :]
        
        # Multiple detection levels
        smiles_subtle = smile_cascade.detectMultiScale(
            mouth_region, scaleFactor=1.4, minNeighbors=8, minSize=(12, 12)
        )
        smiles_clear = smile_cascade.detectMultiScale(
            mouth_region, scaleFactor=1.7, minNeighbors=15, minSize=(15, 15)
        )
        smiles_big = smile_cascade.detectMultiScale(
            mouth_region, scaleFactor=1.8, minNeighbors=22, minSize=(20, 20)
        )
        
        # Classify smile intensity
        if len(smiles_big) > 0:
            expression_signals['laughing'] = 10
            expression_signals['joyful'] = 8
            additional_descriptors.append('teeth_visible')
        elif len(smiles_clear) > 0:
            expression_signals['smiling'] = 8
            expression_signals['cheerful'] = 6
        elif len(smiles_subtle) > 0:
            expression_signals['subtle_smile'] = 5
            expression_signals['playful'] = 4
            
    except:
        pass
    
    # === 2. EYE ANALYSIS (gaze, surprise, expression) ===
    try:
        eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        eye_region = face_region[:int(face_h*0.6), :]
        
        eyes = eye_cascade.detectMultiScale(
            eye_region, scaleFactor=1.1, minNeighbors=5, minSize=(15, 15)
        )
        
        if len(eyes) >= 2:
            # Sort eyes by x position
            eyes_sorted = sorted(eyes, key=lambda e: e[0])
            
            # Analyze eye size and shape
            avg_eye_height = np.mean([h for x, y, w, h in eyes])
            avg_eye_width = np.mean([w for x, y, w, h in eyes])
            eye_aspect = avg_eye_height / avg_eye_width if avg_eye_width > 0 else 0
            
            # Wide eyes (tall aspect) = surprised or curious
            if eye_aspect > 1.3:
                expression_signals['surprised'] = 7
                expression_signals['curious'] = 5
                additional_descriptors.append('eyes_wide')
            elif eye_aspect < 0.7:
                expression_signals['squinting'] = 4
            
            # Check eye position for gaze direction
            eye_x_positions = [x + w/2 for x, y, w, h in eyes]
            avg_eye_x = np.mean(eye_x_positions)
            face_center_x = face_w / 2
            
            # Eyes shifted to one side = looking away
            if abs(avg_eye_x - face_center_x) > face_w * 0.15:
                additional_descriptors.append('looking_away')
            else:
                additional_descriptors.append('eye_contact')
                
    except:
        pass
    
    # === 3. MOUTH VARIANCE (open mouth, teeth) ===
    try:
        mouth_y_start = int(face_h * 0.55)
        mouth_y_end = int(face_h * 0.85)
        mouth_region = face_region[mouth_y_start:mouth_y_end, :]
        
        if mouth_region.size > 0:
            mouth_variance = np.var(mouth_region)
            
            # Very high variance = wide open mouth
            if mouth_variance > 800:
                expression_signals['laughing'] = expression_signals.get('laughing', 0) + 5
                additional_descriptors.append('mouth_open')
            elif mouth_variance > 500:
                expression_signals['smiling'] = expression_signals.get('smiling', 0) + 3
    except:
        pass
    
    # === 4. FACE VARIANCE (serious, calm, expressive) ===
    try:
        face_variance = np.var(face_region)
        face_contrast = np.max(face_region) - np.min(face_region)
        
        # Low variance + low contrast = very calm/serious
        if face_variance < 250 and face_contrast < 100:
            if not expression_signals:  # Only if no other expression
                expression_signals['serious'] = 5
                expression_signals['pensive'] = 4
                expression_signals['thoughtful'] = 3
        
        # High contrast = well-defined features
        if face_contrast > 150:
            additional_descriptors.append('well_lit')
            
    except:
        pass
    
    # === 5. HEAD POSITION/TILT ===
    angle = face_data.get('angle', 'frontal')
    if angle == 'profile':
        additional_descriptors.append('profile')
        expression_signals['profile'] = 6
    elif angle == 'tilted':
        additional_descriptors.append('head_tilted')
        expression_signals['tilted'] = 5
    
    # === 6. FACE FRAMING ===
    face_area = face_box[2] * face_box[3]
    image_area = img_array.shape[0] * img_array.shape[1]
    face_percentage = (face_area / image_area) * 100
    
    if face_percentage > 35:
        additional_descriptors.append('extreme_closeup')
    elif face_percentage > 25:
        additional_descriptors.append('closeup')
    elif face_percentage > 15:
        additional_descriptors.append('portrait')
    
    # === 7. SELECT PRIMARY EXPRESSION ===
    if expression_signals:
        primary_expression = max(expression_signals, key=expression_signals.get)
    else:
        primary_expression = 'neutral'
    
    return primary_expression, additional_descriptors

def analyze_image_characteristics(image, face_data):
    """
    Comprehensive image analysis for LoRA training - MAXIMUM descriptive detail.
    Returns primary expression and ALL applicable descriptors.
    """
    if not face_data:
        return ['neutral']
    
    # Get primary expression and additional details
    primary_expression, detail_descriptors = analyze_facial_expression(image, face_data)
    
    # Combine all descriptors
    all_descriptors = [primary_expression] + detail_descriptors
    
    # Remove duplicates while preserving order
    seen = set()
    unique_descriptors = []
    for desc in all_descriptors:
        if desc not in seen:
            seen.add(desc)
            unique_descriptors.append(desc)
    
    return unique_descriptors if unique_descriptors else ['neutral']

def generate_lora_filename(keyword, file_counter, face_data, target_width, target_height, image=None):
    """
    Simple sequential numbering for LoRA training.
    Format: keyword_0001.png, keyword_0002.png, etc.
    """
    # Simple 4-digit sequential numbering
    filename = f"{keyword}_{file_counter:04d}.png"
    return filename

def determine_descriptor(face_data, target_width, target_height):
    """Fallback descriptor determination (simplified version)"""
    if not face_data:
        return 'neutral'
    
    # Check face angle
    angle = face_data.get('angle', 'frontal')
    if angle == 'profile':
        return 'profile'
    
    # Check if it's a portrait or closeup based on aspect ratio
    if target_height > target_width:
        return 'portrait'
    else:
        return 'closeup'
    
    return 'neutral'

def smart_crop_face(image, target_width, target_height, verbose=True):
    """Crop image focusing on detected face with generous padding to avoid cutting faces"""
    img_array = np.array(image)
    height, width = img_array.shape[:2]
    
    # Step 1: Try full face detection
    face_data = detect_face(img_array)
    
    # Step 2: If no full face, try detecting individual facial features
    if face_data is None:
        face_data = detect_facial_features(img_array)
        if face_data is not None and verbose:
            print(f"  ✓ Facial features detected (eyes/nose/mouth) - cropping around features")
    
    if face_data is not None:
        face = face_data['box']
        angle = face_data['angle']
        x, y, w, h = face
        
        # Calculate center of face
        face_center_x = x + w // 2
        face_center_y = y + h // 2
        
        # MUCH MORE GENEROUS PADDING to avoid cutting faces
        # This ensures we get the whole head, hair, and shoulders
        if angle == 'profile':
            # Profile view - need more horizontal space
            padding_h = 3.0  # Very generous
            padding_v = 2.5
        elif angle == 'tilted':
            # Tilted - symmetric generous padding
            padding_h = 2.8
            padding_v = 2.8
        else:  # frontal or 3/4
            # Front view - include full head, hair, shoulders
            padding_h = 2.5 if target_height > target_width else 2.2
            padding_v = 3.0 if target_height > target_width else 2.5
        
        crop_width = int(w * padding_h)
        crop_height = int(h * padding_v)
        
        # Adjust to target aspect ratio
        aspect_ratio = target_width / target_height
        if crop_width / crop_height > aspect_ratio:
            crop_height = int(crop_width / aspect_ratio)
        else:
            crop_width = int(crop_height * aspect_ratio)
        
        # For portrait shots, shift crop up to include more hair/top of head
        if target_height > target_width:
            # Shift up by 15% of face height to get more hair
            face_center_y = int(face_center_y - h * 0.15)
        else:
            # Square crops - slight shift up
            face_center_y = int(face_center_y - h * 0.05)
        
        # Calculate crop boundaries with maximum area
        left = face_center_x - crop_width // 2
        top = face_center_y - crop_height // 2
        right = left + crop_width
        bottom = top + crop_height
        
        # Adjust if crop goes out of bounds - prefer keeping the face fully visible
        if left < 0:
            left = 0
            right = min(width, crop_width)
        if right > width:
            right = width
            left = max(0, width - crop_width)
        if top < 0:
            top = 0
            bottom = min(height, crop_height)
        if bottom > height:
            bottom = height
            top = max(0, height - crop_height)
        
        # Ensure we have some crop area
        if right <= left or bottom <= top:
            # Fall back to center crop
            left, top, right, bottom = 0, 0, width, height
        
        cropped = image.crop((left, top, right, bottom))
        if verbose:
            confidence = face_data.get('confidence', 'full_face')
            if confidence == 'features_based':
                print(f"  ✓ Facial features detected - cropped around features")
            else:
                print(f"  ✓ Face detected ({angle} view) - generous crop with full context")
    else:
        # NO FACE OR FACIAL FEATURES DETECTED
        # For LoRA training, this image is NOT suitable
        # Still process it but it will go to rejections folder
        # Just do a simple center crop (but it's marked as rejected)
        aspect_ratio = target_width / target_height
        current_ratio = width / height
        
        if current_ratio > aspect_ratio:
            # Image is wider, crop width from center
            new_width = int(height * aspect_ratio)
            left = (width - new_width) // 2
            cropped = image.crop((left, 0, left + new_width, height))
        else:
            # Image is taller, crop height from center
            new_height = int(width / aspect_ratio)
            top = (height - new_height) // 2
            cropped = image.crop((0, top, width, top + new_height))
        
        if verbose:
            print(f"  ❌ NO FACE OR FACIAL FEATURES - Not suitable for LoRA training")
    
    return cropped, face_data

def upscale_image(image, target_width, target_height):
    """Upscale image to target size using Lanczos resampling"""
    return image.resize((target_width, target_height), Image.Resampling.LANCZOS)

def process_single_image(image_path, output_dir, filename, verbose=True, skip_quality_check=False, output_sizes='both', file_counter=None, keyword=None, rejections_dir=None, caption=None):
    """Process a single image with specified output sizes"""
    try:
        if verbose:
            print(f"Processing: {filename}")
        
        # Open image
        img = Image.open(image_path).convert('RGB')
        if verbose:
            print(f"  Original size: {img.size[0]}x{img.size[1]}")
        
        # Quality check - but don't skip, just redirect to rejections folder
        quality_issues = []
        is_rejected = False
        if not skip_quality_check:
            quality = check_image_quality(img)
            if not quality['passed']:
                is_rejected = True
                quality_issues = quality['issues']
                if verbose:
                    print(f"  ⚠ Quality issues: {', '.join(quality['issues'])}")
                    print(f"  → Will save to rejections folder")
        
        # Use rejections directory if image has quality issues
        if is_rejected and rejections_dir:
            actual_output_dir = rejections_dir
        else:
            actual_output_dir = output_dir
        
        results = []
        face_angles = []
        base_name = Path(filename).stem
        
        # Define size options
        size_configs = {
            '512x512': (512, 512, 'square'),
            '512x768': (512, 768, 'portrait'),
            '1024x1024': (1024, 1024, 'large square')
        }
        
        # Determine which sizes to create
        if output_sizes == 'both':
            sizes_to_create = ['512x512', '512x768']
        else:
            sizes_to_create = [output_sizes]
        
        # Check for face detection (do this once before processing sizes)
        has_face = False
        test_crop, test_face_data = smart_crop_face(img, 512, 512, verbose=False)
        
        if test_face_data:
            # Face or facial features detected - crop in on it!
            # Even if face is small in original, cropping will make it large
            has_face = True
        
        # If NO face detected at all, mark as rejected
        if not has_face and not skip_quality_check:
            if not is_rejected:  # Don't override quality issues
                is_rejected = True
                quality_issues.append('no_face_detected')
                if verbose:
                    print(f"  ❌ NO FACE OR FACIAL FEATURES detected")
                    print(f"  → Will save to rejections folder (not suitable for LoRA)")
                # Update output directory
                if rejections_dir:
                    actual_output_dir = rejections_dir
        
        # Process each requested size
        for size_key in sizes_to_create:
            width, height, description = size_configs[size_key]
            
            if verbose:
                print(f"  Creating {width}x{height} version...")
            
            cropped, face_data = smart_crop_face(img, width, height, verbose)
            if face_data and not face_angles:  # Only record angle once
                face_angles.append(face_data['angle'])
            
            if cropped.size != (width, height):
                cropped = upscale_image(cropped, width, height)
            
            # Generate filename with LoRA-training compatible naming
            if keyword and file_counter is not None:
                # Use LoRA naming system with image analysis for descriptors
                output_filename = generate_lora_filename(
                    keyword, 
                    file_counter, 
                    face_data, 
                    width, 
                    height,
                    image=img  # Pass original image for analysis
                )
                
                # If multiple sizes, add size suffix to avoid overwriting
                if len(sizes_to_create) > 1:
                    # Insert size before extension
                    name_parts = output_filename.rsplit('.', 1)
                    output_filename = f"{name_parts[0]}_{width}x{height}.{name_parts[1]}"
            else:
                # Use original format (no keyword provided)
                output_filename = f"{base_name}_{width}x{height}.png"
            
            output_path = actual_output_dir / output_filename
            cropped.save(output_path, 'PNG', quality=95)
            results.append(output_filename)
            
            # Create caption file for LoRA training (same name, .txt extension)
            if caption:
                caption_filename = output_filename.replace('.png', '.txt')
                caption_path = actual_output_dir / caption_filename
                with open(caption_path, 'w', encoding='utf-8') as f:
                    f.write(caption)
            
            if verbose:
                print(f"  ✓ Saved: {output_filename}")
                if caption:
                    print(f"  ✓ Caption: {caption_filename}")
        
        return {
            'skipped': False,
            'files': results,
            'face_angle': face_angles[0] if face_angles else 'no_face',
            'is_rejected': is_rejected,
            'quality_issues': quality_issues
        }
    except Exception as e:
        print(f"  ✗ Error processing {filename}: {str(e)}")
        return {'skipped': True, 'reason': ['processing_error'], 'error': str(e)}

def process_zip_file(zip_path, output_dir=None, create_zip=True, verbose=True, skip_quality_check=False, output_sizes='both', keyword=None, caption=None):
    """Process all images in a ZIP file"""
    zip_path = Path(zip_path)
    
    if not zip_path.exists():
        print(f"❌ Error: ZIP file not found: {zip_path}")
        return False
    
    # Create output directory
    if output_dir is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Always create output in the 'output/' folder, not next to the input zip
        output_base = Path('output')
        output_base.mkdir(exist_ok=True, parents=True)
        output_dir = output_base / f"lora_processed_{timestamp}"
    else:
        output_dir = Path(output_dir)
    
    output_dir.mkdir(exist_ok=True, parents=True)
    
    # Create rejections subdirectory
    rejections_dir = output_dir / "rejections"
    rejections_dir.mkdir(exist_ok=True, parents=True)
    
    if verbose:
        print(f"\n🎨 LoRA Image Processor v{__version__}")
        print(f"=" * 60)
        print(f"Input ZIP: {zip_path}")
        print(f"Output folder: {output_dir}")
        if keyword:
            print(f"Naming pattern: {keyword}_001.png, {keyword}_002.png, ...")
        print(f"=" * 60)
    
    # Create temp extraction directory
    temp_dir = output_dir.parent / f"temp_extract_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    temp_dir.mkdir(exist_ok=True, parents=True)
    
    try:
        # Extract ZIP
        if verbose:
            print(f"\n📦 Extracting ZIP file...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        if verbose:
            print(f"✓ Extraction complete")
        
        # Find all image files (avoid duplicates by using a set)
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.webp'}
        image_files_set = set()
        for ext in image_extensions:
            # Check both lowercase and uppercase extensions
            for file in temp_dir.rglob(f'*{ext}'):
                image_files_set.add(file)
            for file in temp_dir.rglob(f'*{ext.upper()}'):
                image_files_set.add(file)
        
        # Convert set back to list and remove any duplicates
        image_files = sorted(list(image_files_set))
        
        if not image_files:
            print(f"\n❌ No image files found in ZIP!")
            return False
        
        if verbose:
            print(f"\n📸 Found {len(image_files)} images")
            print(f"\n" + "=" * 60)
        
        # Process each image and collect statistics
        processed_count = 0
        rejected_count = 0
        skipped_count = 0
        face_angles = []
        skipped_reasons = []
        no_face_detected = []
        file_counter = 1  # Start numbering from 001
        
        for i, img_path in enumerate(image_files, 1):
            if verbose:
                print(f"\n[{i}/{len(image_files)}]")
            
            # Pass counter and rejections_dir
            counter = file_counter if keyword else None
            result = process_single_image(img_path, output_dir, img_path.name, verbose, skip_quality_check, output_sizes, counter, keyword, rejections_dir, caption)
            
            if isinstance(result, dict):
                if result.get('skipped'):
                    skipped_count += 1
                    skipped_reasons.extend(result.get('reason', []))
                else:
                    num_files = len(result.get('files', []))
                    processed_count += num_files
                    
                    # Track if file was rejected (poor quality)
                    if result.get('is_rejected'):
                        rejected_count += 1
                    
                    # Increment counter by 1 for each input image (not per output file)
                    if keyword:
                        file_counter += 1
                    
                    face_angle = result.get('face_angle')
                    if face_angle and face_angle != 'no_face':
                        face_angles.append(face_angle)
                    elif face_angle == 'no_face':
                        no_face_detected.append(img_path.name)
            else:
                # Old return format compatibility
                processed_count += len(result) if result else 0
                if keyword:
                    file_counter += 1  # Increment once per input image
        
        if verbose:
            print(f"\n" + "=" * 60)
            print(f"✅ Processing Complete!")
            print(f"=" * 60)
            print(f"Input images: {len(image_files)}")
            print(f"Good quality: {len(image_files) - rejected_count - skipped_count}")
            print(f"Low quality (in rejections/): {rejected_count}")
            print(f"Skipped (errors): {skipped_count}")
            print(f"Output files: {processed_count}")
            print(f"Output location: {output_dir.absolute()}")
            
            if rejected_count > 0:
                print(f"\n⚠️  LOW QUALITY FILES (saved to rejections/):")
                print(f"=" * 60)
                print(f"  {rejected_count} images had quality issues but were still processed")
                print(f"  Check: {rejections_dir.absolute()}")
                print(f"\n  Common issues: blur, low contrast, poor lighting")
                print(f"  Tip: Review rejections folder and decide which to keep")
            
            # Quality report
            if skipped_count > 0:
                print(f"\n❌ SKIPPED FILES (processing errors):")
                print(f"=" * 60)
                reason_counts = {}
                for reason in skipped_reasons:
                    reason_counts[reason] = reason_counts.get(reason, 0) + 1
                for reason, count in sorted(reason_counts.items(), key=lambda x: x[1], reverse=True):
                    print(f"  • {count}x {reason}")
            
            # Face detection report
            if no_face_detected:
                print(f"\n⚠️  FACE DETECTION REPORT:")
                print(f"=" * 60)
                print(f"  {len(no_face_detected)} images had no face detected")
                print(f"  These were cropped using smart center crop instead.")
                if len(no_face_detected) <= 10:
                    print(f"\n  Files:")
                    for filename in no_face_detected:
                        print(f"    • {filename}")
                else:
                    print(f"\n  (Too many to list - check output visually)")
                print(f"\n  💡 Tip: These images might be:")
                print(f"     - Side/back views")
                print(f"     - Face too small")
                print(f"     - Poor lighting")
                print(f"     - Non-face subjects")
            
            # Variety analysis
            if face_angles:
                print(f"\n📊 DATASET VARIETY ANALYSIS:")
                print(f"=" * 60)
                angle_counts = {}
                for angle in face_angles:
                    angle_counts[angle] = angle_counts.get(angle, 0) + 1
                
                total_faces = len(face_angles)
                total_processed = len(image_files) - skipped_count
                print(f"  Faces detected: {total_faces}/{total_processed} images ({(total_faces/total_processed*100):.1f}%)")
                print(f"")
                
                for angle, count in sorted(angle_counts.items()):
                    percentage = (count / total_faces) * 100
                    print(f"  • {angle.capitalize()}: {count} images ({percentage:.1f}%)")
                
                # Variety score and recommendations
                variety_score = len(angle_counts)
                print(f"\n  Variety Score: {variety_score}/3")
                
                if variety_score == 1:
                    print(f"  ⚠️  LOW VARIETY - All images are {list(angle_counts.keys())[0]} view")
                    print(f"  💡 Add different angles for better model generalization")
                elif variety_score == 2:
                    print(f"  ✓ GOOD VARIETY - Two different angles detected")
                    print(f"  💡 Consider adding more variety for even better results")
                else:
                    print(f"  ✅ EXCELLENT VARIETY - Multiple angles detected!")
                    print(f"  💡 Great dataset for LoRA training!")
            
            print(f"\n💡 Each image was processed into:")
            print(f"   • 512×512 version (close-up faces)")
            print(f"   • 512×768 version (portrait shots)")
        
        # Create ZIP file for easy distribution
        if create_zip:
            if verbose:
                print(f"\n📦 Creating ZIP file for download...")
            zip_output = output_dir.parent / f"{output_dir.name}.zip"
            with zipfile.ZipFile(zip_output, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in output_dir.iterdir():
                    if file_path.is_file():
                        zipf.write(file_path, file_path.name)
            
            if verbose:
                print(f"✅ ZIP created: {zip_output.absolute()}")
                print(f"\n" + "=" * 60)
                print(f"📥 YOUR IMAGES ARE READY:")
                print(f"=" * 60)
                print(f"Folder: {output_dir.absolute()}")
                print(f"ZIP file: {zip_output.absolute()}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return False
    finally:
        # Cleanup temp directory
        shutil.rmtree(temp_dir, ignore_errors=True)

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='LoRA Image Processor - Process images for Stable Diffusion LoRA training',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python lora_image_processor.py (looks for input/input.zip)
  python lora_image_processor.py my_photos.zip
  python lora_image_processor.py input.zip -o ./output

For more info: https://github.com/yourusername/lora-image-processor
        """
    )
    
    parser.add_argument('input_zip', nargs='?', default='input/input.zip', help='Path to input ZIP file (default: input/input.zip)')
    parser.add_argument('-o', '--output', help='Output directory (default: auto-generated)', default=None)
    parser.add_argument('--keyword', help='Keyword for renaming files (e.g., "MyDaughter"). If not provided, will prompt.', default=None)
    parser.add_argument('--sizes', help='Output sizes: "512x512" (default), "512x768", "1024x1024", or "both"', 
                        default='512x512', choices=['both', '512x512', '512x768', '1024x1024'])
    parser.add_argument('--no-zip', action='store_true', help='Do not create output ZIP file')
    parser.add_argument('--skip-quality-check', action='store_true', help='Skip quality filtering (process all images)')
    parser.add_argument('-q', '--quiet', action='store_true', help='Quiet mode (minimal output)')
    parser.add_argument('-v', '--version', action='version', version=f'%(prog)s {__version__}')
    
    args = parser.parse_args()
    
    # Get keyword for file naming FIRST
    keyword = args.keyword
    if not args.quiet and not keyword:
        print("\n" + "=" * 60)
        print("  KEYWORD FOR FILE NAMING")
        print("=" * 60)
        print("\nFor LoRA training, all images should have consistent names")
        print("with your concept keyword (e.g., 'MyDaughter', 'AlexSmith').")
        print("\nFiles will be renamed to: [keyword]_001.png, [keyword]_002.png, etc.")
        print("\nPress Enter to skip and use original filenames.")
        keyword = input("\nEnter keyword: ").strip()
        if keyword:
            # Clean keyword (remove spaces, special chars)
            keyword = "".join(c for c in keyword if c.isalnum() or c in ('_', '-'))
            if not keyword:
                keyword = None
    
    # Get output size selection - ALWAYS ASK if not in quiet mode
    output_sizes = args.sizes
    if not args.quiet:
        print("\n" + "=" * 60)
        print("  CHOOSE OUTPUT SIZE")
        print("=" * 60)
        print("\nOptions:")
        print("  1. Only 512x512 (recommended - close-up faces)")
        print("  2. Only 512x768 (portraits)")
        print("  3. Only 1024x1024 (SDXL training)")
        print("  4. Both 512x512 AND 512x768 (creates 2 files per photo)")
        print("\nPress Enter for option 1 (recommended)")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == '2':
            output_sizes = '512x768'
        elif choice == '3':
            output_sizes = '1024x1024'
        elif choice == '4':
            output_sizes = 'both'
        else:
            output_sizes = '512x512'  # Default for 1 or Enter
    
    # Process the images
    success = process_zip_file(
        args.input_zip,
        args.output,
        create_zip=not args.no_zip,
        verbose=not args.quiet,
        skip_quality_check=args.skip_quality_check,
        output_sizes=output_sizes,
        keyword=keyword
    )
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
