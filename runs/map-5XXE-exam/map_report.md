# Map without a tracker: room-509 (test_5XXE)

Room-scan poses built without a tracker (scr_map.py). Error against Polaris after one rigid alignment of the whole map on the points 1 m in front of each camera; scene points at 1 m = the error the training labels inherit; 1 s motion = error of the relative pose between frames 30 rows apart (no alignment).

| stage | frames added | mapped | scene points at 1 m, mm (median / p90) | camera position mm | rotation deg | 1 s motion mm (median / p90) | loss mm |
|---|---|---|---|---|---|---|---|
| round 1 (+ camera calibration) | 1556 | 1617/1795 (90 %) | 11.5 / 28.9 | 30.2 / 45.1 | 1.55 | 8.4 / 17.3 | 83.4 |
| round 2 (+ camera calibration) | 178 | 1795/1795 (100 %) | 12.2 / 27.8 | 32.4 / 49.0 | 1.69 | 8.9 / 19.2 | 24.7 |
| final pass (+ camera calibration) | 1795 | 1795/1795 (100 %) | 10.6 / 23.8 | 29.7 / 41.4 | 1.50 | 5.7 / 12.8 | 24.7 |
| pose graph (+ camera calibration) | 0 | 1795/1795 (100 %) | 2.9 / 5.8 | 4.3 / 6.9 | 0.24 | 2.2 / 4.7 | 24.7 |

Camera calibration from `runs/repro/map-3XX/map.json` (fixed, not fitted here: only the alignment uses this session's Polaris) (one fixed camera-frame transform, a property of the probe; Polaris sees the marker, the map the camera): 31.7 mm, 1.51 deg. Rows marked (+ camera calibration) include it. It is not in the labels; `scr_anchor.py track` applies it when placing the US images (network trained with `train --map runs/map-5XXE-exam`, or `track --cam-calib runs/map-5XXE-exam/map.json`).

Timing (map vs Polaris s ms later, same frames; median scene points mm / rotation deg): -200: 8.5 / 0.48, -167: 7.4 / 0.42, -133: 6.4 / 0.37, -100: 5.4 / 0.32, -67: 4.5 / 0.29, -33: 3.5 / 0.26, +0: 2.9 / 0.25, +33: 3.5 / 0.27, +67: 4.3 / 0.30, +100: 5.2 / 0.34, +133: 6.1 / 0.39, +167: 7.1 / 0.45, +200: 8.2 / 0.51. Best +1 ms (no timing offset).

Labels for training: `poses_room-509.json` (`scr_anchor.py train --map runs/map-5XXE-exam`).
