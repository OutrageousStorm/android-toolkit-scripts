#!/usr/bin/env python3
"""
screenshot_compare.py -- Compare two device screenshots for pixel differences
Useful for testing if your tweaks actually changed the UI.
Usage: python3 screenshot_compare.py before.png after.png [--threshold 5]
"""
import sys, subprocess
from pathlib import Path

try:
    from PIL import Image, ImageChops
except ImportError:
    print("Install Pillow: pip install Pillow")
    sys.exit(1)

def compare(img1_path, img2_path, threshold=5):
    img1 = Image.open(img1_path).convert("RGB")
    img2 = Image.open(img2_path).convert("RGB")
    
    if img1.size != img2.size:
        print(f"Image sizes differ: {img1.size} vs {img2.size}")
        return False
    
    diff = ImageChops.difference(img1, img2)
    stat = diff.getextrema()
    if stat == ((0, 0), (0, 0), (0, 0)):
        print("✓ Images are identical")
        return True
    
    # Calculate % changed
    diff_pixels = sum(1 for p in diff.getdata() if p != (0, 0, 0))
    total_pixels = img1.width * img1.height
    pct = (diff_pixels / total_pixels) * 100
    
    print(f"Differences found: {pct:.2f}% of pixels changed")
    if pct > threshold:
        print(f"⚠️  Above threshold ({threshold}%)")
        diff.save("diff_highlighted.png")
        return False
    return True

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 screenshot_compare.py before.png after.png [--threshold 5]")
        sys.exit(1)
    
    before = sys.argv[1]
    after = sys.argv[2]
    threshold = float(sys.argv[4]) if len(sys.argv) > 3 and sys.argv[3] == "--threshold" else 5
    
    if not Path(before).exists() or not Path(after).exists():
        print("File not found")
        sys.exit(1)
    
    ok = compare(before, after, threshold)
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
