import json

lines = open('live_debug_runs/20260404_062947/telemetry.jsonl').readlines()
print(f"Total frames: {len(lines)}")
first = json.loads(lines[0])
last = json.loads(lines[-1])
print(f"First: t={first['time']:.1f} fish_y={first['fish_y']:.3f} box=[{first['box_top']:.3f},{first['box_bottom']:.3f}]")
print(f"Last:  t={last['time']:.1f} fish_y={last['fish_y']:.3f} box=[{last['box_top']:.3f},{last['box_bottom']:.3f}]")
print(f"Duration: {last['time'] - first['time']:.1f}s")

# When did progress drop to 0?
prev_prog = None
for l in lines:
    d = json.loads(l)
    prog = d['progress']
    if prev_prog is not None and prev_prog > 0 and prog == 0:
        print(f"\nProgress dropped to 0 at t={d['time']:.1f} (frame {d['frame']})")
        print(f"  Post-bar duration: {last['time'] - d['time']:.1f}s")
    prev_prog = prog

# Count methods after progress=0
from collections import Counter
method_counts = Counter()
post_bar_frames = 0
for l in lines:
    d = json.loads(l)
    if d['progress'] == 0:
        method_counts[d['method']] += 1
        post_bar_frames += 1
print(f"\nPost-bar frames: {post_bar_frames}")
print("Detection methods after bar gone:")
for method, count in method_counts.most_common():
    print(f"  {method}: {count}")

# Check fish_y ranges after bar gone
post_bar_fish = []
for l in lines:
    d = json.loads(l)
    if d['progress'] == 0:
        post_bar_fish.append(d['fish_y'])
if post_bar_fish:
    print(f"\nPost-bar fish_y: min={min(post_bar_fish):.3f} max={max(post_bar_fish):.3f}")
    # Check how often fish_y changes > 0.01
    moves = 0
    for i in range(1, len(post_bar_fish)):
        if abs(post_bar_fish[i] - post_bar_fish[i-1]) > 0.01:
            moves += 1
    print(f"Fish moves > 0.01 between consecutive frames: {moves}/{len(post_bar_fish)-1}")

# Analyze stuck periods with smarter threshold
print("\n--- Stuck analysis (threshold=0.02, window=3s) ---")
fish_times = []
for l in lines:
    d = json.loads(l)
    fish_times.append((d['time'], d['fish_y'], d['progress']))

last_y = None
last_moved = None
for t, y, prog in fish_times:
    if last_y is None:
        last_y = y
        last_moved = t
    elif abs(y - last_y) > 0.02:
        last_y = y
        last_moved = t
    elif t - last_moved >= 3.0:
        print(f"  STUCK {t - last_moved:5.1f}s at y={last_y:.3f} (t={last_moved:.1f}-{t:.1f}) prog={prog:.2f}")
        last_y = y
        last_moved = t

# Check the note field for any transitions
print("\nNotes in telemetry:")
for l in lines:
    d = json.loads(l)
    if d.get('note') and d['note'] != 'None':
        print(f"  t={d['time']:.1f} note={d['note']}")
