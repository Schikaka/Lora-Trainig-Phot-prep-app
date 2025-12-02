#!/usr/bin/env python3
"""
LoRA Image Processor - Standalone Script
For Stable Diffusion LoRA Training

Author: AI Assistant
Version: 1.0
License: MIT

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

def detect_face(image_np):
    """Detect face in image and return coordinates with angle estimation"""
    if FACE_CASCADE is None:
        return None
        
    gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
    faces = FACE_CASCADE.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    
    if len(faces) > 0:
        # Return largest face
        largest_face = max(faces, key=lambda f: f[2] * f[3])
        x, y, w, h = largest_face
        
        # Estimate face angle by aspect ratio (rough approximation)
        aspect = w / h
        if aspect > 1.2:
            angle = 'profile'  # Side view (wider than tall)
        elif aspect < 0.9:
            angle = 'tilted'   # Head tilt
        else:
            angle = 'frontal'  # Front or 3/4 view
        
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

def smart_crop_face(image, target_width, target_height, verbose=True):
    """Crop image focusing on detected face with intelligent padding based on angle"""
    img_array = np.array(image)
    height, width = img_array.shape[:2]
    
    # Detect face
    face_data = detect_face(img_array)
    
    if face_data is not None:
        face = face_data['box']
        angle = face_data['angle']
        x, y, w, h = face
        
        # Calculate center of face
        face_center_x = x + w // 2
        face_center_y = y + h // 2
        
        # Adjust padding based on face angle for better context
        if angle == 'profile':
            # Profile view - include more horizontal space, less vertical
            padding_h = 2.2
            padding_v = 1.6
        elif angle == 'tilted':
            # Tilted - symmetric padding
            padding_h = 1.8
            padding_v = 1.8
        else:  # frontal or 3/4
            # Front view - include shoulders and hair
            padding_h = 1.8 if target_height > target_width else 1.5
            padding_v = 2.0 if target_height > target_width else 1.5
        
        crop_width = int(w * padding_h)
        crop_height = int(h * padding_v)
        
        # Adjust to target aspect ratio
        aspect_ratio = target_width / target_height
        if crop_width / crop_height > aspect_ratio:
            crop_height = int(crop_width / aspect_ratio)
        else:
            crop_width = int(crop_height * aspect_ratio)
        
        # For portrait shots, shift crop slightly up to include more head/hair
        if target_height > target_width:
            face_center_y = int(face_center_y - h * 0.1)
        
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
        if verbose:
            print(f"  ✓ Face detected ({angle} view) - intelligent crop applied")
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
        if verbose:
            print(f"  ✓ Center cropped (no face detected)")
    
    return cropped, face_data

def upscale_image(image, target_width, target_height):
    """Upscale image to target size using Lanczos resampling"""
    return image.resize((target_width, target_height), Image.Resampling.LANCZOS)

def process_single_image(image_path, output_dir, filename, verbose=True, skip_quality_check=False):
    """Process a single image to create both 512x512 and 512x768 versions"""
    try:
        if verbose:
            print(f"Processing: {filename}")
        
        # Open image
        img = Image.open(image_path).convert('RGB')
        if verbose:
            print(f"  Original size: {img.size[0]}x{img.size[1]}")
        
        # Quality check
        if not skip_quality_check:
            quality = check_image_quality(img)
            if not quality['passed']:
                if verbose:
                    print(f"  ⚠ Quality issues: {', '.join(quality['issues'])}")
                    print(f"  ✗ Skipped (poor quality)")
                return {'skipped': True, 'reason': quality['issues'], 'quality': quality}
        
        results = []
        face_angles = []
        
        # Process for 512x512 (close-up face)
        if verbose:
            print(f"  Creating 512x512 version...")
        cropped_square, face_data = smart_crop_face(img, 512, 512, verbose)
        if face_data:
            face_angles.append(face_data['angle'])
        if cropped_square.size != (512, 512):
            cropped_square = upscale_image(cropped_square, 512, 512)
        
        # Save 512x512 version
        base_name = Path(filename).stem
        square_filename = f"{base_name}_512x512.png"
        square_path = output_dir / square_filename
        cropped_square.save(square_path, 'PNG', quality=95)
        results.append(square_filename)
        if verbose:
            print(f"  ✓ Saved: {square_filename}")
        
        # Process for 512x768 (portrait)
        if verbose:
            print(f"  Creating 512x768 version...")
        cropped_portrait, _ = smart_crop_face(img, 512, 768, verbose)
        if cropped_portrait.size != (512, 768):
            cropped_portrait = upscale_image(cropped_portrait, 512, 768)
        
        # Save 512x768 version
        portrait_filename = f"{base_name}_512x768.png"
        portrait_path = output_dir / portrait_filename
        cropped_portrait.save(portrait_path, 'PNG', quality=95)
        results.append(portrait_filename)
        if verbose:
            print(f"  ✓ Saved: {portrait_filename}")
        
        return {
            'skipped': False,
            'files': results,
            'face_angle': face_angles[0] if face_angles else 'no_face'
        }
    except Exception as e:
        print(f"  ✗ Error processing {filename}: {str(e)}")
        return {'skipped': True, 'reason': ['processing_error'], 'error': str(e)}

def process_zip_file(zip_path, output_dir=None, create_zip=True, verbose=True):
    """Process all images in a ZIP file"""
    zip_path = Path(zip_path)
    
    if not zip_path.exists():
        print(f"❌ Error: ZIP file not found: {zip_path}")
        return False
    
    # Create output directory
    if output_dir is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = zip_path.parent / f"lora_processed_{timestamp}"
    else:
        output_dir = Path(output_dir)
    
    output_dir.mkdir(exist_ok=True, parents=True)
    
    if verbose:
        print(f"\n🎨 LoRA Image Processor v{__version__}")
        print(f"=" * 60)
        print(f"Input ZIP: {zip_path}")
        print(f"Output folder: {output_dir}")
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
        
        # Find all image files
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.webp'}
        image_files = []
        for ext in image_extensions:
            image_files.extend(temp_dir.rglob(f'*{ext}'))
            image_files.extend(temp_dir.rglob(f'*{ext.upper()}'))
        
        if not image_files:
            print(f"\n❌ No image files found in ZIP!")
            return False
        
        if verbose:
            print(f"\n📸 Found {len(image_files)} images")
            print(f"\n" + "=" * 60)
        
        # Process each image and collect statistics
        processed_count = 0
        skipped_count = 0
        face_angles = []
        skipped_reasons = []
        
        for i, img_path in enumerate(image_files, 1):
            if verbose:
                print(f"\n[{i}/{len(image_files)}]")
            result = process_single_image(img_path, output_dir, img_path.name, verbose)
            
            if isinstance(result, dict):
                if result.get('skipped'):
                    skipped_count += 1
                    skipped_reasons.extend(result.get('reason', []))
                else:
                    processed_count += len(result.get('files', []))
                    if result.get('face_angle'):
                        face_angles.append(result['face_angle'])
            else:
                # Old return format compatibility
                processed_count += len(result) if result else 0
        
        if verbose:
            print(f"\n" + "=" * 60)
            print(f"✅ Processing Complete!")
            print(f"=" * 60)
            print(f"Input images: {len(image_files)}")
            print(f"Processed: {len(image_files) - skipped_count}")
            print(f"Skipped: {skipped_count}")
            print(f"Output files: {processed_count}")
            print(f"Output location: {output_dir.absolute()}")
            
            # Quality report
            if skipped_count > 0:
                print(f"\n⚠️  QUALITY REPORT:")
                print(f"=" * 60)
                reason_counts = {}
                for reason in skipped_reasons:
                    reason_counts[reason] = reason_counts.get(reason, 0) + 1
                for reason, count in sorted(reason_counts.items(), key=lambda x: x[1], reverse=True):
                    print(f"  • {count}x {reason}")
                print(f"\nTip: Use better lighting and sharper images for best LoRA results")
            
            # Variety analysis
            if face_angles:
                print(f"\n📊 DATASET VARIETY ANALYSIS:")
                print(f"=" * 60)
                angle_counts = {}
                for angle in face_angles:
                    angle_counts[angle] = angle_counts.get(angle, 0) + 1
                
                total_faces = len(face_angles)
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
  python lora_image_processor.py input.zip
  python lora_image_processor.py input.zip -o ./output
  python lora_image_processor.py input.zip --no-zip
  python lora_image_processor.py input.zip -q

For more info: https://github.com/yourusername/lora-image-processor
        """
    )
    
    parser.add_argument('input_zip', help='Path to input ZIP file containing images')
    parser.add_argument('-o', '--output', help='Output directory (default: auto-generated)', default=None)
    parser.add_argument('--no-zip', action='store_true', help='Do not create output ZIP file')
    parser.add_argument('--skip-quality-check', action='store_true', help='Skip quality filtering (process all images)')
    parser.add_argument('-q', '--quiet', action='store_true', help='Quiet mode (minimal output)')
    parser.add_argument('-v', '--version', action='version', version=f'%(prog)s {__version__}')
    
    args = parser.parse_args()
    
    # Process the images
    success = process_zip_file(
        args.input_zip,
        args.output,
        create_zip=not args.no_zip,
        verbose=not args.quiet
    )
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
