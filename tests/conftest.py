"""Shared pytest fixtures for the fishing bot test suite."""
import json
import pytest

from tests.helpers import (
    BarDetector, FishingController,
    CALIBRATION_FILE, HAS_CALIBRATION, HAS_FRAMES_1, HAS_FRAMES_2,
)

# ── Skip markers ──────────────────────────────────────────────────────
requires_frames_1 = pytest.mark.skipif(
    not HAS_FRAMES_1, reason="Recording 1 frames not available"
)
requires_frames_2 = pytest.mark.skipif(
    not HAS_FRAMES_2, reason="Recording 2 frames not available"
)
requires_calibration = pytest.mark.skipif(
    not HAS_CALIBRATION, reason="calibration_results.json not available"
)


# ── Fixtures ───────────────────────────────────────────────────────────
@pytest.fixture
def detector():
    """Fresh BarDetector instance."""
    return BarDetector()


@pytest.fixture
def controller():
    """Fresh FishingController instance."""
    return FishingController()


@pytest.fixture
def calibration_data():
    """Load calibration ground-truth data."""
    if not HAS_CALIBRATION:
        pytest.skip("calibration_results.json not available")
    with open(CALIBRATION_FILE) as f:
        return json.load(f)
