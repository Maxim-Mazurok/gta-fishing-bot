"""Check actual HSV values of blue bar vs water in real and false frames."""
import cv2, numpy as np, json, os

BLUE_H_MIN, BLUE_H_MAX = 85, 115

def analyze_blue(img, label):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, s, v = hsv[:,:,0], hsv[:,:,1], hsv[:,:,2]
    
    # Mask for hue in blue range
    hue_blue = (h >= BLUE_H_MIN) & (h <= BLUE_H_MAX)
    
    if np.sum(hue_blue) == 0:
        print(f"  {label}: NO blue-hue pixels at all")
        return
    
    blue_s = s[hue_blue]
    blue_v = v[hue_blue]
    
    # Check at different S/V thresholds
    for s_min in [25, 50, 80, 120]:
        for v_min in [20, 50, 80, 120]:
            mask = (hue_blue) & (s >= s_min) & (v >= v_min)
            ratio = np.sum(mask) / max(mask.size, 1)
            if ratio > 0.001:
                print(f"  {label}: S>={s_min} V>={v_min}: {ratio:.1%} of pixels")
    
    print(f"  {label}: blue-hue pixel S: min={blue_s.min()} median={int(np.median(blue_s))} max={blue_s.max()}")
    print(f"  {label}: blue-hue pixel V: min={blue_v.min()} median={int(np.median(blue_v))} max={blue_v.max()}")

# Real bar frames from recordings
for rec_dir in ['2026-03-29 23-47-40', '2026-03-29 23-51-17']:
    frame_path = os.path.join(rec_dir, '001001.png')
    if os.path.exists(frame_path):
        img = cv2.imread(frame_path)
        if img is not None:
            print(f"\n=== REAL BAR: {rec_dir}/001001.png (full frame) ===")
            analyze_blue(img, "full")
            # Crop to approximate bar region (center-ish)
            h, w = img.shape[:2]
            cx, cy = w // 2, h // 2
            x1 = max(0, cx - 100)
            x2 = min(w, cx + 100)
            crop = img[:, x1:x2]
            analyze_blue(crop, "center strip")

# False positive frames from latest debug
for session in ['20260404_063622', '20260404_064521']:
    events_dir = f'live_debug_runs/{session}/events'
    if not os.path.exists(events_dir):
        continue
    # Get the last event's last raw frame
    events = sorted(os.listdir(events_dir))
    if events:
        last_event = events[-1]
        event_dir = os.path.join(events_dir, last_event)
        raw_files = sorted([f for f in os.listdir(event_dir) if f.endswith('_raw.png')])
        if raw_files:
            last_raw = os.path.join(event_dir, raw_files[-1])
            img = cv2.imread(last_raw)
            if img is not None:
                print(f"\n=== FALSE: {session}/{last_event}/{raw_files[-1]} ===")
                analyze_blue(img, "raw crop")

# Also check the search_fail images (no bar)
for session in ['20260404_063622']:
    sf_path = f'live_debug_runs/{session}/search_fail_000.png'
    if os.path.exists(sf_path):
        img = cv2.imread(sf_path)
        if img is not None:
            print(f"\n=== SEARCH FAIL (no bar, full screen): {session}/search_fail_000 ===")
            analyze_blue(img, "full")
