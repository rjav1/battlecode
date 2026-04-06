# Battlecode 2026 Map Analysis -- All 38 Maps

## Executive Summary

38 maps analyzed. Key findings:

- **All maps are reachable with 8-directional movement** (diagonal squeezing through wall corners). Builder bots move in 8 directions and can build roads/conveyors on diagonal tiles, allowing paths through single-thickness wall barriers.
- **BUT 6 maps are BLOCKED with 4-directional BFS**: butterfly, landscape, pixel_forest, pls_buy_cucats_merch, sierpinski_evil, wasteland_oasis. If diagonal wall-corner movement is blocked by the engine, these become pure tiebreak maps. This needs empirical testing.
- **2 maps have PARTIAL ore access** (some ore tiles unreachable even with 8-dir): butterfly (62/94 Ti, 33/57 Ax), pixel_forest (22/26 Ti).
- **Symmetry split**: 16 rotational, 15 horizontal reflection, 7 vertical reflection.
- **Size range**: 20x20 (400 tiles) to 50x50 (2500 tiles). 8 small, 14 medium, 16 large.
- **Ore counts vary massively**: 12 (face) to 184 (starry_night). Resource-scarce maps demand efficiency; ore-rich maps reward expansion.
- **Core distances (8-dir) range from 8 (arena) to 67 (socket)**. Face and starry_night (9) are most rush-friendly.
- **Wall density**: 5.7% (settlement) to 35.6% (wasteland_oasis). High-wall maps create chokepoints and fragmentation.

---

## IMPORTANT: Connectivity Depends on Diagonal Movement

6 maps that are BLOCKED with 4-directional (cardinal) BFS become REACHABLE with 8-directional (including diagonal) BFS. Builder bots can move in all 8 directions (N, NE, E, SE, S, SW, W, NW) and can build at action radius squared = 2 (including diagonals).

**The critical question**: Can a builder bot squeeze through a diagonal gap where two wall tiles meet at corners? If yes, all maps are connected. If the engine blocks diagonal movement when both orthogonal neighbors are walls, these 6 maps have unreachable cores.

| Map | 4-dir Path | 8-dir Path | 4-dir Reach | 8-dir Reach | Notes |
|-----|-----------|-----------|-------------|-------------|-------|
| butterfly | BLOCKED | 14 | 201/784 | 626/784 | Partial ore: 62/94 Ti, 33/57 Ax |
| landscape | BLOCKED | 25 | 240/840 | 840/840 | Fully reachable with 8-dir |
| pixel_forest | BLOCKED | 38 | 208/911 | 847/911 | Partial ore: 22/26 Ti |
| pls_buy_cucats_merch | BLOCKED | 28 | 63/2161 | 2161/2161 | Fully reachable with 8-dir |
| sierpinski_evil | BLOCKED | 24 | 225/688 | 688/688 | Fully reachable with 8-dir |
| wasteland_oasis | BLOCKED | 31 | 160/1030 | 1030/1030 | Fully reachable with 8-dir |

**Strategy if blocked**: Pure economy. Harvest every ore tile on your side. Convert axionite efficiently. Win on tiebreaker (refined Ax delivered > Ti delivered > harvesters > stored Ax > stored Ti).
**Strategy if reachable via diagonal**: These maps become long-distance economy+attack maps. The diagonal squeeze paths are narrow and defensible.

---

## Master Summary Table

Core path distances shown as 8-dir / 4-dir. "8-dir" = diagonal movement allowed. "4-dir" = cardinal only.

