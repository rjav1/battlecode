# v10 Results: Map-Size Adaptation

## Change Made
Added map detection on round 1 in `_core`, setting `self.map_mode` to "tight" / "balanced" / "expand"
based on map area (<=625 / 625-1600 / >=1600). Builder cap now uses mode-specific scaling instead of
the previous flat schedule.

## Regression Tests (buzzing vs buzzing_prev)

| Map            | Winner  | Ti mined (new) | Ti mined (prev) | Notes                        |
|----------------|---------|----------------|-----------------|------------------------------|
| default_medium1 | buzzing | 23530          | 7070            | balanced mode, big economy gap |
| hourglass       | buzzing | 24110          | 24000           | expand mode, close tiebreak  |
| settlement      | buzzing | 19660          | 17910           | expand/balanced mode         |
| corridors       | buzzing | 9930           | 9930            | tight mode, small map — tie broken by resources |
| face            | buzzing | 18970          | 16030           | balanced mode                |

Result: **5/5 wins**. Required: 3/5.

## Self-Play Crash Test
`buzzing vs buzzing` on `default_medium1` — no crash. Ti mined: 23530.

## Ti Mined Check (medium+ maps)
- default_medium1: 23530 (PASS)
- hourglass: 24110 (PASS)
- settlement: 19660 (PASS)
- face: 18970 (PASS)
- corridors: 9930 (tight map — small map exception per checklist)

## Submission
Submitted successfully as **Version 10** (ID: 81300456-784c-4791-84b5-0f244cdb9114)

## Files Changed
- `bots/buzzing/main.py` — map detection + mode-based builder cap in `_core`
- `bots/buzzing_prev/main.py` — saved v9 baseline
