"""Verify resolution-agnostic boot offload detection on screenshots."""
import cv2
import sys
sys.path.insert(0, '.')
from inventory import BootOffloadHandler

handler = BootOffloadHandler()

for name in ['boot_menu_screenshot.png', 'boot_ui_screenshot.png']:
    img = cv2.imread(name)
    if img is None:
        print(f"SKIP {name} (not found)")
        continue
    h, w = img.shape[:2]
    print(f"\n=== {name} ({w}x{h}) ===")

    # Test _crop_roi + _ocr_preprocess
    roi, rx, ry = handler._crop_roi(img, (0.35, 0.80), (0.15, 0.85))
    thresh, scale = handler._ocr_preprocess(roi)
    print(f"  Menu ROI: {roi.shape[1]}x{roi.shape[0]}, scale={scale:.2f}, thresh={thresh.shape[1]}x{thresh.shape[0]}")

    roi2, _, _ = handler._crop_roi(img, (0.45, 0.95), (0.0, 0.40))
    thresh2, scale2 = handler._ocr_preprocess(roi2)
    print(f"  Boot UI ROI: {roi2.shape[1]}x{roi2.shape[0]}, scale={scale2:.2f}")

    # Test boot UI OCR
    import pytesseract
    pytesseract.pytesseract.tesseract_cmd = r'C:\Users\Maxim.Mazurok\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'
    text = pytesseract.image_to_string(thresh2, config='--psm 6 --oem 3')
    has_vb = 'VEHICLE BOOT' in text.upper()
    print(f"  VEHICLE BOOT found: {has_vb}")

    # Test grid slot
    slot = handler._get_grid_slot(img, {'width': w, 'height': h})
    handler._cached_slot = None  # reset cache
    handler._cached_window_size = None
    print(f"  Grid slot: {slot}")

    # Simulate lower resolutions
    for target_w in [1920, 1280, 3840]:
        ratio = target_w / w
        target_h = int(h * ratio)
        resized = cv2.resize(img, (target_w, target_h))
        r2, _, _ = handler._crop_roi(resized, (0.45, 0.95), (0.0, 0.40))
        t2, s2 = handler._ocr_preprocess(r2)
        txt = pytesseract.image_to_string(t2, config='--psm 6 --oem 3')
        has = 'VEHICLE BOOT' in txt.upper()
        slot2 = handler._get_grid_slot(resized, {'width': target_w, 'height': target_h})
        handler._cached_slot = None
        handler._cached_window_size = None
        print(f"  @{target_w}x{target_h}: roi={r2.shape[1]}x{r2.shape[0]} scale={s2:.2f} VEHICLE_BOOT={has} slot={slot2}")
