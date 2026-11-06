# Map without a tracker: room-504 (test_5XXB)

Room-scan poses built without a tracker (scr_map.py). Error against Polaris after one rigid alignment of the whole map on the points 1 m in front of each camera; scene points at 1 m = the error the training labels inherit; 1 s motion = error of the relative pose between frames 30 rows apart (no alignment).

| stage | frames added | mapped | scene points at 1 m, mm (median / p90) | camera position mm | rotation deg | 1 s motion mm (median / p90) | loss mm |
|---|---|---|---|---|---|---|---|
| round 1 (+ camera calibration) | 0 | 3/2562 (0 %) | 90.4 / 93.1 | 51.3 / 62.3 | 9.98 | - / - | 56.6 |
| final pass (+ camera calibration) | 3 | 3/2562 (0 %) | 95.2 / 97.5 | 51.8 / 61.1 | 10.06 | - / - | 56.6 |
| pose graph (+ camera calibration) | 0 | 3/2562 (0 %) | 102.0 / 105.1 | 52.0 / 63.3 | 10.56 | - / - | 56.6 |

Camera calibration from `runs/repro/map-3XX/map.json` (fixed, not fitted here: only the alignment uses this session's Polaris) (one fixed camera-frame transform, a property of the probe; Polaris sees the marker, the map the camera): 31.7 mm, 1.51 deg. Rows marked (+ camera calibration) include it. It is not in the labels; `scr_anchor.py track` applies it when placing the US images (network trained with `train --map runs/map-5XXB-generic`, or `track --cam-calib runs/map-5XXB-generic/map.json`).

Labels for training: `poses_room-504.json` (`scr_anchor.py train --map runs/map-5XXB-generic`).
