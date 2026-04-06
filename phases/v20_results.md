# v20 Results: Prefer Ore Closer to Core

## Change
Ore tile selection now uses a weighted score balancing builder proximity and core proximity:
```python
score = builder_dist + core_dist * 2
```
Previously used only `builder_dist`. The 2x weight on core distance means builders prefer ore that minimizes conveyor chain length, while still avoiding long walks to distant ore.

## Test Results (vs buzzing_prev)

| Map             | Winner       | v20 Ti Mined | prev Ti Mined | Notes                        |
|-----------------|--------------|-------------|---------------|------------------------------|
| default_medium1 | buzzing (v20) | 25,840      | 16,000        | +62% Ti mined, clear win     |
| settlement      | buzzing (v20) | 19,570      | 0             | prev failed to mine at all   |
| face            | buzzing (v20) | 16,670      | 15,930        | narrow win, modest Ti gain   |
| cold            | buzzing_prev  | 9,950       | 14,720        | loss — cold map tight layout |
| corridors       | buzzing_prev  | 9,940       | 14,650        | loss — corridors tight/maze  |

**Result: 3/5 wins — PASS**

## Analysis
- Strong improvement on open/medium maps where multiple ore tiles visible at once — the weighted score picks shorter-chain ore effectively
- Losses on cold and corridors: these are tight/maze maps with limited ore visibility, where the builder often sees only 1-2 ore tiles anyway, so the scoring change has little effect on targeting but the walking behavior toward core-proximal ore may cause the builder to explore less efficiently on constrained layouts
- Ti mined improved significantly on default_medium1 (+62%) and settlement — confirms the hypothesis that shorter chains deliver more resources

## Decision
PASS — submitted as Version 22 (ID: df4049a1-d580-476c-910f-3ac2976f2c26)

## Commit
`a96fc17` — v20: Prefer ore closer to core -- shorter chains, faster delivery
