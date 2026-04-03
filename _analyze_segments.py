import os, json

# Look at the first few and last few frames of each minigame segment
# These are from 20260404_032550 which had 3 minigame entries
sess = '20260404_032550'
tpath = f'live_debug_runs/{sess}/telemetry.jsonl'
with open(tpath) as f:
    lines = f.readlines()

frames = [json.loads(l) for l in lines]
# Find transitions where the frame number resets to 1
segments = []
current = []
for f in frames:
    if f['frame'] == 1 and current:
        segments.append(current)
        current = []
    current.append(f)
if current:
    segments.append(current)

for si, seg in enumerate(segments):
    print(f'\n--- Segment {si+1}: {len(seg)} frames ---')
    # First 3 frames
    for f in seg[:3]:
        print(f"  frame={f['frame']:4d} prog={f['progress']:.3f} fish={f['fish_y']:.3f} "
              f"box=[{f['box_top']:.3f},{f['box_bottom']:.3f}] method={f['method']}")
    # Last 3 frames
    if len(seg) > 6:
        print(f"  ...")
        for f in seg[-3:]:
            print(f"  frame={f['frame']:4d} prog={f['progress']:.3f} fish={f['fish_y']:.3f} "
                  f"box=[{f['box_top']:.3f},{f['box_bottom']:.3f}] method={f['method']}")

# Now check what max_blue_seen value the bar reaches
# Since we don't log blue ratio in telemetry, let's check progress patterns
# High progress that drops could indicate the bar was lost
for si, seg in enumerate(segments):
    progs = [f['progress'] for f in seg]
    max_p = max(progs)
    end_p = progs[-1] if progs else 0
    box_last = seg[-1]['box_top'] if seg else 0
    print(f'\nSeg {si+1}: max_prog={max_p:.3f} end_prog={end_p:.3f} '
          f'end_box_top={box_last:.3f} end_box_bot={seg[-1]["box_bottom"]:.3f}')
