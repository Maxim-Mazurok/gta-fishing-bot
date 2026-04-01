"""Run the fishing controller against the seeded simulator."""

import argparse
import json

from simulation import evaluate_controller


def main():
    parser = argparse.ArgumentParser(description='Evaluate fishing controller against simulator')
    parser.add_argument('--episodes', type=int, default=25, help='Number of simulated catches to run')
    parser.add_argument('--difficulty', choices=('easy', 'medium', 'hard'), default='medium')
    parser.add_argument('--seed', type=int, default=0, help='Base RNG seed for reproducibility')
    parser.add_argument('--timeout', type=float, default=45.0, help='Episode timeout in seconds')
    parser.add_argument('--json', action='store_true', help='Emit full JSON summary')
    args = parser.parse_args()

    summary = evaluate_controller(
        episodes=args.episodes,
        difficulty=args.difficulty,
        seed=args.seed,
        timeout=args.timeout,
    )

    if args.json:
        print(json.dumps(summary, indent=2))
        return

    print(f"difficulty={summary['difficulty']} episodes={summary['episodes']} seed={summary['seed']}")
    print(f"catch_rate={summary['catch_rate']:.1%}")
    print(f"avg_time={summary['avg_time']:.2f}s")
    print(f"avg_inside_ratio={summary['avg_inside_ratio']:.1%}")
    print(f"avg_final_progress={summary['avg_final_progress']:.1%}")


if __name__ == '__main__':
    main()