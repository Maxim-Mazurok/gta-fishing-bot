"""Extract fish weights from selling-screen screenshots using OCR.

Usage:
    python weights/extract_weights.py                  # process all PNGs in weights/
    python weights/extract_weights.py path/to/img.png  # process specific image(s)

Outputs:
    - Prints extracted fish data with per-fish weight and price
    - Validates prices against known PRICES dict
    - Shows NEW fish (not yet in FISH_WEIGHTS) and any price mismatches
    - Appends new entries to sales/constants.py FISH_WEIGHTS dict (preview only)
"""

import re
import sys
from pathlib import Path

import cv2
import pytesseract

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from sales.constants import FISH_WEIGHTS, PRICES


def extract_fish_entries(image_path: str) -> list[dict]:
    """Extract fish entries from a selling-screen screenshot using OCR.

    Returns list of dicts with keys:
        name, total_price, total_weight_g, quantity, price_per_fish, weight_per_fish_g
    """
    img = cv2.imread(image_path)
    if img is None:
        print(f"  Could not read image: {image_path}")
        return []

    # Convert to grayscale for better OCR
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Increase contrast - the game UI has light text on dark background
    # Invert so text is dark on light (better for tesseract)
    _, thresh = cv2.threshold(gray, 120, 255, cv2.THRESH_BINARY)

    # Run OCR
    text = pytesseract.image_to_string(thresh, config="--psm 6")
    # Also try on the original with different preprocessing
    text2 = pytesseract.image_to_string(gray, config="--psm 6")
    # And on inverted
    inverted = cv2.bitwise_not(gray)
    text3 = pytesseract.image_to_string(inverted, config="--psm 6")

    # Combine all text outputs for best coverage
    all_text = text + "\n" + text2 + "\n" + text3

    return parse_ocr_text(all_text)


def parse_ocr_text(text: str) -> list[dict]:
    """Parse OCR text output to extract fish entries.

    Expected patterns in the text:
        FishName
        $XX,XXX  or  $X,XXX
        Weight: XXXg
        N  (quantity)
    """
    entries = []
    lines = [line.strip() for line in text.split("\n") if line.strip()]

    # Known fish names for fuzzy matching
    known_names = set(PRICES.keys()) | set(FISH_WEIGHTS.keys())

    i = 0
    while i < len(lines):
        line = lines[i]

        # Try to find a fish name - check against known names
        matched_name = None
        for name in known_names:
            if name.lower() in line.lower() or line.lower() in name.lower():
                # Require reasonable similarity
                if len(line) >= len(name) * 0.6:
                    matched_name = name
                    break

        if matched_name:
            # Look in the next few lines for price, weight, quantity
            context = " ".join(lines[i : min(i + 6, len(lines))])

            price_match = re.search(r"\$[\s]*([\d,]+)", context)
            weight_match = re.search(r"[Ww]eight[:\s]*([\d,]+)\s*g", context)
            qty_match = None

            # Quantity is usually a standalone small number after weight
            for j in range(i + 1, min(i + 6, len(lines))):
                if re.match(r"^\d{1,3}$", lines[j]):
                    qty_match = int(lines[j])
                    break

            if price_match and weight_match:
                total_price = int(price_match.group(1).replace(",", ""))
                total_weight = int(weight_match.group(1).replace(",", ""))
                qty = qty_match or 1

                if qty > 0 and total_price > 0 and total_weight > 0:
                    entries.append(
                        {
                            "name": matched_name,
                            "total_price": total_price,
                            "total_weight_g": total_weight,
                            "quantity": qty,
                            "price_per_fish": total_price // qty,
                            "weight_per_fish_g": total_weight // qty,
                        }
                    )

        i += 1

    # Deduplicate by name (keep first occurrence)
    seen = set()
    unique = []
    for e in entries:
        if e["name"] not in seen:
            seen.add(e["name"])
            unique.append(e)

    return unique


def validate_entry(entry: dict) -> dict:
    """Validate an extracted entry against known prices.

    Returns dict with validation results:
        price_match: bool
        expected_price: int or None
        is_new_weight: bool
    """
    name = entry["name"]
    result = {"price_match": True, "expected_price": None, "is_new_weight": name not in FISH_WEIGHTS}

    if name in PRICES:
        expected = PRICES[name][0]
        result["expected_price"] = expected
        result["price_match"] = entry["price_per_fish"] == expected

    return result


def process_images(image_paths: list[str]) -> dict[str, int]:
    """Process multiple images and return consolidated fish weights.

    Returns dict of fish_name -> weight_per_fish_g
    """
    all_weights: dict[str, int] = {}
    all_entries: list[dict] = []

    for path in image_paths:
        print(f"\nProcessing: {path}")
        entries = extract_fish_entries(path)
        if not entries:
            print("  No fish entries found")
            continue

        for entry in entries:
            validation = validate_entry(entry)
            status_parts = []

            if validation["is_new_weight"]:
                status_parts.append("NEW")
            if not validation["price_match"]:
                status_parts.append(
                    f"PRICE MISMATCH (expected ${validation['expected_price']:,})"
                )

            status = f" [{', '.join(status_parts)}]" if status_parts else ""

            print(
                f"  {entry['name']:.<25} "
                f"${entry['price_per_fish']:>5,}/fish  "
                f"{entry['weight_per_fish_g']:>4}g/fish  "
                f"(qty {entry['quantity']}){status}"
            )

            # Store weight (consistent values only)
            name = entry["name"]
            weight = entry["weight_per_fish_g"]
            if name in all_weights and all_weights[name] != weight:
                print(f"  WARNING: Inconsistent weight for {name}: {all_weights[name]}g vs {weight}g")
            else:
                all_weights[name] = weight

            all_entries.append(entry)

    return all_weights


def main():
    weights_dir = Path(__file__).parent

    if len(sys.argv) > 1:
        image_paths = sys.argv[1:]
    else:
        image_paths = sorted(str(p) for p in weights_dir.glob("*.png"))

    if not image_paths:
        print("No images found. Place PNG screenshots in the weights/ folder.")
        return

    print(f"Found {len(image_paths)} image(s)")

    extracted = process_images(image_paths)

    # Merge with existing weights
    merged = dict(FISH_WEIGHTS)
    new_count = 0
    for name, weight in extracted.items():
        if name not in merged:
            merged[name] = weight
            new_count += 1

    print(f"\n{'='*60}")
    print(f"Extracted {len(extracted)} fish weights from screenshots")
    print(f"New weights (not in FISH_WEIGHTS): {new_count}")
    print(f"Total known weights: {len(merged)}")

    if new_count > 0:
        print(f"\nNew entries to add to FISH_WEIGHTS in sales/constants.py:")
        for name in sorted(extracted):
            if name not in FISH_WEIGHTS:
                print(f'    "{name}": {extracted[name]},')


if __name__ == "__main__":
    main()
