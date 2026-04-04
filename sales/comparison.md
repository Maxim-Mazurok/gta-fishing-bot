# Location Comparison

Assuming 100s wait for bite + 15s reel-in = 115s per fish (31.3 fish/hour).

| Location     | Fish Caught | $/Fish (sales) | Available Bundles | $/Fish (bundles) | $/Fish (total) |  $/Hour |
|--------------|------------:|---------------:|-------------------|-----------------:|---------------:|--------:|
| Alamo Sea    |         181 |         $1,487 | Alamo Starter     |             $276 |     **$1,763** | $55,189 |
| Land Act Dam |         203 |         $1,670 | none              |               $0 |     **$1,670** | $52,284 |

## Bundle Details

### Alamo Sea

| Bundle        | Fish                                     |   Bonus | Avg Fish to Complete | Avg Time | Bonus/Fish | Catch Rates                                                                              |
|---------------|------------------------------------------|--------:|---------------------:|---------:|-----------:|------------------------------------------------------------------------------------------|
| Alamo Starter | Morwhong, Southern Tuna, Silver Trevally | $10,000 |                   44 |   85 min |       $225 | Morwhong: 12/181 (6.6%) \| Southern Tuna: 5/181 (2.8%) \| Silver Trevally: 11/181 (6.1%) |

## Drop Rate Analysis

### Tier Distribution

Tier drop rates are consistent across locations, suggesting a fixed game mechanic:

| Tier | Alamo Sea | Land Act Dam | Average |
|------|----------:|-------------:|--------:|
| ★★★  |      8.3% |        11.3% |    9.8% |
| ★★   |     27.6% |        27.6% |   27.6% |
| ★    |     64.1% |        61.1% |   62.6% |

### Within-Tier Weights

Fitted smallest integer weights per fish using χ² goodness-of-fit (p > 0.05 = acceptable).

#### Alamo Sea — ★★★ (2 fish, 15 observed)

| Fish            | Count | Observed % | Weight | Expected % | Residual |
|-----------------|------:|-----------:|-------:|-----------:|---------:|
| Silver Trevally |    11 |      73.3% |      8 |      72.7% |     +0.1 |
| Great Barracuda |     4 |      26.7% |      3 |      27.3% |     -0.1 |

χ² = 0.00, df = 1, p = 0.958 — excellent fit

#### Alamo Sea — ★★ (6 fish, 50 observed)

| Fish             | Count | Observed % | Weight | Expected % | Residual |
|------------------|------:|-----------:|-------:|-----------:|---------:|
| Trout            |    16 |      32.0% |     10 |      31.2% |     +0.4 |
| Blue Warehou     |    16 |      32.0% |     10 |      31.2% |     +0.4 |
| Southern Garfish |     7 |      14.0% |      3 |       9.4% |     +2.3 |
| Southern Tuna    |     5 |      10.0% |      3 |       9.4% |     +0.3 |
| Snow Crab        |     4 |       8.0% |      3 |       9.4% |     -0.7 |
| Golden Perch     |     2 |       4.0% |      3 |       9.4% |     -2.7 |

χ² = 2.82, df = 5, p = 0.728 — excellent fit

#### Alamo Sea — ★ (7 fish, 116 observed)

| Fish      | Count | Observed % | Weight | Expected % | Residual |
|-----------|------:|-----------:|-------:|-----------:|---------:|
| Broadbill |    32 |      27.6% |      9 |      27.3% |     +0.4 |
| Albacore  |    22 |      19.0% |      6 |      18.2% |     +0.9 |
| Scollop   |    20 |      17.2% |      6 |      18.2% |     -1.1 |
| Halibut   |    15 |      12.9% |      4 |      12.1% |     +0.9 |
| Morwhong  |    12 |      10.3% |      4 |      12.1% |     -2.1 |
| Redfish   |     8 |       6.9% |      2 |       6.1% |     +1.0 |
| Flathead  |     7 |       6.0% |      2 |       6.1% |     -0.0 |

χ² = 0.60, df = 6, p = 0.996 — excellent fit

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
