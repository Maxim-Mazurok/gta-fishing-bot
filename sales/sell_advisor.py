"""Advise what fish to sell based on inventory dump.

Reads inventory from stdin (tab-separated: name<TAB>count).
Keeps 3 of each fish. Shows completable bundles and surplus non-bundle fish.

Usage:
    python sell_advisor.py            # paste inventory, then Ctrl+Z (Windows) or Ctrl+D
    python sell_advisor.py < inv.txt  # from file
"""

import re
import sys
from collections import Counter

from constants import BUNDLES, FISH_BUNDLES, PRICES

KEEP = 3

# Items that are not fish (equipment, junk, etc.)
NON_FISH_KEYWORDS = {
    "Rod", "Esky", "Electronics", "Handheld Radio", "Homemade Thermite",
    "Crowbar", "Screwdriver", "Patch Kit", "Air Jordans", "Heavy Pistol",
}

# Inventory names that differ from the database names
NAME_ALIASES: dict[str, str] = {
    "Banded Butterfly": "Banded Butterflyfish",
    "Chadphin": "Chadfin",
}


def normalize_name(name: str) -> str:
    return NAME_ALIASES.get(name, name)


def is_fish(name: str) -> bool:
    for kw in NON_FISH_KEYWORDS:
        if kw in name:
            return False
    return True


def parse_inventory(lines: list[str]) -> Counter:
    inv: Counter = Counter()
    for line in lines:
        line = line.strip()
        if not line:
            continue
        match = re.match(r"^(.+?)(?:\t|  +)(\d+)$", line)
        if match:
            name, count = match.group(1).strip(), int(match.group(2))
            name = normalize_name(name)
            if is_fish(name):
                inv[name] += count
    return inv


def compute_bundles(inv: Counter) -> list[tuple[str, int, str]]:
    """Return (bundle_name, count, bottleneck_fish) for completable bundles."""
    results = []
    for name, info in BUNDLES.items():
        sellable = []
        for fish in info["fish"]:
            have = inv.get(fish, 0)
            s = max(0, have - KEEP)
            sellable.append((fish, s))
        min_count = min(s for _, s in sellable)
        if min_count > 0:
            bottleneck = min(sellable, key=lambda x: x[1])
            results.append((name, min_count, bottleneck[0]))
    results.sort(key=lambda x: -BUNDLES[x[0]]["bonus"] * x[1])
    return results


def main() -> None:
    lines = sys.stdin.read().splitlines()
    inv = parse_inventory(lines)

    if not inv:
        print("No fish found in input.")
        return

    # --- Bundles ---
    bundle_fish_set: set[str] = set()
    for info in BUNDLES.values():
        for f in info["fish"]:
            bundle_fish_set.add(f)

    bundles = compute_bundles(inv)

    print("=== COMPLETE BUNDLES ===\n")
    if bundles:
        # Track how many fish are consumed by bundles
        consumed: Counter = Counter()
        total_bonus = 0
        for bname, count, bottleneck in bundles:
            bonus = BUNDLES[bname]["bonus"] * count
            total_bonus += bonus
            fish_list = ", ".join(BUNDLES[bname]["fish"])
            print(f"  {bname} x{count}  (bonus: ${bonus:,})")
            print(f"    Fish: {fish_list}")
            print(f"    Bottleneck: {bottleneck} ({inv.get(bottleneck, 0)} have, {max(0, inv.get(bottleneck, 0) - KEEP)} sellable)")
            for fish in BUNDLES[bname]["fish"]:
                consumed[fish] += count
            print()
        print(f"  Total bundle bonus: ${total_bonus:,}\n")

        # Show remaining after bundles
        print("  Remaining bundle fish after selling:")
        for fish in sorted(consumed):
            have = inv.get(fish, 0)
            remaining = have - consumed[fish]
            print(f"    {fish}: {have} -> {remaining}")
        print()
    else:
        print("  None completable (keeping 3 of each).\n")

    # Impossible bundles
    print("=== IMPOSSIBLE BUNDLES ===\n")
    for bname, info in BUNDLES.items():
        if any(b[0] == bname for b in bundles):
            continue
        missing = []
        zero_sellable = []
        for fish in info["fish"]:
            have = inv.get(fish, 0)
            if have == 0:
                missing.append(fish)
            elif have <= KEEP:
                zero_sellable.append(f"{fish} ({have}, 0 sellable)")
        reasons = []
        if missing:
            reasons.append("missing: " + ", ".join(missing))
        if zero_sellable:
            reasons.append("at keep limit: " + ", ".join(zero_sellable))
        print(f"  {bname}: {'; '.join(reasons)}")
    print()

    # --- Surplus non-bundle fish ---
    print("=== SURPLUS FISH (not in any bundle, over 3) ===\n")
    surplus = []
    for fish, have in sorted(inv.items()):
        if fish in bundle_fish_set:
            continue
        sellable = max(0, have - KEEP)
        if sellable > 0:
            price = PRICES.get(fish, (0, 0, ""))[0]
            value = price * sellable
            surplus.append((fish, have, sellable, price, value))

    if surplus:
        surplus.sort(key=lambda x: -x[4])
        print(f"  {'Fish':<25} {'Have':>5} {'Sell':>5} {'$/ea':>7} {'Total':>9}")
        print(f"  {'-'*25} {'-'*5} {'-'*5} {'-'*7} {'-'*9}")
        total_value = 0
        for fish, have, sellable, price, value in surplus:
            print(f"  {fish:<25} {have:>5} {sellable:>5} ${price:>5,} ${value:>7,}")
            total_value += value
        print(f"\n  Total surplus value: ${total_value:,}")
    else:
        print("  None.")

    # --- Bundle fish with surplus but can't complete bundle ---
    print("\n=== BUNDLE FISH WITH SURPLUS (can't complete their bundle) ===\n")
    bundle_surplus = []
    for fish in sorted(bundle_fish_set):
        have = inv.get(fish, 0)
        sellable = max(0, have - KEEP)
        if sellable <= 0:
            continue
        # Check if this fish's bundles are all impossible
        in_completable = False
        for bname, count, _ in bundles:
            if fish in BUNDLES[bname]["fish"]:
                in_completable = True
                break
        if not in_completable and sellable > 0:
            price = PRICES.get(fish, (0, 0, ""))[0]
            bundle_names = ", ".join(FISH_BUNDLES.get(fish, []))
            bundle_surplus.append((fish, have, sellable, price, bundle_names))

    if bundle_surplus:
        for fish, have, sellable, price, bnames in bundle_surplus:
            print(f"  {fish}: {have} have, {sellable} sellable (${price:,}/ea) — bundle: {bnames}")
    else:
        print("  None.")


if __name__ == "__main__":
    main()
