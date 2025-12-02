#!/usr/bin/env python3
"""Debug script to test the lora processor"""
import sys
from pathlib import Path

print("="*60)
print("DEBUG TEST FOR LORA PROCESSOR")
print("="*60)

# Check if input.zip exists
input_zip = Path('input/input.zip')
print(f"\n1. Checking for input/input.zip...")
print(f"   Exists: {input_zip.exists()}")
if input_zip.exists():
    print(f"   Size: {input_zip.stat().st_size} bytes")

# Run the processor
print(f"\n2. Running processor...")
sys.argv = ['lora_image_processor_standalone.py', '--keyword', 'DebugTest', '--sizes', '512x512', '--skip-quality-check', '-q']

import lora_image_processor_standalone
try:
    lora_image_processor_standalone.main()
except SystemExit:
    pass

# Check output
print(f"\n3. Checking output...")
output_dir = Path('output')
if output_dir.exists():
    processed_dirs = list(output_dir.glob('lora_processed_*'))
    if processed_dirs:
        latest = max(processed_dirs, key=lambda p: p.stat().st_mtime)
        files = list(latest.glob('DebugTest*.png'))
        print(f"   Found {len(files)} output files:")
        for f in sorted(files):
            print(f"     - {f.name}")
    else:
        print("   No processed directories found")
else:
    print("   Output directory doesn't exist")

print("\n" + "="*60)
print("TEST COMPLETE")
print("="*60)
