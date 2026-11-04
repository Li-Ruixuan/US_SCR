# Map without a tracker: room-301, room-302 (train_3XX)

Room-scan poses built without a tracker (scr_map.py). Error against Polaris after one rigid alignment of the whole map on the points 1 m in front of each camera; scene points at 1 m = the error the training labels inherit; 1 s motion = error of the relative pose between frames 30 rows apart (no alignment).

| stage | frames added | mapped | scene points at 1 m, mm (median / p90) | camera position mm | rotation deg | 1 s motion mm (median / p90) | loss mm |
|---|---|---|---|---|---|---|---|
| round 1 (+ camera calibration) | 3037 | 3098/3356 (92 %) | 9.5 / 27.8 | 11.3 / 30.5 | 1.01 | 9.3 / 31.4 | 73.9 |
| round 2 (+ camera calibration) | 258 | 3356/3356 (100 %) | 9.8 / 26.2 | 11.0 / 30.1 | 1.05 | 9.6 / 30.4 | 44.1 |
| final pass (+ camera calibration) | 3343 | 3356/3356 (100 %) | 6.7 / 12.7 | 9.5 / 18.2 | 0.89 | 5.8 / 16.9 | 44.1 |
| pose graph (+ camera calibration) | 0 | 3356/3356 (100 %) | 2.6 / 5.4 | 2.0 / 4.1 | 0.19 | 1.5 / 3.7 | 44.1 |
| re-aligned |  | 3356/3356 (100 %) | 6.4 / 12.1 | 10.4 / 13.2 | 0.63 | 3.4 / 8.4 |  |

Timing (map vs Polaris s ms later, same frames; median scene points mm / rotation deg): -200: 24.8 / 1.74, -167: 21.3 / 1.51, -133: 17.9 / 1.29, -100: 14.7 / 1.09, -67: 11.4 / 0.89, -33: 8.4 / 0.73, +0: 6.4 / 0.63, +33: 6.9 / 0.65, +67: 9.3 / 0.75, +100: 11.9 / 0.90, +133: 15.1 / 1.08, +167: 18.4 / 1.29, +200: 22.0 / 1.50. Best +10 ms (no timing offset).

Labels for training: `poses_room-301.json`, `poses_room-302.json` (`scr_anchor.py train --map runs/repro/map-3XX-nocalib`).
