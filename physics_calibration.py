"""Live physics calibration loading for the fishing controller.

Scans recorded white-box calibration runs, filters obvious outliers, and
derives a robust median physics profile for the live controller and simulator.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from statistics import median


DEFAULT_GRAVITY = 3.24
DEFAULT_THRUST = 3.61
CALIBRATION_ROOT = Path(__file__).with_name('live_physics_calibration')
FIT_ERROR_THRESHOLD = 0.01
WORST_EXPERIMENT_RMSE_THRESHOLD = 0.12
PARAMETER_BOUND_EPSILON = 0.05
OPTIMIZER_MIN = 0.5
OPTIMIZER_MAX = 8.0


@dataclass(frozen=True)
class PhysicsProfile:
    """Controller-ready physics parameters."""

    gravity: float
    thrust: float
    hover: float
    source: str
    session_count: int = 0

    @property
    def hold_accel(self) -> float:
        return self.thrust - self.gravity


def _load_summary(summary_path: Path) -> dict | None:
    try:
        payload = json.loads(summary_path.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError):
        return None

    params = payload.get('params', {})
    experiments = payload.get('experiments', [])
    if not params or not experiments:
        return None

    gravity = float(params.get('release_gravity', 0.0))
    hold_accel = float(params.get('hold_accel', 0.0))
    thrust = float(params.get('suggested_thrust', gravity + hold_accel))
    fit_error = float(payload.get('fit_error', 1e9))
    worst_rmse = max(float(experiment.get('rmse', 1e9)) for experiment in experiments)

    return {
        'session': summary_path.parent.name,
        'gravity': gravity,
        'hold_accel': hold_accel,
        'thrust': thrust,
        'fit_error': fit_error,
        'worst_rmse': worst_rmse,
        'experiments': len(experiments),
    }


def _is_valid_summary(summary: dict) -> bool:
    if summary['experiments'] < 3:
        return False
    if summary['fit_error'] > FIT_ERROR_THRESHOLD:
        return False
    if summary['worst_rmse'] > WORST_EXPERIMENT_RMSE_THRESHOLD:
        return False
    if not (OPTIMIZER_MIN + PARAMETER_BOUND_EPSILON <= summary['gravity'] <= OPTIMIZER_MAX - PARAMETER_BOUND_EPSILON):
        return False
    if not (OPTIMIZER_MIN + PARAMETER_BOUND_EPSILON <= summary['hold_accel'] <= OPTIMIZER_MAX - PARAMETER_BOUND_EPSILON):
        return False
    if summary['thrust'] <= summary['gravity']:
        return False
    return True


def load_live_physics_profile(root_dir: Path | None = None) -> PhysicsProfile:
    """Load a robust aggregate physics profile from recorded live calibrations."""
    if root_dir is None:
        root_dir = CALIBRATION_ROOT

    summaries = []
    if root_dir.exists():
        for summary_path in sorted(root_dir.glob('*/summary.json')):
            summary = _load_summary(summary_path)
            if summary is not None and _is_valid_summary(summary):
                summaries.append(summary)

    if not summaries:
        hover = DEFAULT_GRAVITY / DEFAULT_THRUST
        return PhysicsProfile(
            gravity=DEFAULT_GRAVITY,
            thrust=DEFAULT_THRUST,
            hover=hover,
            source='defaults',
            session_count=0,
        )

    gravity = float(median(summary['gravity'] for summary in summaries))
    thrust = float(median(summary['thrust'] for summary in summaries))
    hover = gravity / thrust
    return PhysicsProfile(
        gravity=gravity,
        thrust=thrust,
        hover=hover,
        source='live-calibration-median',
        session_count=len(summaries),
    )