# Location Comparison

Detected tier: 3 (Alamo Sea, Dam, Roxwood).

Bite wait by location: Alamo Sea 90s, Dam 90s, Roxwood 100s. Reel-in by location: Alamo Sea 23s, Dam 27s, Roxwood 41s.

~ = estimated (not yet observed in catch data)

| Location  | Fish Caught | $/Fish observed | $/Fish model | Available Bundles                                     | $/Fish (bundles) | $/Fish total (obs) | $/Fish total (model) | $/Hour (model) |
|-----------|------------:|----------------:|-------------:|-------------------------------------------------------|-----------------:|-------------------:|---------------------:|---------------:|
| Alamo Sea |         496 |          $1,489 |       $1,426 | Gold Multizone #1, Alamo Starter, Low Level Multizone |             $661 |             $2,150 |           **$2,086** |        $66,468 |
| Dam       |         341 |          $1,664 |       $1,664 | Gold Multizone #1, Low Level Multizone                |             $362 |             $2,027 |           **$2,027** |        $62,358 |
| Roxwood   |         255 |          $1,802 |       $1,866 | Gold Multizone #1, Low Level Multizone                |             $258 |             $2,060 |           **$2,124** |        $54,233 |

## Optimal Allocation

Optimal time split across locations to maximize total $/hour (considering both sale value and cross-location bundle completions):

| Location     | Time % (obs) | $/Fish (obs) | $/Hour (obs) | Time % (model) | $/Fish (model) | $/Hour (model) |
|--------------|-------------:|-------------:|-------------:|---------------:|---------------:|---------------:|
| Alamo Sea    |          55% |       $1,489 |      $55,155 |            55% |         $1,426 |        $53,130 |
| Dam          |          21% |       $1,664 |      $51,207 |            21% |         $1,664 |        $51,207 |
| Roxwood      |          24% |       $1,802 |      $46,003 |            24% |         $1,866 |        $47,641 |
| **Combined** |         100% |              |  **$56,839** |           100% |                |    **$56,118** |

**Observed:** splitting yields **$56,839**/hour vs **$55,155**/hour best solo (+$1,684/hour, +3.1%).
**Model:** splitting yields **$56,118**/hour vs **$53,130**/hour best solo (+$2,988/hour, +5.6%).

## Bundle Details

### Alamo Sea

| Bundle        | Fish                                     |   Bonus | Avg Fish to Complete | Avg Time | Bonus/Fish | Catch Rates                                                                               |
|---------------|------------------------------------------|--------:|---------------------:|---------:|-----------:|-------------------------------------------------------------------------------------------|
| Alamo Starter | Morwhong, Southern Tuna, Silver Trevally | $10,000 |                   52 |   98 min |       $192 | Morwhong: 28/496 (5.6%) \| Southern Tuna: 12/496 (2.4%) \| Silver Trevally: 23/496 (4.6%) |

### Cross-Location

| Bundle              | Fish                             |   Bonus | Avg Fish to Complete | Avg Time | Bonus/Fish | Catch Rates                                                                                                 |
|---------------------|----------------------------------|--------:|---------------------:|---------:|-----------:|-------------------------------------------------------------------------------------------------------------|
| Gold Multizone #1   | Bluefin Tuna, Musky, Dolphinfish | $12,750 |                  187 |  373 min |        $68 | Bluefin Tuna @ Alamo Sea: 4/496 (0.8%) \| Musky @ Dam: 17/341 (5.0%) \| Dolphinfish @ Roxwood: 6/255 (2.4%) |
| Low Level Multizone | Scollop, Carp, Grenadier         | $11,000 |                   57 |  120 min |       $193 | Scollop @ Alamo Sea: 52/496 (10.5%) \| Carp @ Dam: 14/341 (4.1%) \| Grenadier @ Roxwood: 11/255 (4.3%)      |

## Drop Rate Analysis

### Tier Distribution

Tier drop rates are consistent across locations, suggesting a fixed game mechanic:

| Tier        | Alamo Sea |   Dam | Roxwood | Average |
|-------------|----------:|------:|--------:|--------:|
| xxxx purple |      0.2% |  0.0% |    0.4% |    0.2% |
| xxx         |      7.3% | 10.3% |    9.0% |    8.8% |
| xx          |     27.6% | 27.9% |   24.7% |   26.7% |
| x           |     64.3% | 61.9% |   65.9% |   64.0% |

### Within-Tier Weights

Observed frequencies vs model (percentage template) per fish.
Model uses shared percentage templates across all locations (5% granularity).

#### Alamo Sea — xxx (3 fish, 36 observed)

| Fish            | Count | Observed % | Weight | Weight % | Model % | Model % (norm) | Residual |
|-----------------|------:|-----------:|-------:|---------:|--------:|---------------:|---------:|
| Silver Trevally |    23 |      63.9% |     10 |    62.5% |     55% |          55.0% |     +3.2 |
| Great Barracuda |     9 |      25.0% |      3 |    18.8% |     30% |          30.0% |     -1.8 |
| Bluefin Tuna    |     4 |      11.1% |      3 |    18.8% |     15% |          15.0% |     -1.4 |

Weight fit: χ² = 1.88, df = 2, p = 0.390 — good
Model fit (55%/30%/15%): χ² = 1.18, p = 0.554 — excellent

#### Alamo Sea — xx (6 fish, 137 observed)