| Map | Size | Sym | Wall% | Ti | Ax | Path 8d/4d | Nearest Ti | Nearest Ax | Regions | Classification |
|-----|------|-----|-------|----|----|-----------|------------|------------|---------|---------------|
| arena | 25x25 | rot | 6.6 | 10 | 4 | 8/12 | 6 | 3 | 1 | Rush, Scarce |
| bar_chart | 35x40 | vert | 24.3 | 20 | 8 | 19/25 | 10 | 14 | 11 | Choke, Fragment |
| battlebot | 21x29 | horiz | 21.3 | 17 | 6 | 12/12 | 6 | 25 | 3 | Choke |
| binary_tree | 41x30 | horiz | 12.6 | 30 | 24 | 20/22 | 7 | 7 | 2 | Rush, Econ |
| butterfly | 31x31 | horiz | 18.4 | 94 | 57 | 14/BLK | 3 | 13 | 10 | Econ, Fragment |
| chemistry_class | 40x40 | horiz | 7.6 | 34 | 10 | 19/29 | 9 | 19 | 1 | Econ, Choke |
| cinnamon_roll | 30x30 | rot | 18.9 | 12 | 6 | 30/52 | * | * | 7 | Choke, Fragment |
| cold | 37x37 | horiz | 7.2 | 115 | 18 | 12/28 | 10 | 11 | 1 | Econ |
| corridors | 31x31 | horiz | 18.2 | 32 | 6 | 42/46 | 4 | 30 | 1 | Choke |
| cubes | 50x50 | rot | 15.3 | 134 | 40 | 39/54 | 14 | 21 | 1 | Econ, Choke |
| default_large1 | 40x40 | rot | 7.9 | 20 | 10 | 17/48 | 6 | 8 | 1 | Mixed |
| default_large2 | 50x30 | horiz | 13.2 | 28 | 8 | 43/55 | 7 | 32 | 1 | Mixed |
| default_medium1 | 30x30 | rot | 6.4 | 20 | 6 | 9/18 | 9 | 8 | 1 | Rush |
| default_medium2 | 30x30 | horiz | 6.4 | 22 | 6 | 23/29 | 8 | 15 | 1 | Mixed |
| default_small1 | 20x20 | rot | 6.5 | 10 | 4 | 19/34 | 5 | 13 | 1 | Scarce |
| default_small2 | 21x21 | vert | 11.3 | 14 | 4 | 26/32 | 3 | 19 | 1 | Mixed |
| dna | 21x50 | rot | 8.8 | 78 | 76 | 51/59 | 8 | 8 | 1 | Econ, Elongated |
| face | 20x20 | horiz | 9.5 | 8 | 4 | 9/9 | 5 | 10 | 1 | Rush, Scarce |
| galaxy | 40x40 | rot | 8.4 | 16 | 8 | 34/68 | 4 | 15 | 1 | Mixed |
| gaussian | 35x20 | horiz | 12.1 | 12 | 4 | 18/34 | 4 | 13 | 2 | Mixed |
| git_branches | 50x35 | horiz | 16.2 | 90 | 24 | 37/37 | 17 | 33 | 16 | Econ, Fragment |
| hooks | 31x31 | rot | 12.7 | 34 | 8 | 31/46 | 14 | 21 | 1 | Econ |
| hourglass | 27x45 | vert | 13.0 | 40 | 6 | 42/42 | 5 | 20 | 3 | Econ |
| landscape | 30x30 | vert | 6.7 | 76 | 6 | 25/BLK | 15 | 17 | 3 | Econ |
| mandelbrot | 50x41 | vert | 10.6 | 117 | 24 | 38/48 | 8 | 25 | 6 | Econ, Fragment |
| minimaze | 25x25 | horiz | 23.2 | 28 | 6 | 32/40 | 10 | 25 | 1 | Choke |
| pixel_forest | 45x25 | rot | 19.0 | 26 | 11 | 38/BLK | 14 | * | 11 | Choke, Fragment |
| pls_buy_cucats_merch | 49x49 | rot | 10.0 | 60 | 20 | 28/BLK | * | * | 5 | Econ |
| settlement | 50x38 | horiz | 5.7 | 148 | 30 | 43/45 | 11 | 23 | 1 | Econ |
| shish_kebab | 20x20 | rot | 12.5 | 10 | 4 | 19/36 | 8 | * | 5 | Fragment, Scarce |
| sierpinski_evil | 31x31 | horiz | 28.4 | 21 | 8 | 24/BLK | * | * | 66 | Choke, Fragment |
| socket | 50x20 | vert | 30.2 | 42 | 24 | 67/83 | 7 | 15 | 1 | Econ, Choke, Elongated |
| starry_night | 50x41 | rot | 6.6 | 126 | 58 | 9/17 | 10 | 12 | 3 | Rush, Econ |
| thread_of_connection | 20x20 | rot | 13.5 | 34 | 8 | 33/52 | 4 | 21 | 1 | Mixed |
| tiles | 40x30 | vert | 26.5 | 42 | 32 | 31/41 | 9 | 14 | 9 | Econ, Choke, Fragment |
| tree_of_life | 39x30 | horiz | 8.3 | 26 | 6 | 30/70 | 18 | 22 | 2 | Mixed |
| wasteland | 40x40 | rot | 25.0 | 34 | 10 | 38/66 | 16 | 22 | 9 | Econ, Choke, Fragment |
| wasteland_oasis | 40x40 | rot | 35.6 | 46 | 24 | 31/BLK | 14 | * | 54 | Econ, Choke |

**Column definitions**:
- **Sym**: rot = 180-degree rotational, horiz = left-right reflection, vert = top-bottom reflection
- **Path 8d/4d**: BFS distance between cores using 8-directional / 4-directional movement. BLK = blocked.
- **Nearest Ti/Ax**: BFS distance from Core A to closest titanium/axionite tile (4-dir). * = unreachable with 4-dir.
- **Regions**: Number of disconnected non-wall areas (4-dir connectivity). 1 = fully connected.

---

## Detailed Map Analysis

### 1. arena (25x25, rotational)
- **Cores**: (8,10) and (16,14), path=12, very close
- **Resources**: 10 Ti, 4 Ax -- resource-scarce
- **Terrain**: Wide open, only 6.6% walls, single connected region
- **Ore layout**: Scattered around edges, axionite near center between cores
- **Strategy**: Rush-friendly. Short distance, open terrain. Attack early or establish harvesters fast. Scarce resources mean every ore tile is critical.

### 2. bar_chart (35x40, vertical)
- **Cores**: (9,29) and (9,10), path=25 (vertical symmetry)
- **Resources**: 20 Ti, 8 Ax -- moderate
- **Terrain**: Many vertical wall columns creating 11 separate regions, 24.3% walls
- **Chokepoints**: 111 chokepoints -- very high
- **Strategy**: Heavy chokepoint control. Vertical columns create lanes. Navigate around barriers. Ore is moderately distant (10 Ti, 14 Ax from core).

### 3. battlebot (21x29, horizontal)
- **Cores**: (4,4) and (16,4), path=12, close but enclosed
- **Resources**: 17 Ti, 6 Ax -- moderate
- **Terrain**: Both cores enclosed within a large wall boundary. 3 disconnected regions.
- **Key feature**: The outer wall creates an arena. Inner wall structures form a shield-like shape. Axionite is far (25 steps).
- **Strategy**: Arena combat. Cores are enclosed and close. Build up defenses quickly. Control the inner passages.

