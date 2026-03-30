"""Unit tests for BarDetector: initialization, find_bar, detect_elements."""
import numpy as np
import cv2
import pytest
import time

from tests.helpers import (
    BarDetector, SEARCH_MARGIN_X_FRAC, SEARCH_MARGIN_Y_FRAC,
    FRAME_DIR_1, FRAME_DIR_2,
    HAS_FRAMES_1, HAS_FRAMES_2,
    load_frame, detect_on_frame, create_synthetic_bar_image,
)

requires_frames_1 = pytest.mark.skipif(
    not HAS_FRAMES_1, reason="Recording 1 frames not available"
)
requires_frames_2 = pytest.mark.skipif(
    not HAS_FRAMES_2, reason="Recording 2 frames not available"
)


class TestBarDetectorInit:
    """Test BarDetector initialization and default state."""

    def test_initial_state(self, detector):
        assert detector.bar_found is False
        assert detector.fish_y == 0.5
        assert detector.box_top == 0.0
        assert detector.box_bottom == 0.0
        assert detector.box_center == 0.5
        assert detector.progress == 0.0
        assert detector.fish_velocity == 0.0
        assert detector.fish_y_history == []

    def test_default_column_coords_zero(self, detector):
        assert detector.col_x1 == 0
        assert detector.col_x2 == 0
        assert detector.col_y1 == 0
        assert detector.col_y2 == 0

    def test_default_progress_coords_zero(self, detector):
        assert detector.prog_x1 == 0
        assert detector.prog_x2 == 0


class TestFindBar:
    """Test BarDetector.find_bar() with various inputs."""

    def test_empty_image_returns_false(self, detector):
        img = np.zeros((100, 100, 3), dtype=np.uint8)
        assert detector.find_bar(img) is False
        assert detector.bar_found is False

    def test_random_noise_returns_false(self, detector):
        rng = np.random.RandomState(42)
        img = rng.randint(0, 255, (200, 200, 3), dtype=np.uint8)
        assert detector.find_bar(img) is False

    def test_all_blue_image_no_valid_bar(self, detector):
        """A uniformly blue image shouldn't produce a valid bar (no narrow column)."""
        img = np.zeros((200, 200, 3), dtype=np.uint8)
        hsv = np.zeros((200, 200, 3), dtype=np.uint8)
        hsv[:, :, 0] = 100  # Blue hue
        hsv[:, :, 1] = 200  # High saturation
        hsv[:, :, 2] = 200  # Bright
        img = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        assert detector.find_bar(img) is False

    def test_synthetic_bar_found(self, detector):
        """A synthetic bar image should be detectable.

        Note: The image must be large enough that the bar satisfies the
        minimum height requirement (>12% of image height), with proper
        aspect ratio validation (height > 8x width).
        """
        img = create_synthetic_bar_image(width=960, height=540, bar_x=470, bar_w=12)
        found = detector.find_bar(img)
        assert found is True
        assert detector.bar_found is True
        # Bar coordinates should be reasonable
        assert detector.col_x2 > detector.col_x1
        assert detector.col_y2 > detector.col_y1
        bar_h = detector.col_y2 - detector.col_y1
        bar_w = detector.col_x2 - detector.col_x1
        assert bar_h > bar_w * 5  # Tall narrow bar

    def test_bar_width_constraints(self, detector):
        """Bar must be 1-5% of image width."""
        # Too narrow bar
        img = np.zeros((600, 200, 3), dtype=np.uint8)
        hsv = np.zeros((600, 1, 3), dtype=np.uint8)
        hsv[:, :, 0] = 100
        hsv[:, :, 1] = 200
        hsv[:, :, 2] = 200
        img[:, 100:101] = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        assert detector.find_bar(img) is False

    @requires_frames_1
    def test_find_bar_on_real_frame(self, detector):
        """Bar should be found on a minigame frame from recording 1."""
        img = load_frame(FRAME_DIR_1, '001001')
        assert img is not None
        h, w = img.shape[:2]
        cx, cy = w // 2, h // 2
        mx = int(w * SEARCH_MARGIN_X_FRAC)
        my = int(h * SEARCH_MARGIN_Y_FRAC)
        roi = img[cy - my:cy + my, cx - mx:cx + mx]
        assert detector.find_bar(roi) is True
        assert detector.bar_found is True
        bar_h = detector.col_y2 - detector.col_y1
        bar_w = detector.col_x2 - detector.col_x1
        assert bar_h > 100  # Should be >100px tall
        assert 3 <= bar_w <= 40  # Should be narrow

    @requires_frames_1
    def test_find_bar_consistent_across_frames(self):
        """Bar position should be consistent across sequential frames."""
        positions = []
        for frame_name in ['001001', '001050', '001100', '001150']:
            img = load_frame(FRAME_DIR_1, frame_name)
            if img is None:
                continue
            det = BarDetector()
            h, w = img.shape[:2]
            cx, cy = w // 2, h // 2
            mx = int(w * SEARCH_MARGIN_X_FRAC)
            my = int(h * SEARCH_MARGIN_Y_FRAC)
            roi = img[cy - my:cy + my, cx - mx:cx + mx]
            if det.find_bar(roi):
                positions.append((det.col_x1, det.col_x2, det.col_y1, det.col_y2))

        assert len(positions) >= 3, "Should find bar in at least 3 frames"
        # Bar position should vary by at most a few pixels
        x1s = [p[0] for p in positions]
        x2s = [p[1] for p in positions]
        assert max(x1s) - min(x1s) <= 5, "Bar x1 should be consistent"
        assert max(x2s) - min(x2s) <= 5, "Bar x2 should be consistent"


