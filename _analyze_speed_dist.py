"""Analyze true fish speed distribution across sessions, filtering misdetections."""
import json, glob, os, statistics, math

def analyze_session_distribution(session_dir):
    telemetry_file = os.path.join(session_dir, "telemetry.jsonl")
    if not os.path.exists(telemetry_file):
        return None

    entries = []
    with open(telemetry_file) as f:
        for line in f:
            d = json.loads(line)
            if d.get("state") == "MINIGAME":
                entries.append(d)

    if len(entries) < 10:
        return None

    # Method 1: fish_velocity (EMA-smoothed)
    velocities = [abs(e["fish_velocity"]) for e in entries
                  if e.get("fish_velocity") is not None and abs(e["fish_velocity"]) > 0.01]

    # Method 2: fish_speed (the running estimate)
    speeds = [e["fish_speed"] for e in entries
              if e.get("fish_speed") is not None and e["fish_speed"] > 0.01]

    # Method 3: fish_speed_band
    bands = [e["fish_speed_band"] for e in entries
             if e.get("fish_speed_band") is not None and e["fish_speed_band"] > 0.01]

    # Method 4: raw frame-to-frame speed from detected_fish_y  
    # Only use "outside-dip" detections (most reliable) to avoid template noise
    raw_speeds_all = []
    raw_speeds_outside = []
    prev_y, prev_t, prev_method = None, None, None
    for e in entries:
        if e.get("detected_fish_y") is not None:
            y = e["detected_fish_y"]
            t = e["time"]
            method = e.get("method", "")
            if prev_y is not None and prev_t is not None:
                dt = t - prev_t
                if 0.001 < dt < 0.5:  # skip huge gaps (pauses)
                    spd = abs(y - prev_y) / dt
                    raw_speeds_all.append(spd)
                    if method == "outside-dip" and prev_method == "outside-dip":
                        raw_speeds_outside.append(spd)
            prev_y, prev_t, prev_method = y, t, method

    return {
        "session": os.path.basename(session_dir),
        "frames": len(entries),
        "velocities": velocities,
        "speeds": speeds,
        "bands": bands,
        "raw_all": raw_speeds_all,
        "raw_outside": raw_speeds_outside,
    }


def percentiles(data, pcts=[5, 10, 25, 50, 75, 90, 95]):
    if not data:
        return {}
    s = sorted(data)
    n = len(s)
    return {p: s[min(int(n * p / 100), n - 1)] for p in pcts}


def print_distribution(name, data):
    if not data:
        print(f"  {name}: no data")
        return
    pcts = percentiles(data)
    print(f"  {name} (n={len(data)}):")
    print(f"    mean={statistics.mean(data):.4f}  stdev={statistics.stdev(data):.4f}" if len(data) > 1 else f"    mean={statistics.mean(data):.4f}")
    print(f"    p5={pcts[5]:.4f}  p10={pcts[10]:.4f}  p25={pcts[25]:.4f}  "
          f"p50={pcts[50]:.4f}  p75={pcts[75]:.4f}  p90={pcts[90]:.4f}  p95={pcts[95]:.4f}")


def histogram(data, bins=20, width=50):
    if not data:
        return
    # Clip to p99 to ignore extreme outliers in the histogram
    s = sorted(data)
    clip = s[min(int(len(s) * 0.99), len(s) - 1)]
    clipped = [x for x in data if x <= clip]
    
    lo = min(clipped)
    hi = max(clipped)
    if hi <= lo:
        return
    step = (hi - lo) / bins
    counts = [0] * bins
    for x in clipped:
        idx = min(int((x - lo) / step), bins - 1)
        counts[idx] += 1
    mx = max(counts)
    for i, c in enumerate(counts):
        bar_len = int(c / mx * width) if mx > 0 else 0
        lo_val = lo + i * step
        hi_val = lo + (i + 1) * step
        print(f"    {lo_val:>6.3f}-{hi_val:>6.3f} | {'#' * bar_len} {c}")