### 4. binary_tree (41x30, horizontal) [COMPETITIVE]
- **Cores**: (10,16) and (30,16), path=22
- **Resources**: 30 Ti, 24 Ax -- good, balanced
- **Terrain**: Tree-like branching wall structure from top to bottom. 12.6% walls, 2 regions.
- **Ore layout**: Ti at top and bottom branches, Ax on left and right sides. SEPARATED.
- **Key feature**: The tree branches create natural lanes from top to bottom.
- **Strategy**: Balanced map. Decent rush potential (path=22) with moderate economy. Control branches to access resources.

### 5. butterfly (31x31, horizontal) [COMPETITIVE]
- **Cores**: (8,24) and (22,24), 8-dir path=14, 4-dir BLOCKED
- **Resources**: 94 Ti, 57 Ax -- extremely rich, CO-LOCATED
- **Terrain**: Symmetrical butterfly wing pattern with heavy walls (18.4%). 10 fragmented regions (4-dir).
- **Key feature**: With diagonal movement, cores are reachable (path=14, short!). But 32 Ti and 24 Ax tiles remain inaccessible even with 8-dir -- they are in fully enclosed wall pockets.
- **Ore**: Ti and Ax are interleaved along wing patterns. Very close to core (3 steps to Ti). PARTIAL access: only 62/94 Ti and 33/57 Ax reachable.
- **Strategy**: If diagonals work: short rush distance (14) PLUS massive resources makes this a versatile map. If blocked: pure economy on your half.

### 6. chemistry_class (40x40, horizontal)
- **Cores**: (14,23) and (25,23), path=29
- **Resources**: 34 Ti, 10 Ax -- moderate
- **Terrain**: Central double-column wall divides map. Flask-shaped wall structures around cores. 7.6% walls but with strategic chokepoints (30).
- **Key feature**: Central wall forces units to go around. High maze ratio (2.64) means winding paths.
- **Strategy**: The central wall creates two sides with limited crossing points. Control the gaps in the central wall. Long approach required.

### 7. cinnamon_roll (30x30, rotational)
- **Cores**: (2,27) and (27,2), 8-dir path=30, 4-dir path=52, opposite corners
- **Resources**: 12 Ti, 6 Ax -- scarce
- **Terrain**: Spiral wall pattern creating concentric rings. 7 regions (4-dir), 18.9% walls.
- **Key feature**: With diagonal movement, all ore is reachable (12/12 Ti, 6/6 Ax). The spiral creates a winding path but diagonal shortcuts significantly shorten it (30 vs 52 steps).
- **Strategy**: Navigate the spiral. Scarce resources mean every ore tile matters. Long distance favors economy-first.

### 8. cold (37x37, horizontal) [COMPETITIVE]
- **Cores**: (12,14) and (24,14), path=28
- **Resources**: 115 Ti, 18 Ax -- very rich in titanium
- **Terrain**: Diamond-shaped wall enclosure. 7.2% walls, 1 region, open interior.
- **Ore layout**: Massive Ti fields at bottom half. Ax at edges. Co-located Ti/Ax.
- **Key feature**: Huge titanium deposits in southern rows. Both cores are inside the diamond, relatively close.
- **Strategy**: Economy-focused with rush option. Grab the massive Ti deposits. Moderate core distance means aggression is viable.

### 9. corridors (31x31, horizontal)
- **Cores**: (5,15) and (25,15), path=46
- **Resources**: 32 Ti, 6 Ax -- moderate Ti, low Ax
- **Terrain**: Regular grid of vertical wall columns creating corridors. 18.2% walls, 1 region.
- **Key feature**: Perfect grid pattern. Units must navigate around regularly spaced columns. High maze ratio (2.30).
- **Ore layout**: Ti at every corridor intersection. Ax clustered in center.
- **Strategy**: Navigate corridors efficiently. Long path despite moderate euclidean distance. Ore is spread throughout corridors.

### 10. cubes (50x50, rotational)
- **Cores**: (14,35) and (35,14), path=54
- **Resources**: 134 Ti, 40 Ax -- extremely rich
- **Terrain**: Largest map (2500 tiles). Various rectangular structures. 15.3% walls, 1 region.
- **Key feature**: Massive map with many structures creating rooms and passages.
- **Strategy**: Economy map. Huge ore deposits to harvest. Long distance means economy first, then gradually expand toward enemy.

### 11. default_large1 (40x40, rotational)
- **Cores**: (11,25) and (28,14), path=48
- **Resources**: 20 Ti, 10 Ax -- moderate
- **Terrain**: Curved wall creating a large C-shape. 7.9% walls, 1 region.
- **Key feature**: High maze ratio (2.38). The curved wall forces long travel despite moderate euclidean distance.
- **Strategy**: Mixed. Long path means eco-first. Moderate resources require careful harvesting.

### 12. default_large2 (50x30, horizontal)
- **Cores**: (3,16) and (46,16), path=55
- **Resources**: 28 Ti, 8 Ax -- moderate
- **Terrain**: Central wall barrier with flanking structures. 13.2% walls, 1 region.
- **Key feature**: Very long horizontal map. Cores on extreme ends. Path goes around central barrier.
- **Strategy**: Long travel distance. Economy first. Approach from multiple angles around barriers.

