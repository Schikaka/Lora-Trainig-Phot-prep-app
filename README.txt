================================================================
HOW TO INSTALL & RUN THIS APP (WINDOWS)
================================================================

Use the files you see in this folder.

================================================================
1. Go into the folder
================================================================

You already are here:

  lora_image_processor


Perfect.

================================================================
2. Install the Python dependencies
================================================================

You only need ONE command.

Inside the folder, SHIFT+RIGHT-CLICK → Open PowerShell here
or type cmd in the folder path bar.

Then run:

pip install -r requirements.txt


That installs the few libraries this script needs.

If you get "pip not found", use this:

python -m pip install -r requirements.txt

================================================================
3. Put your photos in the INPUT folder
================================================================

Look for the folder:

  input/


Put your ZIP file with photos here. Name it anything you want:

  input/my_photos.zip


Or drag your ZIP file into the input folder.

================================================================
4. Run the Windows version
================================================================

You have a file:

  run_windows.bat


Double-click it.

If Windows blocks it → right-click → Properties → Unblock → Apply → run again.

This batch file automatically runs:

  python lora_image_processor_standalone.py input\your_file.zip


Which is the main app.

The script will ask you which size you want:
  1. Both 512x512 and 512x768 (default)
  2. Only 512x512 (for close-up faces)
  3. Only 512x768 (for portraits)
  4. Only 1024x1024 (for SDXL)

Choose your option and press Enter.

================================================================
5. Get your processed images
================================================================

After processing, find your images in:

  output/


The folder will have a name like:

  output/lora_processed_20251202_123456/


And a ZIP file:

  output/lora_processed_20251202_123456.zip


Download the ZIP file - it contains all your processed images!

================================================================
❗ If you get any errors
================================================================

"python is not recognized"
→ Install Python from python.org
→ CHECK "Add Python to PATH" during install
→ Restart computer
→ Try again

"No module named..."
→ Run: pip install -r requirements.txt

"No such file"
→ Make sure your ZIP is in the input/ folder

================================================================
👍 MANUAL RUN (if double-click fails)
================================================================

Open cmd in this folder, then run:

For both sizes (512x512 and 512x768):
python lora_image_processor_standalone.py input\your_photos.zip

For only 512x512:
python lora_image_processor_standalone.py input\your_photos.zip --sizes 512x512

For only 512x768:
python lora_image_processor_standalone.py input\your_photos.zip --sizes 512x768

For 1024x1024:
python lora_image_processor_standalone.py input\your_photos.zip --sizes 1024x1024

================================================================
FOR MAC/LINUX USERS
================================================================

1. Install Python:
   Mac: brew install python3
   Linux: sudo apt install python3

2. Install dependencies:
   pip3 install -r requirements.txt

3. Put ZIP in input/ folder

4. Run:
   python3 lora_image_processor_standalone.py input/your_photos.zip

5. Get output from output/ folder

================================================================
FOLDER STRUCTURE
================================================================

lora_image_processor/
├── README.txt (this file)
├── lora_image_processor_standalone.py (main program)
├── requirements.txt (dependencies)
├── run_windows.bat (Windows one-click)
├── run_mac_linux.sh (Mac/Linux one-click)
├── check_setup.py (test installation)
├── input/ (PUT YOUR ZIP FILES HERE)
├── output/ (PROCESSED FILES GO HERE)
└── docs/ (all documentation)

================================================================
QUICK REFERENCE
================================================================

Install (one time):
  pip install -r requirements.txt

Use (every time):
  1. Put ZIP in input/ folder
  2. Double-click run_windows.bat
  3. Choose size option
  4. Get output from output/ folder

================================================================
100% FREE SOFTWARE (MIT License)
================================================================

Use for personal or commercial projects!
See LICENSE file for details.

================================================================