class TestDetectElements:
    """Test BarDetector.detect_elements() for white box, fishscale, progress."""

    @requires_frames_1
    def test_detect_returns_dict(self):
        """detect_elements should return a dict with expected keys."""
        img = load_frame(FRAME_DIR_1, '001001')
        assert img is not None
        det, result = detect_on_frame(img)
        assert det is not None
        assert result is not None
        assert 'fish_y' in result
        assert 'box_top' in result
        assert 'box_bottom' in result
        assert 'box_center' in result
        assert 'progress' in result
        assert 'fish_velocity' in result

    @requires_frames_1
    def test_fish_y_in_range(self):
        """fish_y should always be in [0.0, 1.0]."""
        for frame_name in ['001001', '001193', '001205', '001250']:
            img = load_frame(FRAME_DIR_1, frame_name)
            if img is None:
                continue
            det, result = detect_on_frame(img)
            if result:
                assert 0.0 <= result['fish_y'] <= 1.0, \
                    f"fish_y={result['fish_y']} out of range in frame {frame_name}"

    @requires_frames_1
    def test_box_ordering(self):
        """box_top should be less than box_bottom."""
        for frame_name in ['001001', '001193', '001250', '001300']:
            img = load_frame(FRAME_DIR_1, frame_name)
            if img is None:
                continue
            det, result = detect_on_frame(img)
            if result:
                assert result['box_top'] < result['box_bottom'], \
                    f"box_top={result['box_top']} >= box_bottom={result['box_bottom']} in {frame_name}"

    @requires_frames_1
    def test_box_center_between_top_bottom(self):
        """box_center should be midpoint of top and bottom."""
        img = load_frame(FRAME_DIR_1, '001001')
        det, result = detect_on_frame(img)
        if result:
            expected_center = (result['box_top'] + result['box_bottom']) / 2
            assert abs(result['box_center'] - expected_center) < 0.001

    @requires_frames_1
    def test_box_size_reasonable(self):
        """White box should be 10-50% of bar height."""
        img = load_frame(FRAME_DIR_1, '001001')
        det, result = detect_on_frame(img)
        if result:
            box_size = result['box_bottom'] - result['box_top']
            assert 0.05 < box_size < 0.5, f"Box size {box_size:.3f} out of expected range"

    @requires_frames_1
    def test_progress_in_range(self):
        """Progress should be in [0.0, 1.0]."""
        for frame_name in ['001001', '001250', '001500', '002000']:
            img = load_frame(FRAME_DIR_1, frame_name)
            if img is None:
                continue
            det, result = detect_on_frame(img)
            if result:
                assert 0.0 <= result['progress'] <= 1.0, \
                    f"progress={result['progress']} out of range in {frame_name}"

    @requires_frames_1
    def test_none_on_invalid_coords(self):
        """detect_elements returns None when column coords are invalid."""
        img = load_frame(FRAME_DIR_1, '001001')
        det = BarDetector()
        det.bar_found = True
        det.col_x1 = 0
        det.col_x2 = 0  # Zero-width column
        det.col_y1 = 0
        det.col_y2 = 100
        result = det.detect_elements(img)
        assert result is None

    @requires_frames_1
    def test_detection_no_crash_on_all_sampled_frames(self):
        """Detection should not crash on any sampled frame."""
        crash_count = 0
        tested = 0
        for i in range(900, 4520, 50):
            img = load_frame(FRAME_DIR_1, f'{i:06d}')
            if img is None:
                continue
            tested += 1
            try:
                det, result = detect_on_frame(img)
            except Exception as e:
                crash_count += 1
                pytest.fail(f"Crash on frame {i:06d}: {e}")
        assert tested > 10, "Should test at least 10 frames"
        assert crash_count == 0