### 13. default_medium1 (30x30, rotational)
- **Cores**: (10,19) and (19,10), path=18
- **Resources**: 20 Ti, 6 Ax -- moderate
- **Terrain**: Open map with scattered wall clusters. 6.4% walls, 1 region.
- **Strategy**: Rush-friendly. Short path, low walls, open terrain. Standard balanced play.

### 14. default_medium2 (30x30, horizontal)
- **Cores**: (3,3) and (26,3), path=29
- **Resources**: 22 Ti, 6 Ax -- moderate
- **Terrain**: Central walls and side structures. 6.4% walls, 1 region.
- **Strategy**: Mixed. Moderate distance. Standard play.

### 15. default_small1 (20x20, rotational)
- **Cores**: (1,1) and (18,18), path=34
- **Resources**: 10 Ti, 4 Ax -- scarce
- **Terrain**: Scattered small wall clusters. 6.5% walls, 1 region.
- **Key feature**: Despite small map size, cores are in opposite corners making the path long (34 steps).
- **Strategy**: Scarce resources on a small map. Every tile matters.

### 16. default_small2 (21x21, vertical)
- **Cores**: (10,1) and (10,19), path=32
- **Resources**: 14 Ti, 4 Ax -- scarce
- **Terrain**: Diamond-shaped wall ring in center. 11.3% walls, 1 region.
- **Strategy**: Mixed. Navigate around central wall structure.

### 17. dna (21x50, rotational)
- **Cores**: (10,48) and (10,1), path=59
- **Resources**: 78 Ti, 76 Ax -- extremely rich, almost equal Ti and Ax
- **Terrain**: Double helix pattern of Ti and Ax ore intertwined with walls. Narrow (21 wide) but very tall (50).
- **Key feature**: The DNA helix pattern means Ti and Ax alternate along the strands. Highest Ax count in all maps (76)!
- **Strategy**: Economy map. The DNA structure provides abundant resources but in a narrow corridor. Axionite conversion is critical here.

### 18. face (20x20, horizontal)
- **Cores**: (5,7) and (14,7), path=9, SHORTEST IN ALL MAPS
- **Resources**: 8 Ti, 4 Ax -- most scarce
- **Terrain**: Face pattern with eyebrow walls. 9.5% walls, 1 region. Very open.
- **Strategy**: MAXIMUM RUSH. Shortest core distance in all 38 maps. Very few resources. Rush or lose.

### 19. galaxy (40x40, rotational)
- **Cores**: (4,35) and (35,4), path=68
- **Resources**: 16 Ti, 8 Ax -- low
- **Terrain**: Spiral arm pattern. 8.4% walls, 1 region. Wide open with gentle spiral walls.
- **Key feature**: Very long path (68) despite moderate map size. Spiral creates winding route.
- **Strategy**: Economy-oriented. Long distance means no rush. Limited resources require efficient harvesting.

### 20. gaussian (35x20, horizontal)
- **Cores**: (10,17) and (24,17), path=34
- **Resources**: 12 Ti, 4 Ax -- scarce
- **Terrain**: Bell curve / Gaussian distribution shape of walls. 12.1% walls, 2 regions.
- **Key feature**: High maze ratio (2.43). The bell curve wall forces zigzag paths. Cores near bottom.
- **Strategy**: Navigate around bell curve. Scarce resources favor aggression.

### 21. git_branches (50x35, horizontal) 
- **Cores**: (6,5) and (43,5), path=37
- **Resources**: 90 Ti, 24 Ax -- rich
- **Terrain**: Tree branching structure. 16.2% walls, 16 regions -- highly fragmented!
- **Key feature**: Many disconnected small regions. Main area is large (1070 tiles) but 15 smaller pockets exist.
- **Ore**: Far from cores (17 Ti, 33 Ax steps). Resources are deep in the branch structure.
- **Strategy**: Navigate branch structure to reach ore. Many dead ends and isolated pockets.

### 22. hooks (31x31, rotational) [COMPETITIVE]
- **Cores**: (3,22) and (27,8), path=46
- **Resources**: 34 Ti, 8 Ax -- moderate
- **Terrain**: Hook/J-shaped wall structures creating corridors. 12.7% walls, 1 region.
- **Key feature**: Walls create natural defensive positions. Multiple corridors with hook shapes.
- **Ore**: Far from cores (14 Ti, 21 Ax steps). Must push out to harvest.
- **Strategy**: Control corridors. Set up harvester outposts. Moderate economy with defensive positioning.

### 23. hourglass (27x45, vertical)
- **Cores**: (13,43) and (13,1), path=42
- **Resources**: 40 Ti, 6 Ax -- good Ti, low Ax
- **Terrain**: Hourglass shape. Wide at top and bottom, narrow in middle. 13.0% walls, 3 regions.
- **Key feature**: The narrow middle is a massive chokepoint. All traffic must flow through the waist.
- **Strategy**: Control the hourglass waist. Place barriers/turrets at the narrow point. Strong defensive position.

### 24. landscape (30x30, vertical) [COMPETITIVE]
- **Cores**: (3,2) and (3,27), 8-dir path=25, 4-dir BLOCKED
- **Resources**: 76 Ti, 6 Ax -- rich Ti, almost no Ax
- **Terrain**: Mountain ridge walls separate top and bottom. Central Ti highway. 6.7% walls, 3 regions (4-dir), fully connected with 8-dir.
- **Key feature**: With diagonal movement, fully reachable (all 76 Ti, 6 Ax accessible). Mountain ridges still create natural lanes.
- **Ore**: Central horizontal band has alternating Ti patterns. Very Ti-heavy. Two massive Ti highways.
- **Strategy**: Grab the Ti highways on your side. If diagonals work, you can contest the enemy's Ti deposits too.

