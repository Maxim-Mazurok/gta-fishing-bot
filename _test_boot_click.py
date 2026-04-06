"""Test script: find standalone 'Boot' text and mark it with a green dot.

Crops the right-center portion of the screen (where the interaction menu appears)
before running OCR for much better accuracy.
"""
import cv2
import numpy as np
import pytesseract
import sys

pytesseract.pytesseract.tesseract_cmd = (
    r'C:\Users\Maxim.Mazurok\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'
)

img = cv2.imread(sys.argv[1])
if img is None:
    print("Could not read image"); sys.exit(1)

h, w = img.shape[:2]
print(f"Image size: {w}x{h}")

# Crop to the interaction menu region (right-center of screen)
roi_left = int(w * 0.50)
roi_right = int(w * 0.70)
roi_top = int(h * 0.30)
roi_bottom = int(h * 0.75)
roi = img[roi_top:roi_bottom, roi_left:roi_right]

print(f"ROI: x=[{roi_left},{roi_right}] y=[{roi_top},{roi_bottom}] size={roi.shape[1]}x{roi.shape[0]}")

gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

# Scale up 3x for better OCR accuracy on small text
scale = 3
gray = cv2.resize(gray, (gray.shape[1] * scale, gray.shape[0] * scale), interpolation=cv2.INTER_CUBIC)

_, thresh = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY)

data = pytesseract.image_to_data(thresh, config='--psm 6 --oem 3', output_type=pytesseract.Output.DICT)

print("\nAll OCR words in menu ROI:")
for i, text in enumerate(data['text']):
    if text.strip():
        print(f"  line={data['line_num'][i]} word='{text.strip()}' "
              f"at roi=({data['left'][i]},{data['top'][i]}) "
              f"abs=({data['left'][i]+roi_left},{data['top'][i]+roi_top}) "
              f"size=({data['width'][i]}x{data['height'][i]})")

click_pos = None
for i, text in enumerate(data['text']):
    if text.strip().lower() == 'boot':
        line_num = data['line_num'][i]
        # Only consider "real" words (3+ chars) — icon artifacts are 1-2 chars
        real_words = [
            data['text'][j].strip().lower()
            for j in range(len(data['text']))
            if data['line_num'][j] == line_num
            and len(data['text'][j].strip()) >= 3
        ]
        abs_x = roi_left + data['left'][i] // scale + data['width'][i] // scale // 2
        abs_y = roi_top + data['top'][i] // scale + data['height'][i] // scale // 2
        print(f"\nFound 'boot' on line {line_num}, real_words={real_words}")
        if real_words == ['boot']:
            click_pos = (abs_x, abs_y)
            print(f"  -> STANDALONE match at ({abs_x}, {abs_y})")
        else:
            print(f"  -> Skipping (part of: {real_words})")

if click_pos:
    vis = img.copy()
    cv2.circle(vis, click_pos, 15, (0, 255, 0), -1)
    cv2.circle(vis, click_pos, 17, (0, 0, 0), 2)
    out = sys.argv[1].replace('.png', '_marked.png')
    cv2.imwrite(out, vis)
    print(f"\nMarked image saved to: {out}")
else:
    print("\nNo standalone 'Boot' found! Trying full-text fallback...")
    # Show all lines for debugging
    lines = {}
    for i, text in enumerate(data['text']):
        if text.strip():
            ln = data['line_num'][i]
            lines.setdefault(ln, []).append(data['text'][i].strip())
    print("OCR lines:")
    for ln, words in sorted(lines.items()):
        print(f"  line {ln}: {' '.join(words)}")
