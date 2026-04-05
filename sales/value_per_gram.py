"""Fish value-per-gram analysis.

Shows all fish ranked by value density ($/gram), including bundle bonus
contributions. Includes per-location analysis using drop rates.

Usage:
    python sales/value_per_gram.py
"""

import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from sales.constants import (
    BUNDLES,
    FISH_WEIGHTS,
    PRICES,
    REGIONS,
    SALES_DIR,
    TIER_DROP_PERCENTAGES,
    TIER_PRICES,
    fish_per_hour,
    seconds_per_fish,
)


def price_per_gram(name: str, price: int, weight_g: int) -> float:
    """Direct selling price per gram."""
    return price / weight_g


def get_fish_location(name: str) -> str | None:
    """Determine a fish's location from its price and star tier."""
    if name not in PRICES:
        return None
    price, stars, color = PRICES[name]
    if stars >= 4 or stars == 0:
        return "Special"
    if color == "green":
        return "Humane Labs"
    for loc, tiers in TIER_PRICES.items():
        if stars in tiers and tiers[stars] == price:
            return loc
    return None


def bundle_value_per_fish(name: str) -> tuple[float, list[str]]:
    """Estimate bundle bonus value attributable to one fish.

    For each bundle a fish participates in, the bonus is split equally
    among the 3 bundle members as a simple attribution.
    Returns (total_bonus_share, list_of_bundle_names).
    """
    total = 0.0
    bundles = []
    for bundle_name, info in BUNDLES.items():
        if name in info["fish"]:
            share = info["bonus"] / len(info["fish"])
            total += share
            bundles.append(bundle_name)
    return total, bundles


def estimate_weight(name: str) -> int | None:
    """Get known weight or estimate from star tier pattern.

    Observed patterns:
        x (1 star): 300g (14/14)
        xx (2 star): 400g (7/8), 300g (1/8)
        xxx (3 star): 300-500g
    """
    if name in FISH_WEIGHTS:
        return FISH_WEIGHTS[name]
    if name not in PRICES:
        return None
    _, stars, _ = PRICES[name]
    # Use most common observed weight per tier as estimate
    estimates = {1: 300, 2: 400, 3: 400}
    return estimates.get(stars)


def parse_log(path: Path) -> Counter:
    """Parse a sales log file and return fish counts."""
    import re
    totals: Counter = Counter()
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line == "--sold":
            continue
        match = re.match(r"^(.+?)(?:\t|  )(\d+)$", line)
        if match:
            name, count = match.group(1), int(match.group(2))
            totals[name] += count
    return totals


def load_region_data() -> dict[str, Counter]:
    """Load catch data for all regions that have log files."""
    region_data: dict[str, Counter] = {}
    for key, name in REGIONS.items():
        log = SALES_DIR / f"{key}-log.md"
        if log.exists():
            counts = parse_log(log)
            if counts:
                region_data[name] = counts
    return region_data


def compute_location_grams(region_data: dict[str, Counter]) -> list[dict]:
    """Compute value-per-gram stats for each location using observed drop rates.

    Uses bundle $/fish from the existing comparison analysis (computed by
    update_sales.py) rather than re-deriving them here.
    """
    # Import bundle computation from update_sales
    sys.path.insert(0, str(SALES_DIR))
    from update_sales import _compute_bundle_contributions

    # Get bundle $/fish for each location
    bundle_contributions = _compute_bundle_contributions(region_data)

    results = []

    for location, counts in region_data.items():
        total_fish = sum(counts.values())
        if total_fish == 0:
            continue

        # Compute weighted average $/gram and grams/fish
        total_value = 0
        total_weight_g = 0
        fish_with_weight = 0
        fish_details = []

        for name, count in counts.most_common():
            if name not in PRICES:
                continue
            price = PRICES[name][0]
            weight = estimate_weight(name)
            drop_pct = count / total_fish * 100
            is_estimated = name not in FISH_WEIGHTS

            if weight is not None:
                total_value += count * price
                total_weight_g += count * weight
                fish_with_weight += count
                fish_details.append({
                    "name": name,
                    "count": count,
                    "price": price,
                    "weight": weight,
                    "drop_pct": drop_pct,
                    "ppg": price / weight,
                    "estimated": is_estimated,
                })

        if total_weight_g == 0:
            continue

        avg_ppg = total_value / total_weight_g
        avg_weight = total_weight_g / fish_with_weight
        avg_price = total_value / fish_with_weight
        fph = fish_per_hour(location)
        grams_per_hour = avg_weight * fph
        dollars_per_hour_sale = avg_price * fph

        # Bundle contribution from the proper analysis
        loc_bundles = bundle_contributions.get(location, [])
        bundle_per_fish = sum(bpf for _, bpf, _ in loc_bundles)
        bundle_ppg = bundle_per_fish / avg_weight if avg_weight > 0 else 0

        results.append({
            "location": location,
            "total_fish": total_fish,
            "avg_ppg_sale": avg_ppg,
            "avg_ppg_total": avg_ppg + bundle_ppg,
            "avg_weight": avg_weight,
            "avg_price": avg_price,
            "bundle_per_fish": bundle_per_fish,
            "bundle_ppg": bundle_ppg,
            "fph": fph,
            "grams_per_hour": grams_per_hour,
            "dollars_per_hour_sale": dollars_per_hour_sale,
            "dollars_per_hour_total": (avg_price + bundle_per_fish) * fph,
            "fish_details": sorted(fish_details, key=lambda d: -d["ppg"]),
            "coverage": fish_with_weight / total_fish * 100,
        })

    results.sort(key=lambda r: -r["avg_ppg_total"])
    return results


