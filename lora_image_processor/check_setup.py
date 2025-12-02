#!/usr/bin/env python3
"""
Simple setup checker for LoRA Image Processor
Run this to verify everything is installed correctly

Copyright (c) 2025 LoRA Image Processor
Licensed under MIT License - Free and Open Source Software
See LICENSE file for details
"""

import sys

print("=" * 60)
print("  LoRA Image Processor - Setup Checker")
print("=" * 60)
print()

# Check Python version
print("1. Checking Python version...")
version = sys.version_info
if version.major >= 3 and version.minor >= 7:
    print(f"   ✅ Python {version.major}.{version.minor}.{version.micro} - OK!")
else:
    print(f"   ❌ Python {version.major}.{version.minor}.{version.micro} - Too old!")
    print("   Please install Python 3.7 or newer")
    sys.exit(1)

print()

# Check dependencies
print("2. Checking dependencies...")

dependencies = {
    'PIL': 'Pillow (Image processing)',
    'cv2': 'OpenCV (Face detection)',
    'numpy': 'NumPy (Math operations)'
}

all_ok = True
for module, description in dependencies.items():
    try:
        __import__(module)
        print(f"   ✅ {description} - OK!")
    except ImportError:
        print(f"   ❌ {description} - MISSING!")
        all_ok = False

print()

if not all_ok:
    print("❌ Some dependencies are missing!")
    print()
    print("To install, copy and paste this command:")
    print()
    if sys.platform == 'win32':
        print("   pip install pillow opencv-python numpy")
    else:
        print("   pip3 install pillow opencv-python numpy")
    print()
    sys.exit(1)

# All checks passed
print("=" * 60)
print("✅ ALL CHECKS PASSED!")
print("=" * 60)
print()
print("You're ready to use the LoRA Image Processor!")
print()
print("Next steps:")
print("1. Put your photos in a ZIP file")
print("2. Run: python lora_image_processor_standalone.py your_photos.zip")
print()
print("Or use the one-click scripts:")
print("  Windows: run_windows.bat")
print("  Mac/Linux: run_mac_linux.sh")
print()