### 25. mandelbrot (50x41, vertical)
- **Cores**: (3,39) and (3,1), path=48
- **Resources**: 117 Ti, 24 Ax -- very rich
- **Terrain**: Mandelbrot fractal boundary creates complex wall patterns. 10.6% walls, 6 regions.
- **Key feature**: Fractal geometry creates unpredictable passages. Some regions disconnected.
- **Strategy**: Economy-focused. Navigate fractal boundary carefully. Rich resources reward expansion.

### 26. minimaze (25x25, horizontal)
- **Cores**: (1,23) and (23,23), path=40
- **Resources**: 28 Ti, 6 Ax -- moderate
- **Terrain**: Maze pattern with regular corridors. 23.2% walls, 1 connected region.
- **Key feature**: True maze. Despite being fully connected, the maze creates many narrow corridors. High maze ratio (1.82).
- **Strategy**: Pathfinding is critical. Must navigate maze efficiently. Chokepoints everywhere.

### 27. pixel_forest (45x25, rotational)
- **Cores**: (41,13) and (3,11), 8-dir path=38, 4-dir BLOCKED
- **Resources**: 26 Ti, 11 Ax -- moderate
- **Terrain**: Tree/forest pixel art patterns. 19.0% walls, 11 regions (4-dir).
- **Key feature**: With 8-dir, reachable but PARTIAL ore: only 22/26 Ti accessible (4 Ti trapped). All 11 Ax reachable.
- **Strategy**: Long-distance economy map. Identify which Ti tiles are trapped and skip them. Focus on reachable ore.

### 28. pls_buy_cucats_merch (49x49, rotational)
- **Cores**: (13,17) and (35,31), 8-dir path=28, 4-dir BLOCKED
- **Resources**: 60 Ti, 20 Ax -- good
- **Terrain**: Large map with decorative pattern (merch logo). 10.0% walls, 5 regions (4-dir). Fully connected with 8-dir (all 2161 non-wall tiles reachable).
- **Key feature**: With diagonal movement, all 60 Ti and 20 Ax are reachable. Moderate distance.
- **Strategy**: Standard economy map with moderate approach distance. All resources accessible with diagonal movement.

### 29. settlement (50x38, horizontal) [COMPETITIVE]
- **Cores**: (3,24) and (46,24), path=45
- **Resources**: 148 Ti, 30 Ax -- RICHEST MAP (178 total ore)
- **Terrain**: Very open (5.7% walls, lowest!). 1 region. Town layout with building-like wall blocks.
- **Key feature**: Massive Ti deposits arranged in town rows. Ax concentrated in center. Direct path between cores.
- **Strategy**: Economy powerhouse. Grab Ti rows near your core first. Central Ax is contested. Long distance means economy-first.

### 30. shish_kebab (20x20, rotational) [COMPETITIVE]
- **Cores**: (2,2) and (17,17), 8-dir path=19, 4-dir path=36
- **Resources**: 10 Ti, 4 Ax -- scarce
- **Terrain**: Diagonal kebab/diamond shapes on a skewer. 12.5% walls, 5 regions (4-dir).
- **Key feature**: With 8-dir, all 10 Ti and 4 Ax are reachable. The diagonal gaps in diamond walls allow access. Path is much shorter (19 vs 36).
- **Strategy**: Scarce resources. With diagonal movement, it becomes a moderate-distance small map. Every ore tile is precious.

### 31. sierpinski_evil (31x31, horizontal) [COMPETITIVE]
- **Cores**: (3,15) and (27,15), 8-dir path=24, 4-dir BLOCKED
- **Resources**: 21 Ti, 8 Ax -- low
- **Terrain**: Sierpinski triangle fractal pattern. 28.4% walls, 66 regions (4-dir) -- MOST FRAGMENTED with cardinal movement. But with 8-dir, all 688 non-wall tiles are connected in 1 region.
- **Key feature**: Diagonal movement transforms this map from impossible to navigable. All 21 Ti and 8 Ax become reachable. The fractal walls create many thin barriers that diagonal movement bypasses.
- **Strategy**: With diagonals, this is a moderate-distance choke-heavy map. Without diagonals, pure passive income game. MUST test empirically.

### 32. socket (50x20, vertical)
- **Cores**: (3,18) and (3,1), path=83, LONGEST REACHABLE PATH
- **Resources**: 42 Ti, 24 Ax -- good, co-located
- **Terrain**: Dense wall maze (30.2%). Narrow vertical map. 1 connected region.
- **Key feature**: Highest maze ratio (4.88!). Path is 4.88x the euclidean distance. Maximum maze-likeness.
- **Strategy**: Extreme pathfinding challenge. Despite 1 connected region, the winding path is enormous. Patience required.

### 33. starry_night (50x41, rotational)
- **Cores**: (20,24) and (29,16), path=17
- **Resources**: 126 Ti, 58 Ax -- second richest (184 total)
- **Terrain**: Open night sky with scattered star patterns. 6.6% walls, 3 regions.
- **Key feature**: RICH and CLOSE. Short core distance (17) plus massive resources. Best of both worlds.
- **Strategy**: Rush OR economy both viable. Short distance allows aggression, abundant resources support economy. This map rewards versatile bots.

