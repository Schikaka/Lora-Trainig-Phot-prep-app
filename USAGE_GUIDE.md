# LoRA Image Processor - Usage Guide

## Overview
This application processes images from a ZIP file to prepare them for Stable Diffusion LoRA training. It automatically detects faces, crops intelligently, and generates optimal resolution outputs.

## Features
- 🎯 **Face Detection**: Automatically detects faces using OpenCV Haar Cascade
- ✂️ **Smart Cropping**: Centers on detected faces with appropriate padding, falls back to center crop if no face found
- 📐 **Dual Output Formats**:
  - 512×512 pixels - Perfect for close-up face training
  - 512×768 pixels - Ideal for portrait shots
- 🚀 **High-Quality Upscaling**: Uses Lanczos resampling for superior quality
- 📦 **Batch Processing**: Processes all images in your ZIP file at once

## How to Use

### Step 1: Prepare Your Images
1. Collect all your training images (JPG, PNG, BMP, WebP formats supported)
2. Create a ZIP file containing all images
3. No specific folder structure required - the app will find all images recursively

### Step 2: Upload and Process
1. Open the application in your browser
2. Either:
   - Click "Choose a ZIP file" to select your file
   - Drag and drop your ZIP file onto the upload area
3. Click "🎨 Process Images" button
4. Wait for processing to complete (time depends on number and size of images)

### Step 3: Download Results
1. Once processing is complete, you'll see statistics:
   - Number of input images processed
   - Total output files generated (2x input due to dual formats)
2. Click "📥 Download Processed Images" to download your processed ZIP file
3. Extract the ZIP to access your training images

### Output File Naming
For each input image (e.g., `photo.jpg`), you'll get:
- `photo_512x512.png` - Square format for close-up training
- `photo_512x768.png` - Portrait format for full-body training

## Technical Details

### Face Detection
- Uses OpenCV Haar Cascade classifier
- Detects frontal faces automatically
- Adjusts crop area based on face position and size
- Includes intelligent padding (1.8x for square, 1.5x for portrait)

### Cropping Logic
1. If face detected: Centers crop on face with padding
2. If no face: Performs smart center crop maintaining aspect ratio
3. Handles edge cases (face near borders, multiple faces)

### Upscaling
- Uses Lanczos resampling for high quality
- Only upscales if source image is smaller than target
- Preserves image quality during resize operations

### Supported Input Formats
- JPEG (.jpg, .jpeg)
- PNG (.png)
- BMP (.bmp)
- WebP (.webp)

### Output Format
- All outputs saved as PNG with 95% quality
- Maintains color accuracy and detail
- Optimized for LoRA training requirements

## Tips for Best Results

1. **Image Quality**: Use high-quality source images (1024px+ recommended)
2. **Variety**: Include different angles and expressions
3. **Consistency**: Similar lighting and backgrounds work better
4. **Quantity**: 15-30 images typically sufficient for good LoRA training
5. **Face Visibility**: Ensure faces are clearly visible and not obscured

## Troubleshooting

**"No valid image files found in ZIP"**
- Ensure your ZIP contains image files (.jpg, .png, etc.)
- Check that images aren't in unsupported formats

**Processing takes too long**
- Large ZIP files (>100MB) may take several minutes
- Consider processing in smaller batches

**Output images look wrong**
- Verify source images have good quality
- Check that faces are clearly visible in source images
- Some artistic or heavily filtered images may not detect faces correctly

## Architecture

### Backend (FastAPI)
- `/api/process-images` - Handles upload and processing
- `/api/download/{session_id}` - Serves processed files
- `/api/cleanup/{session_id}` - Removes temporary files

### Frontend (React)
- Modern UI with drag-and-drop
- Real-time progress indication
- Responsive design for all devices

### Processing Pipeline
1. Upload ZIP → 2. Extract files → 3. Detect faces → 4. Crop images → 5. Upscale → 6. Generate output ZIP → 7. Download

---

**Enjoy preparing your images for LoRA training! 🎨✨**
