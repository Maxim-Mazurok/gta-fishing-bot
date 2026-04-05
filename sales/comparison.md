# Location Comparison

Detected tier: 3 (Alamo Sea, Dam, Roxwood).

Bite wait by location: Alamo Sea 90s, Dam 90s, Roxwood 100s. Reel-in by location: Alamo Sea 23s, Dam 27s, Roxwood 41s.

~ = estimated (not yet observed in catch data)

| Location  | Fish Caught | $/Fish observed | $/Fish model | Available Bundles                                     | $/Fish (bundles) | $/Fish total (obs) | $/Fish total (model) | $/Hour (model) |
|-----------|------------:|----------------:|-------------:|-------------------------------------------------------|-----------------:|-------------------:|---------------------:|---------------:|
| Alamo Sea |         463 |          $1,477 |       $1,411 | Gold Multizone #1, Alamo Starter, Low Level Multizone |             $678 |             $2,155 |           **$2,089** |        $66,561 |
| Dam       |         335 |          $1,664 |       $1,664 | Gold Multizone #1, Low Level Multizone                |             $369 |             $2,033 |           **$2,033** |        $62,556 |
| Roxwood   |         256 |          $1,795 |       $1,859 | Gold Multizone #1, Low Level Multizone                |             $257 |             $2,052 |           **$2,116** |        $54,021 |

## Optimal Allocation

Optimal time split across locations to maximize total $/hour (considering both sale value and cross-location bundle completions):

| Location     | Time % (obs) | $/Fish (obs) | $/Hour (obs) | Time % (model) | $/Fish (model) | $/Hour (model) |
|--------------|-------------:|-------------:|-------------:|---------------:|---------------:|---------------:|
| Alamo Sea    |          54% |       $1,477 |      $54,610 |            50% |         $1,411 |        $52,524 |
| Dam          |          21% |       $1,664 |      $51,206 |            23% |         $1,664 |        $51,206 |
| Roxwood      |          25% |       $1,795 |      $45,823 |            27% |         $1,859 |        $47,455 |
| **Combined** |         100% |              |  **$56,564** |           100% |                |    **$55,860** |

**Observed:** splitting yields **$56,564**/hour vs **$54,610**/hour best solo (+$1,954/hour, +3.6%).
**Model:** splitting yields **$55,860**/hour vs **$52,524**/hour best solo (+$3,336/hour, +6.4%).

## Bundle Details

### Alamo Sea

| Bundle        | Fish                                     |   Bonus | Avg Fish to Complete | Avg Time | Bonus/Fish | Catch Rates                                                                               |
|---------------|------------------------------------------|--------:|---------------------:|---------:|-----------:|-------------------------------------------------------------------------------------------|
| Alamo Starter | Morwhong, Southern Tuna, Silver Trevally | $10,000 |                   53 |   99 min |       $190 | Morwhong: 28/463 (6.0%) \| Southern Tuna: 11/463 (2.4%) \| Silver Trevally: 21/463 (4.5%) |

### Cross-Location

| Bundle              | Fish                             |   Bonus | Avg Fish to Complete | Avg Time | Bonus/Fish | Catch Rates                                                                                                 |
|---------------------|----------------------------------|--------:|---------------------:|---------:|-----------:|-------------------------------------------------------------------------------------------------------------|
| Gold Multizone #1   | Bluefin Tuna, Musky, Dolphinfish | $12,750 |                  178 |  357 min |        $72 | Bluefin Tuna @ Alamo Sea: 4/463 (0.9%) \| Musky @ Dam: 17/335 (5.1%) \| Dolphinfish @ Roxwood: 6/256 (2.3%) |
| Low Level Multizone | Scollop, Carp, Grenadier         | $11,000 |                   56 |  118 min |       $195 | Scollop @ Alamo Sea: 51/463 (11.0%) \| Carp @ Dam: 14/335 (4.2%) \| Grenadier @ Roxwood: 11/256 (4.3%)      |

## Drop Rate Analysis

### Tier Distribution

Tier drop rates are consistent across locations, suggesting a fixed game mechanic:

| Tier        | Alamo Sea |   Dam | Roxwood | Average |
|-------------|----------:|------:|--------:|--------:|
| xxxx purple |      0.2% |  0.0% |    0.4% |    0.2% |
| xxx         |      7.1% | 10.1% |    9.0% |    8.8% |
| xx          |     26.3% | 28.1% |   24.6% |   26.3% |
| x           |     65.0% | 61.8% |   65.6% |   64.1% |

### Within-Tier Weights

Observed frequencies vs model (percentage template) per fish.
Model uses shared percentage templates across all locations (5% granularity).

#### Alamo Sea — xxx (3 fish, 33 observed)

