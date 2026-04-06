"""Inventory detection and auto shift+click for the fishing bot.

Monitors the screen for the inventory UI (detected via OCR for "YOUR INVENTORY"
text), locates the grid slots, and shift+clicks the second row first column
to move items. Rate-limited to at most once every 26 seconds.

Also supports a "boot offload" mode: periodically opens a nearby vehicle's
boot (trunk) and shift+clicks items from personal inventory into the vehicle,
allowing longer unattended fishing sessions without hitting inventory limits.
"""

import os
import time
import cv2
import numpy as np
import pytesseract
from dotenv import load_dotenv

load_dotenv()

# Point pytesseract at the installed Tesseract binary
pytesseract.pytesseract.tesseract_cmd = (
    r'C:\Users\Maxim.Mazurok\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'
)

# Rate limit: minimum seconds between shift+clicks
INVENTORY_ACTION_COOLDOWN = 26.0

# Set to false to disable inventory shift+click entirely. Configure via .env file.
INVENTORY_ENABLED = os.environ.get('INVENTORY_ENABLED', 'true').lower() in ('1', 'true', 'yes')

# Grid slot to shift+click (1-indexed). Configure via .env file.
INVENTORY_ROW = int(os.environ.get('INVENTORY_ROW', '1')) - 1
INVENTORY_COL = int(os.environ.get('INVENTORY_COL', '4')) - 1

# --- Boot offload settings (env-configurable) ---
# Enable boot offload mode (disables regular inventory clicking when active).
BOOT_OFFLOAD_ENABLED = os.environ.get('BOOT_OFFLOAD_ENABLED', 'false').lower() in ('1', 'true', 'yes')
# Interval in seconds between offloads (default: 1 hour).
BOOT_OFFLOAD_INTERVAL = float(os.environ.get('BOOT_OFFLOAD_INTERVAL', '3600'))
# Number of shift+clicks to perform when offloading (default: 20).
BOOT_OFFLOAD_CLICKS = int(os.environ.get('BOOT_OFFLOAD_CLICKS', '20'))
# Delay in seconds between each shift+click (default: 1s).
BOOT_OFFLOAD_CLICK_DELAY = float(os.environ.get('BOOT_OFFLOAD_CLICK_DELAY', '1.0'))

# When boot offload is active, disable regular per-catch inventory clicking.
if BOOT_OFFLOAD_ENABLED and INVENTORY_ENABLED:
    print("[INV] Boot offload enabled — disabling regular inventory clicking")
    INVENTORY_ENABLED = False


