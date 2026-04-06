"""Advise which fishing location to go to next.

Reads inventory from stdin (tab-separated: name<TAB>count).
Recommends the best location (Dam, Alamo Sea, Roxwood) based on:
  - $/hour (price per fish * fish per hour, accounting for different catch speeds)
  - Bundle bonus potential (which bundles get unblocked)

Usage:
    python location_advisor.py            # paste inventory, then Ctrl+Z / Ctrl+D
    python location_advisor.py < inv.txt  # from file
"""

import sys
from collections import Counter

from constants import BUNDLES, FISH_BUNDLES, PRICES, TIER_PRICES, SALES_DIR, REGIONS
from constants import fish_per_hour, seconds_per_fish
from parsing import fish_location, parse_log
from sell_advisor import KEEP, NON_FISH_KEYWORDS, is_fish, parse_inventory

SESSION_HOURS = 8


def get_location_stats() -> dict[str, Counter]:
    """Load observed fish counts per location from log files."""
    stats: dict[str, Counter] = {}
    for key, name in REGIONS.items():
        log_path = SALES_DIR / f"{key}-log.md"
        if log_path.exists():
            counts = parse_log(log_path)
            if counts:
                stats[name] = counts
    return stats


def location_avg_value(location: str, loc_counts: Counter) -> float:
    """Weighted average $/fish at a location based on observed drop rates."""
    total_fish = sum(loc_counts.values())
    if total_fish == 0:
        return 0
    total_value = 0
    for fish, count in loc_counts.items():
        if fish in PRICES:
            price = PRICES[fish][0]
            total_value += price * count
    return total_value / total_fish


def bundle_potential(inv: Counter, location: str, loc_counts: Counter, session_fish: int) -> list[tuple[str, int, int, str]]:
    """Estimate bundle completions unlockable by fishing at this location.

    Returns list of (bundle_name, estimated_completions, bonus_per, bottleneck_fish).
    """
    total_fish = sum(loc_counts.values())
    if total_fish == 0:
        return []

    results = []
    for bname, info in BUNDLES.items():
        # Check if this location provides any fish the bundle needs
        bundle_fish_at_loc = []
        for fish in info["fish"]:
            if fish_location(fish) == location:
                bundle_fish_at_loc.append(fish)

        if not bundle_fish_at_loc:
            continue

        # Estimate how many of each bundle fish we'd catch in the session
        projected_inv = Counter(inv)
        for fish in bundle_fish_at_loc:
            caught = loc_counts.get(fish, 0)
            drop_rate = caught / total_fish
            expected_catch = int(drop_rate * session_fish)
            projected_inv[fish] += expected_catch

        # Calculate completable bundles with projected inventory
        min_sellable = float("inf")
        bottleneck = ""
        for fish in info["fish"]:
            sellable = max(0, projected_inv.get(fish, 0) - KEEP)
            if sellable < min_sellable:
                min_sellable = sellable
                bottleneck = fish

        completions = int(min_sellable)
        if completions > 0:
            # Subtract what's currently completable
            current_min = float("inf")
            for fish in info["fish"]:
                s = max(0, inv.get(fish, 0) - KEEP)
                current_min = min(current_min, s)
            new_completions = completions - int(current_min)
            if new_completions > 0:
                results.append((bname, new_completions, info["bonus"], bottleneck))

    results.sort(key=lambda x: -x[1] * x[2])
    return results


def main() -> None:
    lines = sys.stdin.read().splitlines()
    inv = parse_inventory(lines)

    if not inv:
        print("No fish found in input.")
        return

    loc_stats = get_location_stats()

    # Only consider locations we have data for
    locations = [loc for loc in ["Dam", "Alamo Sea", "Roxwood"] if loc in loc_stats]

    if not locations:
        print("No location data found (need log files).")
        return

    print("=== LOCATION RECOMMENDATION ===\n")

    scores: list[tuple[str, float, float, list]] = []

    for location in locations:
        loc_counts = loc_stats[location]

        # 1. Average $/fish and $/hour
        avg_val = location_avg_value(location, loc_counts)
        fph = fish_per_hour(location)
        dollar_per_hour = avg_val * fph
        session_fish = int(fph * SESSION_HOURS)
        session_fish_value = avg_val * session_fish

        # 2. Bundle potential
        bundles = bundle_potential(inv, location, loc_counts, session_fish)
        bundle_bonus_total = sum(count * bonus for _, count, bonus, _ in bundles)

        # 3. Total session revenue
        session_total = session_fish_value + bundle_bonus_total

        scores.append((location, avg_val, fph, session_fish, session_fish_value, bundle_bonus_total, bundles, session_total))

        print(f"--- {location} ---")
        print(f"  Avg $/fish: ${avg_val:,.0f}  |  Fish/hr: {fph:.1f}  |  $/hr: ${dollar_per_hour:,.0f}")
        print(f"  {SESSION_HOURS}h session: ~{session_fish} fish, ~${session_fish_value:,.0f} fish value")

        if bundles:
            print(f"  Bundle bonuses unlocked: ${bundle_bonus_total:,}")
            for bname, count, bonus, bottleneck in bundles:
                print(f"    {bname} x{count} = ${count * bonus:,} (bottleneck: {bottleneck})")
        else:
            print("  Bundle bonuses unlocked: $0 (no new bundles)")

        print(f"  Estimated {SESSION_HOURS}h total: ~${session_total:,.0f}")
        print()

    # Rank by total session value
    scores.sort(key=lambda x: -x[7])

    print("=== RANKING ===\n")
    for i, (location, avg_val, fph, session_fish, sfv, bundle_bonus, bundles, session_total) in enumerate(scores, 1):
        marker = " <-- GO HERE" if i == 1 else ""
        print(f"  #{i} {location}: ~${session_total:,.0f} in {SESSION_HOURS}h ({session_fish} fish + ${bundle_bonus:,} bundles){marker}")

    # Show which bundle fish are currently needed
    print("\n=== BUNDLE FISH YOU STILL NEED ===\n")
    for bname, info in BUNDLES.items():
        needed = []
        for fish in info["fish"]:
            have = inv.get(fish, 0)
            sellable = max(0, have - KEEP)
            if sellable == 0:
                loc = fish_location(fish)
                needed.append(f"{fish} ({have} have, from {loc})")
        if needed:
            print(f"  {bname} (${info['bonus']:,} bonus):")
            for n in needed:
                print(f"    NEED: {n}")
            print()


if __name__ == "__main__":
    main()
