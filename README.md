# LoRA Image Processor

A web application for preparing images for Stable Diffusion LoRA training. Automatically detects faces, crops intelligently, and generates optimal resolution outputs.

## Quick Start

1. **Access the Application**
   - Open your browser and navigate to the application URL
   - You'll see the LoRA Image Processor interface

2. **Upload Your Images**
   - Prepare a ZIP file containing your training images (JPG, PNG, BMP, WebP)
   - Drag and drop the ZIP file or click "Choose a ZIP file"

3. **Process Images**
   - Click "🎨 Process Images" button
   - Wait for processing to complete

4. **Download Results**
   - Download the processed ZIP file
   - Each image will have two versions: 512×512 and 512×768

## Features

- 🎯 **Face Detection**: Automatically detects faces using OpenCV
- ✂️ **Smart Cropping**: Centers on faces with intelligent padding
- 📐 **Dual Outputs**: 512×512 (close-up) & 512×768 (portrait)
- 🚀 **High-Quality Upscaling**: Lanczos resampling
- 📦 **Batch Processing**: Process multiple images at once

## Technical Stack

- **Backend**: FastAPI + Python
- **Frontend**: React + Tailwind CSS
- **Image Processing**: OpenCV + Pillow
- **Database**: MongoDB

For detailed usage instructions, see [USAGE_GUIDE.md](USAGE_GUIDE.md)