class InventoryHandler:
    """Detects the inventory UI and shift+clicks grid slots."""

    def __init__(self):
        self._last_action_time = 0.0
        self._cached_slot = None        # (x, y) image-relative coords
        self._cached_window_size = None  # (width, height) when slot was detected

    def _is_on_cooldown(self):
        return (time.perf_counter() - self._last_action_time) < INVENTORY_ACTION_COOLDOWN

    def check_and_act(self, capture, pydirectinput):
        """Check if inventory is open and shift+click second row, first column.

        Args:
            capture: ScreenCapture instance (has ._region for game window).
            pydirectinput: The pydirectinput module for sending input.

        Returns:
            True if an action was performed, False otherwise.
        """
        if not INVENTORY_ENABLED:
            return False

        if self._is_on_cooldown():
            return False

        region = capture._region
        # Capture the full game window
        grab_region = {
            'left': region['left'],
            'top': region['top'],
            'width': region['width'],
            'height': region['height'],
        }
        try:
            screenshot = capture.sct.grab(grab_region)
        except Exception:
            try:
                capture.sct = __import__('mss').mss()
                screenshot = capture.sct.grab(grab_region)
            except Exception:
                return False

        img = np.array(screenshot)[:, :, :3]  # BGRA -> BGR

        # --- Step 1: OCR to detect "YOUR INVENTORY" text ---
        if not self._detect_inventory_text(img):
            return False

        # --- Step 2: Find the grid slot (use cache if window size unchanged) ---
        current_size = (region['width'], region['height'])
        if self._cached_slot is not None and self._cached_window_size == current_size:
            slot_center = self._cached_slot
        else:
            slot_center = self._find_grid_slot(img, row=INVENTORY_ROW, col=INVENTORY_COL)
            if slot_center is None:
                return False
            self._cached_slot = slot_center
            self._cached_window_size = current_size
            print(f"[INV] Cached grid slot at {slot_center} for window size {current_size}")

        # Convert to absolute screen coordinates
        abs_x = region['left'] + slot_center[0]
        abs_y = region['top'] + slot_center[1]

        # --- Step 3: Shift+click ---
        print(f"[INV] Shift+clicking inventory slot at ({abs_x}, {abs_y})")
        pydirectinput.keyDown('shift')
        time.sleep(0.05)
        pydirectinput.click(abs_x, abs_y)
        time.sleep(0.05)
        pydirectinput.keyUp('shift')
        self._last_action_time = time.perf_counter()
        return True

    def _detect_inventory_text(self, img):
        """Use OCR to check if 'YOUR INVENTORY' text is visible on screen."""
        h, w = img.shape[:2]

        # The "YOUR INVENTORY" text is in the upper portion of the screen,
        # roughly in the left-center area. Scan top 40%, middle 60% horizontally.
        roi_top = int(h * 0.15)
        roi_bottom = int(h * 0.45)
        roi_left = int(w * 0.15)
        roi_right = int(w * 0.65)
        roi = img[roi_top:roi_bottom, roi_left:roi_right]

        # Convert to grayscale and threshold to isolate white/light text
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY)

        # Run OCR with fast config
        try:
            text = pytesseract.image_to_string(
                thresh,
                config='--psm 6 --oem 3',
            )
        except Exception as e:
            print(f"[INV] OCR error: {e}")
            return False

        text_upper = text.upper()
        if 'YOUR INVENTORY' in text_upper or 'INVENTORY' in text_upper:
            return True
        return False

    def _find_grid_slot(self, img, row=1, col=0):
        """Find the pixel center of a specific grid slot (0-indexed row/col).

        Detects the semi-transparent grid boxes by looking for their rectangular
        edges using contour detection.

        Returns (x, y) in image coordinates, or None if not found.
        """
        h, w = img.shape[:2]

        # The inventory grid is in the left-center area of the screen
        # Based on the screenshot: roughly x=17%-52%, y=32%-78%
        roi_left = int(w * 0.17)
        roi_right = int(w * 0.52)
        roi_top = int(h * 0.32)
        roi_bottom = int(h * 0.78)
        roi = img[roi_top:roi_bottom, roi_left:roi_right]

        # Detect grid cell edges: the cells have a slightly lighter border
        # on a dark semi-transparent background
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

        # Edge detection to find grid lines
        edges = cv2.Canny(gray, 30, 100)

        # Dilate to connect nearby edges
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        dilated = cv2.dilate(edges, kernel, iterations=2)

        # Find contours
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        roi_h, roi_w = roi.shape[:2]
        # Expected cell size: roughly 1/9 to 1/6 of the grid width
        min_cell = int(roi_w * 0.06)
        max_cell = int(roi_w * 0.25)

        # Filter for rectangular contours that look like grid cells
        cells = []
        for cnt in contours:
            x, y, cw, ch = cv2.boundingRect(cnt)
            # Grid cells are roughly square
            aspect = cw / max(ch, 1)
            if 0.6 < aspect < 1.6 and min_cell < cw < max_cell and min_cell < ch < max_cell:
                cells.append((x, y, cw, ch))

        if len(cells) < 3:
            # Fallback: use a fixed grid layout based on screen proportions
            return self._fixed_grid_slot(img, row, col)

        # Sort cells by y then x to organize into rows
        cells.sort(key=lambda c: (c[1], c[0]))

        # Group into rows: cells within similar y positions
        rows = []
        current_row = [cells[0]]
        for cell in cells[1:]:
            if abs(cell[1] - current_row[0][1]) < current_row[0][3] * 0.5:
                current_row.append(cell)
            else:
                rows.append(sorted(current_row, key=lambda c: c[0]))
                current_row = [cell]
        rows.append(sorted(current_row, key=lambda c: c[0]))

        if row >= len(rows) or col >= len(rows[row]):
            # Not enough rows/cols detected, use fallback
            return self._fixed_grid_slot(img, row, col)

        # Get the target cell
        cell = rows[row][col]
        cx = roi_left + cell[0] + cell[2] // 2
        cy = roi_top + cell[1] + cell[3] // 2
        return (cx, cy)

    def _fixed_grid_slot(self, img, row=1, col=0):
        """Fallback: estimate grid slot position from screen proportions.

        Based on the inventory UI layout observed in the screenshot:
        - Grid starts at roughly x=20%, y=36% of the game window
        - Each cell is about 5.3% wide and 8.5% tall
        - Gap between cells is about 0.3%
        """
        h, w = img.shape[:2]

        # Grid origin (top-left of first cell)
        grid_x0 = int(w * 0.198)
        grid_y0 = int(h * 0.355)

        # Cell dimensions (including gap)
        cell_w = int(w * 0.056)
        cell_h = int(h * 0.088)

        # Target cell center
        cx = grid_x0 + col * cell_w + cell_w // 2
        cy = grid_y0 + row * cell_h + cell_h // 2

        # Sanity check: should be within screen bounds
        if 0 < cx < w and 0 < cy < h:
            return (cx, cy)
        return None


