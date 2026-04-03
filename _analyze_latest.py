import json, os, sys

for session in ['20260404_064521', '20260404_063622']:
    path = f'live_debug_runs/{session}/telemetry.jsonl'
    if not os.path.exists(path):
        continue
    lines = open(path).readlines()
    data = [json.loads(l) for l in lines]
    if not data:
        continue
    
    dur = data[-1]['time'] - data[0]['time']
    print(f"\n=== Session {session}: {len(data)} frames, {dur:.1f}s ===")
    
    # Notes
    for d in data:
        n = d.get('note', '')
        if n and n != 'None':
            print(f"  note t={d['time'] - data[0]['time']:.1f}: {n}")
    
    # Progress stats
    zero_prog = sum(1 for d in data if d['progress'] == 0)
    print(f"  Progress: {zero_prog}/{len(data)} frames at 0 ({100*zero_prog/len(data):.0f}%)")
    
    # Box detection
    no_box = sum(1 for d in data if d['box_top'] == 0 and d['box_bottom'] == 0)
    full_box = sum(1 for d in data if d['box_bottom'] - d['box_top'] > 0.8)
    print(f"  Box: {no_box} no-box, {full_box} full-range (>0.8 span)")
    
    # Methods
    from collections import Counter
    methods = Counter(d['method'] for d in data)
    print(f"  Methods: {dict(methods.most_common())}")
    
    # Fish y range
    fish_ys = [d['fish_y'] for d in data]
    print(f"  Fish y: min={min(fish_ys):.3f} max={max(fish_ys):.3f}")
    
    # First 20 frames
    print(f"  First 15 frames:")
    for d in data[:15]:
        t = d['time'] - data[0]['time']
        print(f"    t+{t:5.2f} fy={d['fish_y']:.3f} box=[{d['box_top']:.3f},{d['box_bottom']:.3f}] "
              f"prog={d['progress']:.2f} method={d['method']}")
    
    # Last 15 frames
    print(f"  Last 15 frames:")
    for d in data[-15:]:
        t = d['time'] - data[0]['time']
        print(f"    t+{t:5.2f} fy={d['fish_y']:.3f} box=[{d['box_top']:.3f},{d['box_bottom']:.3f}] "
              f"prog={d['progress']:.2f} method={d['method']}")

# Check event images
for session in ['20260404_064521', '20260404_063622']:
    events_dir = f'live_debug_runs/{session}/events'
    if os.path.exists(events_dir):
        events = os.listdir(events_dir)
        print(f"\n{session} events: {events[:10]}")
    
    bar_dir = f'live_debug_runs/{session}/bar_detections'
    if os.path.exists(bar_dir):
        files = os.listdir(bar_dir)
        print(f"{session} bar_detections: {files}")
