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
    pip3 install pillow opencv-python numpy
    if [ $? -ne 0 ]; then
        echo ""
        echo "ERROR: Failed to install dependencies!"
        echo "Please run this manually: pip3 install pillow opencv-python numpy"
        read -p "Press Enter to exit..."
        exit 1
    fi
    echo ""
    echo "Dependencies installed successfully!"
fi

echo "Looking for input.zip..."
echo ""

# Check if input.zip exists
if [ ! -f "input.zip" ]; then
    echo "ERROR: input.zip not found!"
    echo ""
    echo "Please create a ZIP file with your images and name it: input.zip"
    echo "Put input.zip in the same folder as this script."
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

echo "Found input.zip! Starting processing..."
echo "===================================="
echo ""

# Run the processor
python3 lora_image_processor_standalone.py input.zip -o output

echo ""
echo "===================================="
echo "DONE! Your processed images are ready."
echo "===================================="
echo ""
echo "Look for the folder: output"
echo "And the file: output.zip"
echo ""
read -p "Press Enter to exit..."