class BootOffloadHandler:
    """Periodically offloads inventory into a nearby vehicle boot (trunk).

    When the configured interval has elapsed, the next fish catch triggers
    the offload sequence:
      1. Press "e" to open the interaction menu.
      2. OCR-find the "Boot" option and click it.
      3. Wait for the boot UI ("VEHICLE BOOT") to fully load.
      4. Shift+click the configured inventory slot N times (transfers items).
      5. Press "2" to close the boot and immediately cast the rod again.
    """

    def __init__(self):
        self._last_offload_time = time.perf_counter()
        self._cached_slot = None
        self._cached_window_size = None

    def is_offload_due(self):
        """Return True when enough time has passed since the last offload."""
        if not BOOT_OFFLOAD_ENABLED:
            return False
        return (time.perf_counter() - self._last_offload_time) >= BOOT_OFFLOAD_INTERVAL

    def perform_offload(self, capture, pydirectinput):
        """Execute the full boot offload sequence.

        Returns True if the offload succeeded and "2" was pressed (casting).
        Returns False if any step failed (caller should fall back to normal flow).
        """
        region = capture._region
        elapsed_min = (time.perf_counter() - self._last_offload_time) / 60.0
        print(f"[BOOT] Starting offload ({BOOT_OFFLOAD_CLICKS} items, "
              f"{elapsed_min:.0f}min since last)...")

        # Step 1: Press "e" to open interaction menu
        print("[BOOT] Opening interaction menu (pressing 'e')...")
        pydirectinput.press('e')
        time.sleep(1.0)

        # Step 2: Find "Boot" text via OCR and click it
        if not self._find_and_click_boot(capture, region, pydirectinput):
            print("[BOOT] Could not find 'Boot' option — likely a false-positive catch")
            print("[BOOT] Pressing 'e' to close vehicle menu, will retry next catch")
            pydirectinput.press('e')
            time.sleep(0.5)
            return False

        # Step 3: Wait for boot UI to fully load
        if not self._wait_for_boot_ui(capture, region):
            print("[BOOT] Boot UI did not open properly — aborting offload")
            pydirectinput.press('e')
            time.sleep(0.5)
            return False

        # Step 4: Shift+click the inventory slot N times
        self._transfer_items(capture, region, pydirectinput)

        # Step 5: Press "2" to close boot and cast
        print("[BOOT] Pressing '2' to close boot and cast...")
        pydirectinput.press('2')
        time.sleep(1.0)

        self._last_offload_time = time.perf_counter()
        print("[BOOT] Offload complete!")
        return True

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _grab_screen(self, capture, region):
        """Capture the full game window as a BGR numpy array."""
        grab_region = {
            'left': region['left'],
            'top': region['top'],
            'width': region['width'],
            'height': region['height'],
        }
        try:
            screenshot = capture.sct.grab(grab_region)
        except Exception:
            capture.sct = __import__('mss').mss()
            screenshot = capture.sct.grab(grab_region)
        return np.array(screenshot)[:, :, :3]

    @staticmethod
    def _ocr_preprocess(img, target_width=1500):
        """Convert an image region to a thresholded grayscale, scaled so that
        its width is at least *target_width* pixels.  This ensures OCR gets
        consistently-sized text regardless of the source resolution.

        Returns (thresh, scale_factor).
        """
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        scale = max(1.0, target_width / gray.shape[1])
        if scale > 1:
            gray = cv2.resize(
                gray,
                (int(gray.shape[1] * scale), int(gray.shape[0] * scale)),
                interpolation=cv2.INTER_CUBIC,
            )
        _, thresh = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY)
        return thresh, scale

    @staticmethod
    def _crop_roi(img, x_frac, y_frac):
        """Crop an image region using fractional bounds (resolution-agnostic).

        Args:
            img: Source BGR image.
            x_frac: (left_frac, right_frac) — horizontal bounds as [0,1] fractions.
            y_frac: (top_frac, bottom_frac) — vertical bounds as [0,1] fractions.

        Returns:
            (roi, roi_left, roi_top) where roi_left/roi_top are pixel offsets
            to convert ROI coords back to full-image coords.
        """
        h, w = img.shape[:2]
        x1, x2 = int(w * x_frac[0]), int(w * x_frac[1])
        y1, y2 = int(h * y_frac[0]), int(h * y_frac[1])
        return img[y1:y2, x1:x2], x1, y1

    def _find_and_click_boot(self, capture, region, pydirectinput, retries=5):
        """OCR the screen to locate the standalone 'Boot' menu option and click it.

        Uses y-proximity (not line_num) to distinguish the standalone "Boot"
        entry from "Unlock Vehicle Boot".  Words within ±half their own height
        are considered on the same visual line.  Icon OCR artifacts (< 3 chars)
        are ignored.

        Fallback: if the vehicle menu is detected (other items visible) but
        "Boot" isn't found by OCR, click at its expected position in the menu.
        """
        menu_detected = False
        # Known vehicle menu items (lowercase) — if we see these, menu is open
        _MENU_MARKERS = {'engine', 'inspect', 'hood', 'unlock', 'vehicle', 'enter', 'tyres', 'tires', 'fix'}

        for attempt in range(retries):
            img = self._grab_screen(capture, region)
            roi, roi_x, roi_y = self._crop_roi(img, (0.35, 0.80), (0.15, 0.85))
            # Use higher upscaling (2500) — menu text is small
            thresh, scale = self._ocr_preprocess(roi, target_width=2500)

            try:
                data = pytesseract.image_to_data(
                    thresh,
                    config='--psm 6 --oem 3',
                    output_type=pytesseract.Output.DICT,
                )
            except Exception as e:
                print(f"[BOOT] OCR error: {e}")
                time.sleep(0.5)
                continue

            # Collect all "real" words (3+ chars) with their vertical centres
            real_entries = []
            for i, text in enumerate(data['text']):
                word = text.strip()
                if len(word) >= 3:
                    cy = data['top'][i] + data['height'][i] / 2
                    real_entries.append((i, word.lower(), cy, data['height'][i]))

            words_found = [w for _, w, _, _ in real_entries]
            if attempt == 0:
                print(f"[BOOT] OCR words: {words_found}")

            # Check if vehicle menu is open
            if any(w in _MENU_MARKERS for w in words_found):
                menu_detected = True

            for idx, word, cy, wh in real_entries:
                if word != 'boot':
                    continue
                # Words on the same visual line: y-centre within half-height
                tolerance = max(wh, 20)
                neighbours = [
                    w for _, w, wy, _ in real_entries
                    if abs(wy - cy) < tolerance and w != 'boot'
                ]
                if not neighbours:
                    x = roi_x + int(data['left'][idx] / scale + data['width'][idx] / scale / 2)
                    y = roi_y + int(data['top'][idx] / scale + data['height'][idx] / scale / 2)
                    abs_x = region['left'] + x
                    abs_y = region['top'] + y
                    print(f"[BOOT] Found standalone 'Boot' at ({abs_x}, {abs_y}), clicking...")
                    pydirectinput.click(abs_x, abs_y)
                    time.sleep(0.5)
                    return True
                else:
                    print(f"[BOOT] Skipping 'Boot' near: {neighbours}")

            print(f"[BOOT] 'Boot' text not found (attempt {attempt + 1}/{retries})")
            time.sleep(1.0)

        # Fallback: menu is open but "Boot" OCR failed — click expected position
        if menu_detected:
            print("[BOOT] Menu detected but 'Boot' not readable — using positional fallback")
            # "Boot" is the 6th item in the menu (0-indexed: 5), positioned at ~55% down
            # the menu area. Menu is roughly at x=55-65%, y=38-62% of screen.
            h, w = img.shape[:2]
            # Boot row: approximately 55% of screen height
            fallback_x = int(w * 0.60)
            fallback_y = int(h * 0.555)
            abs_x = region['left'] + fallback_x
            abs_y = region['top'] + fallback_y
            print(f"[BOOT] Clicking fallback position ({abs_x}, {abs_y})...")
            pydirectinput.click(abs_x, abs_y)
            time.sleep(0.5)
            return True

        return False

    def _wait_for_boot_ui(self, capture, region, timeout=10.0):
        """Wait until 'VEHICLE BOOT' appears and 'Loading' disappears."""
        start = time.perf_counter()
        attempt = 0
        while time.perf_counter() - start < timeout:
            attempt += 1
            img = self._grab_screen(capture, region)
            # Right half, upper portion — where the "VEHICLE BOOT" header appears
            roi, _, _ = self._crop_roi(img, (0.45, 0.95), (0.0, 0.40))
            thresh, _scale = self._ocr_preprocess(roi)

            try:
                text = pytesseract.image_to_string(thresh, config='--psm 6 --oem 3')
            except Exception as e:
                print(f"[BOOT] OCR error on attempt {attempt}: {e}")
                time.sleep(0.5)
                continue

            text_upper = text.upper()
            has_vehicle_boot = 'VEHICLE BOOT' in text_upper
            has_loading = 'LOADING' in text_upper

            text_summary = ' | '.join(
                line.strip() for line in text.split('\n') if line.strip()
            )
            print(f"[BOOT] UI check #{attempt}: "
                  f"VEHICLE_BOOT={has_vehicle_boot} LOADING={has_loading} "
                  f"text=[{text_summary}]")

            if has_vehicle_boot and not has_loading:
                print("[BOOT] Boot UI is open and loaded")
                return True

            if has_vehicle_boot and has_loading:
                print("[BOOT] Boot is loading...")

            time.sleep(0.5)

        print("[BOOT] Timeout waiting for boot UI")
        return False

    def _get_grid_slot(self, img, region):
        """Return the (x, y) image-relative center of the target inventory cell.

        Uses proportional coordinates which scale with any resolution since the
        game UI scales uniformly.  Cell size/position is expressed as fractions
        of the captured window dimensions.
        """
        current_size = (region['width'], region['height'])
        if self._cached_slot is not None and self._cached_window_size == current_size:
            return self._cached_slot

        h, w = img.shape[:2]
        # Grid origin and cell size as fractions — resolution-agnostic
        grid_x0 = int(w * 0.198)
        grid_y0 = int(h * 0.355)
        cell_w = int(w * 0.056)
        cell_h = int(h * 0.088)
        cx = grid_x0 + INVENTORY_COL * cell_w + cell_w // 2
        cy = grid_y0 + INVENTORY_ROW * cell_h + cell_h // 2

        if 0 < cx < w and 0 < cy < h:
            self._cached_slot = (cx, cy)
            self._cached_window_size = current_size
            print(f"[BOOT] Grid slot at ({cx}, {cy}) for "
                  f"row={INVENTORY_ROW + 1}, col={INVENTORY_COL + 1}")
            return (cx, cy)
        return None

    def _transfer_items(self, capture, region, pydirectinput):
        """Shift+click the inventory slot BOOT_OFFLOAD_CLICKS times."""
        img = self._grab_screen(capture, region)
        slot = self._get_grid_slot(img, region)
        if slot is None:
            print("[BOOT] Could not determine grid slot position")
            return

        abs_x = region['left'] + slot[0]
        abs_y = region['top'] + slot[1]

        print(f"[BOOT] Shift+clicking ({abs_x}, {abs_y}) x{BOOT_OFFLOAD_CLICKS} "
              f"(delay={BOOT_OFFLOAD_CLICK_DELAY}s)...")
        for i in range(BOOT_OFFLOAD_CLICKS):
            pydirectinput.keyDown('shift')
            time.sleep(0.05)
            pydirectinput.click(abs_x, abs_y)
            time.sleep(0.05)
            pydirectinput.keyUp('shift')
            if i < BOOT_OFFLOAD_CLICKS - 1:
                time.sleep(BOOT_OFFLOAD_CLICK_DELAY)

        print(f"[BOOT] Transferred {BOOT_OFFLOAD_CLICKS} items")