base = r"c:\Users\Maxim.Mazurok\gta-fishing-bot\live_debug_runs"
sessions = sorted(glob.glob(os.path.join(base, "2026*")))

# Collect all data
all_velocities = []
all_speeds = []
all_bands = []
all_raw_outside = []

per_session = []
for s in sessions:
    r = analyze_session_distribution(s)
    if r:
        per_session.append(r)
        all_velocities.extend(r["velocities"])
        all_speeds.extend(r["speeds"])
        all_bands.extend(r["bands"])
        all_raw_outside.extend(r["raw_outside"])

print(f"=== AGGREGATE DISTRIBUTION across {len(per_session)} sessions ===\n")

print("fish_velocity (EMA-smoothed, |v| > 0.01):")
print_distribution("fish_velocity", all_velocities)
print("  Histogram:")
histogram(all_velocities)

print("\nfish_speed (running estimate):")
print_distribution("fish_speed", all_speeds)
print("  Histogram:")
histogram(all_speeds)

print("\nfish_speed_band (quantized band):")
print_distribution("fish_speed_band", all_bands)
print("  Histogram:")
histogram(all_bands)

print("\nraw frame-to-frame speed (outside-dip only, dt < 0.5s):")
print_distribution("raw_outside", all_raw_outside)
print("  Histogram:")
histogram(all_raw_outside)

# Now show per-session median speeds (using fish_speed which is the running estimate)
print("\n\n=== PER-SESSION MEDIAN fish_speed (running estimate) ===")
print(f"{'Session':<20} {'Frm':>5} {'Median':>7} {'P25':>7} {'P75':>7} {'IQR':>7} {'P90':>7}")
print("-" * 70)
for r in per_session:
    if r["speeds"]:
        p = percentiles(r["speeds"])
        iqr = p[75] - p[25]
        print(f"{r['session']:<20} {r['frames']:>5} {p[50]:>7.3f} {p[25]:>7.3f} {p[75]:>7.3f} {iqr:>7.3f} {p[90]:>7.3f}")

# Focus: what is the "normal" speed if we filter out sessions with high misdetection
print("\n\n=== STABLE SESSIONS (median fish_speed < 0.35) ===")
stable = [r for r in per_session if r["speeds"] and percentiles(r["speeds"])[50] < 0.35]
stable_speeds = []
for r in stable:
    stable_speeds.extend(r["speeds"])
if stable_speeds:
    print_distribution("fish_speed (stable)", stable_speeds)
    print("  Histogram:")
    histogram(stable_speeds, bins=30)

print("\n\n=== HIGH-SPEED SESSIONS (median fish_speed >= 0.35) ===")
fast = [r for r in per_session if r["speeds"] and percentiles(r["speeds"])[50] >= 0.35]
for r in fast:
    p = percentiles(r["speeds"])
    print(f"  {r['session']}: median={p[50]:.3f} p90={p[90]:.3f} frames={r['frames']}")

# Key question: is fish_speed bimodal or unimodal within a single session?
print("\n\n=== WITHIN-SESSION SPEED STABILITY ===")
print("(coefficient of variation = stdev/mean, lower = more stable)")
print(f"{'Session':<20} {'Frm':>5} {'Mean':>7} {'Stdev':>7} {'CV':>6} {'Bands':>20}")
print("-" * 80)
for r in per_session:
    if r["speeds"] and len(r["speeds"]) > 2:
        mn = statistics.mean(r["speeds"])
        sd = statistics.stdev(r["speeds"])
        cv = sd / mn if mn > 0 else 0
        # Count unique bands
        band_counts = {}
        for b in r["bands"]:
            b_round = round(b, 2)
            band_counts[b_round] = band_counts.get(b_round, 0) + 1
        top_bands = sorted(band_counts.items(), key=lambda x: -x[1])[:4]
        band_str = " ".join(f"{b:.2f}({c})" for b, c in top_bands)
        print(f"{r['session']:<20} {r['frames']:>5} {mn:>7.3f} {sd:>7.3f} {cv:>6.2f} {band_str}")
