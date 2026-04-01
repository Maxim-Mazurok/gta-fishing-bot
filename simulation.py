"""Seeded fishing minigame simulator for controller evaluation.

This is not a claim of exact FDG/FiveM source parity. It is a docs-derived,
physics-informed proxy environment that lets the real controller run against
randomized fish motion instead of replayed frame captures.
"""

from __future__ import annotations

from dataclasses import dataclass
import random
from types import SimpleNamespace

from control import FishingController


@dataclass(frozen=True)
class FishDifficulty:
    """Piecewise fish motion parameters for one difficulty tier."""

    name: str
    slow_speed_range: tuple[float, float]
    fast_speed_range: tuple[float, float]
    segment_duration_range: tuple[float, float]
    fast_segment_chance: float
    spontaneous_flip_chance: float
    box_half_height: float
    fill_rate: float
    drain_rate: float


DIFFICULTIES = {
    'easy': FishDifficulty(
        name='easy',
        slow_speed_range=(0.08, 0.14),
        fast_speed_range=(0.16, 0.22),
        segment_duration_range=(0.40, 0.90),
        fast_segment_chance=0.18,
        spontaneous_flip_chance=0.03,
        box_half_height=0.15,
        fill_rate=0.42,
        drain_rate=0.16,
    ),
    'medium': FishDifficulty(
        name='medium',
        slow_speed_range=(0.11, 0.18),
        fast_speed_range=(0.20, 0.28),
        segment_duration_range=(0.28, 0.70),
        fast_segment_chance=0.28,
        spontaneous_flip_chance=0.06,
        box_half_height=0.12,
        fill_rate=0.36,
        drain_rate=0.20,
    ),
    'hard': FishDifficulty(
        name='hard',
        slow_speed_range=(0.16, 0.24),
        fast_speed_range=(0.26, 0.38),
        segment_duration_range=(0.18, 0.45),
        fast_segment_chance=0.40,
        spontaneous_flip_chance=0.11,
        box_half_height=0.10,
        fill_rate=0.32,
        drain_rate=0.24,
    ),
}


class FishingSimulator:
    """Physics simulator for the fishing minigame.

    The box uses the measured gravity/thrust values already baked into the
    controller. Fish motion follows piecewise-constant velocity segments that
    randomly switch between slower and faster phases, matching the public FDG
    docs more closely than replay-only frame tests.
    """

    def __init__(self, difficulty='medium', seed=None, control_hz=60, timeout=45.0):
        if difficulty not in DIFFICULTIES:
            raise ValueError(f"Unknown difficulty: {difficulty}")

        self.profile = DIFFICULTIES[difficulty]
        self.rng = random.Random(seed)
        self.control_hz = control_hz
        self.dt = 1.0 / control_hz
        self.timeout = timeout
        self.reset()

    def reset(self):
        self.time = 0.0
        self.progress = 0.0
        self.box_center = 0.85
        self.box_velocity = 0.0
        self.fish_y = self.rng.uniform(0.25, 0.75)
        self.fish_velocity = 0.0
        self.segment_remaining = 0.0
        self._choose_new_segment(force_direction=self.rng.choice((-1, 1)))
        return self.get_detector()

    def _choose_new_segment(self, force_direction=None):
        use_fast = self.rng.random() < self.profile.fast_segment_chance
        speed_range = self.profile.fast_speed_range if use_fast else self.profile.slow_speed_range
        speed = self.rng.uniform(*speed_range)
        direction = force_direction if force_direction is not None else self.rng.choice((-1, 1))
        self.fish_velocity = speed * direction
        self.segment_remaining = self.rng.uniform(*self.profile.segment_duration_range)

    def _step_fish(self):
        self.segment_remaining -= self.dt
        if self.segment_remaining <= 0.0 or self.rng.random() < self.profile.spontaneous_flip_chance * self.dt * self.control_hz:
            self._choose_new_segment()

        self.fish_y += self.fish_velocity * self.dt
        if self.fish_y < 0.02:
            self.fish_y = 0.02
            self._choose_new_segment(force_direction=1)
        elif self.fish_y > 0.98:
            self.fish_y = 0.98
            self._choose_new_segment(force_direction=-1)

    def _step_box(self, hold):
        acceleration = FishingController.GRAVITY - FishingController.THRUST if hold else FishingController.GRAVITY
        self.box_velocity += acceleration * self.dt
        self.box_center += self.box_velocity * self.dt

        if self.box_center < 0.0:
            self.box_center = 0.0
            self.box_velocity = 0.0
        elif self.box_center > 1.0:
            self.box_center = 1.0
            self.box_velocity = 0.0

    def _step_progress(self):
        inside = self.box_top <= self.fish_y <= self.box_bottom
        prev_progress = self.progress
        rate = self.profile.fill_rate if inside else -self.profile.drain_rate
        self.progress = max(0.0, min(1.0, self.progress + rate * self.dt))
        return inside, self.progress - prev_progress

    @property
    def box_top(self):
        return max(0.0, self.box_center - self.profile.box_half_height)

    @property
    def box_bottom(self):
        return min(1.0, self.box_center + self.profile.box_half_height)

    def step(self, hold):
        self.time += self.dt
        self._step_fish()
        self._step_box(hold)
        inside, progress_delta = self._step_progress()
        caught = self.progress >= 1.0
        timed_out = self.time >= self.timeout
        return {
            'time': self.time,
            'caught': caught,
            'timed_out': timed_out,
            'inside_box': inside,
            'progress': self.progress,
            'progress_delta': progress_delta,
            'fish_y': self.fish_y,
            'fish_velocity': self.fish_velocity,
            'box_center': self.box_center,
            'box_velocity': self.box_velocity,
        }

    def get_detector(self):
        return SimpleNamespace(
            fish_y=self.fish_y,
            fish_velocity=self.fish_velocity,
            box_center=self.box_center,
            box_top=self.box_top,
            box_bottom=self.box_bottom,
            progress=self.progress,
        )


