# LoRA Image Processor - Standalone Script

Process images for Stable Diffusion LoRA training on YOUR computer. No web interface, no browser issues!

## 🚀 Quick Start

### 1. Download the Files

Download these 2 files to your computer:
- `lora_image_processor_standalone.py` (the script)
- `requirements.txt` (dependencies)

### 2. Install Python

**Windows:**
- Download from https://www.python.org/downloads/
- Install and check "Add Python to PATH"

**Mac:**
```bash
brew install python3
```

**Linux:**
```bash
sudo apt install python3 python3-pip
```

### 3. Install Dependencies

Open terminal/command prompt in the folder where you downloaded the files:

```bash
pip install -r requirements.txt
```

Or manually:
```bash
pip install pillow opencv-python numpy
```

### 4. Run the Script

```bash
python lora_image_processor_standalone.py your_images.zip
```

That's it! Your processed images will be in a new folder + ZIP file.

## 📖 Usage Examples

### Basic Usage
```bash
python lora_image_processor_standalone.py photos.zip
```
Creates: `lora_processed_YYYYMMDD_HHMMSS/` folder and ZIP

### Specify Output Folder
```bash
python lora_image_processor_standalone.py photos.zip -o my_output
```
Creates: `my_output/` folder and `my_output.zip`

### Quiet Mode (Less Output)
```bash
python lora_image_processor_standalone.py photos.zip -q
```

### Skip ZIP Creation (Folder Only)
```bash
python lora_image_processor_standalone.py photos.zip --no-zip
```

### Help
```bash
python lora_image_processor_standalone.py --help
```

## ✨ Features

- ✅ **Face Detection** - Automatically finds and centers faces
- ✅ **Smart Cropping** - Falls back to center crop if no face
- ✅ **Dual Outputs** - 512×512 (close-up) & 512×768 (portrait)
- ✅ **High Quality** - Lanczos upscaling
- ✅ **Batch Processing** - Process entire ZIP files
- ✅ **Cross-Platform** - Works on Windows, Mac, Linux

## 📁 Input Format

- **ZIP file** containing your images
- Supported formats: JPG, JPEG, PNG, BMP, WebP
- Any folder structure inside ZIP (recursively searches)

## 📤 Output

For each input image (e.g., `photo.jpg`):
- `photo_512x512.png` - Square format for close-up training
- `photo_512x768.png` - Portrait format for full-body training

Plus:
- Output folder with all images
- ZIP file ready to use for training

## 🔧 Troubleshooting

### "No module named 'cv2'"
```bash
pip install opencv-python
```

### "No module named 'PIL'"
```bash
pip install pillow
```

### "command not found: python"
Try `python3` instead:
```bash
python3 lora_image_processor_standalone.py photos.zip
```

### Script runs but no output
- Check the ZIP file isn't corrupted
- Ensure ZIP contains image files
- Try with `-q` removed to see detailed output

## 💡 Tips

1. **Better Results**: Use high-quality input images (1024px+)
2. **Face Training**: Include variety of angles/expressions
3. **Batch Size**: Process 15-30 images at a time
4. **File Size**: Each output PNG is typically 20-50KB

## 📋 System Requirements

- Python 3.7 or higher
- ~200MB free space per 50 images
- Works offline (no internet needed after install)

## 🎯 Perfect For

- Stable Diffusion LoRA training
- Character/face model training
- Portrait dataset preparation
- Image preprocessing pipelines

## 📝 License

MIT License - Free to use for personal and commercial projects

## 🐛 Issues?

If something doesn't work:
1. Check you installed all dependencies
2. Verify Python version: `python --version` (should be 3.7+)
3. Test with a small ZIP file first (2-3 images)
4. Run without `-q` flag to see detailed errors

## 🎉 That's It!

No web server, no browser issues, just a simple script that works on YOUR computer.

---

**Made with ❤️ for the Stable Diffusion community**
