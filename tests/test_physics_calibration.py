"""Tests for loading live physics calibration profiles."""

import json

from physics_calibration import DEFAULT_GRAVITY, DEFAULT_THRUST, load_live_physics_profile


def _write_summary(root, session_name, gravity, hold_accel, fit_error, worst_rmse):
    session_dir = root / session_name
    session_dir.mkdir(parents=True)
    payload = {
        'params': {
            'release_gravity': gravity,
            'hold_accel': hold_accel,
            'suggested_thrust': gravity + hold_accel,
        },
        'fit_error': fit_error,
        'experiments': [
            {'name': 'exp1', 'rmse': worst_rmse, 'samples': 100},
            {'name': 'exp2', 'rmse': min(worst_rmse, 0.03), 'samples': 100},
            {'name': 'exp3', 'rmse': min(worst_rmse, 0.02), 'samples': 100},
        ],
    }
    (session_dir / 'summary.json').write_text(json.dumps(payload), encoding='utf-8')


def test_load_live_physics_profile_falls_back_to_defaults(tmp_path):
    profile = load_live_physics_profile(tmp_path)

    assert profile.gravity == DEFAULT_GRAVITY
    assert profile.thrust == DEFAULT_THRUST
    assert profile.source == 'defaults'


def test_load_live_physics_profile_uses_median_of_valid_sessions(tmp_path):
    _write_summary(tmp_path, 'good_a', 3.0, 2.8, 0.003, 0.05)
    _write_summary(tmp_path, 'good_b', 3.2, 2.9, 0.002, 0.04)
    _write_summary(tmp_path, 'good_c', 3.4, 3.1, 0.001, 0.03)
    _write_summary(tmp_path, 'bad_bounds', 8.0, 0.5, 0.001, 0.03)
    _write_summary(tmp_path, 'bad_error', 3.3, 3.0, 0.05, 0.03)
    _write_summary(tmp_path, 'bad_rmse', 3.3, 3.0, 0.001, 0.4)

    profile = load_live_physics_profile(tmp_path)

    assert profile.source == 'live-calibration-median'
    assert profile.session_count == 3
    assert profile.gravity == 3.2
    assert profile.thrust == 6.1
    assert abs(profile.hover - (3.2 / 6.1)) < 1e-9