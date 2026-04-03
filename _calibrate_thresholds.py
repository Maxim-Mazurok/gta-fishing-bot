"""Analyze the false positive from session 20260404_043224 and calibrate thresholds."""
import cv2
import numpy as np
import os
import json
import glob

from detection import BarDetector
from config import SEARCH_MARGIN_X_FRAC, SEARCH_MARGIN_Y_FRAC, BLUE_H_MIN, BLUE_H_MAX

# What find_bar currently requires:
# - min_bar_width: 1% of img width
# - aspect ratio > 5:1
# - edge_contrast >= 8
# - bg_contrast >= 6
# - vert_lines >= 1

# Test on real bar frames with different threshold levels
print("=== REAL BAR: edge/bg contrast measurements ===")
for frame_id in ['001001', '001205', '001250']:
    frame_path = f'2026-03-29 23-47-40/{frame_id}.png'
    if not os.path.exists(frame_path):
        continue
    img = cv2.imread(frame_path)
    h, w = img.shape[:2]
    cx, cy = w // 2, h // 2
    mx = int(w * SEARCH_MARGIN_X_FRAC)
    my = int(h * SEARCH_MARGIN_Y_FRAC)
    roi = img[cy-my:cy+my, cx-mx:cx+mx]
    rh, rw = roi.shape[:2]

    det = BarDetector(bootstrap_template=False)
    found = det.find_bar(roi)
    if found:
        bar_w = det.col_x2 - det.col_x1 + 1
        bar_h = det.col_y2 - det.col_y1 + 1
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

        # Edge contrast
        border_pad = min(5, max(2, bar_w))
        left_start = max(0, det.col_x1 - border_pad)
        right_end = min(rw, det.col_x2 + border_pad + 1)
        border_strip = gray[det.col_y1:det.col_y2+1, left_start:right_end]
        profile = np.mean(border_strip.astype(float), axis=0)
        diffs = np.diff(profile)
        edge_contrast = max(abs(np.min(diffs)), abs(np.max(diffs)))

        # Bg contrast
        bar_brightness = np.mean(gray[det.col_y1:det.col_y2+1, det.col_x1:det.col_x2+1])
        left_bg = gray[det.col_y1:det.col_y2+1, max(0,det.col_x1-10):max(0,det.col_x1-1)]
        right_bg = gray[det.col_y1:det.col_y2+1, min(rw,det.col_x2+2):min(rw,det.col_x2+11)]
        lb = np.mean(left_bg) if left_bg.size > 0 else bar_brightness
        rb = np.mean(right_bg) if right_bg.size > 0 else bar_brightness
        bg_contrast = abs(bar_brightness - (lb + rb) / 2)

        # Blue fill within detected bar
        bar_hsv = hsv[det.col_y1:det.col_y2+1, det.col_x1:det.col_x2+1]
        bar_blue = cv2.inRange(bar_hsv, np.array([BLUE_H_MIN, 25, 20]), np.array([BLUE_H_MAX, 255, 255]))
        bar_blue_ratio = np.sum(bar_blue > 0) / max(bar_blue.size, 1)

        # Row continuity: what % of rows have >50% blue pixels
        row_blue_frac = np.mean(bar_blue > 0, axis=1)
        blue_rows_50 = np.sum(row_blue_frac > 0.5) / bar_h

        # Vertical edge lines
        bar_border = gray[det.col_y1:det.col_y2+1, max(0,det.col_x1-3):min(rw,det.col_x2+4)]
        canny = cv2.Canny(bar_border, 50, 150)
        lines = cv2.HoughLinesP(canny, 1, np.pi/180, threshold=20,
                                minLineLength=max(20, bar_h//4), maxLineGap=5)
        vert_lines = 0
        if lines is not None:
            for line in lines:
                lx1, ly1, lx2, ly2 = line[0]
                dx = lx2 - lx1
                dy = ly2 - ly1
                angle = abs(np.degrees(np.arctan2(dy, dx))) if dx != 0 else 90
                if angle > 75:
                    vert_lines += 1

        print(f"  {frame_id}: bar={bar_w}x{bar_h} edge_contrast={edge_contrast:.1f} "
              f"bg_contrast={bg_contrast:.1f} vert_lines={vert_lines} "
              f"bar_blue={bar_blue_ratio:.3f} blue_rows={blue_rows_50:.3f}")


# Also test on second recording
print("\n=== SECOND RECORDING ===")
for frame_id in ['001001', '001100', '001200']:
    frame_path = f'2026-03-29 23-51-17/{frame_id}.png'
    if not os.path.exists(frame_path):
        continue
    img = cv2.imread(frame_path)
    h, w = img.shape[:2]
    cx, cy = w // 2, h // 2
    mx = int(w * SEARCH_MARGIN_X_FRAC)
    my = int(h * SEARCH_MARGIN_Y_FRAC)
    roi = img[cy-my:cy+my, cx-mx:cx+mx]
    rh, rw = roi.shape[:2]
    det = BarDetector(bootstrap_template=False)
    found = det.find_bar(roi)
    if found:
        bar_w = det.col_x2 - det.col_x1 + 1
        bar_h = det.col_y2 - det.col_y1 + 1
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        border_pad = min(5, max(2, bar_w))
        left_start = max(0, det.col_x1 - border_pad)
        right_end = min(rw, det.col_x2 + border_pad + 1)
        border_strip = gray[det.col_y1:det.col_y2+1, left_start:right_end]
        profile = np.mean(border_strip.astype(float), axis=0)
        diffs = np.diff(profile)
        edge_contrast = max(abs(np.min(diffs)), abs(np.max(diffs)))
        bar_brightness = np.mean(gray[det.col_y1:det.col_y2+1, det.col_x1:det.col_x2+1])
        left_bg = gray[det.col_y1:det.col_y2+1, max(0,det.col_x1-10):max(0,det.col_x1-1)]
        right_bg = gray[det.col_y1:det.col_y2+1, min(rw,det.col_x2+2):min(rw,det.col_x2+11)]
        lb = np.mean(left_bg) if left_bg.size > 0 else bar_brightness
        rb = np.mean(right_bg) if right_bg.size > 0 else bar_brightness
        bg_contrast = abs(bar_brightness - (lb + rb) / 2)
        bar_hsv = hsv[det.col_y1:det.col_y2+1, det.col_x1:det.col_x2+1]
        bar_blue = cv2.inRange(bar_hsv, np.array([BLUE_H_MIN, 25, 20]), np.array([BLUE_H_MAX, 255, 255]))
        bar_blue_ratio = np.sum(bar_blue > 0) / max(bar_blue.size, 1)
        row_blue_frac = np.mean(bar_blue > 0, axis=1)
        blue_rows_50 = np.sum(row_blue_frac > 0.5) / bar_h
        print(f"  {frame_id}: bar={bar_w}x{bar_h} edge_contrast={edge_contrast:.1f} "
              f"bg_contrast={bg_contrast:.1f} bar_blue={bar_blue_ratio:.3f} "
              f"blue_rows={blue_rows_50:.3f}")

# Check the false positives
print("\n=== FALSE POSITIVES ===")
for name in ['detected_bar.png', 'bar_area.png']:
    img = cv2.imread(name)
    if img is None:
        continue
    det = BarDetector(bootstrap_template=False)
    found = det.find_bar(img)
    if found:
        print(f"  {name}: STILL DETECTED (shouldn't be!)")
    else:
        print(f"  {name}: rejected OK - {det._last_find_bar_diag}")
