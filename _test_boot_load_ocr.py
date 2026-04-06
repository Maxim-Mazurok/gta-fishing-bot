"""Test boot load OCR: verify count reading and grid positions on a screenshot.

Usage:
    python _test_boot_load_ocr.py <screenshot_path>

Draws annotated grid overlays (left + right) and attempts to OCR the item
count at the configured inventory cell.
"""

import sys
import cv2
import numpy as np
import pytesseract

pytesseract.pytesseract.tesseract_cmd = (
    r'C:\Users\Maxim.Mazurok\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'
)

# Grid constants (must match inventory.py BootLoadHandler)
INV_GRID_X0 = 0.198
BOOT_GRID_X0 = 0.558
GRID_Y0 = 0.355
CELL_W = 0.053
CELL_H = 0.088
GRID_COLS = 6
GRID_ROWS = 4


def draw_grid(img, x0_frac, y0_frac, label, color):
    """Draw a grid overlay on the image."""
    h, w = img.shape[:2]
    x0 = int(w * x0_frac)
    y0 = int(h * y0_frac)
    cw = int(w * CELL_W)
    ch = int(h * CELL_H)

    for r in range(GRID_ROWS):
        for c in range(GRID_COLS):
            x1 = x0 + c * cw
            y1 = y0 + r * ch
            x2 = x1 + cw
            y2 = y1 + ch
            cv2.rectangle(img, (x1, y1), (x2, y2), color, 1)
            # Cell label
            cv2.putText(img, f"{r+1},{c+1}", (x1 + 2, y1 + 12),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.3, color, 1)

    # Grid label
    cv2.putText(img, label, (x0, int(h * y0_frac) - 5),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)


def read_cell_count(img, grid_x0_frac, row, col):
    """OCR the count at the bottom of a grid cell.  Returns (int_or_None, roi_crop)."""
    h, w = img.shape[:2]
    grid_x0 = w * grid_x0_frac
    grid_y0 = h * GRID_Y0
    cell_w = w * CELL_W
    cell_h = h * CELL_H

    # Count text region: bottom of cell
    x1 = int(grid_x0 + col * cell_w - cell_w * 0.1)
    x2 = int(grid_x0 + (col + 1) * cell_w + cell_w * 0.1)
    y1 = int(grid_y0 + row * cell_h + cell_h * 0.60)
    y2 = int(grid_y0 + (row + 1) * cell_h + cell_h * 0.10)

    x1, x2 = max(0, x1), min(w, x2)
    y1, y2 = max(0, y1), min(h, y2)

    roi = img[y1:y2, x1:x2]
    if roi.size == 0:
        return None, None

    # Preprocess: grayscale, upscale, threshold
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    scale = max(1.0, 300 / gray.shape[1])
    if scale > 1:
        gray = cv2.resize(gray, (int(gray.shape[1] * scale), int(gray.shape[0] * scale)),
                          interpolation=cv2.INTER_CUBIC)
    _, thresh = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY)

    try:
        text = pytesseract.image_to_string(
            thresh,
            config='--psm 7 --oem 3 -c tessedit_char_whitelist=0123456789',
        )
    except Exception as e:
        print(f"  OCR error: {e}")
        return None, roi

    digits = ''.join(c for c in text if c.isdigit())
    return (int(digits) if digits else None), roi


def main():
    if len(sys.argv) < 2:
        print("Usage: python _test_boot_load_ocr.py <screenshot_path>")
        sys.exit(1)

    path = sys.argv[1]
    img = cv2.imread(path)
    if img is None:
        print(f"Could not load image: {path}")
        sys.exit(1)

    h, w = img.shape[:2]
    print(f"Image: {w}x{h}")

    # Draw grids
    annotated = img.copy()
    draw_grid(annotated, INV_GRID_X0, GRID_Y0, "LEFT (Inventory)", (0, 255, 0))
    draw_grid(annotated, BOOT_GRID_X0, GRID_Y0, "RIGHT (Boot)", (0, 255, 255))

    # Read counts from all cells in both grids
    print("\n--- LEFT GRID (Personal Inventory) ---")
    for r in range(GRID_ROWS):
        counts = []
        for c in range(GRID_COLS):
            val, _ = read_cell_count(img, INV_GRID_X0, r, c)
            counts.append(str(val) if val is not None else "-")
        print(f"  Row {r+1}: {', '.join(counts)}")

    print("\n--- RIGHT GRID (Vehicle Boot) ---")
    for r in range(GRID_ROWS):
        counts = []
        for c in range(GRID_COLS):
            val, _ = read_cell_count(img, BOOT_GRID_X0, r, c)
            counts.append(str(val) if val is not None else "-")
        print(f"  Row {r+1}: {', '.join(counts)}")

    # Highlight the configured cells
    cw = int(w * CELL_W)
    ch = int(h * CELL_H)

    # Default configured cells (from .env.example defaults)
    inv_row, inv_col = 0, 3   # row=1 col=4 (0-indexed)
    boot_row, boot_col = 0, 0  # row=1 col=1 (0-indexed)

    # Highlight inventory monitor cell (green box, thick)
    ix1 = int(w * INV_GRID_X0) + inv_col * cw
    iy1 = int(h * GRID_Y0) + inv_row * ch
    cv2.rectangle(annotated, (ix1, iy1), (ix1 + cw, iy1 + ch), (0, 255, 0), 3)
    inv_count, _ = read_cell_count(img, INV_GRID_X0, inv_row, inv_col)
    cv2.putText(annotated, f"MONITOR: {inv_count}", (ix1, iy1 - 5),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Highlight boot source cell (cyan box, thick)
    bx1 = int(w * BOOT_GRID_X0) + boot_col * cw
    by1 = int(h * GRID_Y0) + boot_row * ch
    cv2.rectangle(annotated, (bx1, by1), (bx1 + cw, by1 + ch), (0, 255, 255), 3)
    boot_count, _ = read_cell_count(img, BOOT_GRID_X0, boot_row, boot_col)
    cv2.putText(annotated, f"SOURCE: {boot_count}", (bx1, by1 - 5),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)

    print(f"\nConfigured monitor cell (inv row=1, col=4): count = {inv_count}")
    print(f"Configured source cell (boot row=1, col=1): count = {boot_count}")

    out_path = path.rsplit('.', 1)[0] + '_boot_load_annotated.png'
    cv2.imwrite(out_path, annotated)
    print(f"\nAnnotated image saved to: {out_path}")


if __name__ == '__main__':
    main()
