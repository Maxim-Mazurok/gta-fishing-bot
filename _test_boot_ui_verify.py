"""Verify _wait_for_boot_ui logic matches the fixed code."""
import cv2
import sys
import pytesseract

pytesseract.pytesseract.tesseract_cmd = (
    r'C:\Users\Maxim.Mazurok\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'
)

img = cv2.imread(sys.argv[1])
h, w = img.shape[:2]

# Exact same crop as the fixed _wait_for_boot_ui
roi = img[int(h * 0.10):int(h * 0.30), int(w * 0.50):int(w * 0.95)]
gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
_, thresh = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY)
text = pytesseract.image_to_string(thresh, config='--psm 6 --oem 3')
text_upper = text.upper()

has_vehicle_boot = 'VEHICLE BOOT' in text_upper
has_loading = 'LOADING' in text_upper
print(f"VEHICLE BOOT: {has_vehicle_boot}")
print(f"LOADING: {has_loading}")
print(f"Result: {'PASS - boot is open and loaded' if has_vehicle_boot and not has_loading else 'FAIL'}")
