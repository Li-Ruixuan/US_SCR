# Map without a tracker: room-507 (test_5XXC)

Room-scan poses built without a tracker (scr_map.py). Error against Polaris after one rigid alignment of the whole map on the points 1 m in front of each camera; scene points at 1 m = the error the training labels inherit; 1 s motion = error of the relative pose between frames 30 rows apart (no alignment).

| stage | frames added | mapped | scene points at 1 m, mm (median / p90) | camera position mm | rotation deg | 1 s motion mm (median / p90) | loss mm |
|---|---|---|---|---|---|---|---|
| round 1 (+ camera calibration) | 2082 | 2143/2649 (81 %) | 7.0 / 14.0 | 9.9 / 18.2 | 0.53 | 3.9 / 8.4 | 73.4 |
| round 2 (+ camera calibration) | 506 | 2649/2649 (100 %) | 9.7 / 16.1 | 14.4 / 23.3 | 0.69 | 4.3 / 12.7 | 28.7 |
| final pass (+ camera calibration) | 2648 | 2649/2649 (100 %) | 7.4 / 12.9 | 10.7 / 17.3 | 0.45 | 3.2 / 7.1 | 28.7 |
| pose graph (+ camera calibration) | 0 | 2649/2649 (100 %) | 3.3 / 5.5 | 2.2 / 8.4 | 0.27 | 1.0 / 2.9 | 28.7 |

Camera calibration from `runs/repro/map-3XX/map.json` (fixed, not fitted here: only the alignment uses this session's Polaris) (one fixed camera-frame transform, a property of the probe; Polaris sees the marker, the map the camera): 31.7 mm, 1.51 deg. Rows marked (+ camera calibration) include it. It is not in the labels; `scr_anchor.py track` applies it when placing the US images (network trained with `train --map runs/map-5XXC-exam`, or `track --cam-calib runs/map-5XXC-exam/map.json`).

Timing (map vs Polaris s ms later, same frames; median scene points mm / rotation deg): -200: 11.4 / 0.73, -167: 10.0 / 0.65, -133: 8.6 / 0.57, -100: 7.0 / 0.49, -67: 5.6 / 0.41, -33: 4.3 / 0.33, +0: 3.4 / 0.27, +33: 3.4 / 0.29, +67: 4.4 / 0.37, +100: 5.6 / 0.45, +133: 6.8 / 0.55, +167: 8.3 / 0.63, +200: 9.8 / 0.71. Best +15 ms (Polaris lags the images).

Labels for training: `poses_room-507.json` (`scr_anchor.py train --map runs/map-5XXC-exam`).
