# Map without a tracker: room-504 (test_5XXB)

Room-scan poses built without a tracker (scr_map.py). Error against Polaris after one rigid alignment of the whole map on the points 1 m in front of each camera; scene points at 1 m = the error the training labels inherit; 1 s motion = error of the relative pose between frames 30 rows apart (no alignment).

| stage | frames added | mapped | scene points at 1 m, mm (median / p90) | camera position mm | rotation deg | 1 s motion mm (median / p90) | loss mm |
|---|---|---|---|---|---|---|---|
| round 1 (+ camera calibration) | 2179 | 2266/2562 (88 %) | 6.0 / 13.3 | 8.2 / 17.0 | 0.62 | 6.2 / 12.1 | 75.7 |
| round 2 (+ camera calibration) | 296 | 2562/2562 (100 %) | 6.6 / 13.1 | 9.5 / 16.8 | 0.68 | 6.4 / 12.8 | 25.1 |
| final pass (+ camera calibration) | 2558 | 2562/2562 (100 %) | 4.9 / 11.2 | 7.1 / 13.9 | 0.51 | 3.1 / 9.1 | 25.1 |
| pose graph (+ camera calibration) | 0 | 2562/2562 (100 %) | 3.2 / 6.1 | 2.2 / 4.1 | 0.28 | 1.3 / 3.2 | 25.1 |

Camera calibration from `runs/repro/map-3XX/map.json` (fixed, not fitted here: only the alignment uses this session's Polaris) (one fixed camera-frame transform, a property of the probe; Polaris sees the marker, the map the camera): 31.7 mm, 1.51 deg. Rows marked (+ camera calibration) include it. It is not in the labels; `scr_anchor.py track` applies it when placing the US images (network trained with `train --map runs/map-5XXB-generic`, or `track --cam-calib runs/map-5XXB-generic/map.json`).

Timing (map vs Polaris s ms later, same frames; median scene points mm / rotation deg): -200: 14.7 / 0.93, -167: 12.5 / 0.81, -133: 10.5 / 0.69, -100: 8.5 / 0.57, -67: 6.4 / 0.46, -33: 4.4 / 0.35, +0: 3.3 / 0.27, +33: 3.8 / 0.31, +67: 5.3 / 0.39, +100: 7.1 / 0.50, +133: 9.0 / 0.62, +167: 11.0 / 0.75, +200: 13.0 / 0.88. Best +6 ms (no timing offset).

Labels for training: `poses_room-504.json` (`scr_anchor.py train --map runs/map-5XXB-generic`).
