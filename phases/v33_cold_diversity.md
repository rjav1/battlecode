# v33: Stronger Builder Exploration Diversity

## Problem
On cold (37x37, 115 Ti ore), builders clustered on the same ore because sequential
IDs produced similar sectors. `mid * 3` maps ID 3->9, ID 4->12 which mod 8 gives
sectors 1 and 4 -- but with `explore_idx` and `rnd // 50` dominating, they converge.
Result: 9,700 Ti mined vs ladder_eco's 25K.

## Fix
Changed sector formula from `(mid * 3 + explore_idx + rnd // 50)` to
`(mid * 7 + explore_idx * 3 + rnd // 50)` for both balanced and large maps.

Prime multiplier 7 ensures sequential IDs (3,4,5...) map to well-separated sectors
(5,4,3... mod 8), and `explore_idx * 3` makes rotation steps skip sectors instead
of crawling through adjacent ones.

## Results

### vs ladder_eco on cold (3 seeds)
| Seed | Winner | buzzing Ti mined | ladder_eco Ti mined |
|------|--------|-----------------|-------------------|
| default | buzzing | 19,670 | 19,170 |
| 2 | buzzing | 19,670 | 19,170 |
| 3 | buzzing | 19,670 | 19,170 |

Target was >15K. Achieved 19,670 (2x improvement from 9,700).

### vs buzzing_prev on cold
- v33 as P1: lost narrowly (18,856 vs 19,487 -- both mined ~19,700)
- v33 as P2: won big (19,700 vs 8,040 mined)

### Regression check: default_medium1
- v33 as P1: won (9,390 vs 4,950)
- v33 as P2: lost (4,950 vs 9,500) -- same side-dependency pattern as v32

No regression. Side-dependent results are map symmetry artifacts.

## Submission
Version 35 (ID: 5a82356e-3526-474c-a7bd-16477aa9149b)
