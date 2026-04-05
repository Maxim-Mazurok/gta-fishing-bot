"""Measure fish speed across recent debug sessions."""
import json, glob, os, statistics

def analyze_session(session_dir):
    telemetry_file = os.path.join(session_dir, "telemetry.jsonl")
    if not os.path.exists(telemetry_file):
        return None
    
    speeds = []
    velocities = []
    frames = []
    speed_bands = []
    
    with open(telemetry_file) as f:
        for line in f:
            d = json.loads(line)
            if d.get("state") == "MINIGAME" and d.get("fish_velocity") is not None:
                v = abs(d["fish_velocity"])
                if v > 0.01:
                    velocities.append(v)
                if d.get("fish_speed") is not None and d["fish_speed"] > 0.01:
                    speeds.append(d["fish_speed"])
                if d.get("fish_speed_band") is not None and d["fish_speed_band"] > 0.01:
                    speed_bands.append(d["fish_speed_band"])
                frames.append(d["frame"])
    
    if not velocities:
        return None
    
    # Compute frame-to-frame deltas from detected_fish_y for actual pixel speed
    actual_speeds = []
    prev_y = None
    prev_t = None
    with open(telemetry_file) as f:
        for line in f:
            d = json.loads(line)
            if d.get("state") == "MINIGAME" and d.get("detected_fish_y") is not None:
                y = d["detected_fish_y"]
                t = d["time"]
                if prev_y is not None and prev_t is not None:
                    dt = t - prev_t
                    if dt > 0.001:
                        actual_speeds.append(abs(y - prev_y) / dt)
                prev_y = y
                prev_t = t
    
    return {
        "session": os.path.basename(session_dir),
        "frames": len(frames),
        "vel_mean": statistics.mean(velocities),
        "vel_med": statistics.median(velocities),
        "vel_max": max(velocities),
        "spd_mean": statistics.mean(speeds) if speeds else 0,
        "band_mean": statistics.mean(speed_bands) if speed_bands else 0,
        "act_mean": statistics.mean(actual_speeds) if actual_speeds else 0,
        "act_med": statistics.median(actual_speeds) if actual_speeds else 0,
        "act_p90": sorted(actual_speeds)[int(len(actual_speeds)*0.9)] if actual_speeds else 0,
        "act_max": max(actual_speeds) if actual_speeds else 0,
    }

base = r"c:\Users\Maxim.Mazurok\gta-fishing-bot\live_debug_runs"
sessions = sorted(glob.glob(os.path.join(base, "2026*")))
targets = sessions[-20:]

results = []
for s in targets:
    r = analyze_session(s)
    if r:
        results.append(r)

print(f"Analyzing {len(results)} sessions\n")

header = f"{'Session':<20} {'Frm':>4} {'VelMn':>6} {'VelMd':>6} {'VelMx':>6} {'SpdMn':>6} {'BndMn':>6} {'ActMn':>6} {'ActMd':>6} {'ActP90':>6} {'ActMx':>6}"
print(header)
print("-" * len(header))
for r in results:
    print(
        f"{r['session']:<20} "
        f"{r['frames']:>4} "
        f"{r['vel_mean']:>6.3f} "
        f"{r['vel_med']:>6.3f} "
        f"{r['vel_max']:>6.3f} "
        f"{r['spd_mean']:>6.3f} "
        f"{r['band_mean']:>6.3f} "
        f"{r['act_mean']:>6.3f} "
        f"{r['act_med']:>6.3f} "
        f"{r['act_p90']:>6.3f} "
        f"{r['act_max']:>6.3f}"
    )

# Show the latest session in detail
print("\n\n=== LATEST SESSION DETAIL ===")
latest = sessions[-1]
print(f"Session: {os.path.basename(latest)}")
tel = os.path.join(latest, "telemetry.jsonl")
if os.path.exists(tel):
    with open(tel) as f:
        lines = [json.loads(l) for l in f]
    
    mg = [l for l in lines if l.get("state") == "MINIGAME"]
    if mg:
        duration = mg[-1]["time"] - mg[0]["time"]
        print(f"Duration: {duration:.1f}s, Frames: {len(mg)}")
        
        # Speed over time windows
        window = 20
        print(f"\nSpeed by frame window (window={window}):")
        for i in range(0, len(mg), window):
            chunk = mg[i:i+window]
            vels = [abs(c["fish_velocity"]) for c in chunk if c.get("fish_velocity") and abs(c["fish_velocity"]) > 0.01]
            spds = [c["fish_speed"] for c in chunk if c.get("fish_speed") and c["fish_speed"] > 0.01]
            bands = [c["fish_speed_band"] for c in chunk if c.get("fish_speed_band") and c["fish_speed_band"] > 0.01]
            if vels:
                f_start = chunk[0]["frame"]
                f_end = chunk[-1]["frame"]
                spd_str = f"{statistics.mean(spds):.3f}" if spds else "N/A"
                band_str = f"{statistics.mean(bands):.3f}" if bands else "N/A"
                print(
                    f"  Frames {f_start:>4}-{f_end:>4}: "
                    f"vel={statistics.mean(vels):.3f} "
                    f"spd={spd_str:>5} "
                    f"band={band_str:>5}"
                )
