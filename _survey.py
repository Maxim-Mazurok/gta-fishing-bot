import os, json

sessions = sorted([d for d in os.listdir('live_debug_runs') if d.startswith('20260404_')])
for sess in sessions:
    tpath = f'live_debug_runs/{sess}/telemetry.jsonl'
    if not os.path.exists(tpath):
        print(f'{sess}: no telemetry')
        continue
    with open(tpath) as f:
        lines = f.readlines()
    if not lines:
        print(f'{sess}: empty')
        continue
    f1 = json.loads(lines[0])
    fl = json.loads(lines[-1])
    nframes = len(lines)
    max_progress = max(json.loads(l).get('progress', 0) for l in lines)
    notes = [json.loads(l).get('note') for l in lines if json.loads(l).get('note')]
    has_catch = 'fish-caught' in notes
    region = f1.get('region', {})
    rl = region.get('left', '?')
    print(f'{sess}: {nframes:4d}f  max_prog={max_progress:.3f}  catch={has_catch}  region_left={rl}  notes={notes[:3]}')
