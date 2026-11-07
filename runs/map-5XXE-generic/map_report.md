# Map without a tracker: room-508 (test_5XXE)

Room-scan poses built without a tracker (scr_map.py). Error against Polaris after one rigid alignment of the whole map on the points 1 m in front of each camera; scene points at 1 m = the error the training labels inherit; 1 s motion = error of the relative pose between frames 30 rows apart (no alignment).

| stage | frames added | mapped | scene points at 1 m, mm (median / p90) | camera position mm | rotation deg | 1 s motion mm (median / p90) | loss mm |
|---|---|---|---|---|---|---|---|
| round 1 (+ camera calibration) | 1562 | 1623/2640 (61 %) | 13.0 / 27.3 | 36.5 / 51.4 | 2.13 | 12.8 / 28.5 | 81.3 |
| round 2 (+ camera calibration) | 999 | 2622/2640 (99 %) | 11.9 / 24.8 | 25.2 / 41.8 | 1.47 | 11.3 / 28.5 | 38.2 |
| round 3 (+ camera calibration) | 2 | 2624/2640 (99 %) | 11.9 / 24.8 | 25.1 / 41.9 | 1.47 | 11.4 / 28.6 | 28.1 |
| final pass (+ camera calibration) | 2219 | 2624/2640 (99 %) | 11.3 / 21.2 | 18.0 / 31.2 | 0.99 | 8.0 / 21.6 | 28.1 |
| pose graph (+ camera calibration) | 0 | 2624/2640 (99 %) | 5.1 / 8.3 | 10.9 / 15.1 | 0.68 | 3.5 / 8.9 | 28.1 |

Camera calibration from `runs/repro/map-3XX/map.json` (fixed, not fitted here: only the alignment uses this session's Polaris) (one fixed camera-frame transform, a property of the probe; Polaris sees the marker, the map the camera): 31.7 mm, 1.51 deg. Rows marked (+ camera calibration) include it. It is not in the labels; `scr_anchor.py track` applies it when placing the US images (network trained with `train --map runs/map-5XXE-generic`, or `track --cam-calib runs/map-5XXE-generic/map.json`).

Timing (map vs Polaris s ms later, same frames; median scene points mm / rotation deg): -200: 16.9 / 1.02, -167: 14.7 / 0.89, -133: 12.3 / 0.76, -100: 10.0 / 0.66, -67: 7.9 / 0.56, -33: 6.0 / 0.50, +0: 4.9 / 0.53, +33: 5.2 / 0.53, +67: 6.9 / 0.62, +100: 9.0 / 0.74, +133: 11.2 / 0.84, +167: 13.5 / 0.96, +200: 15.7 / 1.10. Best +9 ms (no timing offset).

Labels for training: `poses_room-508.json` (`scr_anchor.py train --map runs/map-5XXE-generic`).
