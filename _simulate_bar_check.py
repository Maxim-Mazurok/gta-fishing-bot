"""Simulate the bar signal check against telemetry to see when it would trigger."""
import json

for session in ['20260404_063622', '20260404_064521']:
    path = f'live_debug_runs/{session}/telemetry.jsonl'
    lines = open(path).readlines()
    data = [json.loads(l) for l in lines]
    
    print(f"\n=== {session}: {len(data)} frames ===")
    
    # Notes
    for d in data:
        n = d.get('note', '')
        if n and n != 'None':
            print(f"  t+{d['time'] - data[0]['time']:.1f}: {n}")
    
    # Simulate: check box_span and pretend strong blue isn't there when progress=0
    # In reality, post-bar frames see water (no strong blue) and invalid box
    bar_signal_lost = None
    for d in data:
        t = d['time']
        box_span = d['box_bottom'] - d['box_top']
        has_valid_box = 0.03 < box_span < 0.50
        prog = d['progress']
        
        # We don't have the actual strong blue ratio in telemetry, but we know:
        # - During real minigame (prog > 0): strong blue is present
        # - After bar gone (prog = 0 for extended period): no strong blue
        # For simulation, use progress > 0 as a proxy for "has strong blue"
        has_strong_blue = prog > 0
        
        if has_valid_box or has_strong_blue:
            bar_signal_lost = None
        else:
            if bar_signal_lost is None:
                bar_signal_lost = t
            elif t - bar_signal_lost >= 2.0:
                elapsed = t - data[0]['time']
                print(f"  BAR SIGNAL CHECK would trigger at t+{elapsed:.1f}s "
                      f"(box_span={box_span:.2f}, prog={prog:.2f})")
                bar_signal_lost = None  # reset to see next trigger point
    
    print(f"  Total duration: {data[-1]['time'] - data[0]['time']:.1f}s")
