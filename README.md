# HOW TO INSTALL & RUN THIS APP (WINDOWS)

Use the files you see in this folder.

---

## 1. Go into the folder

You already are here:

```
lora_image_processor
```

Perfect.

---

## 2. Install the Python dependencies

You only need **ONE command**.

Inside the folder, **SHIFT+RIGHT-CLICK** → **Open PowerShell here**  
or type `cmd` in the folder path bar.

Then run:

```bash
pip install -r requirements.txt
```

That installs the few libraries this script needs.

If you get `"pip not found"`, use this:

```bash
python -m pip install -r requirements.txt
```

---

## 3. Put your photos in the INPUT folder

Look for the folder:

```
input/
```

Put your ZIP file with photos here. Name it anything you want:

```
input/my_photos.zip
```

Or drag your ZIP file into the **input** folder.

---

## 4. Run the Windows version

You have a file:

```
run_windows.bat
```

**Double-click it.**

If Windows blocks it → right-click → Properties → Unblock → Apply → run again.

The script will ask you:

```
Choose output size:
  1. Both 512x512 and 512x768 (default, recommended)
  2. Only 512x512 (close-up faces)
  3. Only 512x768 (portraits)
  4. Only 1024x1024 (SDXL training)
```

Type `1`, `2`, `3`, or `4` and press Enter.

---

## 5. Get your processed images

After processing, find your images in:

```
output/
```

The folder will have a name like:

```
output/lora_processed_20251202_123456/
```

And a ZIP file:

```
output/lora_processed_20251202_123456.zip
```

**Download the ZIP file** - it contains all your processed images!

---

## ❗ If you get any errors

### `"python is not recognized"`

→ Install Python from [python.org](https://www.python.org/downloads/)  
→ **CHECK "Add Python to PATH"** during install  
→ Restart computer  
→ Try again

### `"No module named..."`

→ Run: 

```bash
pip install -r requirements.txt
```

### `"No such file"`

→ Make sure your ZIP is in the **input/** folder

### **Some faces not detected or cut off?**

The tool uses generous padding to capture full faces. If some images show:
- **"No face detected"** → Uses smart center crop instead
- **Half face visible** → Face was too close to image edge

**Solutions:**
- Use photos with faces centered in frame
- Avoid extreme close-ups where face fills entire image
- Make sure faces are clearly visible (good lighting)
- The tool will still process these images using intelligent cropping

After processing, check the output visually and re-process problem images if needed.

---

## 👍 MANUAL RUN (if double-click fails)

Open `cmd` in this folder, then run:

### For both sizes (512x512 and 512x768):
```bash
python lora_image_processor_standalone.py input\your_photos.zip
```

### For only 512x512:
```bash
python lora_image_processor_standalone.py input\your_photos.zip --sizes 512x512
```

### For only 512x768:
```bash
python lora_image_processor_standalone.py input\your_photos.zip --sizes 512x768
```

### For 1024x1024 (SDXL):
```bash
python lora_image_processor_standalone.py input\your_photos.zip --sizes 1024x1024
```

---

## FOR MAC/LINUX USERS

### 1. Install Python:

**Mac:**
```bash
brew install python3
```

**Linux:**
```bash
sudo apt install python3 python3-pip
```

### 2. Install dependencies:
```bash
pip3 install -r requirements.txt
```

### 3. Put ZIP in input/ folder

### 4. Run:
```bash
python3 lora_image_processor_standalone.py input/your_photos.zip
```

### 5. Get output from output/ folder

---

## FOLDER STRUCTURE

```
lora_image_processor/
├── README.md (this file)
├── lora_image_processor_standalone.py (main program)
├── requirements.txt (dependencies)
├── run_windows.bat (Windows one-click)
├── run_mac_linux.sh (Mac/Linux one-click)
├── check_setup.py (test installation)
├── LICENSE (MIT License)
├── input/ (PUT YOUR ZIP FILES HERE)
├── output/ (PROCESSED FILES GO HERE)
└── docs/ (all documentation)
```

---

## QUICK REFERENCE

### Install (one time):
```bash
pip install -r requirements.txt
```

### Use (every time):

1. Put ZIP in **input/** folder
2. Double-click **run_windows.bat**
3. Choose size option (1-4)
4. Get output from **output/** folder

---

## SIZE OPTIONS EXPLAINED

| Option | Size | Best For |
|--------|------|----------|
| 1 | Both 512×512 and 512×768 | Complete dataset (recommended) |
| 2 | Only 512×512 | Close-up faces, SD1.5 |
| 3 | Only 512×768 | Portraits, SD1.5 |
| 4 | Only 1024×1024 | SDXL training |

---

## 100% FREE SOFTWARE

**MIT License** - Use for personal or commercial projects!

See [LICENSE](LICENSE) file for details.

---

## NEED MORE HELP?

See the **docs/** folder for:
- `SIMPLE_GUIDE.txt` - Step-by-step guide
- `BEGINNER_GUIDE.md` - Complete tutorial
- `QUICK_START.txt` - Quick commands

---

**Ready to process your images!** 🎨
