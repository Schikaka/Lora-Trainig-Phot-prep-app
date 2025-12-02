@echo off
echo ====================================
echo    LoRA Image Processor
echo ====================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH!
    echo.
    echo Please install Python from: https://www.python.org/downloads/
    echo IMPORTANT: Check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo Python found! Checking dependencies...
echo.

REM Check if dependencies are installed
python -c "import cv2, PIL, numpy" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages... Please wait...
    echo.
    pip install pillow opencv-python numpy
    if errorlevel 1 (
        echo.
        echo ERROR: Failed to install dependencies!
        echo Please run this manually: pip install pillow opencv-python numpy
        pause
        exit /b 1
    )
    echo.
    echo Dependencies installed successfully!
)

echo Looking for input.zip...
echo.

REM Check if input.zip exists
if not exist "input.zip" (
    echo ERROR: input.zip not found!
    echo.
    echo Please create a ZIP file with your images and name it: input.zip
    echo Put input.zip in the same folder as this script.
    echo.
    pause
    exit /b 1
)

echo Found input.zip! Starting processing...
echo ====================================
echo.

REM Run the processor
python lora_image_processor_standalone.py input.zip -o output

echo.
echo ====================================
echo DONE! Your processed images are ready.
echo ====================================
echo.
echo Look for the folder: output
echo And the file: output.zip
echo.
pause
