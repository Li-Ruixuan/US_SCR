# Map without a tracker: room-403, room-404 (test_4XXB)

Room-scan poses built without a tracker (scr_map.py). Error against Polaris after one rigid alignment of the whole map on the points 1 m in front of each camera; scene points at 1 m = the error the training labels inherit; 1 s motion = error of the relative pose between frames 30 rows apart (no alignment).

| stage | frames added | mapped | scene points at 1 m, mm (median / p90) | camera position mm | rotation deg | 1 s motion mm (median / p90) | loss mm |
|---|---|---|---|---|---|---|---|
| round 1 (+ camera calibration) | 2320 | 2381/2381 (100 %) | 10.6 / 22.3 | 13.3 / 23.0 | 1.09 | 8.2 / 24.8 | 64.4 |
| final pass (+ camera calibration) | 1863 | 2381/2381 (100 %) | 10.1 / 20.8 | 12.6 / 21.5 | 1.00 | 8.0 / 20.8 | 64.4 |
| pose graph (+ camera calibration) | 0 | 2381/2381 (100 %) | 3.1 / 6.0 | 3.0 / 4.2 | 0.27 | 1.4 / 3.0 | 64.4 |

Camera calibration from `runs/repro/map-3XX/map.json` (fixed, not fitted here: only the alignment uses this session's Polaris) (one fixed camera-frame transform, a property of the probe; Polaris sees the marker, the map the camera): 31.7 mm, 1.51 deg. Rows marked (+ camera calibration) include it. It is not in the labels; `scr_anchor.py track` applies it when placing the US images (network trained with `train --map runs/map-4XXB`, or `track --cam-calib runs/map-4XXB/map.json`).

Camera calibration fitted here on one scan alone, errors on the other scan(s) (held out, median): from room-403: 32.6 mm, 1.98 deg -> scene points 3.0 mm, camera 1.7 mm; from room-404: 30.9 mm, 1.96 deg -> scene points 3.2 mm, camera 1.7 mm. Similar values from each scan = a property of the probe; different values = the map's own error.

Timing (map vs Polaris s ms later, same frames; median scene points mm / rotation deg): -200: 23.3 / 1.30, -167: 19.6 / 1.10, -133: 15.8 / 0.90, -100: 12.3 / 0.71, -67: 8.7 / 0.53, -33: 5.3 / 0.36, +0: 3.1 / 0.27, +33: 4.6 / 0.36, +67: 8.0 / 0.53, +100: 11.4 / 0.73, +133: 15.1 / 0.92, +167: 18.9 / 1.13, +200: 22.6 / 1.34. Best +3 ms (no timing offset).

Labels for training: `poses_room-403.json`, `poses_room-404.json` (`scr_anchor.py train --map runs/map-4XXB`).
