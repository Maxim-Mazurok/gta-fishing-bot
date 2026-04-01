"""Simulation tests for controller evaluation against randomized fish motion."""

from control import FishingController
from simulation import FishingSimulator, evaluate_controller, run_controller_episode


class TestFishingSimulator:
    """Validate the docs-derived fishing simulator."""

    def test_reset_returns_detector_like_view(self):
        simulator = FishingSimulator(difficulty='easy', seed=123)
        detector = simulator.reset()

        assert 0.0 <= detector.fish_y <= 1.0
        assert 0.0 <= detector.box_center <= 1.0
        assert 0.0 <= detector.progress <= 1.0
        assert detector.box_top < detector.box_bottom

    def test_step_advances_time_and_progress_bounds(self):
        simulator = FishingSimulator(difficulty='medium', seed=1)
        simulator.reset()
        result = simulator.step(hold=False)

        assert result['time'] > 0.0
        assert 0.0 <= result['progress'] <= 1.0
        assert 0.0 <= result['fish_y'] <= 1.0
        assert 0.0 <= result['box_center'] <= 1.0

    def test_controller_can_catch_easy_seeded_fish(self):
        simulator = FishingSimulator(difficulty='easy', seed=7, timeout=45.0)
        controller = FishingController()

        result = run_controller_episode(controller, simulator)

        assert result['caught'] is True
        assert result['inside_ratio'] > 0.03

    def test_evaluation_summary_is_repeatable(self):
        summary_a = evaluate_controller(episodes=5, difficulty='easy', seed=10, timeout=45.0)
        summary_b = evaluate_controller(episodes=5, difficulty='easy', seed=10, timeout=45.0)

        assert summary_a['catch_rate'] == summary_b['catch_rate']
        assert summary_a['avg_time'] == summary_b['avg_time']
        assert summary_a['avg_inside_ratio'] == summary_b['avg_inside_ratio']

    def test_medium_evaluation_has_useful_progress(self):
        summary = evaluate_controller(episodes=8, difficulty='medium', seed=3, timeout=45.0)

        assert summary['avg_inside_ratio'] > 0.03
        assert summary['avg_final_progress'] >= 0.05
        assert summary['avg_progress_reward'] > summary['avg_progress_penalty']

    def test_calibrated_controller_clears_seeded_regression_suite(self):
        medium = evaluate_controller(episodes=8, difficulty='medium', seed=20, timeout=45.0)
        hard = evaluate_controller(episodes=8, difficulty='hard', seed=30, timeout=45.0)

        assert medium['catch_rate'] >= 0.95
        assert medium['avg_inside_ratio'] >= 0.70
        assert medium['avg_time'] <= 10.0
        assert medium['avg_progress_reward'] >= 0.95
        assert hard['catch_rate'] >= 0.90
        assert hard['avg_inside_ratio'] >= 0.65
        assert hard['avg_time'] <= 12.0
        assert hard['avg_progress_reward'] >= 0.90