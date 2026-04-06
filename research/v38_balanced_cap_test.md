# v38 Balanced Cap Test: cap 10 → 14

## Change
`bots/buzzing/main.py` line 98: balanced map builder cap final value raised from 10 to 14.

```python
# Before
cap = 3 if rnd <= 25 else (5 if rnd <= 100 else (8 if rnd <= 300 else 10))
# After
cap = 3 if rnd <= 25 else (5 if rnd <= 100 else (8 if rnd <= 300 else 14))
```

## Motivation
time_floor for balanced maps = min(6+rnd//150, 12). At rnd 900, time_floor=12, but old cap=10
capped econ_cap at 10. Raising cap to 14 lets econ_cap actually reach 12 in late game.

## Test Results (buzzing v38 vs buzzing_prev)

| Map | Winner | buzzing Ti | buzzing_prev Ti | buzzing Units | buzzing_prev Units |
|-----|--------|-----------|----------------|--------------|-------------------|
| default_medium1 | **buzzing** | 10527 (9380 mined) | 7016 (4950 mined) | 12 | 10 |
| cold | buzzing_prev | 17782 (19670 mined) | **19350 (19700 mined)** | 13 | 10 |
| hourglass | buzzing_prev | 12505 (19850 mined) | **8763 (23970 mined)** | 14 | 10 |

## Analysis

**default_medium1 (W):** Cap increase helps — buzzing builds 2 extra units, mines significantly more ore (+4430 Ti), wins by +3511 Ti.

**cold (L):** Buzzing builds 3 extra units, 53 extra buildings, but delivers *less* titanium (−1568). More builders → higher cost scaling → Ti spent on infrastructure doesn't yield proportional throughput gain on this map.

**hourglass (L):** Buzzing builds 4 extra units, *fewer* buildings (213 vs 257), but mines and delivers far less Ti. The extra builders apparently aren't finding productive ore routes on this map layout.

## Verdict

**Mixed results — do NOT ship as-is.** 

The cap=14 helps on open maps with accessible ore (default_medium1) but hurts on constrained/cold maps where extra builders inflate cost scaling without proportional output. The pattern suggests the issue isn't the cap per se, but the bot's ability to route builders productively. Consider:

1. Only raise cap if visible ore ratio is high
2. Or cap at 12 (matching time_floor ceiling) rather than 14
3. Or gate the raise on `map_mode` (tight vs balanced) more carefully

## Status
NOT submitted. v37 still running on ladder to accumulate matches.
