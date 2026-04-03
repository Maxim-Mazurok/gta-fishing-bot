import json

lines = open('live_debug_runs/20260404_062947/telemetry.jsonl').readlines()
data = [json.loads(l) for l in lines]

# Find all minigame-detected boundaries
boundaries = []
for i, d in enumerate(data):
    note = d.get('note', '')
    if note and 'minigame-detected' in note:
        boundaries.append(i)

print(f"Minigame boundaries at frames: {boundaries}")
print(f"Times: {[data[i]['time'] for i in boundaries]}")

# For each segment, show progress pattern
for seg_idx, start_frame in enumerate(boundaries):
    end_frame = boundaries[seg_idx + 1] if seg_idx + 1 < len(boundaries) else len(data)
    segment = data[start_frame:end_frame]
    
    # Count progress=0 vs >0
    zero_prog = sum(1 for d in segment if d['progress'] == 0)
    nonzero_prog = sum(1 for d in segment if d['progress'] > 0)
    duration = segment[-1]['time'] - segment[0]['time']
    
    print(f"\nSegment {seg_idx}: frames {start_frame}-{end_frame-1}, "
          f"duration={duration:.1f}s, progress: zero={zero_prog} nonzero={nonzero_prog}")
    
    # First 5 seconds of progress
    t0 = segment[0]['time']
    print("  First 10s progress:")
    for d in segment:
        if d['time'] - t0 <= 10:
            print(f"    t+{d['time']-t0:5.2f} prog={d['progress']:.2f} method={d['method']}")
    
    # How long is the longest streak of prog=0?
    max_zero_streak = 0
    cur_streak = 0
    streak_start = None
    max_streak_start = None
    for d in segment:
        if d['progress'] == 0:
            if cur_streak == 0:
                streak_start = d['time']
            cur_streak += 1
        else:
            if cur_streak > max_zero_streak:
                max_zero_streak = cur_streak
                max_streak_start = streak_start
            cur_streak = 0
    if cur_streak > max_zero_streak:
        max_zero_streak = cur_streak
        max_streak_start = streak_start
    print(f"  Max prog=0 streak: {max_zero_streak} frames starting at t={max_streak_start:.1f}" 
          if max_streak_start else "  No zero streaks")
