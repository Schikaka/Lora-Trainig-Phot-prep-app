# LoRA Image Processor v2.0 - Quality-Focused Edition

Process images for BEST Stable Diffusion LoRA training results with intelligent quality control and variety analysis.

## 🎯 What's New - Focus on Quality

### 1. ✅ Automatic Quality Control
- **Blur Detection** - Rejects blurry/out-of-focus images
- **Exposure Check** - Filters overexposed or too-dark photos  
- **Contrast Analysis** - Ensures images have sufficient detail
- **Auto-Skip** - Bad images are automatically excluded

### 2. 🧠 Intelligent Cropping
- **Face Angle Detection** - Detects frontal, profile, and 3/4 views
- **Context-Aware Padding** - Adjusts crop based on face angle
- **Smart Composition** - Includes shoulders, hair, and important context
- **Portrait Optimization** - Better vertical framing for portrait shots

### 3. 📊 Dataset Variety Analysis
- **Angle Distribution** - Shows frontal/profile/tilted breakdown
- **Variety Score** - Rates your dataset (1-3 stars)
- **Recommendations** - Tells you what angles to add
- **Quality Report** - Lists why images were skipped

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Process images (with quality filtering)
python lora_image_processor_standalone.py your_photos.zip

# Process ALL images (skip quality check)
python lora_image_processor_standalone.py your_photos.zip --skip-quality-check
```

## 📖 Usage Examples

### Best Quality (Recommended)
```bash
python lora_image_processor_standalone.py photos.zip
```
✅ Only processes sharp, well-lit, good contrast images

### Process Everything
```bash
python lora_image_processor_standalone.py photos.zip --skip-quality-check
```
⚠️ Processes all images regardless of quality

### Custom Output
```bash
python lora_image_processor_standalone.py photos.zip -o my_lora_data
```

### Quiet Mode
```bash
python lora_image_processor_standalone.py photos.zip -q
```

## 📊 Understanding the Output

### Quality Report
```
⚠️  QUALITY REPORT:
  • 3x blurry (sharpness < 100)
  • 2x too dark (brightness < 30)
  • 1x overexposed (brightness > 225)
```

**What this means:**
- **Blurry** - Camera shake, out of focus, or motion blur
- **Too dark** - Underexposed, poor lighting
- **Overexposed** - Blown highlights, too bright
- **Low contrast** - Flat lighting, washed out

💡 **Fix:** Use better lighting, tripod, and check focus

### Variety Analysis
```
📊 DATASET VARIETY ANALYSIS:
  • Frontal: 15 images (60.0%)
  • Profile: 6 images (24.0%)
  • Tilted: 4 images (16.0%)

  Variety Score: 3/3
  ✅ EXCELLENT VARIETY - Multiple angles detected!
```

**Variety Scores:**
- **1/3** ⚠️  Low - All same angle (add variety!)
- **2/3** ✓ Good - Two angles (pretty good)
- **3/3** ✅ Excellent - All angles (perfect!)

💡 **For best LoRA:** Aim for 3/3 variety score

## 🎯 Tips for Best LoRA Training

### Image Quality Checklist:
- ✅ Sharp focus (no blur)
- ✅ Good lighting (not too dark/bright)
- ✅ Clear subject (in focus, visible)
- ✅ High resolution (1024px+ recommended)
- ✅ Variety of angles

### Dataset Composition:
- **15-30 images** - Sweet spot for most LoRA
- **Multiple angles** - Front, side, 3/4 view
- **Different expressions** - Neutral, smile, serious
- **Varied lighting** - Indoor, outdoor, different times
- **Consistent subject** - Same person/character

### Common Mistakes:
- ❌ All frontal photos (no variety)
- ❌ Poor lighting (too dark/bright)
- ❌ Blurry images (motion/focus issues)
- ❌ Too few images (<10)
- ❌ Too many similar photos

## 🔧 Quality Settings

Default thresholds (built-in):
- **Blur threshold**: 100.0 (Laplacian variance)
- **Min brightness**: 30 (0-255 scale)
- **Max brightness**: 225 (0-255 scale)
- **Min contrast**: 30 (standard deviation)

These are tuned for optimal LoRA training quality.

## 📁 What You Get

For each good quality image (e.g., `photo.jpg`):
- `photo_512x512.png` - Square crop (close-up training)
- `photo_512x768.png` - Portrait crop (full-body training)

Plus:
- **Quality report** - What was skipped and why
- **Variety analysis** - Dataset composition breakdown
- **ZIP file** - All processed images ready to use

## 💡 Pro Tips

1. **Review the Quality Report** - Fix common issues in your next batch
2. **Check Variety Score** - Add missing angles if needed
3. **Use Good Source Images** - GIGO (Garbage In, Garbage Out)
4. **Test Small Batches** - Process 5 images first to check quality
5. **Keep Original ZIP** - You can reprocess with `--skip-quality-check` if needed

## 🆚 Quality Filtering vs No Filtering

### With Quality Filtering (Default)
```bash
python lora_image_processor_standalone.py photos.zip
```
- ✅ Only best images processed
- ✅ Clean dataset
- ✅ Better LoRA results
- ⚠️ Some images skipped

### Without Quality Filtering
```bash
python lora_image_processor_standalone.py photos.zip --skip-quality-check
```
- ✅ All images processed
- ⚠️ May include poor quality images
- ⚠️ Could hurt LoRA training

**Recommendation:** Use default (with filtering) for best results

## 🎓 Understanding Face Angles

- **Frontal** - Looking at camera, face visible
- **Profile** - Side view, 90° angle
- **Tilted** - Head tilt or 3/4 view

**Best mix for LoRA:**
- 60% Frontal
- 25% 3/4 view / Tilted
- 15% Profile

## 📝 System Requirements

- Python 3.7 or higher
- ~200MB free space per 50 images
- Works offline after install

## 🐛 Troubleshooting

**Too many images skipped?**
- Check original image quality
- Use `--skip-quality-check` to process all
- Improve lighting/focus in source photos

**No face detected?**
- Script still works (uses center crop)
- Consider if you need face detection
- Some subjects don't have faces (that's OK!)

**Low variety score?**
- Take photos from different angles
- Add profile and 3/4 views
- Vary your shooting positions

---

**Made for serious LoRA training - Quality over quantity! 🎯**