| Fish             | Count | Observed % | Weight | Weight % | Model % | Model % (norm) | Residual |
|------------------|------:|-----------:|-------:|---------:|--------:|---------------:|---------:|
| Southern Garfish |    35 |      25.5% |      2 |    22.2% |     25% |          25.0% |     +0.8 |
| Trout            |    30 |      21.9% |      2 |    22.2% |     20% |          20.0% |     +2.6 |
| Blue Warehou     |    27 |      19.7% |      2 |    22.2% |     20% |          20.0% |     -0.4 |
| Snow Crab        |    17 |      12.4% |      1 |    11.1% |     15% |          15.0% |     -3.6 |
| Golden Perch     |    16 |      11.7% |      1 |    11.1% |     10% |          10.0% |     +2.3 |
| Southern Tuna    |    12 |       8.8% |      1 |    11.1% |     10% |          10.0% |     -1.7 |

Weight fit: χ² = 2.01, df = 5, p = 0.848 — excellent
Model fit (25%/20%/20%/15%/10%/10%): χ² = 1.48, p = 0.915 — excellent

#### Alamo Sea — x (7 fish, 319 observed)

| Fish      | Count | Observed % | Weight | Weight % | Model % | Model % (norm) | Residual |
|-----------|------:|-----------:|-------:|---------:|--------:|---------------:|---------:|
| Albacore  |    76 |      23.8% |     10 |    23.3% |     20% |          21.1% |     +8.8 |
| Scollop   |    52 |      16.3% |      7 |    16.3% |     15% |          15.8% |     +1.6 |
| Halibut   |    51 |      16.0% |      7 |    16.3% |     15% |          15.8% |     +0.6 |
| Broadbill |    49 |      15.4% |      7 |    16.3% |     15% |          15.8% |     -1.4 |
| Redfish   |    35 |      11.0% |      4 |     9.3% |     10% |          10.5% |     +1.4 |
| Morwhong  |    28 |       8.8% |      4 |     9.3% |     10% |          10.5% |     -5.6 |
| Flathead  |    28 |       8.8% |      4 |     9.3% |     10% |          10.5% |     -5.6 |

Weight fit: χ² = 1.37, df = 6, p = 0.968 — excellent
Model fit (20%/15%/15%/15%/10%/10%/10%/5%): χ² = 3.18, p = 0.786 — excellent

#### Dam — xxx (3 fish, 35 observed)

| Fish          | Count | Observed % | Weight | Weight % | Model % | Model % (norm) | Residual |
|---------------|------:|-----------:|-------:|---------:|--------:|---------------:|---------:|
| Musky         |    17 |      48.6% |      9 |    47.4% |     55% |          55.0% |     -2.2 |
| Pike          |    11 |      31.4% |      5 |    26.3% |     30% |          30.0% |     +0.5 |
| Rainbow Trout |     7 |      20.0% |      5 |    26.3% |     15% |          15.0% |     +1.8 |

Weight fit: χ² = 0.89, df = 2, p = 0.641 — excellent
Model fit (55%/30%/15%): χ² = 0.87, p = 0.647 — excellent

#### Dam — xx (6 fish, 95 observed)

| Fish            | Count | Observed % | Weight | Weight % | Model % | Model % (norm) | Residual |
|-----------------|------:|-----------:|-------:|---------:|--------:|---------------:|---------:|
| Atlantic Salmon |    23 |      24.2% |      8 |    22.2% |     25% |          25.0% |     -0.8 |
| Trevella        |    19 |      20.0% |      8 |    22.2% |     20% |          20.0% |     +0.0 |
| Trumpetfish     |    16 |      16.8% |      5 |    13.9% |     20% |          20.0% |     -3.0 |
| Carp            |    14 |      14.7% |      5 |    13.9% |     15% |          15.0% |     -0.2 |
| Wahoo           |    13 |      13.7% |      5 |    13.9% |     10% |          10.0% |     +3.5 |
| Sturgeon        |    10 |      10.5% |      5 |    13.9% |     10% |          10.0% |     +0.5 |

Weight fit: χ² = 1.80, df = 5, p = 0.876 — excellent
Model fit (25%/20%/20%/15%/10%/10%): χ² = 1.82, p = 0.874 — excellent

#### Dam — x (8 fish, 211 observed)

| Fish                 | Count | Observed % | Weight | Weight % | Model % | Model % (norm) | Residual |
|----------------------|------:|-----------:|-------:|---------:|--------:|---------------:|---------:|
| Murray Cod           |    51 |      24.2% |      9 |    24.3% |     20% |          20.0% |     +8.8 |
| Banded Butterflyfish |    35 |      16.6% |      5 |    13.5% |     15% |          15.0% |     +3.4 |
| Triggerfish          |    28 |      13.3% |      5 |    13.5% |     15% |          15.0% |     -3.6 |
| Sand Whiting         |    26 |      12.3% |      5 |    13.5% |     15% |          15.0% |     -5.6 |
| Cod                  |    25 |      11.8% |      5 |    13.5% |     10% |          10.0% |     +3.9 |
| Escolar              |    20 |       9.5% |      3 |     8.1% |     10% |          10.0% |     -1.1 |
| Brook Trout          |    16 |       7.6% |      3 |     8.1% |     10% |          10.0% |     -5.1 |
| Black Bream          |    10 |       4.7% |      2 |     5.4% |      5% |           5.0% |     -0.6 |

Weight fit: χ² = 2.88, df = 7, p = 0.896 — excellent
Model fit (20%/15%/15%/15%/10%/10%/10%/5%): χ² = 5.66, p = 0.580 — excellent

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
