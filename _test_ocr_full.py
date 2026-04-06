import cv2, pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\Maxim.Mazurok\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'

img = cv2.imread('boot_ui_screenshot.png')
h, w = img.shape[:2]

# Full image OCR at 1x
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
_, thresh = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY)
data = pytesseract.image_to_data(thresh, config='--psm 6 --oem 3', output_type=pytesseract.Output.DICT)
for i, t in enumerate(data['text']):
    if t.strip().upper() in ('YOUR', 'INVENTORY', 'VEHICLE', 'BOOT'):
        ln = data['line_num'][i]
        x, y = data['left'][i], data['top'][i]
        print(f"  word={t.strip()!r} line={ln} at ({x},{y})")

print("\n--- Trying with higher target_width ---")
scale = max(1, 2500 / w)
print(f"scale={scale}")
gray2 = cv2.resize(gray, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_CUBIC)
_, thresh2 = cv2.threshold(gray2, 180, 255, cv2.THRESH_BINARY)
data2 = pytesseract.image_to_data(thresh2, config='--psm 6 --oem 3', output_type=pytesseract.Output.DICT)
for i, t in enumerate(data2['text']):
    if t.strip().upper() in ('YOUR', 'INVENTORY', 'VEHICLE', 'BOOT'):
        ln = data2['line_num'][i]
        x, y = data2['left'][i], data2['top'][i]
        print(f"  word={t.strip()!r} line={ln} at ({x},{y}) -> orig ({int(x/scale)},{int(y/scale)})")