### 34. thread_of_connection (20x20, rotational)
- **Cores**: (3,16) and (16,3), path=52
- **Resources**: 34 Ti, 8 Ax -- moderate, co-located
- **Terrain**: Diagonal thread pattern connecting cores. 13.5% walls, 1 region.
- **Key feature**: Very high maze ratio (2.83). The thread creates an extremely winding path on a small map.
- **Ore**: Ti and Ax arranged along the diagonal thread.
- **Strategy**: Navigate the winding thread. Ore is along the path. Control the thread.

### 35. tiles (40x30, vertical)
- **Cores**: (1,1) and (1,28), path=41
- **Resources**: 42 Ti, 32 Ax -- good, balanced
- **Terrain**: Regular tile/grid pattern with thick walls. 26.5% walls, 9 regions.
- **Key feature**: Grid creates regular rooms connected by narrow gaps. Resources spread across rooms.
- **Strategy**: Control rooms systematically. Navigate grid. Good axionite availability.

### 36. tree_of_life (39x30, horizontal)
- **Cores**: (4,22) and (34,22), path=70
- **Resources**: 26 Ti, 6 Ax -- moderate
- **Terrain**: Tree trunk from bottom, branches spreading upward. 8.3% walls, 2 regions.
- **Key feature**: The trunk creates a major chokepoint. All paths funnel through the narrow trunk. Very high maze ratio (2.33).
- **Strategy**: Control the trunk chokepoint. Place barriers in the narrow passage. Defensive map.

### 37. wasteland (40x40, rotational)
- **Cores**: (3,36) and (36,3), path=66
- **Resources**: 34 Ti, 10 Ax -- moderate
- **Terrain**: Random-looking scattered ruins. 25.0% walls, 9 regions.
- **Key feature**: Chaotic terrain with no clear pattern. Must adapt pathfinding dynamically.
- **Strategy**: Dynamic pathfinding required. No clear lanes or patterns. Adapt to terrain.

### 38. wasteland_oasis (40x40, rotational)
- **Cores**: (8,6) and (31,33), 8-dir path=31, 4-dir BLOCKED
- **Resources**: 46 Ti, 24 Ax -- good
- **Terrain**: Dense wasteland with oasis patches. 35.6% walls -- HIGHEST WALL DENSITY. 54 regions (4-dir), but fully connected with 8-dir (all 1030 non-wall tiles reachable).
- **Key feature**: Despite extreme wall density, diagonal movement connects everything. All 46 Ti and 24 Ax reachable.
- **Strategy**: Navigate through diagonal gaps in wall clusters. Complex pathfinding but all resources are accessible.

---

## Strategic Classification Groups

### Group 1: Rush-Friendly Maps (8-dir path <= 20, low walls)
Best for aggressive bots that attack early.

| Map | Path (8d) | Ti | Ax | Notes |
|-----|-----------|----|----|-------|
| arena | 8 | 10 | 4 | Shortest 8-dir path! Very open. Rush. |
| face | 9 | 8 | 4 | Tied shortest, minimum resources. Rush or die. |
| default_medium1 | 9 | 20 | 6 | Standard rush map. |
| starry_night | 9 | 126 | 58 | Close cores + massive resources. Rush or eco. |
| battlebot | 12 | 17 | 6 | Enclosed arena. Close cores within walls. |
| cold | 12 | 115 | 18 | Close cores + Ti-rich. Rush or economy. |
| butterfly | 14 | 94 | 57 | Short IF diagonals work. Partial ore. |
| default_large1 | 17 | 20 | 10 | Surprisingly short with diagonals! |
| gaussian | 18 | 12 | 4 | Bell curve walls, scarce resources. |
| bar_chart | 19 | 20 | 8 | Vertical lanes. |
| chemistry_class | 19 | 34 | 10 | Central wall divider but short diagonal path. |
| shish_kebab | 19 | 10 | 4 | Short with diagonals, resource-scarce. |
| binary_tree | 20 | 30 | 24 | Moderate rush, branching terrain. |

### Group 2: Economy Maps (ore > 60, large map)
Best for bots that build harvester networks.

| Map | Size | Ti | Ax | Total | Notes |
|-----|------|----|----|-------|-------|
| starry_night | 50x41 | 126 | 58 | 184 | Richest reachable map |
| settlement | 50x38 | 148 | 30 | 178 | Most Ti tiles, very open |
| cubes | 50x50 | 134 | 40 | 174 | Largest map, massive resources |
| dna | 21x50 | 78 | 76 | 154 | Most Ax tiles, narrow corridor |
| butterfly | 31x31 | 94 | 57 | 151 | BLOCKED - pure eco |
| mandelbrot | 50x41 | 117 | 24 | 141 | Fractal terrain |
| cold | 37x37 | 115 | 18 | 133 | Diamond enclosure, Ti-rich |
| git_branches | 50x35 | 90 | 24 | 114 | Branching, fragmented |

### Group 3: Chokepoint/Maze Maps (wall% > 15 or maze ratio > 2)
Best for defensive bots that control narrow passages.

