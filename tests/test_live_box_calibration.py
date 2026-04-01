"""Tests for the live box physics calibration helpers."""

from calibrate_live_box_physics import (
    ExperimentSpec,
    Phase,
    PhysicsParams,
    Sample,
    compute_rmse,
    estimate_initial_velocity,
    fit_window_size,
    fit_physics_params,
    phase_hold_state,
    simulate_observed_sequence,
    step_box_physics,
)


def _make_samples(holds, params, dt=1 / 60, start_y=0.5, start_v=0.0):
    samples = []
    time_value = 0.0
    box_center = start_y
    box_velocity = start_v
    samples.append(Sample(time=0.0, dt=dt, hold=int(holds[0]), duty=float(holds[0]),
                          box_center=box_center, box_top=max(0.0, box_center - 0.1),
                          box_bottom=min(1.0, box_center + 0.1), progress=0.0))

    for hold in holds[1:]:
        accel = -params.hold_accel if hold else params.release_gravity
        box_velocity += accel * dt
        box_center += box_velocity * dt
        box_center = max(0.0, min(1.0, box_center))
        if box_center in (0.0, 1.0):
            box_velocity = 0.0
        time_value += dt
        samples.append(Sample(time=time_value, dt=dt, hold=int(hold), duty=float(hold),
                              box_center=box_center, box_top=max(0.0, box_center - 0.1),
                              box_bottom=min(1.0, box_center + 0.1), progress=0.0))
    return samples


class TestLiveCalibrationHelpers:
    def test_phase_hold_state_for_duty(self):
        phase = Phase('duty', 1.0, duty=0.5)
        hold1, accumulator = phase_hold_state(phase, 0.0, 0.0)
        hold2, accumulator = phase_hold_state(phase, 0.1, accumulator)

        assert hold1 is False
        assert hold2 is True

    def test_estimate_initial_velocity(self):
        samples = [
            Sample(time=0.0, dt=0.1, hold=0, duty=0.0, box_center=0.8, box_top=0.7, box_bottom=0.9, progress=0.0),
            Sample(time=0.1, dt=0.1, hold=0, duty=0.0, box_center=0.82, box_top=0.72, box_bottom=0.92, progress=0.0),
            Sample(time=0.2, dt=0.1, hold=0, duty=0.0, box_center=0.86, box_top=0.76, box_bottom=0.96, progress=0.0),
        ]

        assert estimate_initial_velocity(samples) > 0.0

    def test_simulation_matches_synthetic_sequence(self):
        params = PhysicsParams(release_gravity=3.0, hold_accel=4.0)
        samples = _make_samples([0] * 10 + [1] * 10 + [0] * 10, params)
        simulated = simulate_observed_sequence(samples, params, initial_velocity=0.0)
        rmse = compute_rmse(samples, simulated)

        assert rmse < 0.02

    def test_incremental_step_matches_sequence_simulation(self):
        params = PhysicsParams(release_gravity=3.0, hold_accel=4.0)
        samples = _make_samples([0] * 8 + [1] * 12 + [0] * 6, params)
        expected = simulate_observed_sequence(samples, params, initial_velocity=0.0)

        actual = [samples[0].box_center]
        velocity = 0.0
        for prev, current in zip(samples, samples[1:]):
            dt = max(current.dt, current.time - prev.time, 0.0)
            center, velocity = step_box_physics(actual[-1], velocity, bool(current.hold), dt, params)
            actual.append(center)

        assert actual == expected

    def test_fit_window_size_preserves_aspect_ratio(self, monkeypatch):
        monkeypatch.setattr('calibrate_live_box_physics.get_desktop_size', lambda: (1920, 1080))

        width, height = fit_window_size(2200, 1000)

        assert width <= 1920
        assert height <= 1080
        assert abs((width / height) - (2200 / 1000)) < 0.01

    def test_fit_recovers_known_parameters(self):
        true_params = PhysicsParams(release_gravity=2.8, hold_accel=4.6)
        experiments = [
            {
                'name': 'hold_release',
                'description': 'synthetic',
                'samples': _make_samples([0] * 15 + [1] * 30 + [0] * 30, true_params),
            },
            {
                'name': 'dutyish',
                'description': 'synthetic',
                'samples': _make_samples(([1, 0] * 25), true_params),
            },
        ]

        initial = PhysicsParams(release_gravity=3.24, hold_accel=3.61 - 3.24)
        fitted, loss = fit_physics_params(experiments, initial)

        assert abs(fitted.release_gravity - true_params.release_gravity) < 0.7
        assert abs(fitted.hold_accel - true_params.hold_accel) < 0.4
        assert loss < 0.02