| Fish            | Count | Observed % | Weight | Weight % | Model % | Model % (norm) | Residual |
|-----------------|------:|-----------:|-------:|---------:|--------:|---------------:|---------:|
| Silver Trevally |    21 |      63.6% |     10 |    62.5% |     55% |          55.0% |     +2.9 |
| Great Barracuda |     8 |      24.2% |      3 |    18.8% |     30% |          30.0% |     -1.9 |
| Bluefin Tuna    |     4 |      12.1% |      3 |    18.8% |     15% |          15.0% |     -1.0 |

Weight fit: χ² = 1.31, df = 2, p = 0.519 — excellent
Model fit (55%/30%/15%): χ² = 0.99, p = 0.608 — excellent

#### Alamo Sea — xx (6 fish, 122 observed)

| Fish             | Count | Observed % | Weight | Weight % | Model % | Model % (norm) | Residual |
|------------------|------:|-----------:|-------:|---------:|--------:|---------------:|---------:|
| Southern Garfish |    32 |      26.2% |      9 |    23.1% |     25% |          25.0% |     +1.5 |
| Trout            |    26 |      21.3% |      9 |    23.1% |     20% |          20.0% |     +1.6 |
| Blue Warehou     |    25 |      20.5% |      9 |    23.1% |     20% |          20.0% |     +0.6 |
| Golden Perch     |    15 |      12.3% |      4 |    10.3% |     15% |          15.0% |     -3.3 |
| Snow Crab        |    13 |      10.7% |      4 |    10.3% |     10% |          10.0% |     +0.8 |
| Southern Tuna    |    11 |       9.0% |      4 |    10.3% |     10% |          10.0% |     -1.2 |

Weight fit: χ² = 1.74, df = 5, p = 0.884 — excellent
Model fit (25%/20%/20%/15%/10%/10%): χ² = 0.96, p = 0.966 — excellent

#### Alamo Sea — x (7 fish, 301 observed)

| Fish      | Count | Observed % | Weight | Weight % | Model % | Model % (norm) | Residual |
|-----------|------:|-----------:|-------:|---------:|--------:|---------------:|---------:|
| Albacore  |    69 |      22.9% |      7 |    22.6% |     20% |          21.1% |     +5.6 |
| Scollop   |    51 |      16.9% |      5 |    16.1% |     15% |          15.8% |     +3.5 |
| Halibut   |    47 |      15.6% |      5 |    16.1% |     15% |          15.8% |     -0.5 |
| Broadbill |    47 |      15.6% |      5 |    16.1% |     15% |          15.8% |     -0.5 |
| Redfish   |    31 |      10.3% |      3 |     9.7% |     10% |          10.5% |     -0.7 |
| Morwhong  |    28 |       9.3% |      3 |     9.7% |     10% |          10.5% |     -3.7 |
| Flathead  |    28 |       9.3% |      3 |     9.7% |     10% |          10.5% |     -3.7 |

Weight fit: χ² = 0.45, df = 6, p = 0.998 — excellent
Model fit (20%/15%/15%/15%/10%/10%/10%/5%): χ² = 1.64, p = 0.950 — excellent

#### Dam — xxx (3 fish, 34 observed)

| Fish          | Count | Observed % | Weight | Weight % | Model % | Model % (norm) | Residual |
|---------------|------:|-----------:|-------:|---------:|--------:|---------------:|---------:|
| Musky         |    17 |      50.0% |      2 |    50.0% |     55% |          55.0% |     -1.7 |
| Pike          |    10 |      29.4% |      1 |    25.0% |     30% |          30.0% |     -0.2 |
| Rainbow Trout |     7 |      20.6% |      1 |    25.0% |     15% |          15.0% |     +1.9 |

Weight fit: χ² = 0.53, df = 2, p = 0.767 — excellent
Model fit (55%/30%/15%): χ² = 0.87, p = 0.648 — excellent

#### Dam — xx (6 fish, 94 observed)

| Fish            | Count | Observed % | Weight | Weight % | Model % | Model % (norm) | Residual |
|-----------------|------:|-----------:|-------:|---------:|--------:|---------------:|---------:|
| Atlantic Salmon |    23 |      24.5% |      8 |    22.2% |     25% |          25.0% |     -0.5 |
| Trevella        |    19 |      20.2% |      8 |    22.2% |     20% |          20.0% |     +0.2 |
| Trumpetfish     |    16 |      17.0% |      5 |    13.9% |     20% |          20.0% |     -2.8 |
| Carp            |    14 |      14.9% |      5 |    13.9% |     15% |          15.0% |     -0.1 |
| Wahoo           |    12 |      12.8% |      5 |    13.9% |     10% |          10.0% |     +2.6 |
| Sturgeon        |    10 |      10.6% |      5 |    13.9% |     10% |          10.0% |     +0.6 |

