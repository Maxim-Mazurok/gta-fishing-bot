# Location Comparison

Assuming 100s wait for bite + 15s reel-in = 115s per fish (31.3 fish/hour).

| Location     | Fish Caught | $/Fish (sales) | Available Bundles | $/Fish (bundles) | $/Fish (total) |  $/Hour |
|--------------|------------:|---------------:|-------------------|-----------------:|---------------:|--------:|
| Alamo Sea    |         321 |         $1,468 | Alamo Starter     |             $280 |     **$1,748** | $54,734 |
| Land Act Dam |         203 |         $1,670 | none              |               $0 |     **$1,670** | $52,284 |

## Bundle Details

### Alamo Sea

| Bundle        | Fish                                     |   Bonus | Avg Fish to Complete | Avg Time | Bonus/Fish | Catch Rates                                                                              |
|---------------|------------------------------------------|--------:|---------------------:|---------:|-----------:|------------------------------------------------------------------------------------------|
| Alamo Starter | Morwhong, Southern Tuna, Silver Trevally | $10,000 |                   48 |   92 min |       $208 | Morwhong: 22/321 (6.9%) \| Southern Tuna: 9/321 (2.8%) \| Silver Trevally: 13/321 (4.0%) |

## Drop Rate Analysis

### Tier Distribution

Tier drop rates are consistent across locations, suggesting a fixed game mechanic:

| Tier | Alamo Sea | Land Act Dam | Average |
|------|----------:|-------------:|--------:|
| ★★★  |      6.2% |        11.3% |    8.8% |
| ★★   |     25.9% |        27.6% |   26.7% |
| ★    |     67.9% |        61.1% |   64.5% |

### Within-Tier Weights

Fitted smallest integer weights per fish using χ² goodness-of-fit (p > 0.05 = acceptable).

#### Alamo Sea — ★★★ (2 fish, 20 observed)

| Fish            | Count | Observed % | Weight | Expected % | Residual |
|-----------------|------:|-----------:|-------:|-----------:|---------:|
| Silver Trevally |    13 |      65.0% |      1 |      50.0% |     +3.0 |
| Great Barracuda |     7 |      35.0% |      1 |      50.0% |     -3.0 |

χ² = 1.80, df = 1, p = 0.180 — good fit

#### Alamo Sea — ★★ (6 fish, 83 observed)

| Fish             | Count | Observed % | Weight | Expected % | Residual |
|------------------|------:|-----------:|-------:|-----------:|---------:|
| Trout            |    21 |      25.3% |      8 |      24.2% |     +0.9 |
| Blue Warehou     |    21 |      25.3% |      8 |      24.2% |     +0.9 |
| Southern Garfish |    18 |      21.7% |      8 |      24.2% |     -2.1 |
| Southern Tuna    |     9 |      10.8% |      3 |       9.1% |     +1.5 |
| Snow Crab        |     7 |       8.4% |      3 |       9.1% |     -0.5 |
| Golden Perch     |     7 |       8.4% |      3 |       9.1% |     -0.5 |

χ² = 0.66, df = 5, p = 0.985 — excellent fit

#### Alamo Sea — ★ (7 fish, 218 observed)

| Fish      | Count | Observed % | Weight | Expected % | Residual |
|-----------|------:|-----------:|-------:|-----------:|---------:|
| Albacore  |    47 |      21.6% |      9 |      21.4% |     +0.3 |
| Broadbill |    39 |      17.9% |      7 |      16.7% |     +2.7 |
| Scollop   |    38 |      17.4% |      7 |      16.7% |     +1.7 |
| Halibut   |    31 |      14.2% |      7 |      16.7% |     -5.3 |
| Morwhong  |    22 |      10.1% |      4 |       9.5% |     +1.2 |
| Flathead  |    22 |      10.1% |      4 |       9.5% |     +1.2 |
| Redfish   |    19 |       8.7% |      4 |       9.5% |     -1.8 |

χ² = 1.35, df = 6, p = 0.969 — excellent fit

#### Land Act Dam — ★★★ (3 fish, 23 observed)

| Fish          | Count | Observed % | Weight | Expected % | Residual |
|---------------|------:|-----------:|-------:|-----------:|---------:|
| Musky         |    11 |      47.8% |      7 |      41.2% |     +1.5 |
| Pike          |     8 |      34.8% |      7 |      41.2% |     -1.5 |
| Rainbow Trout |     4 |      17.4% |      3 |      17.6% |     -0.1 |

χ² = 0.48, df = 2, p = 0.788 — excellent fit

#### Land Act Dam — ★★ (6 fish, 56 observed)

| Fish            | Count | Observed % | Weight | Expected % | Residual |
|-----------------|------:|-----------:|-------:|-----------:|---------:|
| Atlantic Salmon |    12 |      21.4% |      1 |      16.7% |     +2.7 |
| Trevella        |    10 |      17.9% |      1 |      16.7% |     +0.7 |
| Wahoo           |     9 |      16.1% |      1 |      16.7% |     -0.3 |
| Sturgeon        |     9 |      16.1% |      1 |      16.7% |     -0.3 |
| Carp            |     9 |      16.1% |      1 |      16.7% |     -0.3 |
| Trumpetfish     |     7 |      12.5% |      1 |      16.7% |     -2.3 |

χ² = 1.43, df = 5, p = 0.921 — excellent fit

#### Land Act Dam — ★ (8 fish, 124 observed)

| Fish             | Count | Observed % | Weight | Expected % | Residual |
|------------------|------:|-----------:|-------:|-----------:|---------:|
| Murray Cod       |    32 |      25.8% |      7 |      25.9% |     -0.1 |
| Banded Butterfly |    21 |      16.9% |      4 |      14.8% |     +2.6 |
| Sand Whiting     |    19 |      15.3% |      4 |      14.8% |     +0.6 |
| Triggerfish      |    14 |      11.3% |      4 |      14.8% |     -4.4 |
| Cod              |    11 |       8.9% |      2 |       7.4% |     +1.8 |
| Black Bream      |    10 |       8.1% |      2 |       7.4% |     +0.8 |
| Escolar          |    10 |       8.1% |      2 |       7.4% |     +0.8 |
| Brook Trout      |     7 |       5.6% |      2 |       7.4% |     -2.2 |

χ² = 2.46, df = 7, p = 0.930 — excellent fit
