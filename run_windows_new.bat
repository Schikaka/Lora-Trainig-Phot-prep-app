@echo off
echo ====================================
echo    LoRA Image Processor
echo    FREE SOFTWARE (MIT License)
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
    pip install -r requirements.txt
    if errorlevel 1 (
        echo.
        echo ERROR: Failed to install dependencies!
        echo Please run this manually: pip install -r requirements.txt
        pause
        exit /b 1
    )
    echo.
    echo Dependencies installed successfully!
    echo.
)

REM Create input and output folders if they don't exist
if not exist "input" mkdir input
if not exist "output" mkdir output

echo Looking for ZIP files in input folder...
echo.

REM Find ZIP files in input folder
dir /b input\*.zip >nul 2>&1
if errorlevel 1 (
    echo ERROR: No ZIP files found in input folder!
    echo.
    echo Please put your photos ZIP file in the "input" folder.
    echo Example: input\my_photos.zip
    echo.
    pause
    exit /b 1
)

REM List available ZIP files
echo Available ZIP files:
echo.
dir /b input\*.zip
echo.

REM Get first ZIP file or let user specify
set /p ZIPFILE="Enter ZIP filename (or press Enter for first file): "
if "%ZIPFILE%"=="" (
    for /f %%i in ('dir /b input\*.zip') do (
        set ZIPFILE=%%i
        goto :gotfile
    )
)
:gotfile

echo.
echo Processing: %ZIPFILE%
echo.

REM Ask for size preference
echo Choose output size:
echo   1. Both 512x512 and 512x768 (default, recommended)
echo   2. Only 512x512 (close-up faces)
echo   3. Only 512x768 (portraits)
echo   4. Only 1024x1024 (SDXL training)
echo.
set /p CHOICE="Enter your choice (1-4) or press Enter for default: "

set SIZES=both
if "%CHOICE%"=="2" set SIZES=512x512
if "%CHOICE%"=="3" set SIZES=512x768
if "%CHOICE%"=="4" set SIZES=1024x1024

echo.
echo Starting processing...
echo ====================================
echo.

REM Run the processor
python lora_image_processor_standalone.py "input\%ZIPFILE%" -o output --sizes %SIZES%

echo.
echo ====================================
echo DONE! Your processed images are ready.
echo ====================================
echo.
echo Look in the "output" folder for:
echo   - Folder with processed images
echo   - ZIP file ready to download
echo.
pause