Weight fit: χ² = 1.92, df = 5, p = 0.861 — excellent
Model fit (25%/20%/20%/15%/10%/10%): χ² = 1.19, p = 0.946 — excellent

#### Dam — x (8 fish, 207 observed)

| Fish                 | Count | Observed % | Weight | Weight % | Model % | Model % (norm) | Residual |
|----------------------|------:|-----------:|-------:|---------:|--------:|---------------:|---------:|
| Murray Cod           |    50 |      24.2% |      5 |    23.8% |     20% |          20.0% |     +8.6 |
| Banded Butterflyfish |    35 |      16.9% |      3 |    14.3% |     15% |          15.0% |     +3.9 |
| Triggerfish          |    28 |      13.5% |      3 |    14.3% |     15% |          15.0% |     -3.1 |
| Sand Whiting         |    26 |      12.6% |      3 |    14.3% |     15% |          15.0% |     -5.1 |
| Cod                  |    23 |      11.1% |      2 |     9.5% |     10% |          10.0% |     +2.3 |
| Escolar              |    19 |       9.2% |      2 |     9.5% |     10% |          10.0% |     -1.7 |
| Brook Trout          |    16 |       7.7% |      2 |     9.5% |     10% |          10.0% |     -4.7 |
| Black Bream          |    10 |       4.8% |      1 |     4.8% |      5% |           5.0% |     -0.3 |

Weight fit: χ² = 2.80, df = 7, p = 0.903 — excellent
Model fit (20%/15%/15%/15%/10%/10%/10%/5%): χ² = 4.88, p = 0.674 — excellent

#### Roxwood — xxx (3 fish, 23 observed)

| Fish          | Count | Observed % | Weight | Weight % | Model % | Model % (norm) | Residual |
|---------------|------:|-----------:|-------:|---------:|--------:|---------------:|---------:|
| Grenadier     |    11 |      47.8% |      9 |    47.4% |     55% |          55.0% |     -1.7 |
| King Mackerel |     6 |      26.1% |      5 |    26.3% |     30% |          30.0% |     -0.9 |
| Dolphinfish   |     6 |      26.1% |      5 |    26.3% |     15% |          15.0% |     +2.5 |

Weight fit: χ² = 0.00, df = 2, p = 0.999 — excellent
Model fit (55%/30%/15%): χ² = 2.22, p = 0.330 — good

#### Roxwood — xx (5 fish, 63 observed)

| Fish         | Count | Observed % | Weight | Weight % | Model % | Model % (norm) | Residual |
|--------------|------:|-----------:|-------:|---------:|--------:|---------------:|---------:|
| Snapper      |    19 |      30.2% |      9 |    27.3% |     25% |          27.8% |     +1.5 |
| Silver Perch |    16 |      25.4% |      9 |    27.3% |     20% |          22.2% |     +2.0 |
| Gummy Shark  |    12 |      19.0% |      5 |    15.2% |     20% |          22.2% |     -2.0 |
| Brown Trout  |    10 |      15.9% |      5 |    15.2% |     15% |          16.7% |     -0.5 |
| Red Snapper  |     6 |       9.5% |      5 |    15.2% |     10% |          11.1% |     -1.0 |

Weight fit: χ² = 2.24, df = 4, p = 0.691 — excellent
Model fit (25%/20%/20%/15%/10%/10%): χ² = 0.87, p = 0.929 — excellent

#### Roxwood — x (8 fish, 168 observed)

| Fish               | Count | Observed % | Weight | Weight % | Model % | Model % (norm) | Residual |
|--------------------|------:|-----------:|-------:|---------:|--------:|---------------:|---------:|
| Grouper            |    45 |      26.8% |      5 |    25.0% |     20% |          20.0% |    +11.4 |
| Dungeness Crab     |    27 |      16.1% |      3 |    15.0% |     15% |          15.0% |     +1.8 |
| Ocean Perch        |    25 |      14.9% |      3 |    15.0% |     15% |          15.0% |     -0.2 |
| Sandy Sprat        |    23 |      13.7% |      3 |    15.0% |     15% |          15.0% |     -2.2 |
| Australian Herring |    17 |      10.1% |      2 |    10.0% |     10% |          10.0% |     +0.2 |
| Amberjack          |    16 |       9.5% |      2 |    10.0% |     10% |          10.0% |     -0.8 |
| Ocean Jacket       |     9 |       5.4% |      1 |     5.0% |     10% |          10.0% |     -7.8 |
| Sand Whiting       |     6 |       3.6% |      1 |     5.0% |      5% |           5.0% |     -2.4 |

Weight fit: χ² = 1.31, df = 7, p = 0.988 — excellent
Model fit (20%/15%/15%/15%/10%/10%/10%/5%): χ² = 8.54, p = 0.288 — good
