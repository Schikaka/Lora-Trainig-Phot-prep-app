# LoRA Image Processor - Python Script

A simple, reliable Python script to process images for Stable Diffusion LoRA training. No web browser, no download issues - just works!

## Features

✨ **Face Detection** - Automatically detects and centers faces
✂️ **Smart Cropping** - Intelligent cropping with face centering or center crop fallback  
📐 **Dual Outputs** - Creates both 512×512 (close-up) and 512×768 (portrait) versions
🚀 **High-Quality** - Lanczos upscaling for superior image quality
📦 **Batch Processing** - Process entire ZIP files at once

## Requirements

Already installed:
- Python 3.11+
- Pillow (PIL)
- OpenCV (cv2)
- NumPy

## Usage

### Basic Usage

```bash
python3 /app/process_lora_images.py your_images.zip
```

This will:
1. Extract images from ZIP
2. Process each image (face detection + cropping + upscaling)
3. Create output folder `lora_processed_YYYYMMDD_HHMMSS`
4. Save all processed images there

### Specify Output Folder

```bash
python3 /app/process_lora_images.py your_images.zip /path/to/output
```

## Example

```bash
# Upload your ZIP file to /tmp/
# Then run:
cd /tmp
python3 /app/process_lora_images.py my_training_photos.zip

# Output will be in: /tmp/lora_processed_20251202_123456/
```

## Output Format

For each input image (e.g., `photo.jpg`), you get:
- `photo_512x512.png` - Square format for close-up face training
- `photo_512x768.png` - Portrait format for full-body training

## Supported Input Formats

- JPEG (.jpg, .jpeg)
- PNG (.png)
- BMP (.bmp)
- WebP (.webp)

## Example Output

```
🎨 LoRA Image Processor
============================================================
Input ZIP: my_photos.zip
Output folder: lora_processed_20251202_181058
============================================================

📦 Extracting ZIP file...
✓ Extraction complete

📸 Found 26 images

============================================================

[1/26]
Processing: IMG_001.jpg
  Original size: 1920x1080
  Creating 512x512 version...
  ✓ Face detected and centered
  ✓ Saved: IMG_001_512x512.png
  Creating 512x768 version...
  ✓ Face detected and centered
  ✓ Saved: IMG_001_512x768.png

...

============================================================
✅ Processing Complete!
============================================================
Input images: 26
Output files: 52
Output location: /tmp/lora_processed_20251202_181058

💡 Each image was processed into:
   • 512×512 version (close-up faces)
   • 512×768 version (portrait shots)
```

## How It Works

1. **Extract ZIP** - Extracts all images to temporary folder
2. **Find Images** - Recursively finds all image files
3. **For Each Image:**
   - Open and convert to RGB
   - Detect face using OpenCV Haar Cascade
   - Crop with face centered (or center crop if no face)
   - Generate 512×512 version
   - Generate 512×768 version
   - Save as high-quality PNG
4. **Cleanup** - Removes temporary files
5. **Done!** - All processed images in output folder

## Tips

- Upload your ZIP to `/tmp/` folder for processing
- Output images are PNG format for best quality
- Face detection works best with clear, frontal faces
- If no face detected, uses smart center cropping
- Processing time: ~1-2 seconds per image

## No Browser Issues!

✅ No JavaScript errors
✅ No download problems  
✅ No CORS issues
✅ Works offline
✅ Simple and reliable
✅ Direct file access

## Questions?

The script is self-contained in `/app/process_lora_images.py`

Run without arguments to see help:
```bash
python3 /app/process_lora_images.py
```