| Map | Wall% | Maze Ratio | Chokes | Notes |
|-----|-------|------------|--------|-------|
| wasteland_oasis | 35.6 | BLOCKED | 432 | Extreme maze, blocked |
| socket | 30.2 | 4.88 | 90 | Most maze-like reachable map |
| sierpinski_evil | 28.4 | BLOCKED | 195 | Fractal, blocked |
| tiles | 26.5 | 1.52 | 40 | Grid rooms |
| wasteland | 25.0 | 1.41 | 268 | Chaotic ruins |
| bar_chart | 24.3 | 1.32 | 111 | Vertical lanes |
| minimaze | 23.2 | 1.82 | 47 | True maze |
| corridors | 18.2 | 2.30 | 0 | Regular grid corridors |
| thread_of_connection | 13.5 | 2.83 | 0 | Winding thread |
| chemistry_class | 7.6 | 2.64 | 30 | Central wall divider |

### Group 4: Diagonal-Dependent Maps (blocked with 4-dir, open with 8-dir)
These maps are ONLY reachable if diagonal movement through wall corners works. Must test!

| Map | 8d Path | Ti Access (8d) | Ax Access (8d) | 4-dir Status |
|-----|---------|----------------|----------------|-------------|
| butterfly | 14 | 62/94 PARTIAL | 33/57 PARTIAL | BLOCKED |
| landscape | 25 | 76/76 full | 6/6 full | BLOCKED |
| pixel_forest | 38 | 22/26 PARTIAL | 11/11 full | BLOCKED |
| pls_buy_cucats_merch | 28 | 60/60 full | 20/20 full | BLOCKED |
| sierpinski_evil | 24 | 21/21 full | 8/8 full | BLOCKED |
| wasteland_oasis | 31 | 46/46 full | 24/24 full | BLOCKED |

**Note**: butterfly and pixel_forest have PARTIAL ore access even with 8-directional movement. Some ore tiles are fully enclosed by walls with no diagonal gaps.

### Group 5: Scarce Resource Maps (total ore <= 18)
Every resource tile is precious. Mistakes are costly.

| Map | Ti | Ax | Path | Notes |
|-----|----|----|------|-------|
| face | 8 | 4 | 9 | Rush map, minimum resources |
| arena | 10 | 4 | 12 | Rush + scarce |
| shish_kebab | 10 | 4 | 36 | Some Ax trapped in walls |
| default_small1 | 10 | 4 | 34 | Corner-to-corner |
| cinnamon_roll | 12 | 6 | 52 | Spiral, some ore unreachable |
| gaussian | 12 | 4 | 34 | Bell curve walls |

---

## Strategic Recommendations by Map Category

### For Rush-Friendly Maps
- Spawn builder bots immediately
- Build roads toward enemy core
- Place gunners along approach path
- Minimize harvester investment -- you may not need economy if you can destroy core quickly
- On face: ALL-IN rush is optimal. 9-step path means contact by turn ~15-20

### For Economy Maps
- Build harvesters on nearest ore immediately
- Establish conveyor networks to transport ore back to core
- Convert axionite to titanium at optimal rate (4:1 ratio)
- Expand harvester network outward
- Only build military units if enemy approaches
- On BLOCKED maps: build harvesters everywhere, no military needed at all

### For Maze/Chokepoint Maps
- Identify narrow passages and fortify them with barriers + gunners
- Use BFS pathfinding -- direct-line movement will fail
- Place sentinels at chokepoints (32 vision radius sq covers corridors well)
- Build barriers to block enemy advancement
- Socket: be patient, path is 83 steps long

### For Diagonal-Dependent Maps
- CRITICAL: At game start, do an 8-directional BFS from core to check if enemy core is reachable
- If reachable via diagonals: treat as normal map with moderate-long distance
- If blocked (engine prevents diagonal squeeze): switch to pure economy mode
- butterfly/pixel_forest: some ore is in fully enclosed pockets even with 8-dir -- skip those
- Build harvesters on ALL reachable ore tiles
- For tiebreaker scoring: refined_axionite_delivered is checked FIRST, then titanium_delivered

### For Scarce Resource Maps
- Prioritize titanium ore (passive income only gives 10 Ti per 4 turns)
- Minimize building costs -- each unit's cost scales with count
- Consider converting axionite to titanium for military advantage (4 Ti per Ax)
- On face/arena: with 8-dir path of 8-9 steps, rush is almost mandatory

---

## Symmetry Analysis and Implications

### Rotational (16 maps)
arena, cinnamon_roll, cubes, default_large1, default_medium1, default_small1, dna, galaxy, hooks, pixel_forest, pls_buy_cucats_merch, shish_kebab, starry_night, thread_of_connection, wasteland, wasteland_oasis

- Core at (x1,y1), enemy core at (w-1-x1, h-1-y1)
- Mirror your strategy: if you go northeast, enemy goes southwest
- Ore distribution is 180-degree symmetric

### Horizontal Reflection (15 maps)
bar_chart (actually vertical file layout), battlebot, binary_tree, butterfly, chemistry_class, cold, corridors, default_large2, default_medium2, gaussian, git_branches, minimaze, settlement, sierpinski_evil, tree_of_life

- Core at (x1,y1), enemy core at (w-1-x1, y1)
- Left-right mirror. If you expand left, enemy can mirror by expanding right
- Vertical approach lanes are symmetric

### Vertical Reflection (7 maps)
bar_chart, default_small2, hourglass, landscape, mandelbrot, socket, tiles

- Core at (x1,y1), enemy core at (x1, h-1-y1)
- Top-bottom mirror. Maps tend to be vertically oriented
- Horizontal approach needed

---

## Maps to ESPECIALLY Test On (Hardest/Trickiest)

