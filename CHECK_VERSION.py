#!/usr/bin/env python3
"""Check which version of the script you have"""
import re

print("=" * 60)
print("VERSION CHECKER")
print("=" * 60)

with open('lora_image_processor_standalone.py', 'r') as f:
    content = f.read()

# Check for the fixes
checks = {
    "Fix 1: Default input path": "default='input/input.zip'" in content,
    "Fix 2: Output to output/ folder": "output_base = Path('output')" in content,
    "Fix 3: Counter increment once": "file_counter += 1" in content and "# Increment counter by 1 for each input image" in content,
}

print("\nChecking for bug fixes in your downloaded version:\n")
all_good = True
for check_name, result in checks.items():
    status = "✅ PRESENT" if result else "❌ MISSING"
    print(f"{status} - {check_name}")
    if not result:
        all_good = False

print("\n" + "=" * 60)
if all_good:
    print("✅ YOU HAVE THE FIXED VERSION!")
else:
    print("❌ YOU HAVE THE OLD VERSION!")
    print("\nYou need to re-download from GitHub after pushing.")
print("=" * 60)
