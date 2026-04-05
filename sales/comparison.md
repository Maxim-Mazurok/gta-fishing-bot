# Location Comparison

Detected tier: 3 (Alamo Sea, Dam, Roxwood).

Bite wait by location: Alamo Sea 90s, Dam 90s, Roxwood 100s. Reel-in by location: Alamo Sea 23s, Dam 27s, Roxwood 41s.

~ = estimated (not yet observed in catch data)

| Location  | Fish Caught | $/Fish observed | $/Fish model | Available Bundles                                     | $/Fish (bundles) | $/Fish total (obs) | $/Fish total (model) | $/Hour (model) |
|-----------|------------:|----------------:|-------------:|-------------------------------------------------------|-----------------:|-------------------:|---------------------:|---------------:|
| Alamo Sea |         499 |          $1,480 |       $1,417 | Gold Multizone #1, Alamo Starter, Low Level Multizone |             $657 |             $2,137 |           **$2,074** |        $66,068 |
| Dam       |         335 |          $1,664 |       $1,664 | Gold Multizone #1, Low Level Multizone                |             $369 |             $2,033 |           **$2,033** |        $62,556 |
| Roxwood   |         256 |          $1,795 |       $1,859 | Gold Multizone #1, Low Level Multizone                |             $257 |             $2,052 |           **$2,116** |        $54,021 |

## Optimal Allocation

Optimal time split across locations to maximize total $/hour (considering both sale value and cross-location bundle completions):

| Location     | Time % (obs) | $/Fish (obs) | $/Hour (obs) | Time % (model) | $/Fish (model) | $/Hour (model) |
|--------------|-------------:|-------------:|-------------:|---------------:|---------------:|---------------:|
| Alamo Sea    |          56% |       $1,480 |      $54,823 |            50% |         $1,417 |        $52,810 |
| Dam          |          20% |       $1,664 |      $51,206 |            23% |         $1,664 |        $51,206 |
| Roxwood      |          24% |       $1,795 |      $45,823 |            27% |         $1,859 |        $47,455 |
| **Combined** |         100% |              |  **$56,592** |           100% |                |    **$55,877** |

**Observed:** splitting yields **$56,592**/hour vs **$54,823**/hour best solo (+$1,769/hour, +3.2%).
**Model:** splitting yields **$55,877**/hour vs **$52,810**/hour best solo (+$3,066/hour, +5.8%).

## Bundle Details

### Alamo Sea

| Bundle        | Fish                                     |   Bonus | Avg Fish to Complete | Avg Time | Bonus/Fish | Catch Rates                                                                               |
|---------------|------------------------------------------|--------:|---------------------:|---------:|-----------:|-------------------------------------------------------------------------------------------|
| Alamo Starter | Morwhong, Southern Tuna, Silver Trevally | $10,000 |                   53 |   99 min |       $190 | Morwhong: 28/499 (5.6%) \| Southern Tuna: 12/499 (2.4%) \| Silver Trevally: 23/499 (4.6%) |

### Cross-Location

| Bundle              | Fish                             |   Bonus | Avg Fish to Complete | Avg Time | Bonus/Fish | Catch Rates                                                                                                 |
|---------------------|----------------------------------|--------:|---------------------:|---------:|-----------:|-------------------------------------------------------------------------------------------------------------|
| Gold Multizone #1   | Bluefin Tuna, Musky, Dolphinfish | $12,750 |                  187 |  374 min |        $68 | Bluefin Tuna @ Alamo Sea: 4/499 (0.8%) \| Musky @ Dam: 17/335 (5.1%) \| Dolphinfish @ Roxwood: 6/256 (2.3%) |
| Low Level Multizone | Scollop, Carp, Grenadier         | $11,000 |                   57 |  119 min |       $194 | Scollop @ Alamo Sea: 52/499 (10.4%) \| Carp @ Dam: 14/335 (4.2%) \| Grenadier @ Roxwood: 11/256 (4.3%)      |

## Drop Rate Analysis

### Tier Distribution

Tier drop rates are consistent across locations, suggesting a fixed game mechanic:

| Tier        | Alamo Sea |   Dam | Roxwood | Average |
|-------------|----------:|------:|--------:|--------:|
| xxxx purple |      0.2% |  0.0% |    0.4% |    0.2% |
| xxx         |      7.2% | 10.1% |    9.0% |    8.8% |
| xx          |     27.5% | 28.1% |   24.6% |   26.7% |
| x           |     63.9% | 61.8% |   65.6% |   63.8% |

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
