"""Verify old EMA vs new median speed model with a misdetection spike."""
from collections import deque

SPEED_BANDS = (0.18, 0.30, 0.60)
SPEED_BAND_TOLERANCE = 0.12
SPEED_ESTIMATE_MIN = 0.05
SPEED_ESTIMATE_MAX = 0.60
SPEED_HISTORY_SIZE = 30

def snap(speed):
    if speed < SPEED_ESTIMATE_MIN:
        return 0.0
    nearest = min(SPEED_BANDS, key=lambda b: abs(b - speed))
    if abs(nearest - speed) <= SPEED_BAND_TOLERANCE:
        return nearest
    return speed

# Simulate: normal velocities then a spike then normal again
velocities = [0.22, 0.25, 0.19, 0.24, 0.21, 0.23, 0.20, 0.25, 0.22, 0.18,
              3.5,   # misdetection spike
              1.2,   # another bad one
              0.22, 0.25, 0.19, 0.24, 0.21, 0.23]

history = deque(maxlen=SPEED_HISTORY_SIZE)
old_speed = 0.0

print(f"{'Vel':>6} {'Snap':>6} {'OldEMA':>8} {'OldBand':>8} {'NewMed':>8} {'NewBnd':>8}")
print("-" * 56)

for v in velocities:
    speed = abs(v)
    snapped = snap(speed) if speed >= SPEED_ESTIMATE_MIN else 0.0

    # Old model (EMA, no clamp)
    if speed >= SPEED_ESTIMATE_MIN:
        if old_speed <= 0.0:
            old_speed = snapped
        else:
            old_speed = 0.65 * old_speed + 0.35 * snapped
        old_band = snap(old_speed)
    else:
        old_band = snap(old_speed)

    # New model (clamp + median)
    if speed >= SPEED_ESTIMATE_MIN and speed <= SPEED_ESTIMATE_MAX:
        snapped_new = snap(speed)
        history.append(snapped_new)
        if len(history) >= 3:
            new_speed = sorted(history)[len(history) // 2]
        else:
            new_speed = snapped_new
        new_band = snap(new_speed)
    else:
        # Rejected by clamp
        if len(history) >= 3:
            new_speed = sorted(history)[len(history) // 2]
        else:
            new_speed = 0
        new_band = snap(new_speed) if new_speed > 0 else 0

    marker = " <-- SPIKE" if speed > 0.7 else ""
    print(f"{v:>6.2f} {snapped:>6.3f} {old_speed:>8.3f} {old_band:>8.3f} {new_speed:>8.3f} {new_band:>8.3f}{marker}")
