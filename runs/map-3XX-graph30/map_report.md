# Map without a tracker: room-301, room-302 (train_3XX)

Room-scan poses built without a tracker (scr_map.py). Error against Polaris after one rigid alignment of the whole map on the points 1 m in front of each camera; scene points at 1 m = the error the training labels inherit; 1 s motion = error of the relative pose between frames 30 rows apart (no alignment).

| stage | frames added | mapped | scene points at 1 m, mm (median / p90) | camera position mm | rotation deg | 1 s motion mm (median / p90) | loss mm |
|---|---|---|---|---|---|---|---|
| round 1 | 2887 | 2948/3356 (88 %) | - / - | 12.7 / 33.7 | 23.31 | 9.2 / 31.5 | 74.1 |
| round 2 | 408 | 3356/3356 (100 %) | - / - | 12.9 / 32.7 | 23.47 | 9.5 / 32.8 | 42.3 |
| final pass | 3349 | 3356/3356 (100 %) | - / - | 8.4 / 16.6 | 17.25 | 6.1 / 17.3 | 42.3 |
| refined | 0 | 3356/3356 (100 %) | - / - | 8.9 / 16.9 | 17.45 | 7.2 / 18.5 | 22.1 |
| re-aligned |  | 3356/3356 (100 %) | 9.0 / 16.0 | 15.3 / 23.5 | 0.93 | 7.2 / 18.5 |  |
| pose graph (from map-3XX) |  | 3356/3356 (100 %) | 7.3 / 12.6 | 12.2 / 16.1 | 0.80 | 3.4 / 8.4 |  |

Stages without scene-point errors were aligned on camera positions only (before 3 Nov): their rotation and position errors include an alignment error.

Labels for training: `poses_room-301.json`, `poses_room-302.json` (`scr_anchor.py train --label-poses`).