### Tier 1 -- Must Test (will break naive bots)
1. **sierpinski_evil** -- 28.4% walls, fractal pattern. Blocked without diagonals. Tests diagonal movement handling.
2. **butterfly** -- Partial ore access (62/94 Ti, 33/57 Ax reachable). Tests handling unreachable ore tiles.
3. **face** -- Path=9 (8-dir), minimum resources. Must handle ultra-aggressive rush games.
4. **socket** -- Path=67 (8-dir), highest wall density among connected maps. Extreme pathfinding.
5. **wasteland_oasis** -- 35.6% walls, path=31 with diagonals. Complex terrain navigation.
6. **pixel_forest** -- Partial ore access (22/26 Ti). Tests skipping unreachable ore.

### Tier 2 -- Important Edge Cases
7. **starry_night** -- Path=9 (8-dir) + 184 ore tiles. Rush AND economy both viable. Tests strategic decision-making.
8. **dna** -- 21-wide corridor with 76 Ax and 78 Ti. Narrow elongated map stress test.
9. **corridors** -- Perfect grid pattern. Tests ability to navigate regular obstacles.
10. **cinnamon_roll** -- Spiral pattern, scarce resources (12 Ti, 6 Ax). Winding paths.
11. **cubes** -- Largest map (50x50), 174 ore tiles. Performance and scale test.
12. **tiles** -- Grid of rooms (26.5% walls). Systematic room clearing.

### Tier 3 -- Competitive Featured Maps
13. **cold** -- Featured. 115 Ti, path=12 (8-dir). Ti-rich, moderate distance. Rush+eco.
14. **settlement** -- Featured. 148 Ti + 30 Ax. Richest map, very open.
15. **binary_tree** -- Featured. 30 Ti + 24 Ax. Branching terrain, balanced resources.
16. **hooks** -- Featured. 34 Ti, path=31. Corridor control with hook-shaped walls.
17. **landscape** -- Featured. 76 Ti, diagonal-dependent. Ti-focused.
18. **shish_kebab** -- Featured. Scarce (10 Ti, 4 Ax), small map with diamond patterns.

---

## Resource Conversion Strategy Guide

Axionite converts to titanium at 4:1 ratio (4 Ti per 1 Ax).

- **High Ax maps** (dna=76, starry_night=58, butterfly=57, cubes=40): Axionite harvesting + conversion is critical for winning tiebreaks
- **Low Ax maps** (shish_kebab=4, face=4, default_small1=4): Focus on Ti, minimal Ax investment
- **Balanced maps** (tiles Ti=42/Ax=32, binary_tree Ti=30/Ax=24): Harvest both equally

For tiebreak scoring: final_score = titanium_held + 4 * refined_axionite_held. This means 1 Ax tile is worth as much as 4 Ti tiles for tiebreak purposes, but you also need Ti to BUILD things.

---

## Map Format Reference

The .map26 files use Protocol Buffers encoding:
- Field 1 (varint): map width
- Field 2 (varint): map height  
- Field 3 (repeated, length-delimited): rows, each containing a sub-field 1 (bytes) with cell values
  - Cell values: 0=empty, 1=wall, 2=titanium_ore, 3=axionite_ore
- Field 4 (repeated, length-delimited): core definitions
  - Sub-field 1 (varint): team (1=A, 2=B)
  - Sub-field 2 (varint): unknown (always 0 or 1)
  - Sub-field 3 (length-delimited): position {field 1=x, field 2=y} -- center of 3x3 core
- Field 5 (varint): symmetry type (0=rotational, 1=horizontal, 2=vertical)

---

## Quick-Reference: Map Selection for Best-of-5

In best-of-5, maps are selected from the pool. Your bot needs to handle ALL map types. Here is the priority testing matrix:

| Capability | Critical Maps | If you fail here... |
|------------|---------------|---------------------|
| Diagonal movement handling | sierpinski_evil, butterfly, landscape, pixel_forest, pls_buy_cucats_merch, wasteland_oasis | Wrong strategy on 16% of maps |
| Partial ore detection | butterfly (62/94 Ti), pixel_forest (22/26 Ti) | Waste time pathfinding to unreachable ore |
| Rush strategy (path <= 12) | face, arena, starry_night, cold, default_medium1, battlebot | Lose to aggressive opponents on close maps |
| Economy mode | settlement, cubes, dna, cold, starry_night (all 100+ ore) | Lose tiebreaker on resource-rich maps |
| Maze pathfinding | socket (67 steps), corridors (42), wasteland_oasis (31) | Units get stuck and waste turns |
| Chokepoint defense | hourglass, tree_of_life, chemistry_class | Enemy rushes through undefended passages |
| Small scarce maps | face (8 Ti), arena (10 Ti), shish_kebab (10 Ti) | Run out of resources with no recovery |
| Large map efficiency | cubes (50x50), settlement (50x38), mandelbrot (50x41) | Timeout or poor performance |
| Tiebreaker optimization | All maps -- game reaches turn 2000 | Lose close games. Refined Ax > Ti > Harvesters |

### Tiebreaker Priority (from GAME_REFERENCE.md)
1. Total refined axionite DELIVERED to core
2. Total titanium DELIVERED to core
3. Number of living harvesters
4. Total axionite currently stored
5. Total titanium currently stored
6. Random coinflip

**Key insight**: Refined axionite delivered is checked BEFORE titanium. Each Ax converted removes 1 from "Ax delivered" and adds 4 to "Ti delivered". So do NOT convert Ax if you expect tiebreak -- keep Ax delivered high.
