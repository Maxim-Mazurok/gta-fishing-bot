# GTA RP Fishing Minigame Automation Bot

Fully automated fishing bot for the GTA RP (FiveM) fishing minigame. Uses
computer vision to detect the minigame UI in real-time and a physics-aware
controller to play the minigame automatically.

## Table of Contents

- [Overview](#overview)
- [How It Works](#how-it-works)
- [Architecture](#architecture)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration Reference](#configuration-reference)
- [Detection Pipeline](#detection-pipeline)
- [Controller Design](#controller-design)
- [Physics Model](#physics-model)
- [Calibration & Testing](#calibration--testing)
- [Project Structure](#project-structure)
- [Development History](#development-history)

---

## Overview

The fishing minigame in GTA RP (FiveM) works as follows:

1. Press **"2"** to cast the fishing line.
2. Wait ~2 minutes for a fish to bite.
3. A **blue column** appears on screen with:
  - A **fishscale icon** (dark, moving up/down with sudden speed and direction changes).
   - A **white box** (player-controlled) overlaying the column.
   - An **orange/red progress bar** next to the column.
4. Hold **space** → box accelerates upward; release → box falls with gravity.
5. Progress bar fills while the fishscale is inside the white box, and drains when outside.
6. Fill the progress bar to 100% to catch the fish. There is no time limit and no fail state — progress can drain to 0% but the minigame continues.
7. After catching, press **"2"** again to repeat.

This bot automates the entire cycle: casting, waiting, playing the minigame, and repeating.

---

## How It Works

```
┌──────────────────────────────────────────────────────┐
│                    GAME WINDOW                       │
│                                                      │
│            ┌─── Blue Column (HSV detection)          │
│            │    ┌── White Box (low saturation)       │
│            │    │   ┌── Fishscale (brightness dip)   │
│            ▼    ▼   ▼                                │
│           ██████████░░░                              │
│           ██████████░░░  ← Progress bar (red fill)   │
│           ██████████░░░                              │
│           ███░░░░░░░░░░                              │
│           ███░░♦░░░░░░░  ← Fish inside white box     │
│           ███░░░░░░░░░░                              │
│           ██████████░░░                              │
│           ██████████░░░                              │
│                                                      │
└──────────────────────────────────────────────────────┘
         │
         ▼ Screen Capture (mss, 60 FPS)
         │
         ▼ HSV Color Detection (OpenCV)
         │
         ├── find_bar()      → Locate blue column
         ├── detect_elements() → Find fish, box, progress
         │
         ▼ PD Controller with Physics Model
         │
         ├── error     = fish_predicted - box_center
         ├── error_rate = fish_velocity - box_velocity
         ├── duty = HOVER - Kp·error - Kd·error_rate
         ├── accumulator PWM → True/False
         │
         ▼ Input Injection (pydirectinput)
         │
         └── keyDown('space') / keyUp('space')
```

---

## Architecture

The system has three layers:

### Layer 1: Screen Capture & Detection

- **`ScreenCapture`**: Uses `mss` for fast screen grabbing. Captures the center
  region for initial bar search, then narrows to just the bar area during gameplay.
- **`BarDetector`**: Computer vision pipeline using HSV color thresholding to
  detect and track the blue column, white box, fishscale position, and progress
  bar fill level.

### Layer 2: Control

- **`FishingController`**: Accumulator-based PWM controller with proportional
  and derivative terms. Uses measured physics (gravity, thrust) to compute
  optimal hold/release patterns.

### Layer 3: Game State Machine

- **`GameState`**: Manages the game flow through five states:
  `IDLE → CASTING → WAITING → MINIGAME → CAUGHT → IDLE`

---

## Installation

### Prerequisites

- **Windows** (required for `pydirectinput` and `mss` screen capture)
- **Python 3.10+**
- **FiveM** (GTA RP client) running
- **Administrator privileges** (required for `pydirectinput` input injection)

### Setup

```powershell
# Create virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install numpy opencv-python mss scipy pydirectinput

# Install test dependencies (optional)
pip install pytest pytest-benchmark
```

### Dependencies

| Package | Purpose |
|---|---|
| `numpy` | Array operations, signal processing |
| `opencv-python` | Image processing (HSV conversion, color detection) |
| `mss` | Fast Windows screen capture |
| `scipy` | Signal filtering (`uniform_filter1d`) |
| `pydirectinput` | Windows input injection (game input) |
| `pytest` | Test framework (optional) |
| `pytest-benchmark` | Performance benchmarks (optional) |

---

## Usage

### Full Automation

```powershell
# Run with admin rights (required for input injection)
.\run.ps1

# Or manually:
python fish.py              # Full automation
python fish.py --debug      # With debug visualization window
python fish.py --reel       # Skip casting, just play minigame
```

### Test Mode

```powershell
# Test on a single image
python fish.py --test path/to/screenshot.png

# Test on a directory of frames
python fish.py --test "2026-03-29 23-47-40"
```

### Running Tests

```powershell
# Run all tests
pytest tests/ -v

# Run with benchmarks
pytest tests/ -v --benchmark-columns=mean,stddev,rounds

# Run only E2E tests
pytest tests/test_e2e_detection.py -v

# Run only unit tests
pytest tests/test_bar_detector.py tests/test_controller.py -v

# Run simulator-based controller evaluation
python evaluate_simulation.py --difficulty medium --episodes 25

# Run live white-box physics calibration against the active minigame
python calibrate_live_box_physics.py

# Run existing regression tests
python test_detection_regression.py
python test_stream.py --verbose
```

### Calibration

```powershell
# Interactive calibration tool
python calibrate.py "2026-03-29 23-47-40"
```

---

## Configuration Reference

### Detection Thresholds

| Parameter | Value | Description |
|---|---|---|
| `BLUE_H_MIN` / `BLUE_H_MAX` | 85 / 115 | HSV hue range for blue column |
| `BLUE_S_MIN` | 25 | Minimum saturation for blue detection |
| `BLUE_V_MIN` | 20 | Minimum value (brightness) for blue detection |
| `WHITE_BOX_SAT_THRESHOLD` | 55 | Saturation below this = white box |
| `FISH_BRIGHTNESS_DROP` | 12 | Brightness dip threshold for fishscale |
| `PROGRESS_H_MIN` / `PROGRESS_H_MAX` | 0 / 12 | Hue range for red/orange progress bar |
| `PROGRESS_S_MIN` | 100 | Minimum saturation for progress detection |
| `PROGRESS_V_MIN` | 80 | Minimum brightness for progress detection |

### Game Timing

| Parameter | Value | Description |
|---|---|---|
| `CAST_DELAY` | 3.0s | Wait after catch before recasting |
| `BITE_WAIT` | 120.0s | Wait for fish to bite |
| `MINIGAME_GRACE` | 5.0s | Grace period before catch detection |
| `CONTROL_HZ` | 60 | Control loop frequency (Hz) |
| `BAR_REDETECT_INTERVAL` | 3.0s | Between bar position re-checks |

### Controller Parameters

| Parameter | Value | Description |
|---|---|---|
| `Kp` | 1.5 | Proportional gain |
| `Kd` | 1.0 | Derivative gain (on error rate) |
| `HOVER` | Auto-loaded | Neutral duty cycle derived from valid live calibration runs |
| `LOOKAHEAD` | 0.10s | Fish position prediction time |

---

## Detection Pipeline

### 1. Bar Finding (`find_bar`)

1. Convert frame to HSV color space.
2. Try progressively lower brightness thresholds (V=200, 150, 100, 75).
3. Find columns with bright blue pixels (H=85-115, S≥25).
4. Group contiguous columns and validate:
   - Width: 1-5% of image width
   - Height: >12% of image height
   - Aspect ratio: >8:1 (tall and narrow)
5. Select the group with the highest bright-pixel score.

### 2. Element Detection (`detect_elements`)

**White Box Detection:**
- Compute mean saturation per row within the blue column.
- Rows with saturation < 55 belong to the white box.
- Find the largest contiguous cluster of low-saturation rows.

**Fishscale Detection (two-pass):**

*Pass 1 — Outside White Box (high confidence):*
- Smooth row brightness and compute local averages.
- Find rows with brightness dip > 12 below local average.
- Filter: must have high saturation (>70) and be outside white box region.
- Cluster dark rows and pick the cluster with the deepest dip.

*Pass 2 — Inside White Box (fallback):*
- Search only within white box bounds.
- Use relaxed brightness threshold (-2 from local average).
- Cluster and pick the best candidate.

*Fallback — Velocity Prediction:*
- If neither pass finds the fish, predict position from velocity history.
- Velocity is estimated from a short recent window so the tracker can adapt
  when the fish switches between slower and faster movement phases.

**Progress Bar Detection:**
- Extract the strip to the right of the blue column.
- Apply HSV mask for red/orange (H=0-12, S≥100, V≥80).
- Count filled rows from bottom up.

### 3. Velocity Tracking

- Maintain a rolling history of (timestamp, fish_y) tuples (max 20).
- Compute velocity as `(y_last - y_first) / (t_last - t_first)`.
- This smooths out quantization noise from pixel-level detection.

---

## Controller Design

The controller uses a **proportional-derivative (PD) control** strategy with
**accumulator-based PWM** output.

### Control Law

```
fish_predicted = fish_y + fish_velocity × LOOKAHEAD
error = fish_predicted - box_center
box_velocity = Δbox_center / Δt
error_rate = fish_velocity - box_velocity
duty = HOVER - Kp × error - Kd × error_rate
```

- **Error term**: drives the box toward the fish.
- **Error-rate term**: provides natural braking — when the box is approaching
  the fish, the error rate opposes the error and reduces duty.
- **HOVER**: baseline duty that keeps the box stationary (counteracts gravity).

### PWM Output

Instead of fixed-period PWM, the controller uses an **accumulator**:

```
accumulator += duty
if accumulator ≥ 1.0:
    accumulator -= 1.0
    output = HOLD (keyDown space)
else:
    output = RELEASE (keyUp space)
```

This spreads hold/release frames evenly across time, giving smoother control
than fixed-period PWM cycles.

---

## Physics Model

Physics are measured experimentally using `measure_box_physics.py` and the
live fitter in `calibrate_live_box_physics.py`. The main app now scans
`live_physics_calibration/*/summary.json`, filters outlier sessions, and uses
the median of valid runs for the controller and simulator. Legacy defaults are
only used when no valid live calibration sessions are available.

Controlled experiments include:

| Parameter | Value | Method |
|---|---|---|
| **Gravity** (downward accel when released) | Auto-loaded | Median of valid live fits |
| **Thrust** (effective upward force while held) | Auto-loaded | Median of valid live fits |
| **Hover duty** | Auto-loaded | gravity / thrust from the active profile |
| **Fish speed** | Variable | Estimated online from the most recent detections |
| **Input lag** | ~100ms | Pulse response measurement |

These values inform the controller's `HOVER`, physics projection, and the
simulator that runs controller regression tests.

---

## Calibration & Testing

### Ground Truth Calibration

The `calibrate.py` tool allows interactive calibration:

1. Loads frame sequences from recording directories.
2. Runs detection and displays results.
3. Allows manual marking of true fishscale positions.
4. Saves results to `calibration_results.json`.

The calibration file contains 113 frames with ground-truth fishscale positions,
box boundaries, and whether the fish is inside the white box.

### Live Projection Calibration

When the main bot runs with `--debug`, it now records projection calibration
artifacts in `live_debug_runs/<session>/`:

- `telemetry.jsonl`: per-frame live detector/controller telemetry
- `projection_calibration.jsonl`: predicted fish/box meeting plans resolved
  against future observed frames
- `projection_summary.json`: aggregate timing, fish prediction, and box
  prediction errors, progress-growth reward statistics, and suggested
  adjustments for lookahead, gravity, and thrust

This gives a direct way to see whether the controller predicted the fish and
white box would meet where they actually met, and what parts of the model are
systematically early, late, weak, or aggressive.

Progress growth is treated as the most reliable live reward signal: if the
progress bar is increasing, the bot is doing something useful even when the
detected fish point is not perfectly centered in the detected white box.

### Test Suite

The project includes a comprehensive test suite:

| Test File | Type | What It Tests |
|---|---|---|
| `tests/test_bar_detector.py` | Unit | BarDetector init, find_bar, detect_elements, velocity, debug |
| `tests/test_controller.py` | Unit | FishingController PWM, physics, gains, reset, state |
| `tests/test_config.py` | Unit | Configuration constants, physics consistency |
| `tests/test_e2e_detection.py` | E2E | Detection accuracy vs ground truth, achievements |
| `tests/test_simulation.py` | Simulation | Seeded controller regression against randomized fish motion using the active calibrated physics and progress-growth reward |
| `tests/test_live_box_calibration.py` | Calibration | Live box-physics fitting helpers and synthetic recovery |
| `tests/test_benchmarks.py` | Perf | Detection & controller latency benchmarks |
| `test_detection_regression.py` | Regression | Known-good/bad frame guard tests |
| `test_stream.py` | Integration | Stream processing with velocity tracking |
| `test_perframe.py` | Ad-hoc | Per-frame fresh-detector detection rates |

### Achievement Criteria

| Achievement | Requirement | Description |
|---|---|---|
| Detection Accuracy | ≥ 80% | Calibrated frames within ±0.035 tolerance |
| Zero Crashes | 0 crashes | Processing entire recording without exceptions |
| Bar Finding | ≥ 95% | Bar found on minigame frames |
| Controller Stability | < 90 transitions/100 frames | No wild oscillation |
| Detection Speed | < 16ms mean | Meets 60 FPS budget |
| Controller Speed | < 1ms mean | Negligible overhead |

---

## Project Structure

```
├── fish.py                        # Main application (BarDetector, FishingController, GameState)
├── run.ps1                        # PowerShell launcher (auto-elevates to admin)
├── calibrate.py                   # Interactive ground-truth calibration tool
├── calibration_results.json       # 113 calibrated frame ground-truth entries
│
├── tests/                         # Test suite
│   ├── conftest.py                # Shared fixtures and helpers
│   ├── test_bar_detector.py       # BarDetector unit tests
│   ├── test_controller.py         # FishingController unit tests
│   ├── test_config.py             # Configuration validation tests
│   ├── test_e2e_detection.py      # E2E detection accuracy & achievements
│   └── test_benchmarks.py         # Performance benchmarks
│
├── test_detection_regression.py   # Regression guard tests
├── test_stream.py                 # Stream detection integration test
├── test_detection.py              # Batch detection test
├── test_perframe.py               # Per-frame detection test
├── test_overlap.py                # Fishscale-in-white-box test
│
├── measure_physics.py             # Fish position dynamics measurement
├── measure_box_physics.py         # Box physics measurement (7 experiments)
├── simulation.py                  # Docs-derived fishing minigame simulator
├── evaluate_simulation.py         # CLI evaluation runner for seeded simulation episodes
├── calibrate_live_box_physics.py  # Live input-driven box-physics calibration UI
├── physics_data.csv               # Fish position time-series data
├── box_physics_data.csv           # Box physics time-series data
├── _fit_physics.py                # Physics model fitting (gravity, thrust)
│
├── analyze_frame.py               # HSV color statistics analysis
├── analyze_bugs.py                # Bug investigation tool
├── analyze_detail.py              # 4x zoomed crop analysis
├── analyze_precise.py             # Per-pixel color sampling
├── analyze_overlap.py             # Fishscale/white-box overlap analysis
├── analyze_uniformity.py          # Pixel distribution analysis
├── extract_frames.py              # Video → PNG frame extraction
├── debug_live.py                  # Live debugging tool
├── verify_fixes.py                # Fix verification script
│
├── _patch_detection.py            # Detection improvement patches
├── _patch_controller.py           # Controller rewrite patches
├── _patch_braking.py              # Error-rate derivative patch
├── _patch_physics_controller.py   # Physics-informed controller patch
├── _patch_hybrid_ctrl.py          # Hybrid control strategy patch
├── _patch_fallback.py             # Fallback mechanism patch
├── _fix_controller.py             # Controller bugfix patches
├── _apply_all.py                  # Patch applicator
├── _apply_all_changes.py          # Alternative patch applicator
├── _apply_edits.py                # Edit applicator
│
├── 2026-03-29 23-47-40/           # Recording 1 frames (3622 PNGs)
├── 2026-03-29 23-51-17/           # Recording 2 frames (1601 PNGs)
└── diag_blue_gone/                # Diagnostic images (blue bar disappearance)
```

---

## Development History

The project went through several iterations of refinement:

1. **Initial version**: Binary hold/release controller with hysteresis threshold.
2. **PWM controller**: Switched to duty-cycle-based control for finer granularity.
3. **Proportional control**: Added Kp gain tuned from physics measurements.
4. **Accumulator PWM**: Replaced fixed-period PWM with accumulator for even distribution.
5. **Error-rate derivative**: Added Kd term tracking box velocity for natural braking.
6. **Detection hardening**: Multiple iterations fixing fishscale detection edge cases,
   especially when the fishscale overlaps with the white box.
7. **Physics calibration**: Measured gravity (3.24 bar/s²), thrust (3.61 bar/s²),
   and hover duty (47%) through controlled experiments.

Each `_patch_*.py` file corresponds to a specific improvement iteration.
