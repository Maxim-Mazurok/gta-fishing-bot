import cv2, pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\Maxim.Mazurok\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'

img = cv2.imread('boot_menu_screenshot.png')
h, w = img.shape[:2]
x1, x2 = int(w*0.35), int(w*0.80)
y1, y2 = int(h*0.15), int(h*0.85)
roi = img[y1:y2, x1:x2]
gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
scale = max(1.0, 1500/gray.shape[1])
if scale > 1:
    gray = cv2.resize(gray, (int(gray.shape[1]*scale), int(gray.shape[0]*scale)), interpolation=cv2.INTER_CUBIC)
_, thresh = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY)
data = pytesseract.image_to_data(thresh, config='--psm 6 --oem 3', output_type=pytesseract.Output.DICT)

print("Block/Par/Line structure:")
for i, t in enumerate(data['text']):
    if t.strip():
        b = data['block_num'][i]
        p = data['par_num'][i]
        l = data['line_num'][i]
        y = data['top'][i]
        ww = data['width'][i]
        hh = data['height'][i]
        x = data['left'][i]
        print(f"  blk={b} par={p} line={l}  word={t.strip()!r:20s} at ({x},{y}) {ww}x{hh}")

# Now check: what if we use (block_num, par_num, line_num) as key?
print("\nGrouped by (block, par, line):")
groups = {}
for i, t in enumerate(data['text']):
    if t.strip():
        key = (data['block_num'][i], data['par_num'][i], data['line_num'][i])
        groups.setdefault(key, []).append(t.strip())
for key in sorted(groups):
    words = groups[key]
    print(f"  {key}: {words}")