class TestRegressionGuards:
    """Critical regression tests: verify known-bad detections are fixed."""

    TOLERANCE = 0.035

    @requires_frames_1
    def test_no_white_box_bottom_false_positive_922(self):
        """Frame 000922: fish must NOT be detected at white box bottom edge."""
        img = load_frame(FRAME_DIR_1, '000922')
        assert img is not None
        det, result = detect_on_frame(img)
        assert result is not None
        fish_y = result['fish_y']
        box_bottom = result['box_bottom']
        assert abs(fish_y - box_bottom) > 0.02, \
            f"False positive: fish={fish_y:.3f} at wb bottom={box_bottom:.3f}"

    @requires_frames_1
    def test_no_white_box_bottom_false_positive_990(self):
        """Frame 000990: fish must NOT be detected at white box bottom edge."""
        img = load_frame(FRAME_DIR_1, '000990')
        assert img is not None
        det, result = detect_on_frame(img)
        assert result is not None
        fish_y = result['fish_y']
        box_bottom = result['box_bottom']
        assert abs(fish_y - box_bottom) > 0.02, \
            f"False positive: fish={fish_y:.3f} at wb bottom={box_bottom:.3f}"

    @requires_frames_1
    @pytest.mark.parametrize("frame_name,expected_y", [
        ('001001', 0.451),
        ('001193', 0.605),
        ('001205', 0.677),
        ('001210', 0.651),
        ('001250', 0.529),
    ])
    def test_outside_box_detection_accuracy(self, frame_name, expected_y):
        """Fish outside white box should be detected within tolerance."""
        img = load_frame(FRAME_DIR_1, frame_name)
        assert img is not None
        det, result = detect_on_frame(img)
        assert result is not None
        error = abs(result['fish_y'] - expected_y)
        assert error <= self.TOLERANCE, \
            f"Frame {frame_name}: fish={result['fish_y']:.3f} expected={expected_y:.3f} error={error:.3f}"

    @requires_frames_1
    @pytest.mark.parametrize("frame_name", ['001195', '001197', '001199', '001201'])
    def test_inside_box_no_false_edge_detection(self, frame_name):
        """Fish inside white box: detection should not snap to box edges."""
        img = load_frame(FRAME_DIR_1, frame_name)
        assert img is not None
        det, result = detect_on_frame(img)
        assert result is not None
        fish_y = result['fish_y']
        near_top = abs(fish_y - result['box_top']) < 0.02
        near_bot = abs(fish_y - result['box_bottom']) < 0.02
        assert not (near_top or near_bot), \
            f"Fish at box edge: fish={fish_y:.3f} box=[{result['box_top']:.3f},{result['box_bottom']:.3f}]"


