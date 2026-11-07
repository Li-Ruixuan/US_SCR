# Map without a tracker: room-503 (test_5XXA)

Room-scan poses built without a tracker (scr_map.py). Error against Polaris after one rigid alignment of the whole map on the points 1 m in front of each camera; scene points at 1 m = the error the training labels inherit; 1 s motion = error of the relative pose between frames 30 rows apart (no alignment).

| stage | frames added | mapped | scene points at 1 m, mm (median / p90) | camera position mm | rotation deg | 1 s motion mm (median / p90) | loss mm |
|---|---|---|---|---|---|---|---|
| round 1 (+ camera calibration) | 1681 | 1742/1763 (99 %) | 9.7 / 20.5 | 15.6 / 30.9 | 0.86 | 8.1 / 19.2 | 66.8 |
| round 2 (+ camera calibration) | 21 | 1763/1763 (100 %) | 9.8 / 20.5 | 15.9 / 31.2 | 0.88 | 8.1 / 19.2 | 24.2 |
| final pass (+ camera calibration) | 1763 | 1763/1763 (100 %) | 7.2 / 17.5 | 12.9 / 24.1 | 0.67 | 4.7 / 12.2 | 24.2 |
| pose graph (+ camera calibration) | 0 | 1763/1763 (100 %) | 3.1 / 6.4 | 2.0 / 4.4 | 0.18 | 1.8 / 4.3 | 24.2 |

Camera calibration from `runs/repro/map-3XX/map.json` (fixed, not fitted here: only the alignment uses this session's Polaris) (one fixed camera-frame transform, a property of the probe; Polaris sees the marker, the map the camera): 31.7 mm, 1.51 deg. Rows marked (+ camera calibration) include it. It is not in the labels; `scr_anchor.py track` applies it when placing the US images (network trained with `train --map runs/map-5XXA-after`, or `track --cam-calib runs/map-5XXA-after/map.json`).

Timing (map vs Polaris s ms later, same frames; median scene points mm / rotation deg): -200: 11.5 / 0.71, -167: 10.1 / 0.63, -133: 8.5 / 0.53, -100: 7.0 / 0.44, -67: 5.4 / 0.34, -33: 3.9 / 0.25, +0: 3.1 / 0.18, +33: 3.4 / 0.21, +67: 4.5 / 0.26, +100: 5.7 / 0.33, +133: 7.2 / 0.41, +167: 8.6 / 0.49, +200: 9.9 / 0.57. Best +7 ms (no timing offset).

Labels for training: `poses_room-503.json` (`scr_anchor.py train --map runs/map-5XXA-after`).
