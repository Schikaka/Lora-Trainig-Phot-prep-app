# 🎨 LoRA Image Processor - Complete Beginner's Guide

**Process your photos for AI training in 3 easy steps - No coding skills needed!**

---

## 📥 STEP 1: Download Everything

Download these 4 files to a folder on your computer (e.g., `Desktop/LoRA-Tool`):

1. ✅ `lora_image_processor_standalone.py` - The main program
2. ✅ `requirements.txt` - List of tools needed
3. ✅ `run_windows.bat` - Windows users click this
4. ✅ `run_mac_linux.sh` - Mac/Linux users click this

**Put all 4 files in the SAME FOLDER!**

---

## 🔧 STEP 2: Install Python (One Time Only)

### Windows Users:

1. Go to: **https://www.python.org/downloads/**
2. Click the big yellow button "Download Python"
3. Run the installer
4. **IMPORTANT:** Check the box "Add Python to PATH" ✅
5. Click "Install Now"
6. Wait... Done!

### Mac Users:

**Option A - Easy Way:**
1. Open "Terminal" (search in Spotlight)
2. Copy and paste this line, press Enter:
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```
3. Then copy and paste:
```bash
brew install python3
```

**Option B - Download:**
1. Go to: **https://www.python.org/downloads/**
2. Download and install

---

## 🚀 STEP 3: First Time Setup

**Windows Users - Copy & Paste These Lines:**

1. Press `Windows Key + R`
2. Type: `cmd` and press Enter
3. Type: `cd Desktop\LoRA-Tool` (or wherever you put the files)
4. Copy and paste this:
```cmd
pip install pillow opencv-python numpy
```
5. Press Enter and wait (takes 1-2 minutes)

**Mac/Linux Users - Copy & Paste These Lines:**

1. Open Terminal
2. Type: `cd Desktop/LoRA-Tool` (or wherever you put the files)
3. Copy and paste this:
```bash
pip3 install pillow opencv-python numpy
```
4. Press Enter and wait (takes 1-2 minutes)

---

## 🎯 STEP 4: Use It! (Easy Method)

### Windows - Double Click Method:

1. Put your photos in a ZIP file (right-click folder → "Compress to ZIP")
2. Rename your ZIP to exactly: `input.zip`
3. Put `input.zip` in the SAME folder as the other files
4. **Double-click `run_windows.bat`**
5. Wait... Done!
6. Find your processed images in `output.zip`

### Mac/Linux - Double Click Method:

1. Put your photos in a ZIP file
2. Rename your ZIP to exactly: `input.zip`
3. Put `input.zip` in the SAME folder as the other files
4. **Double-click `run_mac_linux.sh`**
5. Wait... Done!
6. Find your processed images in `output.zip`

---

## 📋 Alternative: Command Line Method

**Windows - Copy & Paste:**
```cmd
cd Desktop\LoRA-Tool
python lora_image_processor_standalone.py your_photos.zip
```

**Mac/Linux - Copy & Paste:**
```bash
cd Desktop/LoRA-Tool
python3 lora_image_processor_standalone.py your_photos.zip
```

Replace `your_photos.zip` with your actual ZIP filename!

---

## ✅ What You'll See

```
🎨 LoRA Image Processor v1.0.0
============================================================

📦 Extracting ZIP file...
✓ Extraction complete

📸 Found 26 images

[1/26]
Processing: photo1.jpg
  Original size: 1920x1080
  Creating 512x512 version...
  ✓ Face detected (frontal view) - intelligent crop applied
  ✓ Saved: photo1_512x512.png
  Creating 512x768 version...
  ✓ Saved: photo1_512x768.png

...

✅ Processing Complete!
Input images: 26
Processed: 23
Skipped: 3 (poor quality)

📊 DATASET VARIETY ANALYSIS:
  ✅ EXCELLENT VARIETY!

📥 YOUR IMAGES ARE READY:
Folder: lora_processed_20251202_123456
ZIP file: lora_processed_20251202_123456.zip
```

---

## 🎉 You're Done!

Your processed images are ready in the ZIP file!

Each photo now has:
- `photo_512x512.png` - Square version
- `photo_512x768.png` - Tall version

Use these for your LoRA training!

---

## ❓ Troubleshooting (Common Issues)

### "python is not recognized" (Windows)

**Fix:** Python wasn't installed correctly.
1. Uninstall Python
2. Reinstall from python.org
3. **CHECK THE BOX "Add Python to PATH"** ✅

### "command not found: python3" (Mac/Linux)

**Fix:** Try `python` instead of `python3`:
```bash
python lora_image_processor_standalone.py your_photos.zip
```

### "No module named 'cv2'" or "No module named 'PIL'"

**Fix:** Dependencies not installed. Run:

**Windows:**
```cmd
pip install pillow opencv-python numpy
```

**Mac/Linux:**
```bash
pip3 install pillow opencv-python numpy
```

### "No images found in ZIP"

**Fix:** Make sure your ZIP contains image files (JPG, PNG, etc.)
- Right-click images → "Add to archive" or "Compress"
- Don't zip an empty folder

### Program says "Too many images skipped"

**Fix:** Your photos might be blurry or poorly lit.
- Try better photos
- Or use this command to process everything:

**Windows:**
```cmd
python lora_image_processor_standalone.py your_photos.zip --skip-quality-check
```

**Mac/Linux:**
```bash
python3 lora_image_processor_standalone.py your_photos.zip --skip-quality-check
```

---

## 💡 Tips for Best Results

### Good Photos:
- ✅ Sharp and in focus
- ✅ Good lighting
- ✅ Different angles (front, side, 3/4 view)
- ✅ 15-30 photos is perfect
- ✅ High resolution (bigger is better)

### Bad Photos:
- ❌ Blurry
- ❌ Too dark or too bright
- ❌ All the same angle
- ❌ Low resolution
- ❌ Too few photos (<10)

---

## 🆘 Still Need Help?

### Quick Check:
1. ✅ Did you install Python?
2. ✅ Did you check "Add Python to PATH"?
3. ✅ Did you install dependencies (pillow, opencv-python, numpy)?
4. ✅ Are all files in the SAME folder?
5. ✅ Is your ZIP file in the SAME folder?

### Test if Python Works:
**Windows:**
```cmd
python --version
```

**Mac/Linux:**
```bash
python3 --version
```

Should show: `Python 3.11.x` or similar

### Test if Dependencies Work:
```bash
python -c "import cv2; print('OpenCV OK')"
python -c "import PIL; print('Pillow OK')"
```

Should show: `OpenCV OK` and `Pillow OK`

---

## 📝 Summary

**Installation (One Time):**
1. Download 4 files → Put in one folder
2. Install Python (check "Add to PATH")
3. Run: `pip install pillow opencv-python numpy`

**Every Time You Use It:**
1. Put photos in ZIP file
2. Double-click `run_windows.bat` or `run_mac_linux.sh`
3. Done! Get your processed images

**That's it! No coding needed!** 🎉

---

**Made simple for everyone! ❤️**
