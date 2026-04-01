"""Automation loop smoke tests and live-debug helpers."""

from types import SimpleNamespace

import automation


def test_detect_overlap_jump_when_fish_crosses_box():
    """Large fish jumps across the box center should trigger a debug dump reason."""
    detector = SimpleNamespace(
        fish_y=0.66,
        box_top=0.54,
        box_bottom=0.64,
        box_center=0.59,
    )

    reason = automation._detect_overlap_jump(detector, prev_fish_y=0.52)

    assert reason == 'fish_jumped_below_box'


def test_detect_overlap_jump_ignores_small_motion():
    """Normal in-box motion should not be treated as a suspicious jump."""
    detector = SimpleNamespace(
        fish_y=0.602,
        box_top=0.55,
        box_bottom=0.65,
        box_center=0.60,
    )

    reason = automation._detect_overlap_jump(detector, prev_fish_y=0.58)

    assert reason is None