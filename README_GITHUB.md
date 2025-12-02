# 🎨 LoRA Image Processor

**Professional image preparation tool for Stable Diffusion LoRA training**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)](https://github.com/yourusername/lora-image-processor)

## 🎉 100% Free & Open Source

No registration, no hidden costs, use freely for personal or commercial projects!

---

## ✨ Features

- 🎯 **Automatic Face Detection** - Intelligent cropping with face centering
- ✂️ **Smart Cropping** - Context-aware padding based on face angle  
- 📐 **Dual Output Sizes** - 512×512 (close-up) & 512×768 (portrait)
- ✅ **Quality Filtering** - Auto-removes blurry/poorly lit images
- 📊 **Variety Analysis** - Dataset composition scoring
- 🚀 **High-Quality Upscaling** - Lanczos resampling
- 📦 **Batch Processing** - Process entire ZIP files at once

## 🚀 Quick Start

### For Beginners (One-Click)

**Windows:**
```cmd
1. Download all files
2. Install Python from python.org
3. Double-click run_windows.bat
4. Done!
```

**Mac/Linux:**
```bash
1. Download all files
2. Install: brew install python3
3. Double-click run_mac_linux.sh  
4. Done!
```

### For Developers (Command Line)

```bash
# Install dependencies
pip install -r requirements.txt

# Process images
python lora_image_processor_standalone.py your_photos.zip

# With custom output
python lora_image_processor_standalone.py photos.zip -o output_folder

# Skip quality filtering
python lora_image_processor_standalone.py photos.zip --skip-quality-check
```

## 📋 Requirements

- Python 3.7 or higher
- Dependencies (auto-installed):
  - Pillow ≥10.0.0
  - OpenCV ≥4.8.0
  - NumPy ≥1.24.0

## 💡 What It Does

Takes your photos and automatically:

1. ✅ Extracts images from ZIP file
2. ✅ Detects faces and analyzes angles
3. ✅ Filters out blurry/poor quality images
4. ✅ Crops intelligently with face centering
5. ✅ Creates 512×512 and 512×768 versions
6. ✅ Upscales with high quality
7. ✅ Analyzes dataset variety
8. ✅ Packages everything into output ZIP

**Result:** Professional training images ready for LoRA!

## 📖 Documentation

- **START_HERE.txt** - First time? Read this!
- **QUICK_START.txt** - Copy-paste commands
- **BEGINNER_GUIDE.md** - Complete walkthrough
- **README_IMPROVED.md** - Technical details
- **FREEWARE_INFO.txt** - License explained

## 🎯 Example Output

```
🎨 LoRA Image Processor v1.0.0
============================================================

📸 Found 26 images

Processing: photo1.jpg
  ✓ Face detected (frontal view) - intelligent crop applied
  ✓ Saved: photo1_512x512.png
  ✓ Saved: photo1_512x768.png

...

✅ Processing Complete!
============================================================
Input images: 26
Processed: 23
Skipped: 3 (poor quality)

📊 DATASET VARIETY ANALYSIS:
  • Frontal: 13 images (56.5%)
  • Profile: 6 images (26.1%)
  • Tilted: 4 images (17.4%)
  
  Variety Score: 3/3
  ✅ EXCELLENT VARIETY!

📥 YOUR IMAGES ARE READY:
ZIP file: lora_processed_20251202_123456.zip
```

## 🔧 Command-Line Options

```bash
usage: lora_image_processor_standalone.py [-h] [-o OUTPUT] [--no-zip]
                                          [--skip-quality-check] [-q] [-v]
                                          input_zip

Options:
  -o OUTPUT              Custom output directory
  --no-zip              Don't create output ZIP file
  --skip-quality-check  Process all images (don't filter)
  -q, --quiet           Minimal output
  -v, --version         Show version
  -h, --help            Show help message
```

## 📊 Quality Metrics

The tool automatically checks:

- **Sharpness** - Rejects blurry images (Laplacian variance < 100)
- **Brightness** - Filters too dark (<30) or overexposed (>225) images
- **Contrast** - Removes flat, washed-out images (stddev < 30)

Adjustable with `--skip-quality-check` flag.

## 🎓 Perfect For

- Character/face LoRA training
- Portrait model training
- Style transfer datasets
- AI art model fine-tuning
- Dataset preparation pipelines

## 📝 License

**MIT License** - Free and Open Source

✅ Commercial use allowed  
✅ Modification allowed  
✅ Distribution allowed  
✅ Private use allowed

See [LICENSE](LICENSE) file for full text.

## 🤝 Contributing

Contributions welcome!

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 🐛 Bug Reports

Found a bug? [Open an issue](https://github.com/yourusername/lora-image-processor/issues)

## ⭐ Support

If you find this useful:
- ⭐ Star the repository
- 📢 Share with others
- 🐛 Report bugs
- 💻 Contribute code

No monetary donations needed!

## 📜 Citation

If you use this in your research/project:

```
LoRA Image Processor (2025)
https://github.com/yourusername/lora-image-processor
MIT License
```

## 🙏 Acknowledgments

Built with:
- [Pillow](https://python-pillow.org/) - Image processing
- [OpenCV](https://opencv.org/) - Face detection
- [NumPy](https://numpy.org/) - Numerical operations

Made with ❤️ for the AI art community!

---

**Free software for everyone - No strings attached!** 🎉
