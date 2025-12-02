#!/bin/bash

echo "===================================="
echo "   LoRA Image Processor"
echo "   FREE SOFTWARE (MIT License)"
echo "===================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed!"
    echo ""
    echo "Mac users: Install Homebrew, then run: brew install python3"
    echo "Linux users: Run: sudo apt install python3 python3-pip"
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

echo "Python found! Checking dependencies..."
echo ""

# Check if dependencies are installed
python3 -c "import cv2, PIL, numpy" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing required packages... Please wait..."
    echo ""
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo ""
        echo "ERROR: Failed to install dependencies!"
        echo "Please run this manually: pip3 install -r requirements.txt"
        read -p "Press Enter to exit..."
        exit 1
    fi
    echo ""
    echo "Dependencies installed successfully!"
    echo ""
fi

# Create input and output folders if they don't exist
mkdir -p input
mkdir -p output

echo "Looking for ZIP files in input folder..."
echo ""

# Check if there are any ZIP files
if ! ls input/*.zip 1> /dev/null 2>&1; then
    echo "ERROR: No ZIP files found in input folder!"
    echo ""
    echo "Please put your photos ZIP file in the 'input' folder."
    echo "Example: input/my_photos.zip"
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

# List available ZIP files
echo "Available ZIP files:"
echo ""
ls input/*.zip
echo ""

# Get first ZIP file or let user specify
read -p "Enter ZIP filename (or press Enter for first file): " ZIPFILE
if [ -z "$ZIPFILE" ]; then
    ZIPFILE=$(ls input/*.zip | head -1)
else
    ZIPFILE="input/$ZIPFILE"
fi

echo ""
echo "Processing: $ZIPFILE"
echo ""

# Ask for size preference
echo "Choose output size:"
echo "  1. Both 512x512 and 512x768 (default, recommended)"
echo "  2. Only 512x512 (close-up faces)"
echo "  3. Only 512x768 (portraits)"
echo "  4. Only 1024x1024 (SDXL training)"
echo ""
read -p "Enter your choice (1-4) or press Enter for default: " CHOICE

SIZES="both"
case $CHOICE in
    2) SIZES="512x512";;
    3) SIZES="512x768";;
    4) SIZES="1024x1024";;
esac

echo ""
echo "===================================="
echo "KEYWORD FOR FILE NAMING (LoRA Training)"
echo "===================================="
echo ""
echo "For LoRA training, files should be named with your concept keyword."
echo "Example: MyDaughter, AlexSmith, Melodija"
echo ""
echo "Files will be renamed to: [keyword]_001.png, [keyword]_002.png, etc."
echo ""
echo "Press Enter to skip and keep original filenames."
echo ""
read -p "Enter keyword: " KEYWORD

echo ""
echo "Starting processing..."
echo "===================================="
echo ""

# Run the processor with or without keyword
if [ -z "$KEYWORD" ]; then
    python3 lora_image_processor_standalone.py "$ZIPFILE" -o output --sizes $SIZES
else
    python3 lora_image_processor_standalone.py "$ZIPFILE" -o output --sizes $SIZES --keyword "$KEYWORD"
fi

echo ""
echo "===================================="
echo "DONE! Your processed images are ready."
echo "===================================="
echo ""
echo "Look in the 'output' folder for:"
echo "  - Folder with processed images"
echo "  - ZIP file ready to download"
echo ""
read -p "Press Enter to exit..."