class TestVelocityTracking:
    """Test fish velocity estimation across sequential frames."""

    @requires_frames_1
    def test_velocity_builds_over_frames(self):
        """Velocity should become non-zero after processing several frames."""
        det = BarDetector()
        fake_time = 0.0
        dt = 1.0 / 60

        velocities = []
        for i in range(1001, 1020):
            img = load_frame(FRAME_DIR_1, f'{i:06d}')
            if img is None:
                continue
            if not det.bar_found:
                h, w = img.shape[:2]
                cx, cy = w // 2, h // 2
                mx = int(w * SEARCH_MARGIN_X_FRAC)
                my = int(h * SEARCH_MARGIN_Y_FRAC)
                roi = img[cy - my:cy + my, cx - mx:cx + mx]
                if det.find_bar(roi):
                    det.col_x1 += cx - mx
                    det.col_x2 += cx - mx
                    det.col_y1 += cy - my
                    det.col_y2 += cy - my
                    det.prog_x1 += cx - mx
                    det.prog_x2 += cx - mx
            if det.bar_found:
                fake_time += dt
                det.detect_elements(img, now=fake_time)
                velocities.append(det.fish_velocity)

        assert len(velocities) >= 5, "Not enough frames processed"
        # After a few frames, velocity should be non-zero for a moving fish
        later_vels = velocities[3:]
        assert any(abs(v) > 0.01 for v in later_vels), \
            f"Velocity stayed near zero: {later_vels}"

    @requires_frames_1
    def test_velocity_history_limited(self):
        """fish_y_history should not grow beyond 20 entries."""
        det = BarDetector()
        fake_time = 0.0
        dt = 1.0 / 60

        for i in range(1001, 1060):
            img = load_frame(FRAME_DIR_1, f'{i:06d}')
            if img is None:
                continue
            if not det.bar_found:
                h, w = img.shape[:2]
                cx, cy = w // 2, h // 2
                mx = int(w * SEARCH_MARGIN_X_FRAC)
                my = int(h * SEARCH_MARGIN_Y_FRAC)
                roi = img[cy - my:cy + my, cx - mx:cx + mx]
                if det.find_bar(roi):
                    det.col_x1 += cx - mx
                    det.col_x2 += cx - mx
                    det.col_y1 += cy - my
                    det.col_y2 += cy - my
                    det.prog_x1 += cx - mx
                    det.prog_x2 += cx - mx
            if det.bar_found:
                fake_time += dt
                det.detect_elements(img, now=fake_time)

        assert len(det.fish_y_history) <= 20, \
            f"History grew to {len(det.fish_y_history)}, should be <= 20"


class TestDrawDebug:
    """Test the debug visualization method."""

    @requires_frames_1
    def test_draw_debug_returns_image(self):
        """draw_debug should return a valid BGR image."""
        img = load_frame(FRAME_DIR_1, '001001')
        det, result = detect_on_frame(img)
        assert det is not None
        vis = det.draw_debug(img)
        assert vis is not None
        assert vis.shape == img.shape
        assert vis.dtype == np.uint8

    @requires_frames_1
    def test_draw_debug_no_bar_returns_copy(self):
        """draw_debug with bar_found=False should return image copy unchanged."""
        img = load_frame(FRAME_DIR_1, '001001')
        det = BarDetector()
        vis = det.draw_debug(img)
        assert np.array_equal(vis, img)

    @requires_frames_1
    def test_draw_debug_modifies_image(self):
        """draw_debug with detections should modify the image (add overlays)."""
        img = load_frame(FRAME_DIR_1, '001001')
        det, result = detect_on_frame(img)
        vis = det.draw_debug(img)
        # The visualization should differ from original
        assert not np.array_equal(vis, img)
