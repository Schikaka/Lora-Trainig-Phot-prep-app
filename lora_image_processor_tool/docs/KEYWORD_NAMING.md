# 🏷️ Keyword Naming Feature for LoRA Training

## What is This Feature?

This tool now automatically renames your processed images using a keyword you choose. This is **essential for LoRA training** to work properly.

---

## Why Do You Need This?

### The Problem

LoRA (Low-Rank Adaptation) models learn to associate images with a concept. If your images have random names like:
- `IMG_0001.png`
- `DSC_1234.png`
- `photo_abc.png`

The AI doesn't know they're all the same person or subject!

### The Solution

By naming all images with a consistent keyword:
- `MyDaughter_001.png`
- `MyDaughter_002.png`
- `MyDaughter_003.png`

The AI learns: "All these images belong to the concept 'MyDaughter'"

---

## How It Works

### Step 1: You Choose a Keyword

When you run the tool, it will ask:

```
KEYWORD FOR FILE NAMING (LoRA Training)

For LoRA training, files should be named with your concept keyword.
Example: MyDaughter, AlexSmith, Melodija

Files will be renamed to: [keyword]_001.png, [keyword]_002.png, etc.

Enter keyword:
```

### Step 2: Type Your Keyword

Examples of good keywords:
- `MyDaughter`
- `AlexSmith`
- `Melodija`
- `CatMittens`
- `RedCar`

**Rules:**
- Use letters and numbers only
- No spaces (use underscore `_` or dash `-` instead)
- Keep it short and memorable
- Use the same keyword you'll use in your training prompts

### Step 3: Files Get Renamed

All output files will be named:
- `[keyword]_001.png`
- `[keyword]_002.png`
- `[keyword]_003.png`
- etc.

**Numbers always:**
- Start at 001
- Increment by 1
- Have 3 digits (001, 002, ..., 099, 100, ...)

---

## Examples

### Example 1: Training a Person

**Keyword:** `Melodija`

**Input:** 15 photos of Melodija

**Output:**
```
Melodija_001.png (512x512 version)
Melodija_002.png (512x768 version)
Melodija_003.png (512x512 version)
Melodija_004.png (512x768 version)
...
Melodija_029.png (512x512 version)
Melodija_030.png (512x768 version)
```

**Total:** 30 files (2 per original image)

---

### Example 2: Training a Pet

**Keyword:** `MyDog`

**Input:** 20 photos of your dog

**Output:**
```
MyDog_001.png
MyDog_002.png
...
MyDog_040.png
```

---

### Example 3: Training an Object

**Keyword:** `VintageCamera`

**Input:** 12 photos of a vintage camera

**Output:**
```
VintageCamera_001.png
VintageCamera_002.png
...
VintageCamera_024.png
```

---

## Choosing the Right Keyword

### ✅ Good Keywords

- **Unique names:** `Melodija`, `Alessandro`, `KatieJones`
- **Descriptive:** `RedFerrari`, `OldCastle`, `GoldenRetriever`
- **Easy to remember:** `Mom`, `Dad`, `Sister`
- **Unique identifiers:** `Subject01`, `ModelA`, `ProductX`

### ❌ Bad Keywords

- **Too generic:** `person`, `thing`, `photo`
- **Common words:** `man`, `woman`, `car`, `dog`
- **With spaces:** `My Daughter` (use `MyDaughter` instead)
- **Special characters:** `@#$%` (cleaned automatically)

### Why It Matters

When you train your LoRA, you'll use prompts like:
- `"photo of Melodija"`
- `"Melodija smiling"`
- `"portrait of Melodija"`

The keyword in your filenames should **match** the keyword in your prompts!

---

## Using the Feature

### Method 1: Interactive (Batch Files)

1. Double-click `run_windows.bat` or `run_mac_linux.sh`
2. Choose size option
3. **Type your keyword** when prompted
4. Press Enter
5. Done!

### Method 2: Command Line

```bash
# With keyword
python lora_image_processor_standalone.py input/photos.zip --keyword Melodija

# Skip naming (use original names)
python lora_image_processor_standalone.py input/photos.zip
```

---

## What If I Skip the Keyword?

If you press Enter without typing a keyword:
- Files keep original naming pattern: `photo_512x512.png`, `photo_512x768.png`
- **This is NOT recommended for LoRA training!**
- You can rename files manually later, but it's more work

---

## How Numbers Work

### For "Both" Sizes (Default)

If you have 3 images and choose "both" (512x512 and 512x768):

```
Image 1 → Melodija_001.png (512x512)
Image 1 → Melodija_002.png (512x768)
Image 2 → Melodija_003.png (512x512)
Image 2 → Melodija_004.png (512x768)
Image 3 → Melodija_005.png (512x512)
Image 3 → Melodija_006.png (512x768)
```

**Total:** 6 files numbered 001-006

### For Single Size

If you have 3 images and choose only "512x512":

```
Image 1 → Melodija_001.png
Image 2 → Melodija_002.png
Image 3 → Melodija_003.png
```

**Total:** 3 files numbered 001-003

---

## Tips for LoRA Training

### Best Practices

1. **Use a unique keyword** that doesn't appear in common language
2. **Keep the same keyword** across all training sessions for that subject
3. **Use the keyword in your prompts** when generating images
4. **15-30 images** is the sweet spot for most LoRA training
5. **Consistent naming helps** the AI learn faster and better

### Example Workflow

1. **Collect photos:** 20 photos of your subject
2. **Choose keyword:** `Melodija`
3. **Process images:** Run this tool with keyword
4. **Get 40 files:** `Melodija_001.png` through `Melodija_040.png`
5. **Train LoRA:** Use these files with prompts like `"photo of Melodija"`
6. **Generate images:** Use `"Melodija at the beach"` in your prompts

---

## Frequently Asked Questions

### Can I use the same keyword for different training sessions?

**No!** Each subject/concept should have its own unique keyword.
- Person A: `Melodija`
- Person B: `Alessandro`
- Pet: `MyDog`

### Can I change the keyword later?

You can rename files manually, but it's easier to process them again with the correct keyword.

### What if I have 100+ images?

No problem! Numbers go up to 999 (three digits):
- `Melodija_001.png`
- `Melodija_002.png`
- ...
- `Melodija_099.png`
- `Melodija_100.png`
- ...
- `Melodija_200.png` (if you process 100 images with "both" sizes)

### Does capitalization matter?

Use the same capitalization you'll use in training:
- If you'll prompt `"photo of Melodija"` → use `Melodija` as keyword
- If you'll prompt `"photo of melodija"` → use `melodija` as keyword

**Be consistent!**

---

## Summary

✅ **Use keywords for LoRA training**  
✅ **Choose unique, memorable keywords**  
✅ **Match your prompts and filenames**  
✅ **Let the tool number files automatically**  
✅ **15-30 training images is ideal**

This feature makes your LoRA training **much more effective**!

---

**Happy LoRA training!** 🎨
