import json, os

for session in ['20260402_001714', '20260401_232716']:
    path = f'live_debug_runs/{session}/telemetry.jsonl'
    if not os.path.exists(path):
        print(f'{session}: no telemetry')
        continue
    lines = open(path).readlines()
    data = [json.loads(l) for l in lines]
    dur = data[-1]['time'] - data[0]['time']
    print(f"\n{session}: {len(data)} frames, dur={dur:.1f}s")
    
    spans = [d['box_bottom'] - d['box_top'] for d in data]
    valid_box = sum(1 for s in spans if 0.03 < s < 0.50)
    invalid_box = sum(1 for s in spans if s >= 0.50 or s <= 0.03)
    prog_zero = sum(1 for d in data if d['progress'] == 0)
    print(f"  Valid box: {valid_box}, Invalid: {invalid_box}, Prog=0: {prog_zero}/{len(data)}")
    
    bar_signal_lost = None
    triggers = 0
    for d in data:
        t = d['time']
        box_span = d['box_bottom'] - d['box_top']
        has_valid_box = 0.03 < box_span < 0.50
        has_prog = d['progress'] > 0
        if has_valid_box or has_prog:
            bar_signal_lost = None
        else:
            if bar_signal_lost is None:
                bar_signal_lost = t
            elif t - bar_signal_lost >= 2.0:
                triggers += 1
                elapsed = t - data[0]['time']
                print(f"  WOULD TRIGGER at t+{elapsed:.1f}s span={box_span:.2f} prog={d['progress']:.2f}")
                bar_signal_lost = None
    if triggers == 0:
        print("  No triggers (good!)")