def main():
    # Build analysis rows for fish with known weights
    rows = []
    for name, weight_g in sorted(FISH_WEIGHTS.items()):
        if name not in PRICES:
            continue
        price, stars, color = PRICES[name]
        location = get_fish_location(name) or "?"

        ppg = price_per_gram(name, price, weight_g)
        bundle_share, bundle_names = bundle_value_per_fish(name)
        total_value = price + bundle_share
        total_ppg = total_value / weight_g

        rows.append({
            "name": name,
            "price": price,
            "weight_g": weight_g,
            "stars": stars,
            "color": color,
            "location": location,
            "ppg": ppg,
            "bundle_share": bundle_share,
            "bundle_names": bundle_names,
            "total_value": total_value,
            "total_ppg": total_ppg,
        })

    # Also include fish WITHOUT known weights (mark as unknown)
    unknown_weight_rows = []
    for name, (price, stars, color) in sorted(PRICES.items()):
        if name in FISH_WEIGHTS:
            continue
        location = get_fish_location(name) or "?"
        bundle_share, bundle_names = bundle_value_per_fish(name)
        unknown_weight_rows.append({
            "name": name,
            "price": price,
            "stars": stars,
            "color": color,
            "location": location,
            "bundle_share": bundle_share,
            "bundle_names": bundle_names,
        })

    # Sort by total $/gram descending
    rows.sort(key=lambda r: -r["total_ppg"])

    # Generate markdown
    lines = ["# Fish Value Per Gram", ""]
    lines.append(f"Fish with known weights: {len(rows)} / {len(PRICES)}")
    lines.append(f"Fish with unknown weights: {len(unknown_weight_rows)}")
    lines.append("")

    # ── Location comparison ──
    region_data = load_region_data()
    if region_data:
        loc_stats = compute_location_grams(region_data)
        lines.append("## Location Value Density Comparison")
        lines.append("")
        lines.append("Average $/gram per location, weighted by drop rates. "
                      "Uses known weights where available, estimates (from star-tier patterns) otherwise.")
        lines.append("")
        lines.append(
            "| # | Location | $/g (sale) | $/g (w/ bundles) | Avg Weight | Avg $/fish | "
            "Bundle $/fish | g/hour | $/hour (sale) | $/hour (total) | Fish | Coverage |"
        )
        lines.append(
            "|--:|----------|----------:|----------------:|-----------:|-----------:"
            "|--------------:|-------:|--------------:|---------------:|-----:|---------:|"
        )
        for i, s in enumerate(loc_stats, 1):
            lines.append(
                f"| {i} "
                f"| {s['location']} "
                f"| {s['avg_ppg_sale']:.2f} "
                f"| **{s['avg_ppg_total']:.2f}** "
                f"| {s['avg_weight']:.0f}g "
                f"| ${s['avg_price']:,.0f} "
                f"| ${s['bundle_per_fish']:,.0f} "
                f"| {s['grams_per_hour']:,.0f} "
                f"| ${s['dollars_per_hour_sale']:,.0f} "
                f"| ${s['dollars_per_hour_total']:,.0f} "
                f"| {s['total_fish']} "
                f"| {s['coverage']:.0f}% |"
            )

        # Per-location fish breakdown
        for s in loc_stats:
            lines.append("")
            lines.append(f"### {s['location']} — Fish by $/gram")
            lines.append("")
            lines.append("| Fish | $/fish | Weight | $/g | Drop % | Stars | Known |")
            lines.append("|------|-------:|-------:|----:|-------:|-------|-------|")
            for d in s["fish_details"]:
                stars_raw = PRICES[d["name"]]
                star_str = "x" * stars_raw[1]
                if stars_raw[2]:
                    star_str += f" {stars_raw[2]}"
                known = "est." if d["estimated"] else "yes"
                lines.append(
                    f"| {d['name']} "
                    f"| ${d['price']:,} "
                    f"| {d['weight']}g "
                    f"| {d['ppg']:.2f} "
                    f"| {d['drop_pct']:.1f}% "
                    f"| {star_str} "
                    f"| {known} |"
                )

        lines.append("")

    # Main table
    lines.append("## Ranked by Value Density ($/gram)")
    lines.append("")
    lines.append(
        "| # | Fish | Price | Weight | $/g | Bundle Bonus | Total $/fish | Total $/g | Stars | Location |"
    )
    lines.append(
        "|--:|------|------:|-------:|----:|-------------:|-------------:|----------:|-------|----------|"
    )
    for i, r in enumerate(rows, 1):
        star_str = "x" * r["stars"]
        if r["color"] == "green":
            star_str += " green"
        elif r["color"] == "purple":
            star_str += " purple"

        bundle_str = f"${r['bundle_share']:,.0f}" if r["bundle_share"] > 0 else "-"

        lines.append(
            f"| {i} "
            f"| {r['name']} "
            f"| ${r['price']:,} "
            f"| {r['weight_g']}g "
            f"| {r['ppg']:.2f} "
            f"| {bundle_str} "
            f"| ${r['total_value']:,.0f} "
            f"| **{r['total_ppg']:.2f}** "
            f"| {star_str} "
            f"| {r['location']} |"
        )

    # Bundle fish detail
    lines.append("")
    lines.append("## Bundle Fish Details")
    lines.append("")
    bundle_fish = [r for r in rows if r["bundle_share"] > 0]
    if bundle_fish:
        bundle_fish.sort(key=lambda r: -r["total_ppg"])
        lines.append(
            "| Fish | Price | Weight | $/g (base) | Bundle | Bonus Share | Total $/g |"
        )
        lines.append(
            "|------|------:|-------:|-----------:|--------|------------:|----------:|"
        )
        for r in bundle_fish:
            for bn in r["bundle_names"]:
                share = BUNDLES[bn]["bonus"] / len(BUNDLES[bn]["fish"])
                lines.append(
                    f"| {r['name']} "
                    f"| ${r['price']:,} "
                    f"| {r['weight_g']}g "
                    f"| {r['ppg']:.2f} "
                    f"| {bn} "
                    f"| ${share:,.0f} "
                    f"| {(r['price'] + share) / r['weight_g']:.2f} |"
                )
    else:
        lines.append("No bundle fish have known weights yet.")

    # Weight pattern analysis
    lines.append("")
    lines.append("## Weight Patterns")
    lines.append("")
    star_weights: dict[int, list[int]] = {}
    for r in rows:
        star_weights.setdefault(r["stars"], []).append(r["weight_g"])
    lines.append("| Stars | Weights Observed | Min | Max | Most Common |")
    lines.append("|------:|------------------|----:|----:|------------:|")
    for stars in sorted(star_weights):
        weights = star_weights[stars]
        from collections import Counter
        common = Counter(weights).most_common(1)[0]
        lines.append(
            f"| {'x' * stars} "
            f"| {', '.join(str(w) for w in sorted(set(weights)))}g "
            f"| {min(weights)}g "
            f"| {max(weights)}g "
            f"| {common[0]}g ({common[1]}/{len(weights)}) |"
        )

    # Fish without weights
    lines.append("")
    lines.append("## Fish Without Known Weights")
    lines.append("")
    if unknown_weight_rows:
        lines.append("| Fish | Price | Stars | Location | In Bundle |")
        lines.append("|------|------:|-------|----------|-----------|")
        for r in sorted(unknown_weight_rows, key=lambda r: -r["price"]):
            star_str = "x" * r["stars"] if r["stars"] > 0 else "-"
            if r["color"] == "green":
                star_str += " green"
            elif r["color"] == "purple":
                star_str += " purple"
            bundle_str = ", ".join(r["bundle_names"]) if r["bundle_names"] else "-"
            lines.append(
                f"| {r['name']} "
                f"| ${r['price']:,} "
                f"| {star_str} "
                f"| {r['location']} "
                f"| {bundle_str} |"
            )
    else:
        lines.append("All fish have known weights!")

    report = "\n".join(lines) + "\n"

    # Write to file
    output_path = Path(__file__).parent / "weights.md"
    output_path.write_text(report, encoding="utf-8")
    print(f"  weights.md updated ({len(rows)} fish with weights)")


if __name__ == "__main__":
    main()
    # Print report when run directly
    print((Path(__file__).parent / "weights.md").read_text(encoding="utf-8"))
