import cv2, pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\Maxim.Mazurok\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'
import sys
sys.path.insert(0, '.')
from inventory import BootOffloadHandler

handler = BootOffloadHandler()

img = cv2.imread('boot_menu_screenshot.png')
h, w = img.shape[:2]
print(f"Image: {w}x{h}")

roi, roi_x, roi_y = handler._crop_roi(img, (0.35, 0.80), (0.15, 0.85))
thresh, scale = handler._ocr_preprocess(roi)
print(f"ROI: {roi.shape[1]}x{roi.shape[0]}, scale={scale:.2f}")

data = pytesseract.image_to_data(thresh, config='--psm 6 --oem 3', output_type=pytesseract.Output.DICT)

real_entries = []
for i, text in enumerate(data['text']):
    word = text.strip()
    if len(word) >= 3:
        cy = data['top'][i] + data['height'][i] / 2
        real_entries.append((i, word.lower(), cy, data['height'][i]))
        print(f"  word={word!r:20s} cy={cy:.0f} h={data['height'][i]}")

print("\nChecking 'boot' entries:")
for idx, word, cy, wh in real_entries:
    if word != 'boot':
        continue
    tolerance = max(wh, 20)
    neighbours = [w for _, w, wy, _ in real_entries if abs(wy - cy) < tolerance and w != 'boot']
    print(f"  Boot at cy={cy:.0f}, tolerance={tolerance}, neighbours={neighbours}")
    if not neighbours:
        x = roi_x + int(data['left'][idx] / scale + data['width'][idx] / scale / 2)
        y = roi_y + int(data['top'][idx] / scale + data['height'][idx] / scale / 2)
        print(f"  -> STANDALONE at ({x}, {y})")
    else:
        print(f"  -> SKIP (near other words)")
