# HOTFIX: Emergency Revert to eco_opponent Base

**Date:** 2026-04-04
**Trigger:** v4 went 0-5 on ladder
**Action:** Reverted `bots/buzzing/main.py` to `bots/eco_opponent/main.py` (pure economy bot)

## What changed

Replaced the v4 buzzing bot (which had sentinel infrastructure, attacker roles, bridge building)
with the proven eco_opponent bot:
- Builder cap: 3 -> 5 -> 7 (conservative, matches v2 which had 50% win rate)
- Pure economy: no military, no sentinels, no attackers
- Conveyor chains using `d.opposite()` (proven Ti delivery)

## Test result

```
Match: buzzing vs starter on default_medium1
Winner: buzzing (Resources tiebreak, turn 2000)
Titanium: 22,347 total (19,390 mined)
Units: 7
Buildings: 167
```

Ti mined ~19.4K (total 22.3K including starting resources). Bot is functional and mining well.

## Status

- [x] eco_opponent copied to buzzing
- [x] Test passed (buzzing wins vs starter)
- [ ] Submission (not a git repo -- needs manual `cambc.bat submit bots/buzzing/`)
- [ ] Git commit/push (repo not initialized)

## Notes

- This is NOT a git repository, so git commit/push steps could not be executed
- Manual submission via `.\cambc.bat submit bots/buzzing/` still needed
