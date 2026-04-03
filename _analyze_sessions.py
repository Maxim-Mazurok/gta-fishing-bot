import os, json, glob

# Analyze the transition points in sessions - when minigame is re-detected
# and what the blue ratios look like
for sess in ['20260404_032550', '20260404_031713', '20260404_030349']:
    tpath = f'live_debug_runs/{sess}/telemetry.jsonl'
    if not os.path.exists(tpath):
        continue
    with open(tpath) as f:
        lines = f.readlines()

    notes = []
    for i, line in enumerate(lines):
        d = json.loads(line)
        note = d.get('note')
        frame = d.get('frame')
        progress = d.get('progress', 0)
        fish_y = d.get('fish_y', 0)
        box_top = d.get('box_top', 0)
        box_bottom = d.get('box_bottom', 0)
        method = d.get('method', '')
        if note:
            notes.append((frame, note, progress, fish_y, f'{box_top:.3f}-{box_bottom:.3f}', method))

    print(f'\n=== {sess} ({len(lines)} frames) ===')
    for n in notes:
        print(f'  frame={n[0]:4d} note={n[1]:20s} prog={n[2]:.3f} fish={n[3]:.3f} box={n[4]} method={n[5]}')

    # Show last 5 frames before gaps (where state likely changed)
    frames = [json.loads(l) for l in lines]
    # Find where frame numbers jump (state transition happened)
    for i in range(1, len(frames)):
        gap = frames[i]['frame'] - frames[i-1]['frame']
        if gap > 2:
            prev = frames[i-1]
            next_ = frames[i]
            print(f'  GAP at frame {prev["frame"]}->{next_["frame"]} '
                  f'prog={prev["progress"]:.3f}->{next_["progress"]:.3f} '
                  f'box=[{prev["box_top"]:.3f},{prev["box_bottom"]:.3f}]')
