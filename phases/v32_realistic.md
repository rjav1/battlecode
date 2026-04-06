# v32: Tight-Map Early Barrier Defense

## Changes

### 1. Early barrier defense on tight maps (SUCCESSFUL)
- On tight maps (area <= 625), second+ builder (id%5 != 0) places 1-2 barriers
  toward enemy starting at round 5, before rush arrives (~round 20)
- First builder (id%5 == 0) still prioritizes finding ore - no eco delay
- Barrier Ti reserve lowered to 5 on tight maps (was 20) for affordability
- Non-tight maps: barrier logic unchanged (still requires 1+ harvester)

### 2. Balanced map builder cap increase (REVERTED)
- Tried raising balanced cap from 10 to 15, and econ_cap ceiling from 10 to 15
- Result: 15 units spawned but mining unchanged (9690 both times)
- Extra builders consumed Ti on spawn costs (+20% scale each) without reaching new ore
- Root cause: all builders cluster on same ore deposits, more builders != more coverage
- Reverted to v31 values (cap 10, econ_cap ceiling 10)

## Test Results

### Face vs ladder_rush (TARGET: improve)
| Version | Winner | Buzzing Ti (mined) | ladder_rush Ti (mined) |
|---------|--------|-------------------|----------------------|
| v31 | ladder_rush | 6101 (1840) | 9967 (8700) |
| v32 | **buzzing** | **17618 (13840)** | 6283 (4970) |

WIN. Mining went from 1840 to 13840 (+652%). The rush is deflected by early barriers.

### Arena vs ladder_rush (TARGET: no regression)
| Version | Winner | Buzzing Ti (mined) | ladder_rush Ti (mined) |
|---------|--------|-------------------|----------------------|
| v31 | ladder_rush | 17220 (13690) | 16873 (15710) |
| v32 | ladder_rush | 17220 (13690) | 16873 (15710) |

Identical. Second+ builder condition (id%5!=0) prevents barriers on arena
where the rush takes longer and barriers aren't needed.

### Cold vs ladder_eco (TARGET: improve)
| Version | Winner | Buzzing Ti (mined) | ladder_eco Ti (mined) |
|---------|--------|-------------------|----------------------|
| v31 | ladder_eco | 9135 (9690) | 9679 (19530) |
| v32 | ladder_eco | 9135 (9690) | 9679 (19530) |

Identical. Builder cap increase was reverted (no help). The mining gap is
structural: ladder_eco covers both sides of cold with 40 bots. Our 10 bots
all cluster on the same ore deposits. Fixing this requires exploration
diversity, not just more builders.

### default_medium1 vs ladder_eco (regression check)
| Version | Winner | Buzzing Ti (mined) | ladder_eco Ti (mined) |
|---------|--------|-------------------|----------------------|
| v31 | ladder_eco | 5881 (4940) | 92 (4950) |
| v32 | ladder_eco | 5881 (4940) | 92 (4950) |

Identical. No regression.

## Summary
- Face vs ladder_rush: LOSS -> WIN (target met)
- Cold vs ladder_eco: unchanged (target not met - structural issue)
- No regressions on arena or default_medium1

## Deploy recommendation
YES - deploy. Face win is significant, no regressions anywhere.
Cold improvement requires a different approach (exploration diversity, not builder count).
