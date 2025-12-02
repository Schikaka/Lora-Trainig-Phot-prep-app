# EXACT STEPS TO PROCESS YOUR IMAGES

## Step 1: Open Terminal in Emergent
Look for a terminal icon in the Emergent interface (usually in the sidebar or menu)
OR
Click on "Terminal" or "Code Editor" option

## Step 2: Upload Your ZIP File

Option A - Drag and Drop:
1. Find the file upload area in Emergent interface
2. Drag your ZIP file there
3. It will upload to `/tmp/` or `/app/`

Option B - Use the file browser:
1. Look for "Files" or "Explorer" in the sidebar
2. Right-click → Upload
3. Select your ZIP file

## Step 3: Run the Processing Command

Open terminal and run:

```bash
python3 /app/process_lora_images.py /tmp/your_file.zip /tmp/output
```

Replace `your_file.zip` with your actual filename!

## Step 4: Download the Result

The script creates: `/tmp/output.zip`

To download:
1. Go to Files/Explorer in sidebar
2. Navigate to /tmp/
3. Right-click on `output.zip`
4. Click "Download"

OR in terminal:
```bash
ls -lh /tmp/output.zip
```
This shows the file is ready - then download via file manager.

## EXAMPLE:
If your file is `my_photos.zip`:

```bash
# Check if file uploaded
ls -lh /tmp/my_photos.zip

# Process it
python3 /app/process_lora_images.py /tmp/my_photos.zip /tmp/output

# Check output
ls -lh /tmp/output.zip

# Now download output.zip via file manager
```

Done!