def run_controller_episode(controller, simulator):
    """Run one controller episode against the simulator."""
    controller.reset()
    detector = simulator.reset()
    inside_frames = 0
    steps = 0
    progress_reward = 0.0
    progress_penalty = 0.0

    while True:
        hold = controller.update(detector, now=simulator.time)
        step_result = simulator.step(hold)
        detector = simulator.get_detector()
        steps += 1
        if step_result['inside_box']:
            inside_frames += 1
        progress_delta = step_result['progress_delta']
        if progress_delta > 0.0:
            progress_reward += progress_delta
        elif progress_delta < 0.0:
            progress_penalty += -progress_delta
        if step_result['caught'] or step_result['timed_out']:
            return {
                'caught': step_result['caught'],
                'timed_out': step_result['timed_out'],
                'time': step_result['time'],
                'steps': steps,
                'inside_ratio': inside_frames / max(steps, 1),
                'final_progress': step_result['progress'],
                'progress_reward': progress_reward,
                'progress_penalty': progress_penalty,
                'difficulty': simulator.profile.name,
            }


def evaluate_controller(controller_factory=FishingController, episodes=25,
                        difficulty='medium', seed=0, control_hz=60, timeout=45.0):
    """Run multiple seeded simulation episodes and return summary metrics."""
    results = []
    for episode_idx in range(episodes):
        simulator = FishingSimulator(
            difficulty=difficulty,
            seed=seed + episode_idx,
            control_hz=control_hz,
            timeout=timeout,
        )
        controller = controller_factory()
        results.append(run_controller_episode(controller, simulator))

    caught = [result for result in results if result['caught']]
    return {
        'episodes': episodes,
        'difficulty': difficulty,
        'seed': seed,
        'catch_rate': len(caught) / max(episodes, 1),
        'avg_time': sum(result['time'] for result in results) / max(episodes, 1),
        'avg_inside_ratio': sum(result['inside_ratio'] for result in results) / max(episodes, 1),
        'avg_final_progress': sum(result['final_progress'] for result in results) / max(episodes, 1),
        'avg_progress_reward': sum(result['progress_reward'] for result in results) / max(episodes, 1),
        'avg_progress_penalty': sum(result['progress_penalty'] for result in results) / max(episodes, 1),
        'results': results,
    }