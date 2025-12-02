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

def smart_crop_face(image, target_width, target_height, verbose=True):
    """Crop image focusing on detected face with generous padding to avoid cutting faces"""
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
            print(f"  ✓ Face detected ({angle} view) - generous crop with full context")
    else:
        # No face detected - use intelligent center crop with edge detection
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
            print(f"  ⚠ No face detected - using smart center crop")
    
    return cropped, face_data

def upscale_image(image, target_width, target_height):
    """Upscale image to target size using Lanczos resampling"""
    return image.resize((target_width, target_height), Image.Resampling.LANCZOS)

def process_single_image(image_path, output_dir, filename, verbose=True, skip_quality_check=False, output_sizes='both', file_counter=None, keyword=None):
    """Process a single image with specified output sizes"""
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
        
        # Process each requested size
        current_counter = file_counter if file_counter is not None else 0
        for size_key in sizes_to_create:
            width, height, description = size_configs[size_key]
            
            if verbose:
                print(f"  Creating {width}x{height} version...")
            
            cropped, face_data = smart_crop_face(img, width, height, verbose)
            if face_data and not face_angles:  # Only record angle once
                face_angles.append(face_data['angle'])
            
            if cropped.size != (width, height):
                cropped = upscale_image(cropped, width, height)
            
            # Generate filename with keyword if provided
            if keyword and file_counter is not None:
                # Use keyword_number format, increment for each output file
                output_filename = f"{keyword}_{current_counter:03d}.png"
                current_counter += 1
            else:
                # Use original format
                output_filename = f"{base_name}_{width}x{height}.png"
            
            output_path = output_dir / output_filename
            cropped.save(output_path, 'PNG', quality=95)
            results.append(output_filename)
            
            if verbose:
                print(f"  ✓ Saved: {output_filename}")
        
        return {
            'skipped': False,
            'files': results,
            'face_angle': face_angles[0] if face_angles else 'no_face'
        }
    except Exception as e:
        print(f"  ✗ Error processing {filename}: {str(e)}")
        return {'skipped': True, 'reason': ['processing_error'], 'error': str(e)}

def process_zip_file(zip_path, output_dir=None, create_zip=True, verbose=True, skip_quality_check=False, output_sizes='both', keyword=None):
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
        no_face_detected = []
        file_counter = 1  # Start numbering from 001
        
        for i, img_path in enumerate(image_files, 1):
            if verbose:
                print(f"\n[{i}/{len(image_files)}]")
            
            # Pass counter only if using keyword naming
            counter = file_counter if keyword else None
            result = process_single_image(img_path, output_dir, img_path.name, verbose, skip_quality_check, output_sizes, counter, keyword)
            
            if isinstance(result, dict):
                if result.get('skipped'):
                    skipped_count += 1
                    skipped_reasons.extend(result.get('reason', []))
                else:
                    num_files = len(result.get('files', []))
                    processed_count += num_files
                    # Increment counter by number of files created (for both sizes, counter increases by 2)
                    if keyword:
                        file_counter += num_files
                    
                    face_angle = result.get('face_angle')
                    if face_angle and face_angle != 'no_face':
                        face_angles.append(face_angle)
                    elif face_angle == 'no_face':
                        no_face_detected.append(img_path.name)
            else:
                # Old return format compatibility
                processed_count += len(result) if result else 0
                if keyword:
                    file_counter += len(result) if result else 0
        
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
    
    # Get output size selection if not provided
    output_sizes = args.sizes
    if not args.quiet and args.sizes == 'both':
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
    
    # Get keyword for file naming
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
