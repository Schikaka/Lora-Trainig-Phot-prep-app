# Simple Instructions - LoRA Image Processor

## What You Need:
1. Your ZIP file with photos
2. Access to terminal/command line

## Step-by-Step:

### 1. Upload Your ZIP File
Put your ZIP file anywhere accessible on the system. For example:
- `/tmp/my_photos.zip`
- `/app/my_photos.zip`

### 2. Run the Script
```bash
python3 /app/process_lora_images.py /path/to/your_photos.zip /tmp/output
```

Example:
```bash
python3 /app/process_lora_images.py /tmp/my_photos.zip /tmp/output
```

### 3. Get Your Files
The script will create:
- `/tmp/output/` folder with all processed images
- `/tmp/output.zip` ZIP file ready to download

## That's It!

The script outputs:
- 512x512 PNG files (for close-up face training)
- 512x768 PNG files (for portrait training)

## Download Options:

**Option A: Download the ZIP directly**
The script creates a ZIP file at the location you specify + ".zip"
Example: `/tmp/output.zip`

**Option B: Download individual files**
All processed images are in the output folder

**Option C: Use file manager**
Navigate to the output folder in your file browser and download

## No Web Browser Needed!
Just command line → Done.
