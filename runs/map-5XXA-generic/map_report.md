# Map without a tracker: room-501 (test_5XXA)

Room-scan poses built without a tracker (scr_map.py). Error against Polaris after one rigid alignment of the whole map on the points 1 m in front of each camera; scene points at 1 m = the error the training labels inherit; 1 s motion = error of the relative pose between frames 30 rows apart (no alignment).

| stage | frames added | mapped | scene points at 1 m, mm (median / p90) | camera position mm | rotation deg | 1 s motion mm (median / p90) | loss mm |
|---|---|---|---|---|---|---|---|
| round 1 (+ camera calibration) | 2147 | 2208/2697 (82 %) | 10.3 / 17.3 | 19.7 / 34.9 | 1.08 | 13.4 / 29.7 | 71.8 |
| round 2 (+ camera calibration) | 489 | 2697/2697 (100 %) | 10.7 / 18.8 | 24.0 / 40.9 | 1.29 | 14.6 / 36.5 | 36.4 |
| final pass (+ camera calibration) | 2569 | 2697/2697 (100 %) | 8.0 / 14.9 | 21.1 / 32.7 | 1.17 | 9.4 / 27.5 | 36.4 |
| pose graph (+ camera calibration) | 0 | 2697/2697 (100 %) | 4.4 / 8.5 | 6.5 / 10.8 | 0.46 | 3.9 / 12.1 | 36.4 |

Camera calibration from `runs/repro/map-3XX/map.json` (fixed, not fitted here: only the alignment uses this session's Polaris) (one fixed camera-frame transform, a property of the probe; Polaris sees the marker, the map the camera): 31.7 mm, 1.51 deg. Rows marked (+ camera calibration) include it. It is not in the labels; `scr_anchor.py track` applies it when placing the US images (network trained with `train --map runs/map-5XXA-generic`, or `track --cam-calib runs/map-5XXA-generic/map.json`).

Timing (map vs Polaris s ms later, same frames; median scene points mm / rotation deg): -200: 21.6 / 1.40, -167: 18.3 / 1.23, -133: 15.2 / 1.06, -100: 12.0 / 0.88, -67: 8.8 / 0.71, -33: 6.1 / 0.57, +0: 4.4 / 0.46, +33: 5.3 / 0.48, +67: 8.1 / 0.60, +100: 11.3 / 0.76, +133: 14.5 / 0.92, +167: 17.8 / 1.08, +200: 21.0 / 1.26. Best +5 ms (no timing offset).

Labels for training: `poses_room-501.json` (`scr_anchor.py train --map runs/map-5XXA-generic`).
