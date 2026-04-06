"""Test _wait_for_boot_ui OCR against a screenshot of the open boot."""
import cv2
import sys
import pytesseract

pytesseract.pytesseract.tesseract_cmd = (
    r'C:\Users\Maxim.Mazurok\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'
)

img = cv2.imread(sys.argv[1])
if img is None:
    print("Could not read image"); sys.exit(1)

h, w = img.shape[:2]
print(f"Image size: {w}x{h}")

# --- Test 1: full-image OCR (current code) ---
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
_, thresh = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY)
text = pytesseract.image_to_string(thresh, config='--psm 6 --oem 3')
text_upper = text.upper()
print("\n=== Full image OCR ===")
print(f"Has 'VEHICLE BOOT': {'VEHICLE BOOT' in text_upper}")
print(f"Has 'LOADING': {'LOADING' in text_upper}")
# Show relevant lines
for line in text.split('\n'):
    line_s = line.strip()
    if line_s and any(w in line_s.upper() for w in ['VEHICLE', 'BOOT', 'INVENTORY', 'LOADING']):
        print(f"  >> {line_s}")

# --- Test 2: crop to right half (where VEHICLE BOOT header is) ---
roi_right = img[int(h*0.10):int(h*0.30), int(w*0.50):int(w*0.95)]
gray2 = cv2.cvtColor(roi_right, cv2.COLOR_BGR2GRAY)
_, thresh2 = cv2.threshold(gray2, 180, 255, cv2.THRESH_BINARY)
text2 = pytesseract.image_to_string(thresh2, config='--psm 6 --oem 3')
text2_upper = text2.upper()
print("\n=== Right-half header ROI ===")
print(f"Has 'VEHICLE BOOT': {'VEHICLE BOOT' in text2_upper}")
print(f"Has 'LOADING': {'LOADING' in text2_upper}")
for line in text2.split('\n'):
    if line.strip():
        print(f"  >> {line.strip()}")

# --- Test 3: crop + scale 3x ---
scale = 3
gray3 = cv2.resize(gray2, (gray2.shape[1]*scale, gray2.shape[0]*scale), interpolation=cv2.INTER_CUBIC)
_, thresh3 = cv2.threshold(gray3, 180, 255, cv2.THRESH_BINARY)
text3 = pytesseract.image_to_string(thresh3, config='--psm 6 --oem 3')
text3_upper = text3.upper()
print("\n=== Right-half header ROI + 3x scale ===")
print(f"Has 'VEHICLE BOOT': {'VEHICLE BOOT' in text3_upper}")
print(f"Has 'LOADING': {'LOADING' in text3_upper}")
for line in text3.split('\n'):
    if line.strip():
        print(f"  >> {line.strip()}")

# --- Test 4: upper portion only (top 25% of screen, full width) ---
roi_top_area = img[0:int(h*0.25), :]
gray4 = cv2.cvtColor(roi_top_area, cv2.COLOR_BGR2GRAY)
_, thresh4 = cv2.threshold(gray4, 180, 255, cv2.THRESH_BINARY)
text4 = pytesseract.image_to_string(thresh4, config='--psm 6 --oem 3')
text4_upper = text4.upper()
print("\n=== Top 25% full width ===")
print(f"Has 'VEHICLE BOOT': {'VEHICLE BOOT' in text4_upper}")
print(f"Has 'LOADING': {'LOADING' in text4_upper}")
for line in text4.split('\n'):
    if line.strip():
        print(f"  >> {line.strip()}")
